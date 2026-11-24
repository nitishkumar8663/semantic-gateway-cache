# v10 candidate eval set - report

Date: 24 Nov 2026
Status: CANDIDATE. Proposed labels only, must_block False on all, split
null. NOT finalised, NOT frozen, NOT scored. The parent labels and freezes
it; the holdout is scored exactly once.

## Counts

- Prompts: 108 (batch 1 65 surviving + top-up 43 surviving)
- Families: 101
- Cacheable: stable 40, never 44, ttl24 24
- Category: factual 40, action 20, perception 12, agent-task 12,
  generative 13, chatter 11
- Paraphrase groups (2+ phrasings, same group): 7 groups, 14 prompts

## How it was built

Two blind writer batches. Both writers were blind to the guard code, all
verdicts, reports and eval files; each confirmed it read no guard, verdict,
report or eval file.

- Batch 1: 100 prompts (stable 40, never 40, ttl24 20; 8 paraphrase
  groups, 92 families). File: [workspace]/v10-fresh-prompts.json.
- Batch 2 (top-up): 50 prompts (stable 20, never 20, ttl24 10; 6
  paraphrase groups, 44 families). File:
  [workspace]/v10-topup-fresh-prompts.json. Written to less-obvious
  topics after batch 1 collided heavily on canonical trivia.

## Collisions removed (normalised exact match + token Jaccard >= 0.85)

Batch 1: 35 removed, 65 survived. By source: v5 9, v7 8, v6 6, v8 5,
v9 3, v4 2, v3 2. No simulation-workload collisions. Full list:
collisions_batch1.json. Notable: 19 of the 35 were exact duplicates of
prior prompts (the first writer kept picking the most obvious canonical
trivia: largest ocean, Mona Lisa, hexagon, rainbow, Romeo and Juliet,
Japan currency, spider legs, Hobbit, kangaroo, lock/unlock door, open
blinds, dinner ready, haiku about autumn rain, limerick about a forgetful
wizard). The surviving set after batch 1 was 65 prompts with stable 22,
below the top-up triggers (~85 prompts, stable ~25), so a second batch
was written.

Top-up: 7 removed, 43 survived. By source: v6 2, v7 2, v8 1,
v10-batch1 2 (two top-up prompts collided with batch-1 prompts). Full
list: collisions_topup.json.

Total collisions removed: 42.

## Static check under the v2.8 form layers

Regex v1.5 + Rules A/B v6, pure text (Rule C not run), on the merged 108:
- Never 44: 38 blocked by regex or Rules A/B, 6 rely on Rule C alone.
  The 6: v10-061 "When does the sun go down today?", v10-064 "Has the
  post arrived today?", v10-067 "Is the car charged enough for
  tomorrow?", v10-075 "What is on my calendar tomorrow?", v10t-032 "Can
  you check if the oven is still on?", v10t-033 "Is my phone charging in
  the bedroom?".
- FP on cacheable (stable/ttl24): 0.

## Near-paraphrases (noted, not removed)

26 items with token Jaccard 0.70-0.85 against a prior eval prompt. Full
list: near-paraphrases are recorded in the collision-check output file
v10-near-paraphrases.json (VM: [workspace]/v10/, Spark: eval/v10/).
Notable ones:
- v10t-044 "Write a birthday message for a friend who loves cycling."
  (0.727 vs v7-068 "Draft a birthday message for my friend who loves
  cycling."). Same creative-draft class as the v7 holdout FP; a different
  verb (write vs draft). The parent decides at freeze time whether it
  stays.
- v10-041 "Turn on the hallway light" (0.833 vs v9-056 "Turn on the
  hallway light, please."), v10-046 "Could you lower the heating a bit?"
  (0.778 vs v9-042), v10-057 "Has my parcel arrived yet?" (0.800 vs
  v9-063), v10t-030 "Is the washing machine finished yet?" (0.833 vs
  v5-040). Same forms as prior items with a small wording change; these
  test whether the guard generalises rather than memorising exact
  strings.

## Files

VM ([workspace]/v10/):
- eval_set_v10.json (md5 762e806cc260eb5b1a1967df4a61ca19)
- collisions_batch1.json (md5 531857246d4afe873855791b1834c0d2)
- collisions_topup.json (md5 c842dbbfb500e7cf5c36d6811a1a7d02)
- v10-near-paraphrases.json (md5 verified directly, see below)
- V10-REPORT.md (this file; md5 verified directly)

Spark mirror (eval/v10/): same files, md5s verified directly.

Source writer files (VM, not part of the candidate set):
- [workspace]/v10-fresh-prompts.json (batch 1, 100 prompts)
- [workspace]/v10-topup-fresh-prompts.json (batch 2, 50 prompts)

Note: this report's own md5 is NOT listed in the Files table (the v2.5
stale self-md5 bug). It was verified directly VM vs Spark; if the report
is edited after verification, re-verify and re-mirror it.
