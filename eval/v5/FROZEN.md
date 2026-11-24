# v5 frozen eval case

**Status: FROZEN 23 Nov 2026. Labels final. NOT scored yet.**
**Gateway under test:** v2.3-guard (guard v1.0, denylist v1.2,
threshold 0.90 / factual 0.85 / generative 0.85, TTL 24h / 168h).

## Counts

- 91 prompts, 66 families.
- Dev: 59 prompts / 41 families. Holdout: 32 prompts / 25 families.
- Cacheable: stable 49, never 34, ttl24 8.
- Holdout by cacheable: stable 15, never 13, ttl24 4.
- Paraphrase groups (2+ phrasings): 15 groups, 40 prompts
  (14 factual groups, 38 prompts; smalltalk, 2 prompts).
  Groups are kept intact in the split (all phrasings of one
  question in the same split), so the holdout tests unseen
  questions, not unseen phrasings of seen questions.
- Real traffic: none new (audit log and shadow replays unchanged
  since v4; v5 is built from the blind writer's fresh set).
  Per Nitish's framing, eval traffic is good traffic; the verdict
  stands on the scoring as a whole.

## Labelling decisions (parent, Muse, 23 Nov 2026)

- **Routes:** all 91 full, confirmed by the live dispatcher's
  `tier1.route()` ground truth (`no-exact-pattern` for every
  prompt). No fast-route items. No corrections to the proposal.
- **Category / cacheable:** as proposed (factual/stable 49,
  never 34, ttl24 8). No changes.
- **must_block:** the 4 proposed, confirmed (v5-042 "Preheat the
  oven to 180 degrees.", v5-052 "Play some jazz in the kitchen.",
  v5-063 "Where is my parcel?", v5-068 "How many steps have I
  done today?"). 2 in holdout (v5-042, v5-052), 2 in dev
  (v5-063, v5-068). No additions.
- **Family convention:** per-question groups as written (the
  writer already used per-question families). No re-split.
- **Ambiguous prompts:** 0 flagged in v5 (unlike v4's 29).

## Static guard coverage (labelling observation, NOT a score)

Measured before freezing with pure-text checks only (tier1.route,
regex denied(), guard Rules A+B via guard_form_check). Rule C
(embeddings) was NOT run on v5 before freezing, so the holdout
stays uncontaminated until its single scoring.

- Regex + Rules A+B block 21 of 34 never items.
- 13 never items rely on Rule C (embedding margin) alone:
  washing-machine, preheat, boil-kettle, tumble-dryer, coffee,
  play-jazz, play-radio, front-camera, doorbell, parcel, milk,
  steps, boost-heating. All 4 must_block items are in this set.
- Rules A+B have 0 false positives on the 57 stable/ttl24 items.
- **Regex false positive (recorded, not hidden):** the denylist
  pattern `\btemperature\b` blocks 4 stable factual questions:
  "At what temperature does water boil?" (v5-004, v5-005) and
  "At what temperature does water freeze?" (v5-038, v5-039).
  These stay labelled stable: they are genuine stable facts, and
  the block is a guard over-match, not a labelling error. The dev
  scoring will measure the FP rate; if it is non-zero, the SAFETY
  FP sub-criterion (0.0) fails on the evidence.

## Split

By family (group), paraphrase groups intact. Seeded shuffle
(seed 20261123) per category, ceil(n/3) families to holdout.

| Category | Families | Holdout families |
|---|---|---|
| factual | 25 | 9 |
| action | 16 | 6 |
| perception | 10 | 4 |
| agent-task | 8 | 3 |
| generative | 6 | 2 |
| chatter | 1 | 1 |

Holdout groups: factual - author-romeo-juliet, chemical-symbol-gold,
currency-japan, formula-water, language-brazil, largest-continent,
largest-ocean, planet-closest-sun, sides-hexagon; action -
appliances-oven, appliances-vacuum, garden-hose, garden-watering,
media-pause-music, media-play-music; perception -
appliances-fridge, appliances-washing-machine, security-doorbell,
weather-coat-today; agent-task - lists-add-eggs,
shopping-order-groceries, shopping-order-takeaway; generative -
generative-story-cat, generative-story-robot; chatter - smalltalk.

Note: chatter has a single family (smalltalk, 2 prompts), so it
goes to the holdout whole; dev still holds 4 generative ttl24
families, so both splits hold ttl24 items.

## Pass criteria

The AGREED criteria (see [workspace]/v3/v3/PASS_CRITERIA.md),
unchanged for v5. SAFETY needs denylist recall 1.0, must-block
all, 0 never stored, 0 unsafe, FP 0.0. VALUE needs non-seed safe
rate >= 0.10. COST p95 check <= 50 ms. DATA is the set size and
real share, reported factually.

## Scoring rules

- Score dev first for sanity (detail allowed).
- Score the holdout EXACTLY ONCE, summary only. The holdout
  scoring is the single allowed one.
- Do NOT use v5 failures to tune the guard. A failure on v5
  needs a v6 (new guard + new fresh holdout).
- The v4 holdout stays retired (scored once). The v3 holdout
  stays retired (scored twice).

## Files

- eval_set.json (all 91, frozen), eval_set_dev.json (59),
  eval_set_holdout.json (32), FROZEN.md (this file).
- Candidate: eval_set_v5.json (pre-freeze, labels proposed).
  Source: v5-fresh-prompts.json (blind writer, 100 prompts,
  9 collisions removed).
- VM: [workspace]/v5/. Spark:
  [spark-home]/team/gateway-shadow-trial/eval/v5/.
  md5-verified identical (see below).
