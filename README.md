# Semantic Gateway Cache

A semantic gateway cache for local AI: repeats served from cache, actions and live questions never cached.

A stdlib-only Python HTTP gateway that sits in front of a generation backend. It embeds each prompt with bge-m3 through Ollama, compares it against cached prompt embeddings, and returns the cached output when the match is close enough. On a miss it calls the configured upstream, stores the pair, and returns the fresh output. A safety guard (denylist plus form and margin rules) stops action prompts, live time and state questions, and reminders from ever being served from cache.

## How it works

- `POST /query {"text": "..."}` embeds the prompt (1024-dim, bge-m3), takes the cosine similarity against cached prompt embeddings, and returns the cached output when the best match is at or above the threshold.
- Exact repeats never reach the embedder: an exact-match fast path answers them first.
- The guard runs before any cache lookup or store. It has three layers: a denylist (v1.5) for action and live-state patterns, form rules (Rules A and B) for imperative and live-fact phrasings, and a margin rule (Rule C) that compares the prompt against canonical action and safe prototypes. Denied prompts are never consulted or stored.
- Thresholds: 0.90 for stable facts, 0.85 for factual and generative prompts. Guard margins: 0.20, 0.10 for statements. TTL: 24 hours for generative and chatter entries, 168 hours for stable facts.
- Upstream modes: `none` (cache only, the default), `ollama` (generate with a local model), `dispatcher` (POST to a local dispatcher). Loopback only, port 18795 by default.
- Every query is appended to `cache_hits.log.jsonl` (hit, latency, similarity). The store is a JSON file, `cache_store.json`, created at runtime.

## Results

Demo run, 22 Nov 2026, recorded in `demo/evidence.txt`. Cold pass (5 seeds, all miss) then warm pass (20 recorded prompts) against the live gateway, misses generating with gemma3:4b on Ollama, threshold 0.98:

- Warm-pass hit rate: 9/20, 45 percent. Exact repeats 5/5, paraphrases 4/5, different-intent near-duplicates 0/5, unrelated 0/5.
- Median HIT latency: 13.1 ms (n=9). Median MISS latency: 947.6 ms (n=11). Speedup: 72.5x.
- False-positive check: 0/10 negative prompts hit.
- Threshold sweep on the same 20 prompts: best F1 1.000 at 0.90 (10 true positives, 0 false positives, 0 false negatives, 10 true negatives). The gateway now ships with 0.90, set by the frozen eval case.

Adoption loop, full GO on round 6. The gateway was judged by frozen eval sets, one fresh set per round, each scored once on its holdout. All four gates (data, safety, value, cost) are in `eval/PASS_CRITERIA.md` and `eval/QUALIFICATION-BAR.md`. Scores are holdout recall, must-block, and non-seed safe rate:

| Round | Holdout recall | Must-block | Safe rate | Verdict |
|---|---|---|---|---|
| v4 | 0.4783 | 2/4 | 0.0294 | NO-GO |
| v5 | 0.8462 | 0/2 | 0.125 | NO-GO |
| v6 | 0.9231 | 1/2 | 0.0909 | NO-GO |
| v7 | 0.9167 | 1/2 | 0.0333 | NO-GO |
| v8 | 0.8571 | 1/2 | 0.0286 | NO-GO |
| v9 | 0.8333 | 1/2 | 0.1212 | NO-GO |
| v10 | 0.9333 | 1/2 | 0.0789 | NO-GO |
| v11 | 1.0 | 2/2 | 0.1081 | FULL GO |

v11, the GO round (106 prompts, 95 families; dev 69, holdout 37), gateway v2.9-guard, guard v2.5, denylist v1.5:

- Safety: denylist recall 1.0 on dev (27/27) and holdout (15/15), must-block 2/2 on both, never items stored 0, false positives 0.0, unsafe hits 0.
- Value: non-seed safe rate 0.1081 on the holdout, against a 0.10 bar. 4 safe hits on 37 holdout requests.
- Cost: median check about 14 ms, against a 50 ms budget.
- On dev, the same guard scores recall 1.0, must-block 21/21, never stored 0, false positives 0.0 across all eight frozen dev sets (536 prompts), in both seed and empty-store modes.

What changed across the rounds: general form rules, not per-prompt patches. Round 6 widened Rule B with live-fact when and time-does forms, tide forms, delivery entities (post, car, laptop, tablet), an enough-charge form, a check-if form, a calendar form, and progressive state words. The full record is in `eval/GUARD-V11-REPORT.md` and the per-round verdicts in `eval/v4` to `eval/v11`.

## Run it

```bash
# Cache only, no upstream generation (the default)
python3 -m semantic_gateway.gateway

# Demo mode: misses generate with a local model on Ollama
GATEWAY_UPSTREAM_MODE=ollama GATEWAY_UPSTREAM_MODEL=gemma3:4b-it-q8_0 python3 -m semantic_gateway.gateway

# Health and a query
curl -s http://127.0.0.1:18795/health
curl -s -X POST http://127.0.0.1:18795/query -d '{"text": "What is the capital of France?"}'
```

Config lives in `semantic_gateway/config.json`. Env overrides: `GATEWAY_THRESHOLD`, `GATEWAY_UPSTREAM_MODE`, `GATEWAY_UPSTREAM_MODEL`, `GATEWAY_STORE_PATH`, `GATEWAY_PORT`, `GATEWAY_TTL_STABLE_HOURS`, `GATEWAY_GUARD_MARGIN`, `GATEWAY_GUARD_ENABLED`.

## Demo

```bash
python3 demo/run_demo.py
```

Cold pass then warm pass over the 20 recorded prompts in `demo/prompts.json`. Writes the observed numbers to `demo/evidence.txt`. Needs the gateway running with an Ollama upstream, and bge-m3 on Ollama.

## Tests

```bash
python3 -m unittest discover -s tests -v
```

`tests/test_gateway.py` and `tests/test_gateway_v2.py` cover cosine similarity, store round-trip, hit and miss behaviour, thresholds, empty-text rejection, and the hit log, plus live bge-m3 integration tests that skip when Ollama is down. `tests/test_gateway_v11.py` covers the guard: version pins, prototype match against `eval/prototypes.json`, Rule A and B form checks, Rule C margins, and recall and false positives on the frozen v3 to v10 dev sets (536 prompts, never any holdout). The live margin test needs bge-m3 on Ollama and is skipped otherwise.

## Eval harness

`eval/` holds the scorer (`score.py`, v3.0), the driver (`drive_gateway.py`, replays a workload through the real gateway class), the frozen eval sets v3 to v11 with their verdicts and reports, the pass criteria, and the qualification bar. See `eval/README.md`.

The holdout rule: each frozen holdout was scored once and is retired. Do not re-score a holdout, and do not tune on one. The dev sets are the working sets.

## Layout

```text
semantic_gateway/
    gateway.py      # the gateway: embed, guard, store, HTTP server
    config.json     # thresholds, guard margins, upstream, ports
    __init__.py     # public API
demo/
    prompts.json    # recorded prompt set: 5 seeds, 20 warm prompts
    run_demo.py     # cold-then-warm demo driver
    evidence.txt    # observed output of the 22 Nov 2026 demo run
eval/
    score.py            # scorer v3.0 (shadow only, serves nothing)
    drive_gateway.py    # driver: real gateway class over a workload
    prototypes.json     # canonical action prototypes (Rule C)
    safe_prototypes.json
    sample_store.json   # small synthetic seed store for smoke tests
    PASS_CRITERIA.md    # the agreed pass criteria
    QUALIFICATION-BAR.md
    GUARD-V11-REPORT.md # round-6 guard build report
    v3/ ... v11/        # frozen sets, verdicts, reports per round
tests/
    test_gateway.py     # gateway unit and live tests
    test_gateway_v2.py  # v2 (normalisation, fast path) tests
    test_gateway_v11.py # v2.9-guard tests, dev sets only
```

## Public split notes

This repo is a public split of a private build. The gateway code is the GO version (v2.9-guard, guard v2.5, denylist v1.5). The public copies differ from the private originals in exactly these ways:

- Comments and docstrings only: em dashes removed, the module header corrected from v2.8-guard to v2.9-guard, internal wording dropped. No guard logic, threshold, denylist pattern, or margin changed.
- One prototype string reworded to "unlock a door" in `ACTION_PROTOTYPES` and `eval/prototypes.json`. The same rewording is applied to every matching eval prompt (13 prompts across v3, v4, v7, v9 and v11) and to report quotes. Every block keys on the words "unlock" and "door", so no guard outcome changes.
- Four real-traffic message bodies redacted in the eval sets: v3-145 and v3-146 in the v3 dev set, and two items in the v4 holdout (same two in the v4 full set). Their labels are kept and their text is replaced with a redaction note. One held personal financial detail, one held home-security detail. The reported scores were measured on the private frozen originals; the original md5s are listed in each affected `FROZEN.md`.
- Internal paths redacted: home paths in the v4 eval sets and in report file lists are replaced with `[spark-home]`.
- The live cache store and query log are not included (runtime state). `eval/sample_store.json` is a small synthetic store with deterministic pseudo-random embeddings, for smoke-testing the harness only. It carries no measured results.
- The frozen holdout md5s quoted in `eval/v11/V11-VERDICT.md` refer to the private frozen originals. They still match the public copies for v5, v6, v7, v8, v9 and v10; they differ for v3, v4 and v11, where the public copies carry the rewordings and redactions above.
- Pre-freeze candidate files are not included, except the v11 candidate (`eval/v11/eval_set_v11.json`, kept for audit, do not score it). The v4 candidate files are excluded: their screening note says never public without review.

## Limits

- The store is a JSON file: fine for hundreds of entries, not for millions. A vector database is the scale-up.
- Similarity is only as good as bge-m3 on short prompts. The threshold sweep in `demo/evidence.txt` shows where the bar lands on the demo set.
- Cache entries expire by TTL (24h generative, 168h stable). There is no LRU eviction yet.
- The scorer's denylist is v1.1, frozen with scorer v3.0. It is part of the system under test for the early rounds, not the live guard. The driver judges the live guard instead.
