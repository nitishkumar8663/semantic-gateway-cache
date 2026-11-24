# v8 verdict - NO-GO (round 3 of the gateway loop)

**Verdict: NO-GO.** Gateway v2.6-guard (guard v2.2) on the frozen v8 eval set.
SAFETY FAIL, VALUE FAIL, COST PASS. The v8 holdout is RETIRED (scored
once, never to be re-scored or used for tuning).

## Scores (frozen v2.6-guard, threshold 0.90 / factual 0.85 / generative 0.85,
TTL 24h/168h, seed store cache_store_backup_20261123.json; seed and empty
modes identical)

| Gate | Dev (sanity, 62) | Holdout (once, 35) | Bar |
|---|---|---|---|
| Safe hits / unsafe hits | 4 / 0 | 1 / 0 | - |
| Non-seed safe rate | 0.0645 | 0.0286 | >= 0.10 |
| Denylist recall | 0.8333 (20/24) | 0.8571 (12/14) | 1.0 |
| Must-block | 0/2 | 1/2 | all |
| Never items stored | 4 | 2 | 0 |
| FP | 0.0 | 0.0 | 0.0 |
| Median check | 15.9 / 14.3 ms | 14.3 / 12.7 ms | p95 <= 50 ms |

## What failed
- **SAFETY FAIL.** The v2.6 dev recall of 1.0 (on the v3+v4+v5+v6+v7
  dev sets) did not generalise to v8. On v8 dev, 4 never items escaped
  and were stored: alarm-softened (must-block), kettle-boiled
  (must-block), book-taxi-softened, where-phone. On the holdout, 2
  never items escaped and were stored, including 1 of the 2
  must-block items. FP is 0.0 on both splits (the message-regex fix
  held). No wrong or stale answer was actually served (0 unsafe
  hits); the failure is the guard being incomplete, not the cache
  serving bad answers.
- **VALUE FAIL.** 0.0286 vs the 0.10 bar. Only 1 hit in the holdout,
  despite 3 paraphrase groups (6 prompts) landing there. The
  paraphrase pairs are not hitting reliably at the 0.85 factual
  threshold, so value is under-measured as well as low. The same
  code scored 0.24 on v3 dev and 0.27 on v5 dev, so the value
  mechanism works when repeats exist and hit.
- **COST PASS.** Median check ~14 ms, well under the 50 ms budget.
  (Run JSONs carry no p95 field; medians are consistent across modes.)

## Why the guard did not generalise
The v8 escapes are the same classes the v8 candidate named as
round-4 material: softened imperatives ("can/could you ... ?")
escape Rule A via the question guard (alarm, book-taxi, heating-down
was caught by Rule C on dev but the class is not reliably covered),
and novel state/location forms ("has the kettle boiled", "where did
I put my phone") have no Rule B form. Rule C (embedding margin) did
not separate these from safe questions. The v2.6 Rule B widening
fixed the v7 escapes (washing, parcel, weather, house-temp) but the
next failure class is already visible. The build's documented next
lever is widening Rule B to these fresh failure classes (uncontracted
weather-like, a presence form, softened-imperative handling, more
completion state words), with a fine-tuned embedding model as the
fallback.

## Holdout discipline
The retired v3/v4/v5/v6/v7 holdouts were never read, scored or tuned
to (md5s unchanged: v7 9f6d891c, v6 608d937b, v5 66d12303, v4 136bf650,
v3 281f1249). The v8 holdout was scored exactly once (summary only);
its detail was not read. The v8 holdout is now RETIRED.

## Files
- Frozen set: `eval/v8/eval_set.json`, `eval_set_dev.json`,
  `eval_set_holdout.json`, `FROZEN.md` (md5-verified VM vs Spark)
- Runs: `eval/v8/v26_dev_seed.json`, `v26_dev_empty.json`,
  `v26_holdout_seed.json`, `v26_holdout_empty.json`
  (md5-verified VM vs Spark)
- This verdict: `eval/v8/V8-VERDICT.md`
- Guard report: `eval/GUARD-V8-REPORT.md` (does NOT list its own md5
  in its Files table, avoiding the v2.5 stale self-md5 bug; the parent
  verified 8fb1a420 directly)

## Next
Round 4 (v9) starts per the loop order: a stronger guard (Rule B
widening to the fresh failure classes named above, plus a presence
form and more completion state words) and a fresh v9 eval set from a
blind writer. The v8 holdout failures are not the tuning target.
