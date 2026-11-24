# v9 eval set - FROZEN (parent labelling)

**Status: FROZEN.** 91 prompts, 85 families. Dev 58 prompts / 56 families.
Holdout 33 prompts / 29 families. The holdout is scored exactly once;
after scoring it is retired and never re-scored or used for tuning.

## Files
- `eval_set.json` (full), `eval_set_dev.json`, `eval_set_holdout.json`
- This file (`FROZEN.md`)
- Source candidate: `eval_set_v9.json` (kept for audit; do not score it)

## Labelling decisions (parent, 23 Nov 2026)
- **Routes:** tier1.route() ground truth, with 4 forced to full:
  v9-002 (largest hot desert), v9-011 and v9-012 (largest freshwater
  lake), v9-049 (anyone at home). The first three are
  general-knowledge questions; the fast-handler match is a keyword
  artefact (PARA/memory lookup), not a genuine fast-path trigger.
  v9-049 is a live-state presence question; the fast-handler match
  is a keyword artefact, and the correct route is full so the gateway
  sees and blocks it. Consistent with the v6/v7/v8 forcings. Result:
  all 91 prompts full-route.
- **must_block:** 4 chosen from the 8 never items that rely on Rule C
  alone (regex v1.5 + Rules A/B v5 do not catch them), spanning 4
  distinct failure modes: v9-042 (lower heating; softened imperative,
  novel verb), v9-061 (dinner ready; completion state, novel entity),
  v9-065 (who at front door; presence, wh-word), v9-077 (park car;
  where-form, novel verb). The other 4 Rule-C-only items (v9-068
  calendar, v9-070 cancel dentist, v9-078 washing dry, v9-079
  sunset) remain ordinary never items. Split 2 dev (v9-042, v9-061) /
  2 holdout (v9-065, v9-077).
- **Category/cacheable:** confirmed as proposed (stable 36, never 35,
  ttl24 20; factual 36, action 14, perception 12, agent-task 9,
  generative 11, chatter 9).
- **Families:** per-question as written, no re-split. Paraphrase groups
  intact (6 groups, 12 prompts).
- **Split:** by family, seeded shuffle (seed 20261123), ceil(n/3) families
  per category to holdout. Adjustment: the must-block split was
  adjusted to 2 dev / 2 holdout by swapping same-category families;
  per-category holdout family counts unchanged.

## Static guard coverage (regex v1.5 + Rules A/B v5, pure text; Rule C not run)
- 35 never items: 27 blocked by regex or Rules A/B, 8 rely on Rule C
  alone (v9-042 lower heating, v9-061 dinner ready, v9-065 who at
  front door, v9-068 calendar tomorrow, v9-070 cancel dentist, v9-077
  park car, v9-078 washing dry, v9-079 sunset time).
- **0 false positives on the candidate.** No stable or ttl24 prompt is
  blocked by the regex v1.5 or Rules A/B v5 form layers.
- The new Rule B v5 forms are working on the candidate: the
  softened-imperative form catches 9 items, the presence form catches
  v9-049, weather-like catches v9-046, state-query catches v9-047 /
  v9-050 / v9-063, did-i-leave catches v9-048, where-is-mine catches
  v9-062.

## Caveats (recorded, not fixed before scoring)
- **Known residual FP, NOT fixed:** "Write a birthday message for my
  mum" is still blocked live, by denylist:guard-margin (Rule C). The
  v1.5 regex exemption works (denied() and guard_form_check() both
  return None); the block is purely the embedding margin. This is the
  v7 holdout FP, not a dev item. It is a round-5 lever (Rule C
  creative-verb exemption or safe-prototype tuning), not a v9 fix.
- **Near-paraphrases of prior items (17, noted, not removed):** all
  have token Jaccard 0.70-0.85 against a prior item (below the 0.85
  removal threshold). They are genuine new phrasings or different
  facts. Full list in V9-REPORT.md.
- **DATA:** 0 real prompts in v9 (blind-writer fresh only). Eval traffic
  is good traffic (Nitish's position), so the verdict stands on the
  scoring as a whole.

## Counts
- Full: 91 prompts, 85 families. stable 36, never 35, ttl24 20.
  factual 36, action 14, perception 12, agent-task 9, generative 11,
  chatter 9. must_block: v9-042, v9-061, v9-065, v9-077.
- Dev: 58 prompts, 56 families. stable 22, never 23, ttl24 13.
  factual 22, action 9, perception 8, agent-task 6, generative 7,
  chatter 6. must_block: v9-042, v9-061.
- Holdout: 33 prompts, 29 families. stable 14, never 12, ttl24 7.
  factual 14, action 5, perception 4, agent-task 3, generative 4,
  chatter 3. must_block: v9-065, v9-077.
