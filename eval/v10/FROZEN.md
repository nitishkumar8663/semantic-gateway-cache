# v10 eval set - FROZEN (parent labelling)

**Status: FROZEN.** 108 prompts, 101 families. Dev 70 prompts / 66 families.
Holdout 38 prompts / 35 families. The holdout is scored exactly once;
after scoring it is retired and never re-scored or used for tuning.

## Files
- `eval_set.json` (full), `eval_set_dev.json`, `eval_set_holdout.json`
- This file (`FROZEN.md`)
- Source candidate: `eval_set_v10.json` (kept for audit; do not score it)

## Labelling decisions (parent, 24 Nov 2026)
- **Routes:** tier1.route() ground truth. All 108 route full; no
  forcing needed (first round with no fast-route keyword artefacts).
- **must_block:** 4 chosen from the 6 never items that rely on Rule C
  alone (regex v1.5 + Rules A/B v6 do not catch them), spanning 4
  distinct failure modes: v10-061 (sun go down; live fact, "when"
  form), v10-064 (post arrived; completion state, novel entity),
  v10t-032 (check if oven still on; "check if" form), v10t-033
  (phone charging; progressive state form). The other 2 Rule-C-only
  items (v10-067 car charged, v10-075 calendar tomorrow) remain
  ordinary never items. Split 2 dev (v10-061, v10-064) / 2 holdout
  (v10t-032, v10t-033).
- **v10t-044 KEPT** ("Write a birthday message for a friend who loves
  cycling."): near-paraphrase of the v7 holdout FP item v7-068
  (Jaccard 0.727, below the 0.85 removal threshold), different verb
  (write vs draft). It tests whether the Rule C creative-draft
  exemption generalises to a new phrasing of the same class. It sits
  in the holdout.
- **Category/cacheable:** confirmed as proposed (stable 40, never 44,
  ttl24 24; factual 40, action 20, perception 12, agent-task 12,
  generative 13, chatter 11).
- **Families:** per-question as written, no re-split. Paraphrase groups
  intact (7 groups, 14 prompts).
- **Split:** by family, seeded shuffle (seed 20261123), ceil(n/3) families
  per category to holdout. Adjustment: the must-block split was
  adjusted to 2 dev / 2 holdout by swapping same-category families;
  per-category holdout family counts unchanged.

## Static guard coverage (regex v1.5 + Rules A/B v6, pure text; Rule C not run)
- 44 never items: 38 blocked by regex or Rules A/B, 6 rely on Rule C
  alone (v10-061 sun go down, v10-064 post arrived, v10-067 car
  charged, v10-075 calendar tomorrow, v10t-032 check if oven still
  on, v10t-033 phone charging).
- **0 false positives on the candidate.** No stable or ttl24 prompt is
  blocked by the regex v1.5 or Rules A/B v6 form layers.
- The new Rule B v6 forms are working on the candidate: the
  softened-imperative form catches 4 items, state-query catches 6,
  where-is-mine catches v10-065, "lower" as a Rule A verb catches
  v10t-026, "cancel" catches v10-076, "dim" catches v10-050 /
  v10t-021, "pause" catches v10t-028, "text" catches v10-080.

## Caveats (recorded, not fixed before scoring)
- **DATA:** 0 real prompts in v10 (blind-writer fresh only, two
  batches). Eval traffic is good traffic (Nitish's position), so the
  verdict stands on the scoring as a whole.
- **Near-paraphrases (26, noted, not removed):** all have token
  Jaccard 0.70-0.85 against a prior item (below the 0.85 removal
  threshold). They are genuine new phrasings or different facts.
  Full list in v10-near-paraphrases.json. Notable: v10-041 (0.833 vs
  v9-056), v10-046 (0.778 vs v9-042), v10-057 (0.800 vs v9-063),
  v10t-030 (0.833 vs v5-040). These test whether the guard
  generalises rather than memorising exact strings.
- **Live store note:** the v2.8 build's live probes stored the
  birthday-message prompt in the live store (34 entries, was 33).
  The live store is shadow-only and the shadow upstream is a stub,
  so this does not affect serving. The scoring uses the frozen seed
  store, not the live store.

## Counts
- Full: 108 prompts, 101 families. stable 40, never 44, ttl24 24.
  factual 40, action 20, perception 12, agent-task 12, generative
  13, chatter 11. must_block: v10-061, v10-064, v10t-032, v10t-033.
- Dev: 70 prompts, 66 families. stable 26, never 29, ttl24 15.
  factual 26, action 13, perception 8, agent-task 8, generative 8,
  chatter 7. must_block: v10-061, v10-064.
- Holdout: 38 prompts, 35 families. stable 14, never 15, ttl24 9.
  factual 14, action 7, perception 4, agent-task 4, generative 5,
  chatter 4. must_block: v10t-032, v10t-033.
