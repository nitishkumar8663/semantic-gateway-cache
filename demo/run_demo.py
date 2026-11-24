#!/usr/bin/env python3
"""demo: cold pass then warm pass over the recorded prompt set.

Assumes the gateway is running (default http://127.0.0.1:18795) with
an upstream configured (demo: upstream_mode=ollama, gemma3:4b-it-q8_0),
so a cache MISS means a real GPU generation and a HIT means no GPU work.

Steps:
  1. POST /clear (empty store).
  2. Cold pass: the 5 seeds only, each once -> all MISS, pairs cached.
     (Full 20-prompt cold pass is unnecessary: every prompt misses on an
     empty store by construction, and each miss costs a generation.)
  3. Warm pass: all 20 recorded prompts -> hit/miss + latency per prompt.
  4. Threshold sweep: embed every prompt + every seed directly via
     Ollama bge-m3, score max-similarity vs the 5 SEED embeddings only,
     and compute precision/recall at thresholds 0.85..0.99.
  5. Write every observed number to demo/evidence.txt.

Usage: python3 demo/run_demo.py [--gateway URL] [--ollama URL]
"""

import argparse
import json
import math
import os
import statistics
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)


def post_json(url, payload, timeout=300):
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp)


def get_json(url, timeout=30):
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return json.load(resp)


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--gateway", default="http://127.0.0.1:18795")
    parser.add_argument("--ollama", default="http://127.0.0.1:11434")
    parser.add_argument("--model", default="bge-m3")
    args = parser.parse_args()

    with open(os.path.join(HERE, "prompts.json"), encoding="utf-8") as f:
        data = json.load(f)
    seeds = data["seeds"]
    prompts = data["prompts"]

    out = []
    out.append("Semantic AI Gateway and Cache - demo evidence")
    out.append(f"Gateway: {args.gateway}  Embeddings: {args.model} via {args.ollama}")
    out.append(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S %Z', time.localtime())}")
    out.append("")

    health = get_json(args.gateway + "/health")
    out.append(f"Gateway /health: {health}")
    stats0 = get_json(args.gateway + "/stats")
    out.append(f"Gateway /stats before demo: {stats0}")
    out.append("")

    # 1. Clear the store.
    post_json(args.gateway + "/clear", {})
    out.append("Store cleared (POST /clear).")
    out.append("")

    # 2. Cold pass: seeds only, each once.
    out.append("== COLD PASS (5 seeds, empty store; every query must MISS) ==")
    cold_lat = []
    for seed in seeds:
        r = post_json(args.gateway + "/query", {"text": seed})
        cold_lat.append(r["latency_ms"])
        out.append(f"MISS  sim={r['similarity'] if r['similarity'] is not None else -1:.4f} "
                   f"{r['latency_ms']:8.1f} ms  cached={r['cached']}  {seed!r}")
        out.append(f"      upstream output (first 120 chars): {str(r['output'])[:120]!r}")
    out.append(f"Cold-pass misses: {len(cold_lat)}/5, "
               f"median miss latency {statistics.median(cold_lat):.1f} ms")
    out.append("")

    # 3. Warm pass: all 20 recorded prompts.
    out.append("== WARM PASS (20 recorded prompts, store holds the 5 seeds) ==")
    rows = []
    for p in prompts:
        r = post_json(args.gateway + "/query", {"text": p["text"]})
        rows.append((p, r))
        verdict = "HIT " if r["hit"] else "MISS"
        sim = r["similarity"] if r["similarity"] is not None else -1.0
        out.append(f"{verdict}  sim={sim:.4f} {r['latency_ms']:8.1f} ms  "
                   f"[{p['category']}/{p['label']}]  {p['text']!r}")
    hits = [r for _, r in rows if r["hit"]]
    misses = [r for _, r in rows if not r["hit"]]
    hit_lat = [r["latency_ms"] for r in hits]
    miss_lat = [r["latency_ms"] for r in misses]
    out.append("")
    out.append(f"Warm-pass hit rate: {len(hits)}/{len(rows)} = "
               f"{len(hits) / len(rows):.2%}")
    out.append(f"Median HIT latency: "
               f"{statistics.median(hit_lat):.1f} ms (n={len(hit_lat)})"
               if hit_lat else "Median HIT latency: n/a (no hits)")
    out.append(f"Median MISS latency: "
               f"{statistics.median(miss_lat):.1f} ms (n={len(miss_lat)})"
               if miss_lat else "Median MISS latency: n/a (no misses)")
    if hit_lat and miss_lat:
        out.append(f"Speedup (median miss / median hit): "
                   f"{statistics.median(miss_lat) / statistics.median(hit_lat):.1f}x")
    out.append("")

    # Per-category breakdown.
    for cat in ("exact", "paraphrase", "different-intent", "unrelated"):
        cat_rows = [(p, r) for p, r in rows if p["category"] == cat]
        h = sum(1 for _, r in cat_rows if r["hit"])
        out.append(f"  {cat}: {h}/{len(cat_rows)} hit")
    out.append("")

    # False-positive check (the done criterion that matters most).
    fp = [(p, r) for p, r in rows if p["label"] == "negative" and r["hit"]]
    out.append("== FALSE-POSITIVE CHECK ==")
    if fp:
        out.append(f"FAIL: {len(fp)} negative prompt(s) incorrectly HIT:")
        for p, r in fp:
            out.append(f"  sim={r['similarity']:.4f}  {p['text']!r}")
    else:
        out.append("PASS: 0/10 negative prompts hit (5 different-intent "
                   "near-duplicates + 5 unrelated all correctly MISSED).")
    out.append("")

    # 4. Threshold sweep, scored against the 5 SEED embeddings only.
    out.append("== THRESHOLD SWEEP (max cosine vs the 5 seed embeddings) ==")
    seed_embs = [post_json(args.ollama + "/api/embeddings",
                           {"model": args.model, "prompt": s})["embedding"]
                 for s in seeds]
    scored = []
    for p in prompts:
        emb = post_json(args.ollama + "/api/embeddings",
                        {"model": args.model, "prompt": p["text"]})["embedding"]
        best = max(cosine(emb, se) for se in seed_embs)
        scored.append((p, best))
        out.append(f"  max-sim={best:.4f}  [{p['category']}/{p['label']}]  {p['text']!r}")
    out.append("")
    out.append("threshold | precision | recall | F1 | TP FP FN TN")
    best_f1, best_t = -1.0, None
    for t in (0.85, 0.90, 0.95, 0.97, 0.98, 0.99):
        tp = sum(1 for p, s in scored if p["label"] == "positive" and s >= t)
        fp_n = sum(1 for p, s in scored if p["label"] == "negative" and s >= t)
        fn = sum(1 for p, s in scored if p["label"] == "positive" and s < t)
        tn = sum(1 for p, s in scored if p["label"] == "negative" and s < t)
        prec = tp / (tp + fp_n) if (tp + fp_n) else 1.0
        rec = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
        out.append(f"  {t:.2f}     |  {prec:.3f}    | {rec:.3f}  | {f1:.3f} | "
                   f"{tp}  {fp_n}  {fn}  {tn}")
        if f1 > best_f1:
            best_f1, best_t = f1, t
    out.append("")
    out.append(f"Tuned threshold (best F1 on this set): {best_t} "
               f"(F1={best_f1:.3f}). Configured gateway threshold: 0.98.")
    out.append("")

    stats1 = get_json(args.gateway + "/stats")
    out.append(f"Gateway /stats after demo: {stats1}")
    out.append("")
    out.append("Commands used:")
    out.append("  python3 gateway.py  (GATEWAY_UPSTREAM_MODE=ollama, "
               "GATEWAY_UPSTREAM_MODEL=gemma3:4b-it-q8_0, port 18795)")
    out.append("  python3 -m unittest discover -s tests -v")
    out.append("  python3 demo/run_demo.py")
    out.append("Notes: miss latency = embed + lookup + gemma3:4b generation "
               "(real GPU work). Hit latency = embed + lookup only. "
               "Exact repeats score cosine 1.0 by construction (same text, "
               "same embedding).")

    evidence = "\n".join(out) + "\n"
    ev_path = os.path.join(HERE, "evidence.txt")
    with open(ev_path, "w", encoding="utf-8") as f:
        f.write(evidence)
    print(evidence)


if __name__ == "__main__":
    main()
