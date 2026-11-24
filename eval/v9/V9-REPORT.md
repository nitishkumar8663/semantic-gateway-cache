# v9 candidate eval set report (round 4)

Date: 2026-11-23. Status: CANDIDATE. NOT finalised, NOT frozen, NOT
scored. The parent labels and freezes it.

## Counts

- Total: 91 prompts, 85 families.
- Cacheable: stable 36, never 35, ttl24 20.
- Categories: factual 36, action 14, perception 12, agent-task 9,
  generative 11, chatter 9.
- Paraphrase groups: 6 intact groups of 2 (12 prompts):
  V9-deepest-lake, V9-first-artificial-satellite,
  V9-tallest-waterfall, V9-driest-place, V9-largest-freshwater-lake,
  V9-longest-mountain-range. Two more groups were written but broken
  by collisions (see below).

## How it was built

A blind writer (a child agent, blind to all guard code, verdicts,
reports and eval files) wrote 100 fresh prompts to
[workspace]/v9-fresh-prompts.json (md5
da5ba5fc3e88a98ff2e9fe7148e5c2b7). It confirmed it read no guard,
verdict, report or eval file. Mix as briefed: stable 40, never 40,
ttl24 20; 8 paraphrase groups; canonical trivia avoided.

Collision check (normalised exact match + token Jaccard >= 0.85)
against the v3, v4, v5, v6, v7, v8 full sets (617 prompts) and the
600-request simulation workload (guard-build/simulation_workload.
json), 1,217 prior prompts in total. 9 collisions removed, all from
prior eval sets, none from the simulation workload:

| id | text | Jaccard | source |
| --- | --- | --- | --- |
| v9-001 | What is the largest hot desert in the world? | 1.0 | v5 v5-022 |
| v9-013 | What is the fastest land animal? | 1.0 | v5 v5-089 |
| v9-029 | What is the largest land mammal? | 0.857 | v7 v7-020 |
| v9-040 | What is the capital city of Norway? | 0.857 | v4 v4-027 |
| v9-051 | Remind me to call Mum at six this evening. | 1.0 | v8 v8-034 |
| v9-058 | Please preheat the oven to 180 degrees. | 0.857 | v5 v5-042 |
| v9-064 | Is it raining outside at the moment? | 0.857 | v8 v8-032 |
| v9-069 | Remind me to water the plants on Sunday. | 1.0 | v8 v8-040 |
| v9-076 | Has the kettle boiled? | 1.0 | v8 v8-031 |

Collisions by source: v5 3, v7 1, v4 1, v8 4. Full list in
[workspace]/v9-collisions.json (md5
d747842fccfb7944b1273ed5291664f7).

Surviving set 91 prompts, stable 36. Both are above the top-up
triggers (below ~85 prompts, or stable below ~25), so no second
blind batch was written. Note: the 9 collisions broke 2 of the 8
paraphrase groups (V9-largest-hot-desert lost v9-001, V9-fastest-
land-animal lost v9-013); the surviving member of each is now a
singleton. 6 intact groups remain. The parent may top up at freeze
time if 6 groups is too few for the value measurement.

## Labels

Proposed labels only (cacheable, category, group). must_block False
on all 91. split null on all 91. The parent sets must_block and the
dev/holdout split at freeze time.

## Static check under the current guard's form layers (v2.7)

Run from the repo root with the live v2.7 module (denylist regex + Rules
A/B, before Rule C):

- Never blocked by form layers: 27 of 35.
- 8 never rely on Rule C alone: v9-042 "Could you lower the heating
  in the bedroom a bit?" (lower is not in the action verb list),
  v9-061 "Is dinner ready yet?" (dinner is not a live entity),
  v9-065 "Who is at the front door?" (wh-word "who"; the presence
  form needs "is someone/anyone"), v9-068 "What's on my calendar
  tomorrow?" (agent-task, no form), v9-070 "Can you cancel my
  dentist appointment on Thursday?" (cancel is not in the action
  verb list), v9-077 "Where did I park the car?" (park is not
  covered), v9-078 "Is the washing dry yet?" (dry is not a state
  word), v9-079 "What time is sunset today?" (live daily fact, no
  form). These are the same kind of Rule C reachers as prior rounds
  (v8 had 8); they are not failures, they are what Rule C is for.
- FP on cacheable (stable/ttl24) under the form layers: 0.

## Near-paraphrases of prior items (noted, not removed)

17 prompts have token Jaccard 0.70-0.85 against a prior item (below
the 0.85 removal threshold). They are genuine new phrasings or
different facts, not duplicates:

- v9-008 waterfall/highest vs v5-011 mountain/highest (0.750)
- v9-017 largest volcano vs v4-084 largest planet (0.700)
- v9-020 dodecagon sides vs v5-090 hexagon sides (0.750)
- v9-021 silver symbol vs v5-007 gold symbol (0.750)
- v9-028 smallest bird vs v8t-020 largest bird (0.750)
- v9-031 Switzerland currency vs v5-028 Japan currency (0.714)
- v9-037 largest amphibian vs v5-036 largest mammal (0.750)
- v9-041 turn off kitchen lights vs v7-029 same action (0.750)
- v9-043 start washing machine vs v8-021 same action (0.800)
- v9-044 open living room blinds vs v8-017 same action (0.833)
- v9-047 washing finished vs v6-045 washing machine finished
  (0.833)
- v9-050 back door locked vs v3-022 door locked (0.800)
- v9-065 who is at the front door vs v5-059 who is at the door
  (0.833)
- v9-066 add milk to shopping list vs v7-056 add milk and bread
  (0.750)
- v9-083 birthday toast vs v8-048 wedding toast (0.727)
- v9-090 good morning how are you vs v8-054 good morning how are
  you doing today (0.714)
- v9-093 haiku about the sea vs v6-087 poem about the sea (0.778)

## Files

- [workspace]/v9/eval_set_v9.json: 65a51b64d732f9bfde284020f3ffe6f1
  (91 prompts, candidate, must_block False, split null).
- [workspace]/v9-fresh-prompts.json:
  da5ba5fc3e88a98ff2e9fe7148e5c2b7 (100 prompts, blind writer batch).
- [workspace]/v9-collisions.json:
  d747842fccfb7944b1273ed5291664f7 (9 collisions).
- Spark mirror: [spark-home]/team/gateway-shadow-trial/eval/v9/
  (eval_set_v9.json and V9-REPORT.md; md5s verified VM vs Spark by
  direct comparison: eval_set_v9.json
  65a51b64d732f9bfde284020f3ffe6f1, V9-REPORT.md
  8bfdb8a1fae3b0558cf85e203c5b829f, both identical on VM and Spark).
