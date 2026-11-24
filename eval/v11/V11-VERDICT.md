# v11 verdict - FULL GO (round 6 of the gateway loop)

**Verdict: FULL GO.** Gateway v2.9-guard (guard v2.5) on the frozen v11
eval set. SAFETY PASS, VALUE PASS, COST PASS. All three agreed gates
pass on a fresh holdout. The loop is complete; the gateway is cleared
for adoption. The v11 holdout is RETIRED (scored once, never to be
re-scored or used for tuning).

## Scores (frozen v2.9-guard, threshold 0.90 / factual 0.85 / generative
0.85, TTL 24h/168h, seed store cache_store_backup_20261123.json; seed
and empty modes identical)

| Gate | Dev (sanity, 69) | Holdout (once, 37) | Bar |
|---|---|---|---|
| Safe hits / unsafe hits | 9 / 0 | 4 / 0 | - |
| Non-seed safe rate | 0.1304 | 0.1081 | >= 0.10 |
| Denylist recall | 1.0 (27/27) | 1.0 (15/15) | 1.0 |
| Must-block | 2/2 | 2/2 | all |
| Never items stored | 0 | 0 | 0 |
| FP | 0.0 | 0.0 | 0.0 |
| Median check | 16.1 / 14.2 ms | 15.0 / 13.2 ms | p95 <= 50 ms |

## What happened
- **SAFETY PASS.** Recall 1.0, must-block 2/2, never stored 0, FP 0.0
  on the holdout. The dev recall of 1.0 generalised to v11: the new
  Rule B v7 forms caught every never item the blind writers produced
  (all 42 form-blocked, 0 Rule-C-only). No wrong or stale answer was
  served (0 unsafe hits).
- **VALUE PASS.** 0.1081 vs the 0.10 bar. The paraphrase groups fixed
  v4's under-measurement and the gateway serves real repeat value:
  4 safe hits on 37 holdout requests.
- **COST PASS.** Median check ~14-15 ms, well under the 50 ms budget.
  (Run JSONs carry no p95 field; medians are consistent across modes.
  One slow embed in the dev seed run, max 130.8 ms, is a single
  cold-load outlier, not a median.)

## The loop in full (holdout recall / must-block / safe rate)
- v4: 0.4783, 2/4, 0.0294 - NO-GO
- v5: 0.8462, 0/2, 0.125 - NO-GO
- v6: 0.9231, 1/2, 0.0909 - NO-GO
- v7: 0.9167, 1/2, 0.0333 - NO-GO
- v8: 0.8571, 1/2, 0.0286 - NO-GO
- v9: 0.8333, 1/2, 0.1212 - NO-GO
- v10: 0.9333, 1/2, 0.0789 - NO-GO
- v11: 1.0, 2/2, 0.1081 - FULL GO

The mechanism that got it there: Rule B v7 widening (live-fact-when /
live-fact-time-does / tide-when forms, "post" + "car" + "laptop" +
"tablet" in _LIVE_ENTITIES, "enough charge" form, "check if" form,
calendar form, progressive state words). The v10 dev escapes (sun-go-
down, post-arrived, car-charged, calendar-tomorrow) are all form-caught
under v2.9, and the v11 blind writers produced 0 Rule-C-only never
items: the form layers now cover everything they wrote.

## Holdout discipline
The retired v3/v4/v5/v6/v7/v8/v9/v10 holdouts were never read, scored
or tuned to (md5s unchanged: v10 f5c648b1, v9 2279b731, v8 8caea065,
v7 9f6d891c, v6 608d937b, v5 66d12303, v4 136bf650, v3 281f1249). The
v11 holdout was scored exactly once (summary only); its detail was
not read. The v11 holdout is now RETIRED.

## Files
- Frozen set: `eval/v11/eval_set.json`, `eval_set_dev.json`,
  `eval_set_holdout.json`, `FROZEN.md` (md5-verified VM vs Spark)
- Runs: `eval/v11/v29_dev_seed.json`, `v29_dev_empty.json`,
  `v29_holdout_seed.json`, `v29_holdout_empty.json`
  (md5-verified VM vs Spark)
- This verdict: `eval/v11/V11-VERDICT.md`
- Guard report: `eval/GUARD-V11-REPORT.md` (verified directly,
  md5 be45018d)

## Next
The loop is complete. The gateway v2.9-guard is cleared for adoption
live on the Spark. Adoption is Nitish's call: the next step is the
adoption gate (live on the Spark, then the Medium article), and after
that trial 2 (agentic P4 3-tier memory) per the adoption order.
