# v6 candidate eval set - report

**Status: CANDIDATE ONLY.** Proposed labels, not finalised, not
frozen, not scored. The parent labels and freezes this set (assigns
the dev/holdout split, confirms cacheable/category/route, sets
must_block) before its single scoring. Do NOT score this candidate.

## What it is

- **File:** `eval_set_v6.json` (this directory; Spark mirror:
  `eval/v6/eval_set_v6.json`, md5 `2baf1474fc1560971b34e45536989242`)
- **89 prompts, 77 families.** cacheable: stable 43, never 36,
  ttl24 10. Category: factual 43, action 18, perception 11,
  agent-task 7, generative 7, chatter 3.
- **Paraphrase groups:** 10 stable groups with 2+ phrasings (22
  prompts); 67 singleton families. The 10 stable paraphrase groups
  are what make value measurable (recall after the first phrasing).
- **4 proposed must_block** (see below). `must_block` is False on
  every item in the candidate; the parent sets it at labelling.
  `split` is null on every item; the parent assigns dev/holdout.

## How it was built

1. A blind prompt writer (child agent, blind to the guard code; did
   not read any verdict/report/eval files) wrote 110 fresh prompts
   to `[workspace]/v6-fresh-prompts.json`. Counts as written:
   stable 59, never 41, ttl24 10.
2. Collision check (`guard-v6-build/collision_check_v6.py`):
   normalised exact match plus token Jaccard >= 0.85, against the
   v3, v4, v5 full sets (dev + holdout) and the 600-request
   simulation workload (`guard-build/simulation_workload.json`).
   The check is a mechanical freshness check: it only reports
   which v6 prompts collide, never the prior prompts' contents,
   and no holdout content was used to change the guard (the guard
   was already built and deployed before this check ran).
3. **21 collisions removed.** 19 against the v5 full set (16
   stable, 5 never), 1 against the simulation workload
   (V6-japan-capital, Jaccard 0.857), 0 against v3 or v4. The v5
   collisions are mostly canonical trivia the writer reproduced
   independently (spider legs, Mona Lisa, gold symbol, leap-year
   days, largest ocean/desert, water formula, boiling point,
   first moon walker, hexagon sides, continents count) plus five
   hard never forms (fridge door open, play jazz, out of milk,
   steps today, add to shopping list). Full list:
   `guard-v6-build/collisions_v6.json`.
4. 89 prompts remain. No replacements were written (the writer's
   batch is the batch; the parent can top up at labelling if it
   wants a round 90-100).

## Composition note

89 prompts is one short of the ~90-100 target, and 77 families is
above the ~65 target. The shortfall is the collision rate on
canonical trivia (the writer reproduced v5's general-knowledge
questions). The never side is strong: 36 fresh never items across
action (18), perception (11) and agent-task (7), including new
categories (lawn, garden, sprinklers, hose, car keys, sleep,
doorbell) and new phrasings of the hard forms (parcel, steps,
milk, camera, doorbell).

## Proposed must_block (4)

Chosen from the 8 never items the form layers (regex v1.3 +
Rule A v2 + Rule B v2) do NOT catch, i.e. the ones that rely on
Rule C alone. The selection used only the form-rule structure
(which layer catches an item); Rule C was never run on the v6
set, and no recall / must-block / value was computed. The 8
form-rule misses are `guard-v6-build/v6_form_misses.json`. The 4
proposed must_block span 4 failure modes:

| Group | Text | Failure mode |
|---|---|---|
| V6-lawn-mowing | Mow the lawn this afternoon. | Novel imperative verb (mow not in Rule A) |
| V6-door-camera-who | Who is at the front door right now? | Perception, no state word |
| V6-doorbell-rang | Did someone just ring the doorbell? | Live event, doorbell not an entity |
| V6-car-keys-where | Where are my car keys? | Location, "where are" (not "where is") |

The other 4 form-rule misses (Run the dishwasher now; Is the
alarm armed at the moment?; How many hours did I sleep last
night?; Is it raining outside right now?) remain as ordinary never
items: they still must be blocked for recall, they are just not
designated must_block.

## Real traffic

No new real traffic was available. The audit log and shadow
replays are thin, as expected. This set is blind-writer fresh
prompts, not real traffic. Recorded honestly per the task. (Nitish's
position: eval traffic is good traffic, so fresh eval prompts
count as holdout traffic.)

## What the parent does next

1. Label and freeze: confirm cacheable/category/route per item,
   set `must_block` (accept or change the 4 proposals), assign the
   dev/holdout split (suggested: holdout ~30 prompts with the 4
   must_block in it, dev the rest; the exact split is the parent's
   call), set `frozen: true` and `status: "frozen"`.
2. Score the holdout exactly once with the v2.4-guard driver run
   (threshold 0.90 / factual 0.85 / generative 0.85, TTL 24h/168h,
   seed store `cache_store_backup_20261123.json`, seed and empty
   modes, temp stores).
3. Deliver the verdict against PASS_CRITERIA.md (safety: denylist
   recall 1.0, must-block all, 0 never stored, 0 unsafe, FP 0.0;
   value: non-seed safe rate >= 0.10; cost: p95 check <= 50 ms).
