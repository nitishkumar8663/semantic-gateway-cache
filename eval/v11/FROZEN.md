# v11 eval set - FROZEN (parent labelling)

**Status: FROZEN.** 106 prompts, 95 families. Dev 69 prompts / 62 families.
Holdout 37 prompts / 33 families. The holdout is scored exactly once;
after scoring it is retired and never re-scored or used for tuning.

## Files
- `eval_set.json` (full), `eval_set_dev.json`, `eval_set_holdout.json`
- This file (`FROZEN.md`)
- Source candidate: `eval_set_v11.json` (kept for audit; do not score it)

## Labelling decisions (parent, 24 Nov 2026)
- **Routes:** tier1.route() ground truth, with 5 forced to full:
  v11-021 (kangaroo country), v11-027 (plants absorb gas),
  v11t-012 (smallest country), v11t-034 (temperature in study),
  v11t-050 (film on a rainy evening). The first three are
  general-knowledge questions; the fast-handler match is a keyword
  artefact (PARA/memory lookup), not a genuine fast-path trigger.
  v11t-034 is a live-state temperature question; the fast-handler
  match is a keyword artefact, and the correct route is full so the
  gateway sees and blocks it. v11t-050 is a chatter recommendation;
  the fast-handler match is a keyword artefact, and the correct route
  is full so the gateway can cache it for 24h. Consistent with the
  v6/v7/v8/v9/v10 forcings. Result: all 106 prompts full-route.
- **must_block:** there are NO Rule-C-only never items in v11 (all 42
  are form-blocked), so must_block is picked from the hardest
  new-form items, spanning 4 distinct failure modes: v11-063 (car
  charged enough; enough-charge form), v11-068 (check if washing is
  dry; check-if form), v11t-031 (anyone in the garden; presence
  form), v11-065 (did I leave the oven on; did-i-leave/state-query
  form). The other check-if items (v11t-030, v11t-033) remain
  ordinary never items. Split 2 dev (v11-065, v11-068) / 2 holdout
  (v11-063, v11t-031).
- **v11-027 KEPT** ("What gas do plants absorb from the air?"):
  near-paraphrase of v8-002 (Jaccard 0.800, below the 0.85 removal
  threshold), photosynthesis-adjacent. It is a stable factual
  question that tests whether the gateway can serve a stable factual
  answer. It is not a collision, so it stays.
- **Category/cacheable:** confirmed as proposed (stable 44, never 42,
  ttl24 20; factual 44, action 20, perception 11, agent-task 11,
  generative 14, chatter 6).
- **Families:** per-question as written, no re-split. Paraphrase groups
  intact (11 groups, 22 prompts).
- **Split:** by family, seeded shuffle (seed 20261123), ceil(n/3) families
  per category to holdout. Adjustment: the must-block split was
  adjusted to 2 dev / 2 holdout by swapping same-category families;
  per-category holdout family counts unchanged.

## Static guard coverage (regex v1.5 + Rules A/B v7, pure text; Rule C not run)
- 42 never items: 42 blocked by regex or Rules A/B, 0 rely on Rule C
  alone. This is the first round with no Rule-C-only never items: the
  form layers now cover everything the blind writers produced.
- **0 false positives on the candidate.** No stable or ttl24 prompt is
  blocked by the regex v1.5 or Rules A/B v7 form layers.
- The new Rule B v7 forms are working on the candidate: the check-if
  form catches 3 items, the presence form catches v11t-031, the
  state-query form catches 5 items, did-i-leave catches v11-067, the
  softened-imperative form catches 6 items, "lower"/"schedule"/
  "cancel"/"resume"/"brighten"/"pause"/"dim" as Rule A verbs catch
  their items.

## Caveats (recorded, not fixed before scoring)
- **DATA:** 0 real prompts in v11 (blind-writer fresh only, two
  batches). Eval traffic is good traffic (Nitish's position), so the
  verdict stands on the scoring as a whole.
- **Near-paraphrases (30, noted, not removed):** all have token
  Jaccard 0.70-0.85 against a prior item (below the 0.85 removal
  threshold). They are genuine new phrasings or different facts.
  Full list in v11-near-paraphrases.json.
- **Form coverage note:** because all 42 never items are form-blocked,
  the holdout's safety result will test whether the new v2.9 forms
  generalise (the forms were built against v10 dev, not v11), not
  whether Rule C separates hard items. If the holdout escapes in
  classes the forms do not cover, the next lever is either a further
  general Rule B form for those classes, or the fine-tuned embedding
  model.

## Counts
- Full: 106 prompts, 95 families. stable 44, never 42, ttl24 20.
  factual 44, action 20, perception 11, agent-task 11, generative
  14, chatter 6. must_block: v11-063, v11-065, v11-068, v11t-031.
- Dev: 69 prompts, 62 families. stable 29, never 27, ttl24 13.
  factual 29, action 13, perception 7, agent-task 7, generative 9,
  chatter 4. must_block: v11-065, v11-068.
- Holdout: 37 prompts, 33 families. stable 15, never 15, ttl24 7.
  factual 15, action 7, perception 4, agent-task 4, generative 5,
  chatter 2. must_block: v11-063, v11t-031.

## Public split note

This is the public copy of the frozen v11 set. It differs from the private frozen original only by rewordings applied to the public copy: em dashes removed, an unlock example reworded, internal project references removed. No prompt was redacted and no label changed.
The reported scores were measured on the private frozen originals.

Original (private) md5s:

- `eval_set.json`: 1870b7dec97b8adc383901d6cbcf528a
- `eval_set_dev.json`: 68e55eddfd0ac22bd7bd6964c1859029
- `eval_set_holdout.json`: 6a471182881141ce3854fede4c992fe8

Public copy md5s (at the time this note was written; they change if the public copy is re-cleaned):

- `eval_set.json`: 867409e57144a740ff72cc7c39ea83d1
- `eval_set_dev.json`: 10211c346081a43120c0c24b953ebb61
- `eval_set_holdout.json`: c70ca284b6452797c8f38e16cd83eacc
