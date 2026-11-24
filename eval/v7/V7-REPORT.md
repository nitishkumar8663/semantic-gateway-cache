# v7 candidate eval set - report

**Status: CANDIDATE ONLY.** Proposed labels, not finalised, not
frozen, not scored. The parent labels and freezes this set (assigns
the dev/holdout split, confirms cacheable/category/route, sets
must_block) before its single scoring. Do NOT score this candidate.

## What it is

- **File:** `eval_set_v7.json` (this directory; Spark mirror:
  `eval/v7/eval_set_v7.json`, md5 `dbb5af65490351707aaaa0ace46526bf`,
  verified VM vs Spark)
- **81 prompts, 76 families.** cacheable: stable 28, never 33,
  ttl24 20. Category: factual 28, action 17, perception 8,
  agent-task 8, generative 10, chatter 10.
- **Paraphrase groups:** 5 stable groups with 2+ phrasings (10
  prompts); 71 singleton families. The 5 intact groups are
  Everest height, Hamlet author, largest planet, Moon landing
  year, photosynthesis gas.
- **Proposed must_block: 4 (provisional, see below).**
  `must_block` is False on every item in the candidate; the
  parent sets it at labelling. `split` is null on every item;
  the parent assigns dev/holdout.

## How it was built

1. A blind prompt writer (child agent, blind to the guard code;
   did not read any verdict/report/eval files) wrote 100 fresh
   prompts to `[workspace]/v7-fresh-prompts.json`. Counts as
   written: stable 40, never 40, ttl24 20. Category: factual 40,
   action 20, perception 12, agent-task 8, generative 10,
   chatter 10. 10 paraphrase groups (20 prompts).
2. Collision check (`guard-v7-build/collision_check_v7.py`):
   normalised exact match plus token Jaccard >= 0.85, against the
   v3, v4, v5, v6 full sets (dev + holdout) and the 600-request
   simulation workload (`guard-build/simulation_workload.json`).
   The check is a mechanical freshness check: it only reports
   which v7 prompts collide, never the prior prompts' contents.
3. **19 collisions removed.** 18 exact, 1 Jaccard (leap-year
   days, j=0.889). By source: v5 8, v6 6, v3 3, v4 1,
   simulation 1. The collisions are mostly canonical trivia the
   writer reproduced independently (capital of France/Japan,
   boiling point, speed of light, gold symbol, longest river,
   hexagon sides, Mona Lisa, continents, liquid metal, spider
   legs, leap-year days) plus seven hard never forms (washing
   machine quick wash, lock front door, preheat oven 180, raining
   now, what time is it, car keys, oven still on). Full list:
   `guard-v7-build/collisions_v7.json`.
4. 81 prompts remain. No replacements were written (the writer's
   batch is the batch; the parent can top up at labelling if it
   wants a round 90-100).

## Composition note

81 prompts is below the ~90-100 target, and 28 stable is below
the ~40 target. The shortfall is the collision rate on canonical
trivia (the writer reproduced prior general-knowledge questions).
Only 5 paraphrase groups survived intact (10 prompts), so value
measurement on the holdout will be weaker than v6's: few repeat
opportunities, the same under-measurement caveat as v4. The never
side is strong: 33 fresh never items across action (17),
perception (8) and agent-task (8), including new forms (heating
up, thermostat, washing finished, weather now, doorbell who,
front door presence, house temperature, parcel delivered). The
ttl24 side is 20 (10 chatter + 10 generative), above the ~10
target.

## Proposed must_block (4, PROVISIONAL)

Chosen from the 8 never items the v2.4 form layers (regex v1.3 +
Rule A v2 + Rule B v2) do NOT catch, i.e. the ones that rely on
Rule C alone. The selection used only the form-rule structure
(which layer catches an item); Rule C was never run on the v7
set, and no recall / must-block / value was computed. The
form-rule check was run with the v2.4 rules (the live guard at
the time of writing); **the parent re-runs it with the v2.5
guard's rules at labelling, and the proposal may change.**
The 8 form-rule misses are: v7-031 heating-up, v7-032
thermostat-18, v7-046 washing-finished, v7-048 weather-now,
v7-049 doorbell-who, v7-050 anyone-front-door, v7-052
house-temperature-now, v7-053 parcel-delivered. The 4 proposed
must_block span 4 failure modes:

| Item | Text | Failure mode |
|---|---|---|
| v7-031 | Can you turn the heating up a bit? | Heating imperative, softened form ("can you", "a bit") |
| v7-046 | Is the washing finished yet? | State check, "finished" on a generic noun |
| v7-049 | Who just rang the doorbell? | Live event, doorbell, past tense |
| v7-053 | Has my parcel been delivered yet? | Delivery state, perfect tense |

The other 4 form-rule misses (thermostat-18, weather-now,
anyone-front-door, house-temperature-now) remain as ordinary
never items: they still must be blocked for recall, they are
just not designated must_block.

## False positive found (v2.4 rules)

One cacheable prompt is blocked by the v2.4 form layers:
v7-068 "Draft a birthday message for my friend who loves
cycling." (regex `\bmessage\b` matches "message" in a creative
prompt). This is the same message-regex FP class as v6; the
v2.5 guard's regex narrowing is supposed to remove it. The
parent verifies at labelling with the v2.5 rules.

## Near-paraphrases of prior items (noted, not removed)

- v7-049 "Who just rang the doorbell?" is a new phrasing of the
  v6 holdout doorbell item ("Did someone just ring the
  doorbell?"; Jaccard 0.375, below the 0.85 threshold). It tests
  whether the guard generalises to a doorbell form in a
  different tense and structure.
- v7-053 "Has my parcel been delivered yet?" is a new phrasing
  of the v5 dev parcel item and the v6 parcel item (different
  tense and structure). It tests generalisation to a delivery
  state question.
- v7-031 "Can you turn the heating up a bit?" is a new phrasing
  of the v6 heating item (softened form, no degree specified).
Both are below the Jaccard 0.85 collision threshold and test
generalisation to new phrasings, not exact repeats.

## Real traffic

No new real traffic was available. The audit log and shadow
replays are thin, as expected. This set is blind-writer fresh
prompts, not real traffic. Recorded honestly per the task.
(Nitish's position: eval traffic is good traffic, so fresh eval
prompts count as holdout traffic.)

## What the parent does next

1. Label and freeze: confirm cacheable/category/route per item,
   re-run the form-rule check with the v2.5 guard's rules,
   set `must_block` (accept or change the 4 proposals), assign
   the dev/holdout split (suggested: holdout ~27 prompts with
   the 4 must_block split across dev/holdout; the exact split is
   the parent's call), set `frozen: true` and `status: "frozen"`.
2. Score the holdout exactly once with the v2.5-guard driver run
   (threshold 0.90 / factual 0.85 / generative 0.85, TTL 24h/168h,
   seed store `cache_store_backup_20261123.json`, seed and empty
   modes, temp stores).
3. Deliver the verdict against PASS_CRITERIA.md (safety: denylist
   recall 1.0, must-block all, 0 never stored, 0 unsafe, FP 0.0;
   value: non-seed safe rate >= 0.10; cost: p95 check <= 50 ms).
