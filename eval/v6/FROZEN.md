# v6 eval set - FROZEN (parent labelling)

**Status: FROZEN.** 89 prompts, 77 families. Dev 56 prompts / 49 families.
Holdout 33 prompts / 28 families. The holdout is scored exactly once;
after scoring it is retired and never re-scored or used for tuning.

## Files
- `eval_set.json` (full), `eval_set_dev.json`, `eval_set_holdout.json`
- This file (`FROZEN.md`)
- Source candidate: `eval_set_v6.json` (kept for audit; do not score it)

## Labelling decisions (parent, 23 Nov 2026)
- **Routes:** tier1.route() ground truth, with 3 forced to full:
  v6-002, v6-003 (plants absorb gas), v6-006 (largest ocean). Those three
  are general-knowledge questions; the fast-handler match is a keyword
  artefact (PARA/memory lookup), not a genuine fast-path trigger.
  Consistent with the v4-047 forcing. Result: all 89 prompts full-route.
- **must_block:** the 4 proposed items confirmed: v6-053 (mow the lawn),
  v6-061 (who is at the front door), v6-062 (did someone ring the
  doorbell), v6-079 (where are my car keys). These are 4 of the 8 never
  items that rely on Rule C alone (regex + Rules A/B do not catch them).
  Split 2 dev (v6-053, v6-079) / 2 holdout (v6-061, v6-062).
- **Category/cacheable:** confirmed as proposed (stable 43, never 36,
  ttl24 10; factual 43, action 18, perception 11, agent-task 7,
  generative 7, chatter 3).
- **Families:** per-question as written, no re-split. Paraphrase groups
  intact (10 stable groups, 22 prompts).
- **Split:** by family, seeded shuffle (seed 20261123), ceil(n/3) families
  per category to holdout. No adjustment needed: the shuffle naturally
  gave 2 must_block in dev and 2 in holdout.

## Static guard coverage (regex v1.3 + Rules A/B, pure text; Rule C not run)
- 36 never items: 28 blocked by regex or Rules A/B, 8 rely on Rule C
  alone (v6-046 dishwasher, v6-053 mow, v6-061 door-who, v6-062
  doorbell, v6-063 alarm-armed, v6-070 sleep, v6-078 raining,
  v6-079 car-keys).
- **3 false positives found on v6 (guard would block cacheable prompts):**
  - v6-015 "Count the continents for me, how many are there?" - Rule A
    matches leading verb "count", but this is a factual question (7
    continents). In HOLDOUT (continents-count family).
  - v6-019 "Water boils at what temperature at sea level?" - Rule A
    matches leading word "water" (verb form), but here "water" is a
    noun. In DEV (water-boiling-point family).
  - v6-083 "Write a short story about a lighthouse keeper who finds a
    message in a bottle." - regex `\bmessage\b` matches "message" in a
    creative-writing prompt. In DEV (story-lighthouse-bottle family).
  These are real guard weaknesses (Rule A matches the first word
  regardless of part of speech; the message regex is too broad). They
  were latent in v2.3 and are exposed by v6. The guard is NOT patched
  before scoring; the verdict measures them honestly. If the holdout FP
  (v6-015) makes FP > 0, that is a SAFETY FAIL and the next round fixes
  the FP.

## Caveats (recorded, not fixed before scoring)
- **Preheat/play verbs:** Rule A v2 includes "preheat" and "play", which
  coincide with the v5 holdout must-block verbs. The v6 must_block items
  do not involve those verbs, so the must_block test is clean. The v6
  preheat item (v6-047, "Preheat the oven to one hundred and eighty
  degrees") is a new phrasing of the v5 holdout preheat item (digits
  spelled out); the v6 play item (v6-059, "Play the radio station I was
  listening to yesterday") is a new phrasing of the v5 dev play item.
  Both test whether the verb class generalises to new phrasings.
- **Near-paraphrases of v5 items:** v6-066 "Where is my parcel? Has it
  arrived yet?" is a near-paraphrase of the v5 dev parcel item (extra
  clause). v6-047 (above) is a near-paraphrase of the v5 holdout preheat
  item. Both are below the Jaccard 0.85 collision threshold and test
  generalisation to new phrasings, not exact repeats.
- **DATA:** 0 real prompts in v6 (blind-writer fresh only). Eval traffic
  is good traffic (Nitish's position), so the verdict stands on the
  scoring as a whole.

## Counts
- Full: 89 prompts, 77 families. stable 43, never 36, ttl24 10.
  factual 43, action 18, perception 11, agent-task 7, chatter 3,
  generative 7. must_block: v6-053, v6-061, v6-062, v6-079.
- Dev: 56 prompts, 49 families. stable 27, never 23, ttl24 6.
  factual 27, action 12, perception 7, agent-task 4, chatter 2,
  generative 4. must_block: v6-053, v6-079.
- Holdout: 33 prompts, 28 families. stable 16, never 13, ttl24 4.
  factual 16, action 6, perception 4, agent-task 3, chatter 1,
  generative 3. must_block: v6-061, v6-062.
