# v5 verdict - semantic gateway

**Verdict: NO-GO.**
**Gateway under test:** v2.3-guard (guard v1.0, denylist v1.2,
threshold 0.90 / factual 0.85 / generative 0.85, TTL 24h / 168h).
**Date:** 23 Nov 2026. **Eval case:** frozen v5 (91 prompts,
66 families; dev 59/41, holdout 32/25). **Holdout scored exactly
once, summary only.**

## Holdout (the verdict)

Both modes identical.

| Metric | Seed | Empty | Bar | Result |
|---|---|---|---|---|
| Requests / consulted | 32 / 21 | 32 / 21 | - | - |
| Hits (safe / unsafe) | 4 / 0 | 4 / 0 | 0 unsafe | PASS |
| Weighted unsafe | 0 | 0 | 0 | PASS |
| Non-seed safe rate | 0.125 (4/32) | 0.125 (4/32) | >= 0.10 | PASS |
| Denylist recall | 0.8462 (11/13) | 0.8462 (11/13) | 1.0 | FAIL |
| Must-block | 0 / 2 | 0 / 2 | all | FAIL |
| Never items stored | 2 | 2 | 0 | FAIL |
| Denylist FP | 0.0 | 0.0 | 0.0 | PASS |
| Median check | 14.6 ms | 13.3 ms | p95 <= 50 ms | PASS |

## Dev (sanity, detail allowed)

Both modes identical. 59 requests, 41 consulted, 14 hits all
safe, 0 unsafe. Non-seed safe rate 0.2373 (14/59). Recall
0.6667 (14/21). Must-block 0/2. Never stored 7. FP 0.1053.
Median check 15.4 / 13.8 ms. Denylist-blocked 18.

The 7 dev escapes (stored): Boil the kettle, Has the tumble
dryer finished?, Make me a coffee., Play the radio in the
bedroom., Where is my parcel? (must-block), Are we out of milk?,
How many steps have I done today? (must-block). Rule C blocked
only 2 in dev (front-door camera, boost heating).

## Gates

- **SAFETY: FAIL.** Recall 0.8462 (holdout) and 0.6667 (dev),
  must-block 0/2 in both splits, 2 never items stored in the
  holdout (7 in dev). The guard catches the easy never items
  (regex and Rules A+B block 11 of 13 in the holdout) but misses
  the hard ones that rely on Rule C alone.
- **VALUE: PASS.** Holdout 0.125 vs the 0.10 bar; dev 0.2373.
  The paraphrase groups fixed v4's under-measurement: value is
  now measurable, and it clears the bar.
- **COST: PASS.** Median check ~14 ms, well inside the 50 ms
  p95 budget. (The guard report's p95 claim, 25.6/22.9 ms, is
  not traceable to a run artifact; the verified medians are
  14.4/13.3 ms on v4 dev and 14.6/13.3 ms on v5 holdout.)
- **DATA: MARGINAL.** 32 holdout prompts, 25 families, 0 real
  prompts (all blind-writer fresh). No new real traffic was
  available. Per Nitish's framing, eval traffic is good traffic;
  the verdict stands on the scoring as a whole.

## Why it fails

The 2 holdout escapes are the 2 must-block items: "Preheat the
oven to 180 degrees." (v5-042) and "Play some jazz in the
kitchen." (v5-052). Both rely on Rule C alone ("preheat" and
"play" are not in the Rule A verb class, and neither matches a
Rule B form). Rule C's embedding margin did not catch them, so
they were stored (miss-stored), poisoning the store. The same
pattern held on dev: both dev must-block items (parcel, steps)
escaped, and Rule C blocked only 2 of 13 Rule-C-only items.

The guard generalises to the easy cases and fails on the hard
ones. That is the sharpest test v5 was built to run, and the
guard fails it.

## The temperature false positive (dev only)

On dev, the regex `\btemperature\b` blocks 4 stable factual
questions ("At what temperature does water boil?" x2, "At what
temperature does water freeze?" x2), giving dev FP 0.1053. The
holdout has no temperature-phrased factual questions, so holdout
FP is 0.0 and the FP did not decide the holdout verdict. The FP
is a real guard weakness (the regex over-matches): any future
set containing temperature-phrased factual questions would fail
the SAFETY FP sub-criterion (0.0) on it. It is recorded here, not
hidden, and the 4 prompts stay labelled stable.

## Nuance

0 unsafe hits means no wrong or stale answer was actually served
in the holdout (all 4 hits were safe). The failure is the guard
being incomplete: 2 never items were stored, so a future similar
prompt could hit on them and be served a stale or wrong answer.
The mechanism is not safe enough to adopt live.

## What next (per the EDD loop)

- The v5 holdout is RETIRED (scored once). Do not re-score it
  or use it for tuning.
- Do NOT use v5 failures to tune this guard. A fix needs a v6:
  a stronger guard mechanism (the current Rules A+B+C are not
  sufficient for the hard cases) plus a fresh v6 holdout built
  from new prompts, labelled by the parent, frozen, and scored
  once.
- v2.3-guard stays SHADOW ONLY on :18795. No live serving, no
  repo push, no Medium article .
- Trial 2 (agentic P4 memory engine) is the next adoption
  candidate, unless Nitish orders a v6 first.

## Files

- Verdict: [workspace]/v5/V5-VERDICT.md (VM) + Spark
  eval/v5/V5-VERDICT.md (md5-verified identical).
- Frozen set: [workspace]/v5/eval_set.json (md5
  1970c919603c4336afa3353b80486c08), eval_set_dev.json
  (d6a6565c291fe1b46d8000684d196dd4), eval_set_holdout.json
  (66d12303d0c01e6c1c30f7ead76c702b), FROZEN.md
  (6fb9ac58be127c8e9b8ecf994a876d10). Spark mirror identical.
- Runs: v5/v23_dev_seed.json (fe0f72182ef1610fb79ece3c0cae0971),
  v5/v23_dev_empty.json (7af4377b167c959db64ee1c56ec5851d),
  v5/v23_holdout_seed.json (36183770e0dae3d8bc1882a984211639),
  v5/v23_holdout_empty.json (8c660d40b8cabc1ee10afda89d07171d).
  VM and Spark identical.
