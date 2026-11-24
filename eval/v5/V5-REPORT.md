# v5 candidate eval set - report

**Status: CANDIDATE ONLY. Not frozen, not scored, labels PROPOSED.**
The parent labels and freezes v5 before its single scoring. The
v4 holdout was not used. The guard (v2.3-guard) was NOT tuned on
v5 in any way.

**Date:** 23 Nov 2026 (evening). **Built from:** the blind prompt
writer's fresh set (100 prompts, written blind to the guard code),
minus 9 collisions. **No new real traffic** was available: the
dispatcher audit log and shadow replays are unchanged since v4
(the next shadow replay is Tue 24 Nov 06:00 UTC), and the live
gateway log since the v2.3-guard deploy contains only the
deploy-verification test queries. So v5 is built from the blind
writer's fresh set, as the task specified (no padding beyond it).

## Counts (91 prompts, 66 families)

| Cacheable | n | Categories |
|---|---|---|
| stable | 49 | factual 49 |
| never | 34 | action 16, perception 10, agent-task 8 |
| ttl24 | 8 | chatter 2, generative 6 |

- Paraphrase groups (2+ phrasings): 15 groups, 40 prompts. 14
  factual groups (38 prompts) for VALUE measurement + smalltalk
  (2 prompts). Each group is one question in 2-3 genuinely
  different phrasings (word order, synonyms, "tell me" form,
  statement form). This fixes v4's under-measurement of value
  (most stable families were singletons after the per-question
  re-split).
- Factual singletons: 11 (stable, one phrasing each, new topics).
- Never families: 34 (each never item is its own family).
- Proposed must_block: 4 (the guard's hardest never cases - see
  below). PROPOSAL ONLY; the parent finalises must_block at
  labelling.

## What is new in v5 (vs v3/v4)

**New never categories** (the guard's generalisation test):
appliances (washing machine, dishwasher, oven, kettle, fridge,
robot vacuum, tumble dryer, coffee machine), garden (watering,
mowing, sprinklers, hose), media (play music, TV on, volume down,
pause, radio), home security (arm alarm, front camera, doorbell,
alarm check), shopping/delivery (order groceries, book taxi,
track parcel, order takeaway, milk stock), health (take medicine,
drink water, steps today). Plus new phrasings of lights
("dim the bedroom lights"), heating ("boost the heating for an
hour"), lists, reminders, and weather ("do I need a coat today?").

**Hard cases for the guard** (deliberately included; they probe
the guard's known blind spots):
- "Preheat the oven to 180 degrees." - "preheat" is not in the
  Rule A verb class.
- "Play some jazz in the kitchen." / "Play the radio in the
  bedroom." - "play" is not in the Rule A verb class.
- "Boil the kettle." - "boil" is not in the verb class.
- "Boost the heating for an hour." - "boost" is not in the verb
  class.
- "Make me a coffee." - "make" is deliberately excluded from
  Rule A (it also heads creative requests).
- "Show me the front door camera." / "Who is at the door?" -
  no leading action verb, no Rule B form.
- "Where is my parcel?" - a live-status query; the status
  prototypes were removed from Rule C (they caused false
  positives), so this tests whether Rule C catches it anyway.
- "Are we out of milk?" - live pantry state, no Rule A/B form.
- "How many steps have I done today?" - live health data phrased
  as a "how many" question (looks factual).
- "Is the washing machine finished?" / "Has the tumble dryer
  finished?" - "finished" is not in the Rule B state words, and
  "has" is not a Rule B interrogative.
These are the items most likely to be missed. They are the
sharpest test of whether the guard generalises or only memorised
dev. (Proposed must_block: "Preheat the oven to 180 degrees.",
"Play some jazz in the kitchen.", "Where is my parcel?",
"How many steps have I done today?")

**Near-paraphrases of v3/v4 items, kept deliberately** (different
normalised text, so not collisions; they test within-category
generalisation):
- "Is the fridge door open?" vs v3 "is the door open" (different
  object: fridge door vs door).
- "Add eggs to the shopping list." vs v4 "add eggs to my shopping
  list" (determiner differs).
- "Remind me to call Mum at 6pm." vs v4 "remind me to call Mum at
  six" (time format differs).
- "Do I need a coat today?" vs v4 "do I need a jacket today?"
  (clothing differs).
- "Write me a haiku about coffee." vs v3 "write me a haiku about
  rain" (topic differs).

## Collisions removed (9)

Exact normalised matches against v3, v4, or the simulation set.
All 9 are generic short prompts (greetings, "what time is it",
a haiku about rain, one planet question).

| Prompt | Found in |
|---|---|
| Which planet is closest to the Sun? | v4 (V4-F-planets-mercury) |
| What time is it? | v3 (R-T2), sim (T2) |
| Hi there. | sim (GR1) |
| Good morning. | v3 (R-GR), sim (GR1) |
| Tell me a joke. | v3 (R-C1), sim (C1) |
| Make me laugh. | v3 (R-C1), sim (C1) |
| What's up? | v4 (V4-F-smalltalk) |
| Good night. | v3 (R-GR) |
| Write me a haiku about rain. | v3 (G2), sim (G2) |

Removing "Which planet is closest to the Sun?" leaves the
planet-closest-sun family as a singleton ("What is the nearest
planet to the Sun?"). Removing the 5 smalltalk greetings leaves
smalltalk with 2 items ("How are you today?", "How's it going?").
Removing the haiku about rain deletes the generative-haiku-rain
family. No near-duplicates (token Jaccard >= 0.85) were found
beyond the 9 exact collisions.

## Proposed labels (for the parent to finalise)

- category / cacheable: as written by the blind writer, kept as
  proposed. All 91 are route=full (no bus items in v5; they are
  all user prompts that would reach the gateway as full-route).
- must_block: 4 proposed (listed above). The parent confirms or
  changes these at labelling.
- split: "candidate (not frozen, not scored)". ts is None (the
  driver will use live time). No dev/holdout split yet - the
  parent splits by family at freezing time.
- Every item carries "labelled_by": "proposed (parent to
  finalise)" and "must_block_proposed": true, so no one mistakes
  the candidate for a frozen set.

## Files

- Candidate set: [workspace]/v5/eval_set_v5.json (VM) + Spark
  mirror [spark-home]/team/gateway-shadow-trial/eval/v5/eval_set_v5.json
  (md5-verified below)
- Blind writer output: [workspace]/v5-fresh-prompts.json
  (100 prompts, the source; 9 removed as collisions)
- Collision check: [workspace]/guard-build/check_v5_collisions.py
- Build script: [workspace]/guard-build/build_eval_set_v5.py
- This report: [workspace]/v5/V5-REPORT.md (VM) + Spark mirror
  eval/v5/V5-REPORT.md

## What the parent still needs to do (NOT done here)

1. Label v5 (confirm or change category/cacheable/route/
   must_block per item; confirm the 4 proposed must_block items).
2. Freeze v5 (FROZEN.md, dev/holdout split by family, pass
   criteria reference). The dev/holdout split should keep
   paraphrase groups intact (all phrasings of one question in the
   same split, so the holdout tests unseen questions, not unseen
   phrasings of seen questions) - or split by family as v4 did,
   and note the choice.
3. Score the frozen v2.3-guard ONCE against the v5 holdout
   (summary only). Do not score v5 before freezing, and do not
   use v5 failures to tune the guard (that would need a v6).
