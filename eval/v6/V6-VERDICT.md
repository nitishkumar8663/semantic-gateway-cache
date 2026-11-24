# v6 verdict - NO-GO (round 1 of the loop)

**Gateway:** v2.4-guard (guard v2.0; denylist v1.3; Rule A v2 + Rule B v2;
Rule C margin 0.20; 33 action + 17 safe prototypes; thresholds 0.90 /
factual 0.85 / generative 0.85; TTL 24h / 168h stable).
**Eval set:** frozen v6 (89 prompts, 77 families; dev 56/49, holdout 33/28).
**Scored:** 23 Nov 2026, drive_gateway_v3.py, seed store
cache_store_backup_20261123.json (16 entries), temp stores only.
**Verdict: NO-GO.** SAFETY FAIL, VALUE FAIL (just below the bar),
COST PASS.

## Holdout (scored exactly once, summary only; both modes identical)
- 33 requests, 20 consulted, 13 blocked by denylist, 0 route-blocked.
- Hits 3 safe, 0 unsafe. Weighted unsafe 0.
- **Non-seed safe rate 0.0909 (3/33) vs the 0.10 bar. VALUE FAIL.**
- **Denylist recall 0.9231 (12/13) vs 1.0. SAFETY FAIL.**
- **Must-block 1/2 vs all. SAFETY FAIL.** Door-who blocked by Rule C
  (guard-margin); doorbell escaped and was stored (similarity 0.4506,
  no match).
- **Never items stored 1 vs 0. SAFETY FAIL.** The doorbell prompt.
- **FP 0.05 vs 0.0. SAFETY FAIL.** One stable prompt blocked:
  v6-015 "Count the continents for me, how many are there?" (Rule A
  matched the leading verb "count").
- Median check 14.6 ms (seed) / 13.3 ms (empty). COST PASS (median well
  under the 50 ms budget; the run JSONs carry no p95 field, same
  provenance gap as the v5 report).

## Dev (sanity, detail allowed; both modes identical)
- 56 requests, 34 consulted, 22 blocked by denylist, 0 route-blocked.
- Hits 3 safe, 0 unsafe. Non-seed safe rate 0.0536.
- Recall 0.8696 (20/23). Must-block 0/2. Never stored 3.
- FP 0.0606 (2 FPs, both in dev).
- Median check 14.9 ms (seed) / 13.7 ms (empty).

## What escaped (dev detail)
Three never items were stored (Rule C did not block them):
- "Mow the lawn this afternoon." (must-block; similarity 0.4798)
- "How many hours did I sleep last night?" (similarity not recorded)
- "Where are my car keys?" (must-block; similarity 0.4691)
The holdout escape was "Did someone just ring the doorbell?"
(similarity 0.4506). All four are short, everyday forms. Rule C's
single global margin of 0.20 does not separate them from safe
prompts. The v2.4 dev recall of 1.0 (on v3/v4/v5 dev) did not
generalise to these fresh forms.

## False positives (guard blocking cacheable prompts)
- Dev: "Water boils at what temperature at sea level?" (Rule A matched
  leading word "water", here a noun) and "Write a short story about a
  lighthouse keeper who finds a message in a bottle." (regex
  `\bmessage\b` matched "message" in a creative prompt).
- Holdout: "Count the continents for me, how many are there?" (Rule A
  matched leading verb "count" on a factual question).
Rule A matches the first word regardless of part of speech, and the
message regex is too broad. These were latent in v2.3 and are exposed
by v6.

## Hits (dev, all safe)
- "Name the highest mountain in the world." (sim 0.931, matched "What
  is the tallest mountain on Earth?")
- "A hexagon has how many sides?" (sim 0.9245, matched "Tell me the
  number of sides on a hexagon.")
- "Tell me which vitamin we get from sunlight." (sim 0.8868, matched
  "Which vitamin does sunlight help our bodies make?")
Holdout hits: 3 safe, 0 unsafe (summary only, no detail).

## Gates vs the agreed pass criteria
- SAFETY: FAIL (recall 0.9231, must-block 1/2, never stored 1, FP 0.05).
- VALUE: FAIL (0.0909 vs 0.10; just below the bar).
- COST: PASS (median ~14 ms).
- DATA: MARGINAL (0 real prompts in v6; eval traffic is good traffic).

## Nuance
0 unsafe hits means no wrong or stale answer was actually served. The
failure is the guard being incomplete (Rule C misses short everyday
forms; Rule A and the message regex over-block). The value shortfall
is small (0.0909 vs 0.10) and is partly the v6 set's shape (only 10
paraphrase groups; most stable families are singletons, so few repeat
opportunities).

## Next (loop round 2)
The v6 holdout is RETIRED (scored once, never to be re-scored or used
for tuning). Round 2 (v7) builds a stronger guard plus a fresh v7
candidate set. The most promising lever, documented in
GUARD-V6-REPORT.md, is a per-category Rule C margin (a lower margin
for the imperative class, keeping 0.20 for questions), validated on
dev first and keeping FP 0.0. The FP fixes (Rule A part-of-speech
awareness, narrowing the message regex) are a general pattern-class
fix, not per-item patches.

## Files
- Frozen set: `eval/v6/eval_set.json`, `eval_set_dev.json`,
  `eval_set_holdout.json`, `FROZEN.md` (md5-verified VM and Spark).
- Runs: `eval/v6/v24_dev_seed.json`, `v24_dev_empty.json`,
  `v24_holdout_seed.json`, `v24_holdout_empty.json` (md5-verified VM
  and Spark). Dev detail: `v24_dev_seed.jsonl`, `v24_dev_empty.jsonl`
  (Spark only).
- Guard report: `eval/GUARD-V6-REPORT.md`.
- This verdict: `eval/v6/V6-VERDICT.md` (VM mirror
  `[workspace]/v6/V6-VERDICT.md`).
