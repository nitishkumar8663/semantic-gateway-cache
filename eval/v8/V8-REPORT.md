# v8 candidate eval set - report

**Status: CANDIDATE ONLY.** Proposed labels, not finalised, not
frozen, not scored. The parent labels and freezes this set (assigns
the dev/holdout split, confirms cacheable/category/route, sets
must_block) before its single scoring. Do NOT score this candidate.

## What it is

- **File:** `eval_set_v8.json` (this directory; Spark mirror:
  `eval/v8/eval_set_v8.json`)
- **62 prompts, 59 families.** cacheable: stable 14, never 30,
  ttl24 18. Category: factual 14, action 11, perception 8,
  agent-task 11, generative 9, chatter 9.
- **Paraphrase groups:** 3 stable groups with 2 phrasings (6
  prompts): largest-ocean, photosynthesis, ww2-end-year.
  56 singleton families.
- **Proposed must_block: 4 (provisional, see below).**
  `must_block` is False on every item in the candidate; the
  parent sets it at labelling. `split` is null on every item;
  the parent assigns dev/holdout.

## How it was built

1. A blind prompt writer (child agent, blind to the guard code;
   did not read any verdict/report/eval files) wrote 100 fresh
   prompts to `[workspace]/v8-fresh-prompts.json`. Counts as
   written: stable 40, never 40, ttl24 20. Category: factual 40,
   action 17, perception 12, agent-task 11, generative 10,
   chatter 10. 8 paraphrase groups (16 prompts).
2. Collision check (`guard-v8-build/collisions_v8.json`):
   normalised exact match plus token Jaccard >= 0.85, against the
   v3, v4, v5, v6, v7 full sets (dev + holdout) and the 600-request
   simulation workload (`guard-build/simulation_workload.json`).
   The check is a mechanical freshness check: it only reports
   which v8 prompts collide, never the prior prompts' contents.
3. **38 collisions removed.** 33 exact, 5 Jaccard. By source: v7
   16, v5 9, v6 4, v4 4, v3 3, simulation 2. The collisions are
   mostly canonical trivia the writer reproduced independently
   (Everest height, France/Japan capitals, boiling point, Hamlet,
   gold symbol, continents, Mona Lisa, spider legs, longest river,
   hexagon sides, leap-year days, largest desert, freezing point)
   plus ten hard never forms (unlock/lock doors, set timer,
   kettle on, bedroom lamp off, robot vacuum, washing/dishwasher
   finished, car keys, oven on). Full list:
   `guard-v8-build/collisions_v8.json`.
4. 62 prompts remain. No replacements were written (the writer's
   batch is the batch; the parent can top up at labelling if it
   wants a round 90-100).

## Composition note

62 prompts is well below the ~90-100 target, and 14 stable is
well below the ~40 target. The shortfall is the collision rate
(38%, vs 19% for v7): the writer reproduced v7's canonical
trivia almost wholesale. Only 3 paraphrase groups survived
intact (6 prompts), so value measurement on the holdout will be
weaker than v7's: few repeat opportunities, the same
under-measurement caveat as v4 and v7, worse. The never side is
strong: 30 fresh never items across action (11), perception (8)
and agent-task (11), including new forms (thermostat down,
washing-machine start, dishwasher stop, alarm softened, speaker
volume, oven off, lights-still-on-upstairs, kettle boiled,
raining-at-the-moment, anyone-in-kitchen, message-Reema,
text-Ravi-birthday, book-table, order-pizza). The ttl24 side is
18 (9 generative + 9 chatter).

## Proposed must_block (4, PROVISIONAL)

Chosen from the 6 never items the v2.6 form layers (regex v1.5 +
Rule A v3 + Rule B v4) do NOT catch, i.e. the ones that rely on
Rule C alone. The selection used only the form-rule structure
(which layer catches an item); Rule C was never run on the v8
set, and no recall / must-block / value was computed. The
form-rule check was run with the v2.6 guard's rules. The 6
form-rule misses are: v8-023 alarm-softened, v8-028 weather-like
(uncontracted), v8-029 someone-front-door, v8-031 kettle-boiled,
v8-033 anyone-in-kitchen, v8-036 book-taxi-softened. The 4
proposed must_block span 4 failure modes:

| Item | Text | Failure mode |
|---|---|---|
| v8-023 | Can you set an alarm for seven in the morning? | Softened imperative ("can you" + trailing "?"): the v2.5 question guard keeps Rule A off |
| v8-028 | What is the weather like outside right now? | Uncontracted weather-like ("what is", not "what's"): the v2.6 weather-like form matches the contracted form only |
| v8-029 | Is someone at the front door? | Presence-at-door ("someone", not "anyone"): no Rule B presence form |
| v8-031 | Has the kettle boiled? | Completion-state with a novel state word ("boiled", not finished/done/ready/delivered/arrived) |

The other 2 form-rule misses (v8-033 anyone-in-kitchen,
presence-in-room; v8-036 book-taxi-softened, same softened
class as v8-023) remain as ordinary never items: they still must
be blocked for recall, they are just not designated must_block.

## False positives found (v2.6 rules)

None. No cacheable prompt is blocked by the regex v1.5 or
Rules A/B v4 form layers (0 FP on the candidate). The
message-for creative guard was verified on synthetic prompts of
the same class (draft/write a birthday message for ...); the
v7 holdout birthday-message text itself was NOT used as a test
(it is retired).

## Known gaps the candidate exposes (recorded, NOT fixed)

The v2.6 guard is frozen for the v8 scoring. These gaps were
found by the candidate and are round-4 material, not round-3
fixes - changing the guard after seeing the candidate would be
tuning to the test:
- The weather-like form matches "what's" only; "what is the
  weather like" escapes it (v8-028). A round-4 fix would widen
  the form to the uncontracted phrasing as a general class.
- Softened imperatives ("can/could you ... ?") escape Rule A
  via the question guard (v8-023, v8-036). The v2.5 report named
  this as a known residual risk; the candidate confirms it is a
  live class.
- No Rule B presence form ("is someone/anyone at/in ..."):
  v8-029, v8-033 rely on Rule C.
- "Boiled" is not a Rule B state word (v8-031).

## Near-paraphrases of prior items (noted, not removed)

- v8-028 "What is the weather like outside right now?" is a new
  phrasing of the v7 dev weather-now item ("What's the weather
  like outside at the moment?"; uncontracted form). It tests
  whether the guard generalises to the uncontracted phrasing.
- v8-030 (kept, "Has my parcel been delivered?") is a shorter
  phrasing of the v7 dev parcel item ("Has my parcel been
  delivered yet?"). It tests the delivery state form without
  "yet".
- v8-001 (kept, "Which playwright wrote the play Hamlet?") is a
  new phrasing of the v7 hamlet-author group. It tests a fresh
  factual phrasing.
- v8-010 (kept, "What year did humans first land on the Moon?")
  is a new phrasing of the v7 moon-landing-year group.
All are below the Jaccard 0.85 collision threshold and test
generalisation to new phrasings, not exact repeats.

## Real traffic

No new real traffic was available. The audit log and shadow
replays are thin, as expected. This set is blind-writer fresh
prompts, not real traffic. Recorded honestly per the task.
(Nitish's position: eval traffic is good traffic, so fresh eval
prompts count as holdout traffic.)

## What the parent does next

1. Label and freeze: confirm cacheable/category/route per item,
   re-run the form-rule check with the v2.6 guard's rules,
   set `must_block` (accept or change the 4 proposals), assign
   the dev/holdout split (suggested: holdout ~21 prompts with
   the 4 must_block split across dev/holdout; the exact split is
   the parent's call), set `frozen: true` and `status: "frozen"`.
   The parent may top up the set at labelling if it wants a
   round 90-100 (a top-up the parent writes would not be blind;
   note it as such in FROZEN.md if done).
2. Score the holdout exactly once with the v2.6-guard driver run
   (threshold 0.90 / factual 0.85 / generative 0.85, TTL 24h/168h,
   seed store `cache_store_backup_20261123.json`, seed and empty
   modes, temp stores).
3. Deliver the verdict against PASS_CRITERIA.md (safety: denylist
   recall 1.0, must-block all, 0 never stored, 0 unsafe, FP 0.0;
   value: non-seed safe rate >= 0.10; cost: p95 check <= 50 ms).
