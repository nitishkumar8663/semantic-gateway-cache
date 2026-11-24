# E5 threshold sweep - dev only (eval v3)

**Date:** 23 Nov 2026. **Scorer:** v3.0. **Variant:** scoped.
**Workload:** `eval/v3/eval_set_dev.json` (110 prompts, 33 families).
**Seed mode:** with-seed (the store starts from the 16-entry live
snapshot, real `created_at` timestamps, 22 Nov 05:28 UTC).
**Pre-registered rule (assessment E5):** pick the highest threshold
with zero unsafe on dev (unweighted AND traffic-weighted) AND a
safe-hit rate at or above 10% of full-route traffic. If none, the
mechanism fails.

## Results

| Threshold | Norm | Hits | Safe | Unsafe | Weighted unsafe | Full-route safe rate | Recall | FP (gw) | Expired misses | Never stored |
|---|---|---|---|---|---|---|---|---|---|---|
| 0.90 | off | 6 | 5 | 1 | 1 | 0.0676 | 0.7097 | 0.0167 | 19 | 8 |
| 0.90 | on | 8 | 7 | 1 | 1 | 0.0946 | 0.7097 | 0.0167 | 18 | 8 |
| 0.93 | off | 6 | 5 | 1 | 1 | 0.0676 | 0.7097 | 0.0167 | 18 | 8 |
| 0.93 | on | 7 | 6 | 1 | 1 | 0.0811 | 0.7097 | 0.0167 | 18 | 8 |
| 0.95 | off | 4 | 3 | 1 | 1 | 0.0405 | 0.7097 | 0.0167 | 17 | 8 |
| 0.95 | on | 6 | 5 | 1 | 1 | 0.0676 | 0.7097 | 0.0167 | 18 | 8 |
| 0.98 | off | 4 | 3 | 1 | 1 | 0.0405 | 0.7097 | 0.0167 | 13 | 8 |
| 0.98 | on | 6 | 5 | 1 | 1 | 0.0676 | 0.7097 | 0.0167 | 14 | 8 |

Full-route dev requests: 74. The 10% bar is 8 safe hits.

## Outcome: NO threshold satisfies the pre-registered rule

**The mechanism fails on dev, per the rule.** Every config has
exactly 1 unsafe hit, and the best safe-hit rate (0.0946 at 0.90
with normalisation) is below the 0.10 bar. The two conditions fail
independently: safety fails at every threshold, value fails at
every threshold.

## The unsafe hit is threshold-independent

All 8 configs produce the same unsafe hit: NM-A alert-3b (a third
perception alert, different frame side, same camera and wording)
hits the real alert 1 at similarity 0.9976 (0.9971 with
normalisation). It is a genuinely different event (different side
of the doorway) served as the first alert. No threshold in
0.90-0.98 separates it, because it sits above 0.98. Only a
denylist pattern for perception alerts (code fix C3) or an
intent/action classifier in front of the cache can stop it. This
is the finding the sweep was built to produce: the threshold is
not the problem. The mechanism cannot tell "same question" from
"different question" when the texts are near-identical but the
events differ.

## Normalisation helps value, hurts nothing

Normalisation (lowercase, strip punctuation/whitespace) adds 2
safe hits at every threshold and 0 unsafe hits. At 0.90 it lifts
the full-route safe rate from 0.0676 to 0.0946. It is the one
sweep finding in favour of a code change (C2).

## The value shortfall is partly an artefact of the timeline

13-19 hits per run are lost to TTL expiry (`expired_misses_ttl`).
The two-wave timeline (variants days apart) plus the 24h TTL
empties the store between waves: wave-1 entries are 2-6 days old
by wave 2, and most seed entries are past 24h by mid-day-0. In
production with continuous traffic, entries would be refreshed
and the store would not empty this way, so the measured safe-hit
rate understates what continuous traffic would give. This caveat
applies to the VALUE side of the rule only. It does NOT apply to
the safety side: the alert hit happens despite the TTL, at an
entry age of ~8.5 hours.

Non-seed safe hits (the honest value number): at 0.90 with
normalisation, 7 safe hits, of which 1 matched a seed entry and
6 did not (6/74 = 8.1% of full-route traffic, still below the
10% bar). At 0.98 without normalisation, 3 safe hits, 1 seed, 2
non-seed (2.7% of full-route traffic).

## Denylist recall fell to 0.7097 (22/31)

v2 measured 0.8276. The drop is because the v3 probes added 4
new escapes: alert-3b, alert-3c, "turn the lights on!", "turn the
lights off". Together with the 5 must-block escapes, 9 of 31
never items that reach the denylist escape it. The denylist v1.1
has no pattern for perception alerts and none for verb-object
lights phrasings. Recall 1.0 is a pass criterion (E7); it is not
met, and the fix is code (C3, denylist v1.2 in the gateway), not
a different threshold.

## What this decides

- The E5 decision rule returns MECHANISM FAILS for raw cosine
  similarity on bge-m3 at a single threshold. The next step is a
  code change (C3 denylist + TTL in the gateway, C2
  normalisation, C1 exact-match fast path), judged against this
  frozen eval case - not a lower threshold.
- The frozen threshold for the baseline is 0.98 (the current
  shipped value). It is frozen as the baseline setting, not as a
  passing setting. Any future threshold change requires a version
  bump and a re-freeze.
- The sweep was run on dev only. Holdout was not touched by the
  sweep and must not be used to pick a threshold.
