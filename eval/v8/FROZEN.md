# v8 eval set - FROZEN (parent labelling)

**Status: FROZEN.** 97 prompts, 89 families. Dev 62 prompts / 57 families.
Holdout 35 prompts / 32 families. The holdout is scored exactly once;
after scoring it is retired and never re-scored or used for tuning.

## Files
- `eval_set.json` (full), `eval_set_dev.json`, `eval_set_holdout.json`
- This file (`FROZEN.md`)
- Source candidate: `eval_set_v8.json` (merged; kept for audit; do not
  score it). Top-up source: `v8-topup-fresh-prompts.json` (40 written).
  Top-up collisions: `collisions_topup.json` (5 removed).

## How the set was built
- Original v8 candidate: blind writer wrote 100 prompts; 38 collisions
  removed (33 exact, 5 Jaccard) against v3/v4/v5/v6/v7 + simulation.
  62 prompts remained (stable 14, never 30, ttl24 18).
- Top-up: a second blind writer (blind to the guard code and to the
  v8 candidate) wrote 40 prompts; 5 collisions removed (4 exact, 1
  Jaccard) against v3/v4/v5/v6/v7 + simulation + the v8 candidate.
  35 prompts merged (stable 17, never 8, ttl24 10).
- The top-up is labelled as such in FROZEN.md because the parent
  commissioned it after seeing the 62-prompt composition. Both writers
  were blind to the guard code; neither saw any verdict, report, eval
  file, or guard code. The collision checks are mechanical freshness
  checks: they report which prompts collide, never the prior prompts'
  contents.

## Labelling decisions (parent, 23 Nov 2026)
- **Routes:** tier1.route() ground truth, with 2 forced to full:
  v8-002, v8-003 (photosynthesis gas). Those two are
  general-knowledge questions; the fast-handler match is a keyword
  artefact (PARA/memory lookup), not a genuine fast-path trigger.
  Consistent with the v6/v7 forcings. Result: all 97 prompts
  full-route.
- **must_block:** the 4 proposed items confirmed: v8-023
  (alarm-softened), v8-028 (weather-like uncontracted), v8-029
  (someone-front-door), v8-031 (kettle-boiled). These are 4 of the 8
  never items that rely on Rule C alone (regex v1.5 + Rules A/B v4 do
  not catch them). The top-up added 2 more Rule-C-only items
  (v8t-022 heating-down, v8t-028 where-phone); they remain ordinary
  never items. Split 2 dev (v8-023, v8-031) / 2 holdout (v8-028,
  v8-029).
- **Category/cacheable:** confirmed as proposed (stable 31, never 38,
  ttl24 28; factual 31, action 16, perception 9, agent-task 13,
  generative 14, chatter 14).
- **Families:** per-question as written, no re-split. Paraphrase groups
  intact (8 groups, 16 prompts).
- **Split:** by family, seeded shuffle (seed 20261123), ceil(n/3) families
  per category to holdout. No adjustment needed: the shuffle naturally
  gave 2 must_block in dev and 2 in holdout.

## Static guard coverage (regex v1.5 + Rules A/B v4, pure text; Rule C not run)
- 38 never items: 30 blocked by regex or Rules A/B, 8 rely on Rule C
  alone (v8-023 alarm-softened, v8-028 weather-like uncontracted,
  v8-029 someone-front-door, v8-031 kettle-boiled, v8-033
  anyone-in-kitchen, v8-036 book-taxi-softened, v8t-022 heating-down,
  v8t-028 where-phone).
- **0 false positives on the candidate.** No stable or ttl24 prompt is
  blocked by the regex v1.5 or Rules A/B v4 form layers.

## Caveats (recorded, not fixed before scoring)
- **Size:** 97 prompts, 31 stable, 8 paraphrase groups. Better than the
  original 62-prompt candidate (14 stable, 3 groups), and value
  measurement on the holdout is now meaningful, though still thinner
  than v3/v6. Not topped up further: the top-up already brought the
  set to ~97 prompts.
- **Near-paraphrases of prior items:** v8-028 "What is the weather like
  outside right now?" is a new phrasing of the v7 dev weather-now item
  (uncontracted form). v8-030 "Has my parcel been delivered?" is a
  shorter phrasing of the v7 dev parcel item (without "yet"). v8-001
  "Which playwright wrote the play Hamlet?" is a new phrasing of the
  v7 hamlet-author group. v8-010 "What year did humans first land on
  the Moon?" is a new phrasing of the v7 moon-landing-year group. All
  are below the Jaccard 0.85 collision threshold and test
  generalisation to new phrasings, not exact repeats.
- **Known gaps the candidate exposes (round-4 material, NOT fixed):**
  the weather-like form matches "what's" only; softened imperatives
  escape Rule A via the question guard; no Rule B presence form;
  "boiled" is not a state word; "where did I put" is not a Rule B
  form. Changing the guard after seeing the candidate would be
  tuning to the test.
- **DATA:** 0 real prompts in v8 (blind-writer fresh only). Eval traffic
  is good traffic (Nitish's position), so the verdict stands on the
  scoring as a whole.

## Counts
- Full: 97 prompts, 89 families. stable 31, never 38, ttl24 28.
  factual 31, action 16, perception 9, agent-task 13, generative 14,
  chatter 14. must_block: v8-023, v8-028, v8-029, v8-031.
- Dev: 62 prompts, 57 families. stable 20, never 24, ttl24 18.
  factual 20, action 10, perception 6, agent-task 8, generative 9,
  chatter 9. must_block: v8-023, v8-031.
- Holdout: 35 prompts, 32 families. stable 11, never 14, ttl24 10.
  factual 11, action 6, perception 3, agent-task 5, generative 5,
  chatter 5. must_block: v8-028, v8-029.
