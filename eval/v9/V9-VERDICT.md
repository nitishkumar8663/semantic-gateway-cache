# v9 verdict - NO-GO (round 4 of the gateway loop)

**Verdict: NO-GO.** Gateway v2.7-guard (guard v2.3) on the frozen v9 eval set.
SAFETY FAIL, VALUE PASS, COST PASS. The v9 holdout is RETIRED (scored
once, never to be re-scored or used for tuning).

## Scores (frozen v2.7-guard, threshold 0.90 / factual 0.85 / generative 0.85,
TTL 24h/168h, seed store cache_store_backup_20261123.json; seed and empty
modes identical)

| Gate | Dev (sanity, 58) | Holdout (once, 33) | Bar |
|---|---|---|---|
| Safe hits / unsafe hits | 2 / 0 | 4 / 0 | - |
| Non-seed safe rate | 0.0345 | 0.1212 | >= 0.10 |
| Denylist recall | 0.7826 (18/23) | 0.8333 (10/12) | 1.0 |
| Must-block | 0/2 | 1/2 | all |
| Never items stored | 5 | 2 | 0 |
| FP | 0.0 | 0.0 | 0.0 |
| Median check | 15.7 / 14.3 ms | 15.0 / 13.0 ms | p95 <= 50 ms |

## What happened
- **SAFETY FAIL.** The v2.7 dev recall of 1.0 (on the v3-v8 dev sets)
  did not generalise to v9. On v9 dev, 5 never items escaped and were
  stored: lower-heating (must-block), dinner-ready (must-block),
  cancel-dentist, washing-dry, sunset-time. On the holdout, 2 never
  items escaped and were stored, including 1 of the 2 must-block
  items. FP is 0.0 on both splits. No wrong or stale answer was
  actually served (0 unsafe hits); the failure is the guard being
  incomplete, not the cache serving bad answers.
- **VALUE PASS.** 0.1212 vs the 0.10 bar. The first time value has
  passed on a holdout. The paraphrase groups hit reliably (4 safe
  hits in the holdout, all from paraphrase pairs), so the value
  mechanism works when repeats exist and hit. Dev value (0.0345) is
  low because the dev split holds fewer paraphrase pairs; it is a
  sanity check, not the gate.
- **COST PASS.** Median check ~14-15 ms, well under the 50 ms budget.
  (Run JSONs carry no p95 field; medians are consistent across modes.
  One slow embed, 102.5 ms, appeared in dev seed mode; the median is
  unaffected.)

## Why the guard did not generalise
The v2.7 Rule B v5 forms work on the candidate: the
softened-imperative form catches 9 items, the presence form catches
v9-049, weather-like catches v9-046, state-query catches v9-047 /
v9-050 / v9-063, did-i-leave catches v9-048, where-is-mine catches
v9-062. The v9 escapes are the same kind of Rule C reachers as prior
rounds, but Rule C did not separate them: softened imperatives with
verbs outside the action list ("lower", "cancel"), completion states
with novel entities/state words ("dinner ready", "washing dry"), and
live daily facts with no form ("sunset time"). The form widening
fixed the v8 escapes (alarm, kettle, book-taxi, where-phone) but the
next failure class is already visible. The build's documented next
lever is a Rule C creative-verb exemption for the birthday-message
FP, then Rule B widening to any new v9 escape classes.

## Holdout discipline
The retired v3/v4/v5/v6/v7/v8 holdouts were never read, scored or
tuned to (md5s unchanged: v8 8caea065, v7 9f6d891c, v6 608d937b,
v5 66d12303, v4 136bf650, v3 281f1249). The v9 holdout was scored
exactly once (summary only); its detail was not read. The v9
holdout is now RETIRED.

## Files
- Frozen set: `eval/v9/eval_set.json`, `eval_set_dev.json`,
  `eval_set_holdout.json`, `FROZEN.md` (md5-verified VM vs Spark)
- Runs: `eval/v9/v27_dev_seed.json`, `v27_dev_empty.json`,
  `v27_holdout_seed.json`, `v27_holdout_empty.json`
  (md5-verified VM vs Spark)
- This verdict: `eval/v9/V9-VERDICT.md`
- Guard report: `eval/GUARD-V9-REPORT.md` (its Files section still
  lists the pre-edit V9-REPORT.md md5 8bfdb8a1; the re-mirrored file
  is 6c7ff6b4 on both sides. Documentation only.)

## Next
Round 5 (v10) starts per the loop order: a stronger guard (Rule C
creative-verb exemption for the birthday-message FP first, then
Rule B widening to the fresh v9 escape classes - novel softened-
imperative verbs, completion-state entities/words, live-fact forms)
and a fresh v10 eval set from a blind writer. The v9 holdout
failures are not the tuning target.
