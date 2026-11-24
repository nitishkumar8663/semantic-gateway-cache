# v11 candidate eval set - report

Date: 24 Nov 2026
Status: CANDIDATE. Proposed labels only, must_block False on all, split
null. NOT finalised, NOT frozen, NOT scored. The parent labels and freezes
it; the holdout is scored exactly once.

## Counts

- Prompts: 106 (batch 1 67 surviving + top-up 39 surviving)
- Families: 95
- Cacheable: stable 44, never 42, ttl24 20
- Category: factual 44, action 20, perception 11, agent-task 11,
  generative 14, chatter 6
- Paraphrase groups (2+ phrasings, same group): 11 groups, 22 prompts

## How it was built

Two blind writer batches. Both writers were blind to the guard code, all
verdicts, reports and eval files; each confirmed it read no guard, verdict,
report or eval file.

- Batch 1: 100 prompts (stable 40, never 40, ttl24 20; 9 paraphrase
  groups, 91 families). File: [workspace]/v11-fresh-prompts.json.
- Batch 2 (top-up): 50 prompts (stable 20, never 20, ttl24 10; 7
  paraphrase groups, 43 families). File:
  [workspace]/v11-topup-fresh-prompts.json. Written to less-obvious
  topics after batch 1 collided heavily on canonical trivia.

## Collisions removed (normalised exact match + token Jaccard >= 0.85)

Batch 1: 33 removed, 67 survived. By source: v8 11, v10 6, v6 5, v5 4,
v4 2, v9 2, v7 2, v3 1. No simulation-workload collisions. Full list:
collisions_batch1.json. Notable: 30 of the 33 were exact duplicates. The
first writer picked topics straight from the brief's example list that
were already used in prior sets (spider legs, liquid metal at room
temperature, guacamole, rainbow, Romeo and Juliet, hexagon, closest
planet to the Sun, Hobbit author) and the most obvious never forms
(lock the front door, set a timer for twenty minutes, send a message to
Reema, add milk to the shopping list, remind me to water the plants,
where is my phone, weather right now, sun go down, calendar tomorrow,
post arrived) and ttl24 (lighthouse keeper story, wedding toast, joke
about cats, what are you up to this weekend, feeling tired, how was your
day, what should I do this weekend). The surviving set after batch 1 was
67 prompts, below the top-up trigger (~85 prompts), so a second batch
was written.

Top-up: 11 removed, 39 survived. By source: v11-batch1 4, v9 3, v10 2,
v8 1, v5 1. No simulation-workload collisions. Full list:
collisions_topup.json. Notable: both "deepest lake" paraphrase prompts
collided exactly with v9-003/v9-004, so that whole group dropped out;
"tallest building", "minutes in a day", "tallest mountain in Africa"
and "where did I put my keys" collided with batch-1 survivors; "haiku
about the sea at dawn" with v9-093; "joke about dogs" with v10-092;
"bones in the adult human body" with v8t-011; "robot vacuum in the
hallway" with v10t-024; "poem about autumn rain" at 0.857 vs v5-077.

Total collisions removed: 44.

## Static check under the v2.9 form layers

Regex v1.5 + Rules A/B v7, pure text (Rule C not run), on the merged 106:
- Never 42: 42 blocked by regex or Rules A/B, 0 rely on Rule C alone.
  New-form coverage in the set: v11-063 "Is my car charged enough to
  drive tomorrow?" (state-query), v11-068 "Can you check if the washing
  is dry?" (check-if), v11t-030 "Can you check if the garage door is
  open?" (check-if), v11t-033 "Can you check if the laundry has
  finished?" (check-if), v11t-031 "Is anyone in the garden right now?"
  (presence), v11t-034 "What is the temperature in the study right
  now?" (regex).
- FP on cacheable (stable/ttl24): 0.

Note for the parent at freeze time: there are no Rule-C-only never items
in this candidate, so must_block cannot be picked from the usual
Rule-C-only pool. The hardest items are the new-form ones above and the
form-blocked state queries; the parent decides which 2 become must_block.

## Near-paraphrases (noted, not removed)

30 items with token Jaccard 0.70-0.85 against a prior eval prompt. Full
list: v11-near-paraphrases.json (VM: [workspace]/v11/, Spark:
eval/v11/). Notable ones:
- v11-027 "What gas do plants absorb from the air?" (0.800 vs v8-002
  "What gas do plants absorb from the air for photosynthesis?"). This is
  a photosynthesis-adjacent question, a topic on the avoid-list. It
  survived because it is a near-paraphrase, not a collision, and the
  rule is noted-not-removed. The parent decides at freeze time whether
  it stays.
- v11-046 "Start the vacuum in the hallway." (0.833 vs v10t-024 "Start
  the robot vacuum in the hallway."), v11-087 "Write a short story about
  a cat who learns to paint." (0.818 vs v10-081 "...a cat who learns to
  fly"), v11-089 "Write a poem about the first snow of winter." (0.800
  vs v8-046, a haiku on the same topic), v11-010 "What is the smallest
  ocean in the world?" (0.750 vs v8-006 "largest ocean"), v11-013 "What
  is the tallest building in the world?" (0.750 vs v5-010 "tallest
  mountain"). Same forms as prior items with a small wording change;
  these test whether the guard generalises rather than memorising exact
  strings.

## Files

VM ([workspace]/v11/):
- eval_set_v11.json (md5 b4168a5e1a09a5b29381baa4307f5dde)
- collisions_batch1.json (md5 eaf4f01eec786c925f9e7886ac636202)
- collisions_topup.json (md5 3d39d23d012cbe3cfbebdf74b8157e33)
- v11-near-paraphrases.json (md5 f0d395ad91666dd315d06f999b95cf58)
- V11-REPORT.md (this file; md5 verified directly)

Spark mirror (eval/v11/): same files, md5s verified directly.

Source writer files (VM, not part of the candidate set):
- [workspace]/v11-fresh-prompts.json (batch 1, 100 prompts)
- [workspace]/v11-topup-fresh-prompts.json (batch 2, 50 prompts)

Note: this report's own md5 is NOT listed in the Files table (the v2.5
stale self-md5 bug). It was verified directly VM vs Spark; if the report
is edited after verification, re-verify and re-mirror it.
