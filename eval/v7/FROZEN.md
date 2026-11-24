# v7 eval set - FROZEN (parent labelling)

**Status: FROZEN.** 81 prompts, 76 families. Dev 51 prompts / 48 families.
Holdout 30 prompts / 28 families. The holdout is scored exactly once;
after scoring it is retired and never re-scored or used for tuning.

## Files
- `eval_set.json` (full), `eval_set_dev.json`, `eval_set_holdout.json`
- This file (`FROZEN.md`)
- Source candidate: `eval_set_v7.json` (kept for audit; do not score it)

## Labelling decisions (parent, 23 Nov 2026)
- **Routes:** tier1.route() ground truth, with 2 forced to full:
  v7-012 (photosynthesis gas), v7-021 (kangaroo country). Those two
  are general-knowledge questions; the fast-handler match is a keyword
  artefact (PARA/memory lookup), not a genuine fast-path trigger.
  Consistent with the v6 and v4-047 forcings. Result: all 81 prompts
  full-route.
- **must_block:** the 4 proposed items confirmed: v7-031 (heating-up),
  v7-046 (washing-finished), v7-049 (doorbell-who), v7-053
  (parcel-delivered). These are 4 of the 8 never items that rely on
  Rule C alone (regex v1.4 + Rules A/B v3 do not catch them; the set
  is unchanged from the v2.4 form-rule check). Split 2 dev (v7-046,
  v7-053) / 2 holdout (v7-031, v7-049).
- **Category/cacheable:** confirmed as proposed (stable 28, never 33,
  ttl24 20; factual 28, action 17, perception 8, agent-task 8,
  generative 10, chatter 10).
- **Families:** per-question as written, no re-split. Paraphrase groups
  intact (5 stable groups, 10 prompts).
- **Split:** by family, seeded shuffle (seed 20261123), ceil(n/3) families
  per category to holdout. No adjustment needed: the shuffle naturally
  gave 2 must_block in dev and 2 in holdout.

## Static guard coverage (regex v1.4 + Rules A/B v3, pure text; Rule C not run)
- 33 never items: 25 blocked by regex or Rules A/B, 8 rely on Rule C
  alone (v7-031 heating-up, v7-032 thermostat-18, v7-046
  washing-finished, v7-048 weather-now, v7-049 doorbell-who, v7-050
  anyone-front-door, v7-052 house-temperature-now, v7-053
  parcel-delivered).
- **1 false positive found on v7 (guard would block a cacheable prompt):**
  - v7-068 "Draft a birthday message for my friend who loves cycling."
    - regex `\bmessage\b[^,;]{0,12}\b(to|for)\b` matches "message for"
    in a creative-writing prompt. The v2.5 denylist narrowing did NOT
    remove this FP (the report's claim was wrong; verified with the
    v2.5 rules at labelling). In HOLDOUT (birthday-message-cyclist
    family). The guard is NOT patched before scoring; the verdict
    measures it honestly. If the holdout FP makes FP > 0, that is a
    SAFETY FAIL and the next round fixes the FP.
- No form-rule FPs (Rules A/B v3 block no stable or ttl24 prompt).

## Caveats (recorded, not fixed before scoring)
- **Size:** 81 prompts is below the ~90-100 target; 28 stable is below
  the ~40 target; only 5 paraphrase groups survived. Value measurement
  on the holdout will be weaker (few repeat opportunities, the same
  under-measurement caveat as v4). Not topped up: the parent writing
  prompts would not be blind (it knows the guard code), which would
  bias the set.
- **Near-paraphrases of prior items:** v7-049 "Who just rang the
  doorbell?" is a new phrasing of the v6 holdout doorbell item
  (different tense and structure; Jaccard 0.375). v7-053 "Has my parcel
  been delivered yet?" is a new phrasing of the v5 dev parcel item and
  the v6 parcel item. v7-031 "Can you turn the heating up a bit?" is a
  new phrasing of the v6 heating item (softened form). All are below
  the Jaccard 0.85 collision threshold and test generalisation to new
  phrasings, not exact repeats.
- **DATA:** 0 real prompts in v7 (blind-writer fresh only). Eval traffic
  is good traffic (Nitish's position), so the verdict stands on the
  scoring as a whole.

## Counts
- Full: 81 prompts, 76 families. stable 28, never 33, ttl24 20.
  factual 28, action 17, perception 8, agent-task 8, generative 10,
  chatter 10. must_block: v7-031, v7-046, v7-049, v7-053.
- Dev: 51 prompts, 48 families. stable 18, never 21, ttl24 12.
  factual 18, action 11, perception 5, agent-task 5, generative 6,
  chatter 6. must_block: v7-046, v7-053.
- Holdout: 30 prompts, 28 families. stable 10, never 12, ttl24 8.
  factual 10, action 6, perception 3, agent-task 3, generative 4,
  chatter 4. must_block: v7-031, v7-049.
