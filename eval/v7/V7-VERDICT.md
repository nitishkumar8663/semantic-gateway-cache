# v7 verdict - NO-GO (round 2 of the gateway loop)

**Verdict: NO-GO.** Gateway v2.5-guard (guard v2.1) on the frozen v7 eval set.
SAFETY FAIL, VALUE FAIL, COST PASS. The v7 holdout is RETIRED (scored
once, never to be re-scored or used for tuning).

## Scores (frozen v2.5-guard, threshold 0.90 / factual 0.85 / generative 0.85,
TTL 24h/168h, seed store cache_store_backup_20261123.json; seed and empty
modes identical)

| Gate | Dev (sanity, 51) | Holdout (once, 30) | Bar |
|---|---|---|---|
| Safe hits / unsafe hits | 3 / 0 | 1 / 0 | - |
| Non-seed safe rate | 0.0588 | 0.0333 | >= 0.10 |
| Denylist recall | 0.8095 (17/21) | 0.9167 (11/12) | 1.0 |
| Must-block | 0/2 | 1/2 | all |
| Never items stored | 4 | 1 | 0 |
| FP | 0.0 | 0.0556 (1/18) | 0.0 |
| Median check | 15.5 / 14.1 ms | 14.3 / 13.3 ms | p95 <= 50 ms |

## What failed
- **SAFETY FAIL.** The v2.5 dev recall of 1.0 (on the v3+v4+v5+v6 dev
  sets) did not generalise to v7. On v7 dev, 4 never items escaped and
  were stored: washing-finished (must-block), parcel-delivered
  (must-block), weather-now, house-temperature-now. On the holdout, 1
  never item escaped and was stored, and 1 of the 2 must-block items
  escaped. The FP is the birthday-message prompt (v7-068), blocked by
  the regex `\bmessage\b... (to|for)` matching "message for" in a
  creative prompt; the v2.5 narrowing did not remove it, as predicted
  in FROZEN.md. No wrong or stale answer was actually served (0 unsafe
  hits); the failure is the guard being incomplete, not the cache
  serving bad answers.
- **VALUE FAIL.** 0.0333 vs the 0.10 bar. Partly under-measurement:
  v7 has only 5 paraphrase groups and 10 stable prompts in the
  holdout, so few repeat opportunities. The same code scored 0.24 on
  v3 dev and 0.27 on v5 dev, so the value mechanism works when
  repeats exist; v7's small stable side under-measures it.
- **COST PASS.** Median check ~14 ms, well under the 50 ms budget.
  (Run JSONs carry no p95 field; medians are consistent across modes.)

## Why the guard did not generalise
The v7 never forms that escaped are all perception/state questions
("Is the washing finished yet?", "What's the weather like outside at
the moment?", "How warm is it in the house right now?", "Has my parcel
been delivered yet?"). Rule C (embedding margin) did not separate
them from safe factual questions, and the form layers (regex, Rules
A/B) have no pattern for these forms. The v2.5 per-category margin
(statement 0.10) helped the dev sets but not these short everyday
forms. The build's documented next lever is a second, intent-trained
embedding model for the guard only, since bge-m3 retrieval similarity
cannot separate the short-form band.

## Holdout discipline
The retired v3/v4/v5/v6 holdouts were never read, scored or tuned to
(md5s unchanged: v6 608d937b, v5 66d12303, v4 136bf650, v3 281f1249).
The v7 holdout was scored exactly once (summary only); its detail was
not read. The v7 holdout is now RETIRED.

## Files
- Frozen set: `eval/v7/eval_set.json`, `eval_set_dev.json`,
  `eval_set_holdout.json`, `FROZEN.md` (md5-verified VM vs Spark)
- Runs: `eval/v7/v25_dev_seed.json`, `v25_dev_empty.json`,
  `v25_holdout_seed.json`, `v25_holdout_empty.json`
  (md5-verified VM vs Spark)
- This verdict: `eval/v7/V7-VERDICT.md`
- Guard report: `eval/GUARD-V7-REPORT.md` (one documentation
  discrepancy: its Files table lists its own md5 as 8a3c7aa8, but the
  actual file md5 is fd28e626 on both VM and Spark; stale self-md5
  from an earlier draft, documentation only)

## Next
Round 3 (v8) starts per the loop order: a stronger guard (the
intent-trained embedding model lever, plus the message-regex FP fix as
a general pattern-class fix) and a fresh v8 eval set from a blind
writer. The v7 holdout failures are not the tuning target.
