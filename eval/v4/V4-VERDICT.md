# v4 verdict - gateway v2.2-enh

**Verdict: NO-GO.** v2.2-enh does not earn a full GO on the frozen v4
eval case. The blocker is the safety guard: denylist v1.2 does not
generalise to the broader v4 distribution. Value also fails, partly
because v4 under-measures it (few repeat questions after the
per-question re-split). Cost passes. No unsafe hit occurred in the
holdout - the failure is the guard being incomplete, not an actual
bad serving.

**Date:** 23 Nov 2026 (evening). **Code:** gateway v2.2-enh
(threshold 0.90, factual 0.85, generative 0.85, denylist v1.2,
TTL 24h / 168h stable, normalise on, exact-match on).
**Eval case:** v4 frozen (105 prompts / 45 families; dev 70/29,
holdout 35/16; real 16, 6 in holdout). Holdout scored exactly once,
summary only, seed + empty modes. Dev scored for sanity (detail
allowed). Driver: drive_gateway_v3.py. Seed store:
cache_store_backup_20261123.json.

## Gate-by-gate

| Gate | Bar | Dev seed / empty | Holdout seed / empty | Verdict |
|---|---|---|---|---|
| DATA | set big enough, real share reported | 70 prompts / 29 families | 35 prompts / 16 families, 6 real | MARGINAL |
| SAFETY unsafe hits | 0 unweighted + weighted | 0 / 0 | 0 / 0 | PASS |
| SAFETY denylist recall | 1.0 | 0.4783 (22/46) | 0.3333 (7/21) | FAIL |
| SAFETY must-block | all blocked | 2/4 | 3/4 | FAIL |
| SAFETY never stored | 0 | 24 | 14 | FAIL |
| SAFETY denylist FP (gateway) | 0.0 | 0.0 | 0.0 | PASS |
| VALUE non-seed safe rate | >= 0.10 | 0.0429 / 0.0571 | 0.0294 / 0.0294 | FAIL |
| COST p95 check | <= 50 ms | median 12.6 / 11.2 ms | median 11.9 / 9.8 ms | PASS |

Overall: NO-GO (SAFETY and VALUE fail; DATA marginal; COST pass).

## What the numbers mean

**Denylist recall 0.33 (holdout).** The denylist v1.2 is a hand-written
regex list designed on v3 dev. It covers only 7 of the 21 holdout
never items. The gaps, verified against the gateway's own denied()
function: no pattern for heating, timers, lists, or appliances; no
pattern for the verbs kill / bolt / secure; the switch pattern needs
"switch on/off X" and misses "switch X on/off" ("switch the bedroom
lamp on"); the door patterns need "is the door" or "is ... locked"
and miss "is the back door shut" / "is the side door closed"; the
time patterns need "what's the time" and miss "what is the time in
Tokyo". The denylist generalises across phrasings of the verbs it
knows, and fails on new verbs, new categories, and word-order
variants. That is a property of a regex list, not a labelling
artefact: the routes are the real dispatcher's tier1.route()
decisions, and the never labels follow the v3 convention.

**Must-block 3/4 (holdout).** The miss is "switch the bedroom lamp
on" (lights-on) - the word-order gap above. Dev must-block was 2/4
(lights-off: "switch the bedroom lamp off" and "kill the study
light" missed).

**Never stored 14 (holdout), 24 (dev).** Never items the denylist
missed reached the gateway, missed the cache, and were stored. That
is store poisoning: a stored never item can be served to a later
similar prompt. The 14 were in the driver's temp store, deleted
after the run; the live store was not touched and is not poisoned.
But the live gateway runs the same code, so in live use a missed
never item would be stored the same way. This follows from recall
below 1.0; it is not a separate bug.

**Unsafe hits 0.** The gateway did not serve a wrong or stale answer
in the holdout (or dev). The unblocked never items did not match
anything in the cache, so no bad serving occurred. The safety failure
is the guard being incomplete (recall, must-block, store poisoning),
not an actual bad serving in this run. The distinction matters: the
gateway is not actively harmful on this traffic, but its safety is
not assured for broader traffic.

**VALUE 0.029 (holdout).** One non-seed safe hit in 34 full-route
prompts. Two causes. First, the v4 set under-measures value: the
per-question re-split left most stable families as singletons, so
there are few repeat questions to hit (v3 dev, with paraphrase
families, measured 0.24 for the same code). The value number on v4
is a lower bound, not the gateway's true value. Second, the
denominator is large (34 full-route prompts, 21 of them never items
that can never be safe hits). The next eval set (v5) needs
paraphrase pairs per stable question so value is measurable.

**COST PASS.** Median total check 11.9 ms (seed) / 9.8 ms (empty)
on the holdout; max embed 43 / 52 ms. p95 was not directly measured
on the holdout (summary only, no detail by the holdout rule), but
the median is ~12 ms and the same code measured p95 26.5 ms on v3
dev, inside the 50 ms budget. Footprint unchanged (bge-m3 0.69 GB).
Rollback tested at 2.0 s.

**DATA MARGINAL.** The set is big enough (105/45; holdout 35/16).
The real share is thin (16 real prompts of 105, 6 in the holdout),
so the verdict rests mostly on eval traffic. Per Nitish's framing
(eval traffic is good traffic) the scoring stands; the split is
reported factually, not as a discount.

## What would need to change for a GO

1. **The guard must generalise.** Two options. (a) Patch the denylist
   to v1.3: add patterns for heating, timers, lists, appliances, the
   verbs kill / bolt / secure, and the "switch X on/off" word order.
   Quick, but a v5 holdout with new phrasings will likely find new
   gaps; regex patching is whack-a-mole. (b) Replace the regex
   denylist with a generalising guard (embedding similarity to
   action prototypes, or a small classifier). Bigger change, but the
   one that actually generalises. Recommended as the real fix.
2. **The eval set must measure value.** v5 needs paraphrase pairs
   per stable question (2+ phrasings each), so repeat hits are
   measurable, plus fresh never items to test the new guard.
3. **Re-validate on v5.** New code + new fresh holdout, scored once.
   The v4 holdout is retired (scored once, as required).

The gateway stays shadow (not live) until a full GO. The shadow
timer keeps running (next run Tue 24 Nov 06:00 UTC).

## Files

- Frozen case: `eval_set.json`, `eval_set_dev.json`,
  `eval_set_holdout.json`, `FROZEN.md` (Spark eval/v4/, VM
  [workspace]/v4/, md5-verified identical)
- Dev runs: `v22_dev_seed.json`, `v22_dev_empty.json` (+ .jsonl detail)
- Holdout runs (summary only): `v22_holdout_seed.json`
  (md5 b098d2ec1ab13a67c20598bf747faf34),
  `v22_holdout_empty.json` (md5 639fb2d9fc63420e54cc59555c83dc88)
- This report: `V4-VERDICT.md`
