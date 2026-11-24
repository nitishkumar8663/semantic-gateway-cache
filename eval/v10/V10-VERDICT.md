# v10 verdict - NO-GO (round 5 of the gateway loop)

**Verdict: NO-GO.** Gateway v2.8-guard (guard v2.4) on the frozen v10 eval
set. SAFETY FAIL, VALUE FAIL, COST PASS. The v10 holdout is RETIRED
(scored once, never to be re-scored or used for tuning).

## Scores (frozen v2.8-guard, threshold 0.90 / factual 0.85 / generative 0.85,
TTL 24h/168h, seed store cache_store_backup_20261123.json; seed and empty
modes identical)

| Gate | Dev (sanity, 70) | Holdout (once, 38) | Bar |
|---|---|---|---|
| Safe hits / unsafe hits | 3 / 0 | 3 / 0 | - |
| Non-seed safe rate | 0.0429 | 0.0789 | >= 0.10 |
| Denylist recall | 0.8621 (25/29) | 0.9333 (14/15) | 1.0 |
| Must-block | 0/2 | 1/2 | all |
| Never items stored | 4 | 1 | 0 |
| FP | 0.0 | 0.0 | 0.0 |
| Median check | 15.6 / 14.3 ms | 14.7 / 13.4 ms | p95 <= 50 ms |

## What happened
- **SAFETY FAIL.** The v2.8 dev recall of 1.0 (on the v3-v9 dev sets)
  did not generalise to v10. On v10 dev, 4 never items escaped and
  were stored: sun-go-down (must-block), post-arrived (must-block),
  car-charged, calendar-tomorrow. On the holdout, 1 never item escaped
  and was stored (1 of the 2 must-block items). FP is 0.0 on both
  splits. No wrong or stale answer was actually served (0 unsafe
  hits); the failure is the guard being incomplete, not the cache
  serving bad answers.
- **VALUE FAIL.** 0.0789 vs the 0.10 bar. Close, but below. The
  holdout has 3 paraphrase pairs landing there; only 3 hits in total.
  (v9 passed value at 0.1212; v10's holdout value is lower because
  fewer paraphrase pairs hit, not because the mechanism regressed.
  Dev value 0.0429 is a sanity check, not the gate.)
- **COST PASS.** Median check ~14-15 ms, well under the 50 ms budget.
  (Run JSONs carry no p95 field; medians are consistent across modes.)

## Progress
This is the closest round yet. Holdout recall 0.9333 is the best so
far (v4 0.4783, v5 0.8462, v6 0.9231, v7 0.9167, v8 0.8571, v9 0.8333,
v10 0.9333). Only 1 never item escaped on the holdout, down from 2 in
v8/v9. The Rule C creative-draft exemption fixed the birthday-message
FP (live probe: unblocked under v2.8, miss-stored, 17.02 ms), and the
v10 holdout's own birthday-message paraphrase (v10t-044, "Write a
birthday message for a friend who loves cycling.") was not FP-blocked.
The new Rule B v6 forms work: state-query catches 6 items, the
softened-imperative form catches 4, "lower"/"cancel"/"dim"/"pause"/
"text" as Rule A verbs catch their items.

## Why the guard did not generalise
The v10 escapes are the same kind of Rule C reachers as prior rounds,
but Rule C did not separate them: a live-fact variant ("when does the
sun go down", not "what time is sunset"), a completion state with a
novel entity ("post arrived", "post" missing from _LIVE_ENTITIES), a
state question with a novel entity and form ("car charged enough"),
and an agent-task with no form ("calendar tomorrow"). The form
widening fixed the v9 escapes (lower-heating, dinner-ready,
cancel-dentist, washing-dry, sunset-time) but the next failure class
is already visible. The build's documented next lever is widening
Rule B to these fresh classes (a "when does the sun go down" form,
"post" in _LIVE_ENTITIES, a "charged enough" form, a "check if" form,
a progressive "charging" form), with the fine-tuned embedding model
as the fallback if those classes still do not generalise.

## Holdout discipline
The retired v3/v4/v5/v6/v7/v8/v9 holdouts were never read, scored or
tuned to (md5s unchanged: v9 2279b731, v8 8caea065, v7 9f6d891c,
v6 608d937b, v5 66d12303, v4 136bf650, v3 281f1249). The v10 holdout was
scored exactly once (summary only); its detail was not read. The v10
holdout is now RETIRED.

## Files
- Frozen set: `eval/v10/eval_set.json`, `eval_set_dev.json`,
  `eval_set_holdout.json`, `FROZEN.md` (md5-verified VM vs Spark)
- Runs: `eval/v10/v28_dev_seed.json`, `v28_dev_empty.json`,
  `v28_holdout_seed.json`, `v28_holdout_empty.json`
  (md5-verified VM vs Spark)
- This verdict: `eval/v10/V10-VERDICT.md`
- Guard report: `eval/GUARD-V10-REPORT.md` (its own md5 is not listed
  in its Files table, avoiding the v2.5 stale self-md5 bug; the parent
  verified 3bab329a directly)

## Next
Round 6 (v11) starts per the loop order: a stronger guard (Rule B
widening to the fresh v10 escape classes - "when does the sun go
down" form, "post" in _LIVE_ENTITIES, a "charged enough" form, a
"check if" form, a progressive "charging" form) and a fresh v11 eval
set from a blind writer. The v10 holdout failures are not the tuning
target.
