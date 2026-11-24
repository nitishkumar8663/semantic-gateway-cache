#!/usr/bin/env python3
"""Drive the REAL gateway code over a frozen v3 workload (dev or holdout).

C1-C6 validation harness. It does NOT change the frozen scorer
(eval/score.py v3.0): that scorer simulates the gateway, and its
denylist is hardcoded v1.1, so it cannot judge denylist v1.2 in code.
This driver instead replays the frozen workload through the actual
gateway.Gateway class (imported from --gateway) with a stub upstream
and the real bge-m3 embedder, and computes the summary metrics with
the SAME definitions as score.py v3.0 (copied verbatim below, so the
numbers are comparable to the E6 baseline).

Protocol (identical to the scorer's):
  - Seed store: the live cache_store.json snapshot, real created_at.
    With --normalise, seed entries are re-embedded from normalised
    text (exactly what scorer --normalise does).
  - Workload replayed in file order (or --shuffle-seed).
  - The gateway enforces route scoping, denylist v1.2, TTL and the
    exact-match fast path itself; the driver only applies the eval
    semantics (unsafe = never hit, or ttl24 hit on an entry older
    than TTL) to the gateway's returned facts.
  - Never touches the live store or the live gateway: temp store +
    temp log, deleted afterwards.

Holdout rule: holdout runs print ONLY the summary. --detail is
refused for any workload whose filename contains "holdout": holdout
failures are never read during iteration.

Usage:
  python3 drive_gateway.py --gateway semantic_gateway/gateway.py \
      --workload eval/v3/eval_set_dev.json --threshold 0.98 \
      --seed-mode with-seed --out eval/v3/c1_dev_seed.json \
      --detail eval/v3/c1_dev_seed.jsonl
"""
import argparse
import importlib.util
import json
import math
import os
import random
import sys
import tempfile
import time
import urllib.request

OLLAMA = "http://127.0.0.1:11434"
DRIVER_VERSION = "drive_gateway.py v1.1 (v2.2-enh flags)"
DEFAULT_THRESHOLD = 0.98


def load_gateway(path):
    spec = importlib.util.spec_from_file_location("gateway_under_test", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def embed(text):
    body = json.dumps({"model": "bge-m3", "prompt": text}).encode()
    req = urllib.request.Request(
        OLLAMA + "/api/embeddings", data=body,
        headers={"Content-Type": "application/json"})
    t0 = time.monotonic()
    with urllib.request.urlopen(req, timeout=120) as r:
        data = json.load(r)
    return data["embedding"], (time.monotonic() - t0) * 1000.0


def wilson(k, n, z=1.96):
    """Wilson 95% CI. Same as scorer v3.0."""
    if n == 0:
        return None
    p = k / n
    d = 1.0 + z * z / n
    centre = (p + z * z / (2.0 * n)) / d
    half = z * math.sqrt(p * (1.0 - p) / n + z * z / (4.0 * n * n)) / d
    return [round(max(0.0, centre - half), 4),
            round(min(1.0, centre + half), 4)]


def med(xs):
    xs = sorted(xs)
    return xs[len(xs) // 2] if xs else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gateway", required=True,
                    help="path to gateway.py under test")
    ap.add_argument("--workload", required=True)
    ap.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD)
    ap.add_argument("--ttl-hours", type=float, default=24.0)
    ap.add_argument("--ttl-stable-hours", type=float, default=168.0,
                    help="E1: TTL for stable-factual entries (gateway_v3)")
    ap.add_argument("--threshold-factual", type=float, default=None,
                    help="E3: lower threshold for stable-factual queries")
    ap.add_argument("--threshold-generative", type=float, default=None,
                    help="E6: lower threshold for stable-generative queries")
    ap.add_argument("--frame-strip-factual", action="store_true",
                    help="E2: strip request frames for factual queries")
    ap.add_argument("--legacy-backfill", action="store_true",
                    help="E4: classify legacy entries at load")
    ap.add_argument("--no-generative-ttl", dest="generative_ttl",
                    action="store_false", default=True,
                    help="E5 off: creative artefacts keep 24h (v2.1)")
    ap.add_argument("--normalise", dest="normalise", action="store_true",
                    default=True)
    ap.add_argument("--no-normalise", dest="normalise", action="store_false")
    ap.add_argument("--exact", dest="exact", action="store_true", default=True)
    ap.add_argument("--no-exact", dest="exact", action="store_false")
    ap.add_argument("--denylist", dest="denylist", action="store_true",
                    default=True)
    ap.add_argument("--no-denylist", dest="denylist", action="store_false")
    ap.add_argument("--route-scoping", dest="route_scoping",
                    action="store_true", default=True)
    ap.add_argument("--no-route-scoping", dest="route_scoping",
                    action="store_false")
    ap.add_argument("--seed-mode", choices=["with-seed", "empty"],
                    default="with-seed")
    ap.add_argument("--seed-store", default=None,
                    help="seed store JSON (default: eval/sample_store.json)")
    ap.add_argument("--shuffle-seed", type=int, default=None)
    ap.add_argument("--out", required=True)
    ap.add_argument("--detail", default=None)
    args = ap.parse_args()

    is_holdout = "holdout" in os.path.basename(args.workload)
    if is_holdout and args.detail:
        raise SystemExit("holdout rule: --detail refused for holdout runs; "
                         "summary only")

    gw_mod = load_gateway(args.gateway)
    with open(args.workload, encoding="utf-8") as f:
        wl = json.load(f)
    items = wl.get("requests") or wl.get("prompts")
    if items is None:
        raise SystemExit("workload needs a 'requests' or 'prompts' list")
    if args.shuffle_seed is not None:
        indexed = list(enumerate(items))
        random.Random(args.shuffle_seed).shuffle(indexed)
    else:
        indexed = list(enumerate(items))

    # Seed store: same snapshot the scorer uses. With --normalise,
    # re-embed seed entries from normalised text (scorer --normalise
    # protocol); without it, use the stored embeddings as-is.
    seed_path = args.seed_store or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "sample_store.json")
    seed = []
    seed_ts = []
    if args.seed_mode == "with-seed":
        with open(seed_path, encoding="utf-8") as f:
            seed = json.load(f).get("entries", [])
    tmpdir = tempfile.mkdtemp(prefix="drive-gw-")
    store_path = os.path.join(tmpdir, "store.json")
    seed_entries = []
    for si, e in enumerate(seed):
        ts = e.get("created_at")
        if ts is not None:
            seed_ts.append(ts)
        emb = e["embedding"]
        norm = gw_mod.normalize_text(e["prompt"])
        if args.normalise:
            # E2: with frame stripping on, seed entries are embedded
            # from the stripped text, exactly as the gateway does.
            emb, _ms = embed(gw_mod.embedding_text(
                norm, args.frame_strip_factual))
            norm = gw_mod.embedding_text(norm, args.frame_strip_factual)
        seed_entries.append({
            "prompt": e["prompt"],
            "prompt_norm": norm,
            "output": e.get("output", ""),
            "embedding": emb,
            "created_at": ts,
            "hits": e.get("hits", 0),
            "source": "live-store-seed",
            "entry_id": f"seed-{si}",
        })
    with open(store_path, "w", encoding="utf-8") as f:
        json.dump({"entries": seed_entries}, f)

    cfg = {
        "threshold": args.threshold,
        "embedding_model": "bge-m3",
        "ollama_url": OLLAMA,
        "upstream_mode": "none",
        "upstream_model": "gemma3:4b-it-q8_0",
        "upstream_max_tokens": 48,
        "dispatcher_url": "http://127.0.0.1:18791",
        "store_path": store_path,
        "log_path": os.path.join(tmpdir, "hits.log"),
        "host": "127.0.0.1",
        "port": 18795,
        "ttl_hours": args.ttl_hours,
        "ttl_stable_hours": args.ttl_stable_hours,
        "threshold_factual": args.threshold_factual,
        "threshold_generative": args.threshold_generative,
        "frame_strip_factual": args.frame_strip_factual,
        "legacy_backfill": args.legacy_backfill,
        "generative_ttl": args.generative_ttl,
        "normalise": args.normalise,
        "exact_match": args.exact,
        "denylist_enabled": args.denylist,
        "route_scoping": args.route_scoping,
        "keep_alive": "24h",
    }
    gw = gw_mod.Gateway(cfg, embedder=gw_mod.OllamaEmbedder(
        OLLAMA, "bge-m3", keep_alive="24h"),
        upstream=lambda text: "STUB-OUTPUT")

    n = 0
    n_consulted = 0
    n_hit = 0
    n_safe_hit = 0
    n_unsafe_hit = 0
    n_stale_ttl24_hit = 0
    n_blocked_deny = 0
    n_blocked_route = 0
    n_expired_miss = 0
    n_exact = 0
    n_paraphrase = 0
    n_never_stored = 0
    by_cat = {}
    by_route = {}
    fam_seen = {}
    fam_recall_hits = {}
    emb_lat, look_lat, tot_lat = [], [], []
    first_embed_ms = None
    detail = []
    must_block_detail = []
    t_start = time.monotonic()
    ttl_s = args.ttl_hours * 3600.0

    for order, (orig_i, item) in enumerate(indexed):
        text = (item.get("text") or "").strip()
        if not text:
            continue
        cat = item.get("category", "?")
        cacheable = item.get("cacheable", "?")
        route = item.get("route", "?")
        group = item.get("group", "?")
        ts = item.get("ts")
        weight = max(1, int(item.get("real_live_n", 0) or 0))
        must_block = bool(item.get("must_block", False))
        n += 1

        res = gw.query(text, route=route, now=ts)
        consulted = res.get("blocked_by") is None
        blocked_by = res.get("blocked_by")
        if not consulted:
            if (blocked_by or "").startswith("route:"):
                n_blocked_route += 1
            elif (blocked_by or "").startswith("denylist:"):
                n_blocked_deny += 1
            rec = {"i": orig_i, "order": order, "text": text[:160],
                   "group": group, "category": cat,
                   "cacheable": cacheable, "route": route,
                   "request_ts": ts, "consulted": False,
                   "blocked_by": blocked_by, "hit": False,
                   "cache_status": ("blocked-route" if blocked_by
                                    and blocked_by.startswith("route:")
                                    else "blocked-denylist"),
                   "route_decision": route,
                   "similarity": None, "matched_prompt": None,
                   "matched_entry_id": None, "matched_entry_ts": None,
                   "matched_entry_age_s": None, "entry_source": None,
                   "must_block": must_block,
                   "real_live_n": int(item.get("real_live_n", 0) or 0),
                   "weight": weight}
            detail.append(rec)
            if must_block:
                must_block_detail.append(
                    {"text": text[:120], "group": group,
                     "outcome": "blocked", "blocked_by": blocked_by})
            continue
        n_consulted += 1

        hit = bool(res["hit"])
        sim = res.get("similarity")
        sim = -1.0 if sim is None else sim
        emb_ms = res.get("embed_ms") or 0.0
        look_ms = res.get("lookup_ms") or 0.0
        tot_ms = res.get("latency_ms") or 0.0
        if not res.get("exact_hit") and first_embed_ms is None:
            first_embed_ms = emb_ms
        if not res.get("exact_hit"):
            emb_lat.append(emb_ms)
        look_lat.append(look_ms)
        tot_lat.append(tot_ms)
        matched_age = res.get("matched_entry_age_s")
        expired = bool(res.get("expired_miss"))
        unsafe_kind = None
        if hit:
            n_hit += 1
            if sim >= 0.99995:
                n_exact += 1
            else:
                n_paraphrase += 1
            # E1a: stale ttl24 hits are unsafe, not just "never".
            if cacheable == "never":
                unsafe_kind = "never"
            elif (cacheable == "ttl24" and matched_age is not None
                    and matched_age > ttl_s):
                unsafe_kind = "stale-ttl24"
                n_stale_ttl24_hit += 1
            if unsafe_kind:
                n_unsafe_hit += 1
            else:
                n_safe_hit += 1
        else:
            if expired:
                n_expired_miss += 1
            if res.get("cached") and cacheable == "never":
                n_never_stored += 1
        c = by_cat.setdefault(cat, {"n": 0, "hits": 0, "unsafe": 0})
        c["n"] += 1
        if hit:
            c["hits"] += 1
            if unsafe_kind:
                c["unsafe"] += 1
        r = by_route.setdefault(route, {"n": 0, "hits": 0})
        r["n"] += 1
        if hit:
            r["hits"] += 1
        if group != "?":
            seen_before = fam_seen.get(group, 0)
            fam_seen[group] = seen_before + 1
            if hit and seen_before >= 1:
                fam_recall_hits[group] = fam_recall_hits.get(group, 0) + 1
        if unsafe_kind:
            cache_status = ("hit-unsafe-never" if unsafe_kind == "never"
                            else "hit-unsafe-stale-ttl24")
        elif hit:
            cache_status = "hit-safe"
        elif expired:
            cache_status = "miss-expired"
        else:
            cache_status = "miss-stored"
        rec = {"i": orig_i, "order": order, "text": text[:160],
               "group": group, "category": cat,
               "cacheable": cacheable, "route": route,
               "request_ts": ts, "consulted": True,
               "blocked_by": None, "hit": hit,
               "cache_status": cache_status,
               "route_decision": route,
               "similarity": round(sim, 4),
               "matched_prompt": (res.get("matched_prompt") or "")[:120],
               "matched_entry_id": res.get("matched_entry_id"),
               "matched_entry_ts": res.get("matched_entry_ts"),
               "matched_entry_age_s": (round(matched_age, 1)
                                       if matched_age is not None else None),
               "entry_source": res.get("entry_source"),
               "unsafe_kind": unsafe_kind,
               "expired_miss": expired,
               "must_block": must_block,
               "real_live_n": int(item.get("real_live_n", 0) or 0),
               "weight": weight,
               "embed_ms": round(emb_ms, 1),
               "lookup_ms": round(look_ms, 1),
               "total_ms": round(tot_ms, 1),
               "store_size": len(gw.store.entries)}
        detail.append(rec)
        if must_block:
            must_block_detail.append(
                {"text": text[:120], "group": group,
                 "outcome": ("UNSAFE-HIT" if unsafe_kind else
                             "hit-safe" if hit else "miss-stored"),
                 "blocked_by": None,
                 "similarity": round(sim, 4),
                 "matched_prompt": (res.get("matched_prompt") or "")[:120]})
        if n % 100 == 0:
            print(f"progress: {n} requests, {n_hit} hits, "
                  f"store={len(gw.store.entries)}", flush=True)

    # Denylist quality, measured on labels (same definitions as scorer).
    never_items = [d for d in detail if d["cacheable"] == "never"]
    deny_recall = None
    deny_fp = None
    deny_fp_gateway = None
    deny_fp_bus = None
    never_reached = 0
    never_route_blocked = 0
    reached = [d for d in never_items
               if not (d.get("blocked_by") or "").startswith("route:")]
    never_reached = len(reached)
    never_route_blocked = len(never_items) - never_reached
    blocked_reached = sum(1 for d in reached if not d["consulted"])
    deny_recall = (round(blocked_reached / never_reached, 4)
                   if never_reached else None)
    safe_items = [d for d in detail if d["cacheable"] in ("stable", "ttl24")]
    gw_safe = [d for d in safe_items if d["category"] != "agent-task"]
    bus_safe = [d for d in safe_items if d["category"] == "agent-task"]

    def fp_rate(items):
        if not items:
            return None
        fp = sum(1 for d in items
                 if not d["consulted"]
                 and (d.get("blocked_by") or "").startswith("denylist:"))
        return round(fp / len(items), 4)

    deny_fp = fp_rate(safe_items)
    deny_fp_gateway = fp_rate(gw_safe)
    deny_fp_bus = fp_rate(bus_safe)

    fam_recall = {}
    for g, seen in fam_seen.items():
        fam_recall[g] = {
            "seen": seen,
            "hits_after_first": fam_recall_hits.get(g, 0),
            "recall_after_first": round(
                fam_recall_hits.get(g, 0) / max(seen - 1, 1), 4)
            if seen > 1 else None,
        }

    # E1d: traffic-weighted results, same analytic computation as scorer.
    w_requests = 0
    w_hits = 0
    w_unsafe = 0
    for d in detail:
        w = d.get("weight", 1)
        w_requests += w
        if not d["consulted"]:
            continue
        w_hits += (w - 1) + (1 if d["hit"] else 0)
        if d["cacheable"] == "never":
            w_unsafe += (w - 1) + (1 if d.get("unsafe_kind") else 0)
        elif d.get("unsafe_kind"):
            w_unsafe += 1
    w_safe = w_hits - w_unsafe

    full_n = sum(1 for d in detail if d["route"] == "full")
    full_safe = sum(1 for d in detail
                    if d["route"] == "full" and d["hit"]
                    and not d.get("unsafe_kind"))
    full_hit_rate = round(full_safe / full_n, 4) if full_n else 0
    # Pass-criteria VALUE metric: seed-matched hits do not count.
    non_seed_full_safe = sum(1 for d in detail
                             if d["route"] == "full" and d["hit"]
                             and not d.get("unsafe_kind")
                             and d.get("entry_source") != "live-store-seed")
    non_seed_full_rate = (round(non_seed_full_safe / full_n, 4)
                          if full_n else 0)

    summary = {
        "driver": DRIVER_VERSION,
        "scorer_version": "v3.0",
        "gateway_version": gw_mod.GATEWAY_VERSION,
        "gateway_path": os.path.basename(args.gateway),
        "gateway_config": {
            "threshold": args.threshold,
            "threshold_factual": args.threshold_factual,
            "threshold_generative": args.threshold_generative,
            "frame_strip_factual": args.frame_strip_factual,
            "legacy_backfill": args.legacy_backfill,
            "generative_ttl": args.generative_ttl,
            "ttl_hours": args.ttl_hours,
            "ttl_stable_hours": args.ttl_stable_hours,
            "normalise": args.normalise,
            "exact_match": args.exact,
            "denylist_enabled": args.denylist,
            "denylist": gw_mod.DENYLIST_VERSION if args.denylist else None,
            "route_scoping": args.route_scoping,
        },
        "workload": os.path.basename(args.workload),
        "threshold": args.threshold,
        "normalise": args.normalise,
        "seed_mode": args.seed_mode,
        "shuffle_seed": args.shuffle_seed,
        "requests": n,
        "consulted": n_consulted,
        "blocked_by_denylist": n_blocked_deny,
        "blocked_by_route_scoping": n_blocked_route,
        "hits": n_hit,
        "hit_rate": round(n_hit / n, 4) if n else 0,
        "hit_rate_ci95": wilson(n_hit, n),
        "hit_rate_of_consulted": round(n_hit / n_consulted, 4) if n_consulted else 0,
        "safe_hits": n_safe_hit,
        "unsafe_hits": n_unsafe_hit,
        "unsafe_rate": round(n_unsafe_hit / n, 4) if n else 0,
        "unsafe_rate_ci95": wilson(n_unsafe_hit, n),
        "unsafe_share_of_hits": round(n_unsafe_hit / n_hit, 4) if n_hit else 0,
        "stale_ttl24_hits": n_stale_ttl24_hit,
        "exact_hits_sim_1": n_exact,
        "paraphrase_hits": n_paraphrase,
        "expired_misses_ttl": n_expired_miss,
        "never_items_stored": n_never_stored,
        "full_route_requests": full_n,
        "full_route_safe_hits": full_safe,
        "full_route_safe_hit_rate": full_hit_rate,
        "non_seed_full_route_safe_hits": non_seed_full_safe,
        "non_seed_full_route_safe_hit_rate": non_seed_full_rate,
        "weighted_requests": w_requests,
        "weighted_hits": w_hits,
        "weighted_hit_rate": round(w_hits / w_requests, 4) if w_requests else 0,
        "weighted_safe_hits": w_safe,
        "weighted_unsafe_hits": w_unsafe,
        "weighted_unsafe_rate": round(w_unsafe / w_requests, 4) if w_requests else 0,
        "denylist_recall_on_never_reached": deny_recall,
        "never_items_reached_denylist": never_reached,
        "never_items_route_blocked": never_route_blocked,
        "denylist_false_positive_on_safe": deny_fp,
        "denylist_false_positive_gateway_traffic": deny_fp_gateway,
        "denylist_false_positive_bus_bodies": deny_fp_bus,
        "must_block_total": len(must_block_detail),
        "must_block_blocked": sum(
            1 for m in must_block_detail if m["outcome"] == "blocked"),
        "must_block_hit": sum(
            1 for m in must_block_detail if m["outcome"] in ("hit-safe", "UNSAFE-HIT")),
        "must_block_unsafe": sum(
            1 for m in must_block_detail if m["outcome"] == "UNSAFE-HIT"),
        "must_block_detail": must_block_detail,
        "by_category": by_cat,
        "by_route": by_route,
        "family_recall": fam_recall,
        "seed_entries": len(seed),
        "seed_ts_min": min(seed_ts) if seed_ts else None,
        "seed_ts_max": max(seed_ts) if seed_ts else None,
        "final_store_entries": len(gw.store.entries),
        "first_embed_ms": round(first_embed_ms, 1) if first_embed_ms else None,
        "median_embed_ms": round(med(emb_lat), 1) if emb_lat else None,
        "median_lookup_ms": round(med(look_lat), 1) if look_lat else None,
        "median_total_check_ms": round(med(tot_lat), 1) if tot_lat else None,
        "max_embed_ms": round(max(emb_lat), 1) if emb_lat else None,
        "wall_seconds": round(time.monotonic() - t_start, 1),
    }
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    if args.detail:
        with open(args.detail, "w", encoding="utf-8") as f:
            for d in detail:
                f.write(json.dumps(d) + "\n")
    print(json.dumps(summary, indent=2))
    # Neatness: remove the temp store/log.
    try:
        for p in (store_path, os.path.join(tmpdir, "hits.log")):
            if os.path.exists(p):
                os.remove(p)
        os.rmdir(tmpdir)
    except OSError:
        pass


if __name__ == "__main__":
    main()
