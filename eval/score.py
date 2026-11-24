#!/usr/bin/env python3
"""Score a prompt workload through the gateway's EXACT lookup logic.

Scorer v3.0 (2026-11-23, frozen for eval set v3). Shadow only. It
NEVER touches the live gateway store or its /query endpoint, NEVER
calls the dispatcher, and serves nothing. It embeds with bge-m3 via
Ollama /api/embeddings (legacy prompt form, same as gateway.py),
raw cosine similarity, against a private in-memory copy of the seed
store snapshot (eval/sample_store.json by default).

Changes vs scorer v2 (see eval/v3/FROZEN.md for the freeze):
  E1a  Stale ttl24 hits count UNSAFE: unsafe = cacheable "never" OR
       (ttl24 AND matched-entry age > TTL). v2 counted only "never".
  E1b  family_recall fixed: the numerator counts only hits on
       occurrences AFTER the first of a family (v2 counted first
       hits too, so recall could exceed 1.0).
  E1c  Denylist FP split by population: gateway traffic vs BUS
       bodies (v2 mixed them; BUS bodies are not gateway traffic).
  E1d  Traffic-weighted results reported beside unweighted
       (weight = max(1, real_live_n)), computed analytically from
       the detail: a consulted item's repeats hit at sim 1.0 once
       the first occurrence is stored or hits.
  E1e  Seed entries use their REAL created_at timestamps (v2 set
       ts=None, so TTL never bound on seed matches).
  E1f  Trace fields on every detail row (E2): request ts, route
       decision, cache status, similarity, matched entry ID and
       age, entry source.
  E1g  must_block reporting: prompts flagged must_block (the 5
       denylist escapes) get an explicit outcome each.
  E1h  Store-poisoning metric: never items stored during the run.
  E1i  --threshold, --normalise, --seed-mode, --shuffle-seed flags.
  E1j  Wilson 95% CIs on the headline rates.
  E1k  Lookup precomputes entry norms (speed only; same results).

Variants:
  asbuilt  every request consults the cache; on miss it is stored.
           No denylist, no TTL, no route scoping.
  scoped   the conditional-GO variant from the trial report:
           - only route=full requests consult the cache (dispatcher
             fast-paths first);
           - a denylist blocks action/time patterns from being
             consulted or stored;
           - entries older than --ttl-hours (default 24) are expired
             and treated as misses.

Usage:
  python3 score.py --workload eval/v3/eval_set_dev.json --variant asbuilt \
      --out eval/v3/report_dev_asbuilt.json --detail eval/v3/detail_dev_asbuilt.jsonl
  python3 score.py --workload eval/v3/eval_set_dev.json --variant scoped \
      --threshold 0.95 --normalise --seed-mode with-seed \
      --out eval/v3/sweep_scoped_t095_norm.json

Workload format: JSON object with a "prompts" list (eval set) or a
"requests" list (simulation). Each item: text, category, cacheable
(stable|ttl24|never), route (fast|full), group, ts (epoch seconds or
null), real_live_n, must_block (bool), seed_duplicate (bool).
"""
import argparse
import json
import math
import os
import random
import re
import sys
import time
import urllib.request

OLLAMA = "http://127.0.0.1:11434"
SCORER_VERSION = "v3.0"
TRACE_SCHEMA_VERSION = "v3.0"
DEFAULT_THRESHOLD = 0.98
# Default seed store: the synthetic sample store shipped in this repo.
# Pass --seed-store to use a live store snapshot instead.
STORE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "sample_store.json")

# Denylist v1.1 (2026-11-23, after eval v1 found v1.0 false positives).
# UNCHANGED in scorer v3.0: the denylist is part of the system under
# test, not part of the scorer. v1.2 (closing the 5 escapes) is a code
# fix (C3), judged by this scorer, not baked into it.
DENYLIST_VERSION = "v1.1"
DENYLIST = [
    r"\bunlock\b", r"\block\b",
    r"\bturn (on|off)\b", r"\bswitch (on|off)\b",
    r"\bsend\b", r"\bmessage\b",
    r"\bremind me (to|on)\b", r"\bset a reminder\b", r"\breminder (for|on|to)\b",
    r"\bbuild\b", r"\brebuild\b",
    r"\bopen the door\b",
    r"\btell (maa|mama|papa|nimu|reema)\b",
    r"\bfollow @",
    r"\btemperature\b", r"\btemp\b",
    r"\bwhat time is it\b", r"\bwhat'?s the time\b", r"\bcurrent time\b",
    r"\btell me the time\b",
    r"\bwhat(?:'s| is) the date\b", r"\bwhat day is it\b",
    r"\btoday'?s date\b",
    r"\bis the door\b", r"\bis .* locked\b", r"\bis .* unlocked\b",
    r"\bgpu temp\b",
    r"\bis the spark\b",
    r"\bstatus of\b", r"\bwhat'?s the status\b",
    r"\bhow (hot|cold) is it\b", r"\bhow hot is the\b",
    r"\bhumidity\b",
    r"\brain (today|tomorrow)\b", r"\bwill it rain\b",
]
DENYLIST_COMPILED = [re.compile(p) for p in DENYLIST]


def denied(text):
    low = text.lower()
    for pat in DENYLIST_COMPILED:
        if pat.search(low):
            return pat.pattern
    return None


def normalize_text(text):
    """C2 probe: what the gateway would embed after normalisation.
    Lowercase, strip, drop trailing punctuation, collapse whitespace.
    Used only with --normalise; the as-built gateway does not do this.
    """
    t = text.strip().lower()
    t = re.sub(r"[.!?,:;]+$", "", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def embed(text):
    body = json.dumps({"model": "bge-m3", "prompt": text}).encode()
    req = urllib.request.Request(
        OLLAMA + "/api/embeddings", data=body,
        headers={"Content-Type": "application/json"})
    t0 = time.monotonic()
    with urllib.request.urlopen(req, timeout=120) as r:
        data = json.load(r)
    return data["embedding"], (time.monotonic() - t0) * 1000.0


def norm_of(vec):
    return math.sqrt(sum(x * x for x in vec))


def wilson(k, n, z=1.96):
    """Wilson 95% CI for a proportion. Returns [lo, hi] or None."""
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
    ap.add_argument("--workload", required=True)
    ap.add_argument("--variant", choices=["asbuilt", "scoped"], required=True)
    ap.add_argument("--ttl-hours", type=float, default=24.0)
    ap.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD)
    ap.add_argument("--normalise", action="store_true",
                    help="embed normalised text (C2 probe); default off")
    ap.add_argument("--seed-mode", choices=["with-seed", "empty"],
                    default="with-seed",
                    help="with-seed: start from the seed store snapshot; "
                         "empty: cold start, no seed entries")
    ap.add_argument("--seed-store", default=None,
                    help="seed store JSON (default: eval/sample_store.json "
                         "or $GATEWAY_SEED_STORE)")
    ap.add_argument("--shuffle-seed", type=int, default=None,
                    help="shuffle prompt order deterministically (noise "
                         "floor); default keeps file order")
    ap.add_argument("--out", required=True)
    ap.add_argument("--detail", default=None)
    args = ap.parse_args()

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

    # Seed store: REAL created_at timestamps (E1e). v2 set ts=None,
    # so the TTL never bound on seed matches. With --normalise, seed
    # entries are re-embedded from normalised text (the stored
    # embeddings are for the raw prompts).
    seed = []
    seed_ts = []
    if args.seed_mode == "with-seed":
        with open(args.seed_store or STORE, encoding="utf-8") as f:
            seed = json.load(f).get("entries", [])
    store = []
    for si, e in enumerate(seed):
        ts = e.get("created_at")
        if ts is not None:
            seed_ts.append(ts)
        emb = e["embedding"]
        if args.normalise:
            emb, _ms = embed(normalize_text(e["prompt"]))
        store.append({"prompt": e["prompt"], "embedding": emb,
                      "norm": norm_of(emb), "ts": ts,
                      "source": "live-store-seed",
                      "entry_id": f"seed-{si}"})

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

        consulted = True
        blocked_by = None
        if args.variant == "scoped":
            if route != "full":
                consulted = False
                blocked_by = "route:fast-path-first"
                n_blocked_route += 1
            else:
                pat = denied(text)
                if pat:
                    consulted = False
                    blocked_by = f"denylist:{pat}"
                    n_blocked_deny += 1
        if not consulted:
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

        query = normalize_text(text) if args.normalise else text
        emb, emb_ms = embed(query)
        emb_norm = norm_of(emb)
        if first_embed_ms is None:
            first_embed_ms = emb_ms
        emb_lat.append(emb_ms)
        t1 = time.monotonic()
        best_sim = -1.0
        best_entry = None
        ttl_s = args.ttl_hours * 3600.0
        for e in store:
            if (args.variant == "scoped" and ts is not None
                    and e.get("ts") is not None
                    and ts - e["ts"] > ttl_s):
                continue  # expired: not eligible for a hit
            s = sum(x * y for x, y in zip(emb, e["embedding"]))
            s = s / (emb_norm * e["norm"]) if emb_norm and e["norm"] else 0.0
            if s > best_sim:
                best_sim = s
                best_entry = e
        look_ms = (time.monotonic() - t1) * 1000.0
        look_lat.append(look_ms)
        tot_lat.append(emb_ms + look_ms)
        hit = best_sim >= args.threshold
        matched_age = None
        if best_entry is not None and ts is not None \
                and best_entry.get("ts") is not None:
            matched_age = ts - best_entry["ts"]
        expired = False
        unsafe_kind = None
        if hit:
            n_hit += 1
            if best_sim >= 0.99995:
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
            # Was there a match that only lost to TTL expiry?
            if args.variant == "scoped" and ts is not None:
                for e in store:
                    if e.get("ts") is not None and ts - e["ts"] > ttl_s:
                        s = sum(x * y for x, y in zip(emb, e["embedding"]))
                        s = s / (emb_norm * e["norm"]) if emb_norm and e["norm"] else 0.0
                        if s >= args.threshold:
                            expired = True
                            n_expired_miss += 1
                            break
            store.append({"prompt": text, "embedding": emb,
                          "norm": emb_norm, "ts": ts,
                          "source": "shadow-workload",
                          "entry_id": f"workload-{orig_i}"})
            if cacheable == "never":
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
            # E1b: recall counts only hits AFTER the first occurrence.
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
               "similarity": round(best_sim, 4),
               "matched_prompt": ((best_entry or {}).get("prompt", "") or "")[:120],
               "matched_entry_id": (best_entry or {}).get("entry_id"),
               "matched_entry_ts": (best_entry or {}).get("ts"),
               "matched_entry_age_s": (round(matched_age, 1)
                                       if matched_age is not None else None),
               "entry_source": (best_entry or {}).get("source"),
               "unsafe_kind": unsafe_kind,
               "expired_miss": expired,
               "must_block": must_block,
               "real_live_n": int(item.get("real_live_n", 0) or 0),
               "weight": weight,
               "embed_ms": round(emb_ms, 1),
               "lookup_ms": round(look_ms, 1),
               "total_ms": round(emb_ms + look_ms, 1),
               "store_size": len(store)}
        detail.append(rec)
        if must_block:
            must_block_detail.append(
                {"text": text[:120], "group": group,
                 "outcome": ("UNSAFE-HIT" if unsafe_kind else
                             "hit-safe" if hit else "miss-stored"),
                 "blocked_by": None,
                 "similarity": round(best_sim, 4),
                 "matched_prompt": ((best_entry or {}).get("prompt", "") or "")[:120]})
        if n % 100 == 0:
            print(f"progress: {n} requests, {n_hit} hits, "
                  f"store={len(store)}", flush=True)

    # Denylist quality, measured on labels (scoped only). Recall is
    # computed ONLY over never items that actually reached the denylist
    # (route=full); never items stopped earlier by route scoping are
    # counted separately.
    never_items = [d for d in detail if d["cacheable"] == "never"]
    deny_recall = None
    deny_fp = None
    deny_fp_gateway = None
    deny_fp_bus = None
    never_reached = 0
    never_route_blocked = 0
    if args.variant == "scoped":
        reached = [d for d in never_items
                   if not (d.get("blocked_by") or "").startswith("route:")]
        never_reached = len(reached)
        never_route_blocked = len(never_items) - never_reached
        blocked_reached = sum(1 for d in reached if not d["consulted"])
        deny_recall = (round(blocked_reached / never_reached, 4)
                       if never_reached else None)
        # E1c: FP split by population. BUS bodies are agent-task
        # traffic that never traverses the dispatcher; they are not
        # gateway traffic and must not share the FP denominator.
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

    # E1b: family recall, numerator only after-first hits.
    fam_recall = {}
    for g, seen in fam_seen.items():
        fam_recall[g] = {
            "seen": seen,
            "hits_after_first": fam_recall_hits.get(g, 0),
            "recall_after_first": round(
                fam_recall_hits.get(g, 0) / max(seen - 1, 1), 4)
            if seen > 1 else None,
        }

    # E1d: traffic-weighted results, computed analytically from the
    # detail. Weight w = max(1, real_live_n). A consulted item's
    # repeats hit at sim 1.0: if the first occurrence hit, repeats
    # hit the same entry; if it missed, it was stored, so repeats
    # hit the stored first occurrence. Repeats are consecutive, so
    # their matched-entry age is 0 (fresh, never stale). Blocked
    # items contribute no hits. A repeat of a "never" item is an
    # unsafe hit; repeats of stable/ttl24 items are safe.
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

    # Full-route traffic (the traffic the scoped variant touches).
    full_n = sum(1 for d in detail if d["route"] == "full")
    full_safe = sum(1 for d in detail
                    if d["route"] == "full" and d["hit"]
                    and not d.get("unsafe_kind"))
    full_hit_rate = round(full_safe / full_n, 4) if full_n else 0

    summary = {
        "scorer_version": SCORER_VERSION,
        "trace_schema_version": TRACE_SCHEMA_VERSION,
        "workload": os.path.basename(args.workload),
        "variant": args.variant,
        "denylist": DENYLIST_VERSION if args.variant == "scoped" else None,
        "ttl_hours": args.ttl_hours if args.variant == "scoped" else None,
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
        "final_store_entries": len(store),
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


if __name__ == "__main__":
    main()
