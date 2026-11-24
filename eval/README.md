# Eval harness

Repeatable, eval-driven development for the semantic gateway cache. The harness scores the gateway's lookup logic against labelled prompt sets, under two variants: `asbuilt` (no guards) and `scoped` (full-route only, denylist, 24h TTL). The frozen sets v3 to v11 are the record of the adoption loop: one fresh set per round, each scored once on its holdout, ending in a FULL GO on v11.

## Layout

- `score.py` - the scorer, v3.0. Shadow only: it never touches the live gateway store, never calls the dispatcher, serves nothing. It embeds with bge-m3 through Ollama and replays a workload against a private in-memory copy of the seed store.
- `drive_gateway.py` - the driver. It replays a workload through the real gateway class (imported from `--gateway`) with a stub upstream and the real bge-m3 embedder, and computes summary metrics with the same definitions as the scorer. It refuses `--detail` for any workload whose filename contains "holdout": holdout runs print the summary only.
- `prototypes.json`, `safe_prototypes.json` - the canonical action and safe prototypes (Rule C). The unit tests assert the gateway module constants match these files.
- `sample_store.json` - a small synthetic seed store (5 entries, deterministic pseudo-random embeddings, labelled inside the file). It exists so the harness runs without a live store. It carries no measured results.
- `PASS_CRITERIA.md` - the agreed pass criteria (all four gates conjunctive, one FAIL means NO-GO).
- `QUALIFICATION-BAR.md` - the general adoption bar (data, safety, value, cost) every trial is scored against.
- `GUARD-V11-REPORT.md` - the round-6 guard build report. Earlier guard and enhancement reports sit beside it.
- `TRACE_SCHEMA.md`, `dispatcher-instrumentation-spec.md` - the trace schema and the dispatcher instrumentation spec (spec only, not applied).
- `v3/` to `v11/` - one frozen set per round: `eval_set.json` (full), `eval_set_dev.json`, `eval_set_holdout.json`, `FROZEN.md`, and the round verdict and report.

## Frozen sets

| Set | Prompts | Families | Dev | Holdout | Verdict |
|---|---|---|---|---|---|
| v3 | 154 | 47 | 110 | 44 | NO-GO (mechanism fail) |
| v4 | 105 | 34 | 70 | 35 | NO-GO |
| v5 | 91 | 66 | 59 | 32 | NO-GO |
| v6 | 89 | 77 | 56 | 33 | NO-GO |
| v7 | 81 | 76 | 51 | 30 | NO-GO |
| v8 | 97 | 89 | 62 | 35 | NO-GO |
| v9 | 91 | 85 | 58 | 33 | NO-GO |
| v10 | 108 | 101 | 70 | 38 | NO-GO |
| v11 | 106 | 95 | 69 | 37 | FULL GO |

v3 is the frozen baseline case, not a loop round. Rounds v4 to v11 each froze a fresh set, built the guard against the dev half only, and scored the holdout once. The v11 holdout is retired, as are all earlier holdouts.

## How to run

Needs bge-m3 on Ollama at `http://127.0.0.1:11434`. Run dev sets only. Never score a holdout.

```bash
# Scorer, scoped variant, dev set, with the sample seed store
python3 eval/score.py --workload eval/v11/eval_set_dev.json --variant scoped \
    --threshold 0.90 --seed-mode with-seed --out /tmp/report_dev.json

# Same, cold start (no seed entries)
python3 eval/score.py --workload eval/v11/eval_set_dev.json --variant scoped \
    --threshold 0.90 --seed-mode empty --out /tmp/report_dev_empty.json

# Driver: the real gateway class over the dev set
python3 eval/drive_gateway.py --gateway semantic_gateway/gateway.py \
    --workload eval/v11/eval_set_dev.json --threshold 0.90 \
    --seed-mode with-seed --out /tmp/drive_dev.json
```

`--seed-store` points the scorer or driver at a different seed store. `$GATEWAY_SEED_STORE` does the same for the scorer. The headline metrics in every summary JSON: `hit_rate`, `safe_hits` and `unsafe_hits` (an unsafe hit is a `never` item served, or a `ttl24` hit on an entry older than 24h), `denylist_recall_on_never_reached` (must be 1.0), `denylist_false_positive_on_safe` (must be 0.0), `family_recall`, and must-block outcomes.

## How to read a verdict

Each `V*-VERDICT.md` scores the four gates on the dev set (sanity) and the holdout (once). A GO needs all four gates to pass on the holdout: zero unsafe hits, denylist recall 1.0, must-block all blocked, never items stored 0, false positives 0.0, non-seed safe rate at or above 0.10, and median check latency under 50 ms. The v11 verdict is the GO; the earlier verdicts name the gate that failed and what had to change.

## Public split notes

- The public copies of the eval sets differ from the private frozen originals in the ways listed in the top-level README: one reworded prompt family, four redacted message bodies, redacted home paths. The original md5s are listed in each affected `FROZEN.md`. Reported scores were measured on the private frozen originals.
- Pre-freeze candidate files are not included, except `v11/eval_set_v11.json`, the v11 candidate kept for audit. Do not score it: it carries proposed labels, `must_block` false on all items, and no split. The v4 candidate files are excluded entirely.
- The per-round run JSONs (score summaries and detail files) are not included. The verdicts and reports summarise them.
- The set builders are not included. They read private traffic logs, so they cannot run on a public copy. The frozen sets are the artefacts.
