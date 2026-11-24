# Eval set v4 - semantic gateway

**Date:** 23 Nov 2026 (evening). **Order:** Nitish, 23 Nov 2026 -
"Need a full go, so need more changes" (data half), plus his update
the same evening approving generated fresh prompts for the v4 holdout.
**Author:** subagent (workstream 2). **Status: CANDIDATE, NOT frozen,
NOT labelled.** Supersedes `V4-CANDIDATE-REPORT.md` (real-traffic-only
candidate, 24 prompts / 13 families), which stays on file as the
record of the real-traffic half.

## Verdict: BIG ENOUGH

- **105 prompts, 34 families.** A 1/3 holdout split gives **~11
  holdout families**, inside the 10–15 target.
- Under the v3-consistent bus reading (bus bodies = one BUS family,
  already in v3 dev) the set is 28 families and the holdout would be
  ~9 families, just under target; the parent decides the bus-family
  question at labelling.
- Fresh prompts alone (21 families) would give only ~7 holdout
  families, so the real-traffic and demo families in the set matter
  to the count.
- **Framing (Nitish, 23 Nov 2026): eval traffic is good traffic.** The
  real vs synthetic split below is factual reporting. The v4 verdict
  stands on the v4 scoring as a whole and is NOT discounted for the
  synthetic share. A full GO from the v4 scoring is a full GO.

## Real vs synthetic split (factual)

| Origin | Prompts | Families |
|---|---|---|
| Real (bus envelopes, Muse↔Vidyut) | 16 | 6 (task-literal; 0 v3-consistent) |
| Synthetic / eval-derived | 89 | 28 |
| - of which fresh eval prompts | 81 | 21 |
| - of which demo / test fixtures | 8 | 7 |
| **Total** | **105** | **34** |

Real share: 15% of prompts, 18% of families (task-literal).

## Counts

### Families by category (proposed; writer's categories kept verbatim)

| Category | Families | Prompts |
|---|---|---|
| factual | 12 | 30 |
| agent-task | 10 | 32 |
| action | 6 | 19 |
| perception | 3 | 12 |
| time | 2 | 8 |
| chatter | 1 | 4 |

Note: the fresh writer's category `time` is kept as written;
v3-equivalent is `time-state`. No generative family survived: the
fresh file has none, and the real-traffic half has none outside v3.

### Families by proposed cacheable label

| Proposed cacheable | Families | Prompts |
|---|---|---|
| stable | 18 | 46 |
| never | 14 | 51 |
| ttl24 | 2 | 8 |

## The 34 families (proposed labels only - the parent labels v4)

### Fresh eval prompts (81 prompts, 21 families)

Source: `v4-fresh-prompts.json`, 92 prompts / 23 writer families,
written blind to the gateway code by a separate agent, 23 Nov 2026.
Proposed route/cacheable follow v3 precedent per family (see
`build_eval_set_v4.py` for the per-family reasoning).

| Family | Cat. | Proposed route / cacheable | Prompts |
|---|---|---|---|
| V4-F-capitals | factual | full / stable | 3 (Norway×2, Canada; Japan excluded, sim) |
| V4-F-planets-space | factual | full / stable | 4 |
| V4-F-cooking-howto | factual | full / stable | 4 |
| V4-F-translations | factual | full / stable | 4 |
| V4-F-authors-books | factual | full / stable | 4 |
| V4-F-science-why | factual | full / stable | 4 |
| V4-F-smalltalk | chatter | fast / ttl24 | 4 |
| V4-F-lights-on | action | full / never | 4 (must_block: parent decides) |
| V4-F-lights-off | action | full / never | 4 (must_block: parent decides) |
| V4-F-door-lock | action | fast / never | 3 (back-door prompt excluded, sim) |
| V4-F-door-unlock | action | full / never | 3 (back-door prompt excluded, sim) |
| V4-F-heating | action | full / never | 4 |
| V4-F-time-now | time | fast / never | 4 |
| V4-F-weather | time | full / never | 4 |
| V4-F-lights-state | perception | fast / never | 4 |
| V4-F-door-state | perception | fast / never | 4 |
| V4-F-appliance-state | perception | fast / never | 4 |
| V4-F-reminders | agent-task | fast / never | 4 |
| V4-F-timers-alarms | agent-task | fast / never | 4 |
| V4-F-memory-lookup | agent-task | fast / ttl24 | 4 |
| V4-F-lists | agent-task | full / never | 4 (mixed family, parent may split) |

### Real traffic: bus task threads (16 prompts, 6 proposed families)

Proposed label for all six: **agent-task / full / stable**,
must_block false (v3 BUS precedent). See the candidate report for
the thread detail. Family definition is AMBIGUOUS (one BUS family
vs six task families); the parent decides.

| Family | Thread | Prompts |
|---|---|---|
| V4-B2 | Stage 1 step 4 + qwen3.8 reload + plugin investigation | 3 |
| V4-B3 | before_dispatch plugin build/install/test | 5 |
| V4-B4 | Bad-cop review: Workplace post draft | 1 |
| V4-B5 | Portfolio review after the 5 Nov sell-off | 2 |
| V4-B6 | Bad-cop review: Gate 5 Medium draft | 3 |
| V4-B7 | Self-improvement nightly reports (7 + 12 Nov) | 2 |

### Eval-derived: demo / test fixtures (8 prompts, 7 would-be families)

Kept from the real-traffic half, flagged `fresh=false`. They are the
only non-v3 texts found in the gateway's own logs, and the only
near-miss coverage in v4 (Spain capital, fry-egg, cellular
respiration). The parent may drop them at labelling.

| Family | Text(s) | Proposed label |
|---|---|---|
| V4-D0 | How do I reset my Wi-Fi router? / How can I restart my Wi-Fi router? | factual / full / stable |
| V4-D1 | What is the capital of Spain? | factual / full / stable |
| V4-D2 | How do I reset my Wi-Fi password? | factual / full / stable |
| V4-D3 | What is the best way to fry an egg? | factual / full / stable |
| V4-D4 | Explain cellular respiration in one sentence. | factual / full / stable |
| V4-D5 | What is 17 multiplied by 6? | factual / full / stable |
| V4-D6 | unlock a door if it is raining | action / full / never |

## Exclusions from the fresh file (11 prompts)

| Text | Family | Reason |
|---|---|---|
| what is the capital of Japan? | capitals | Simulation text (sim NOVEL group) |
| lock the back door | door-lock | Simulation text (sim NOVEL group) |
| unlock a back door | door-unlock | Simulation text (sim NOVEL group) |
| morning, good evening, hey there, hiya | greetings (whole family) | Same task as v3 R-GR (greeting family, forced to dev). 'hey there' is also a sim GR1 collision. |
| tell me something funny, got a joke for me?, make me laugh, cheer me up with a joke | jokes (whole family) | Same task as v3 R-C1 (joke family). 'make me laugh' is verbatim in v3 R-C1 and a sim C1 collision. |

The 600-request simulation set was NOT reused as eval data in any
form; it was used only for this contamination check (600 requests,
123 unique normalised texts; its non-NOVEL groups mirror v3 families
and are covered by the v3-family analysis). Nothing was invented by
this build: the only generated prompts in v4 are the separate
agent's fresh file, approved by Nitish.

## Ambiguous families (10 - flagged, not guessed)

- **V4-B2..V4-B7 (bus threads):** one BUS family vs six task families;
  plus the v3 BUS label tension (stable although 0 hits expected).
- **V4-F-lights-on, V4-F-lights-off:** must_block needs the parent's
  call (same task frame as v3 must-block R-A3 / NM-A probe).
- **V4-F-lists:** mixed mutation/query family; worst-case label
  full/never proposed; parent may split.
- **V4-D6 (conditional unlock):** single test-fixture case; whether a
  conditional action belongs with the never families is for the parent.

## Family-convention note (parent may re-split before freezing)

v3 families are per-question (one question, paraphrases together).
The fresh writer's families are per-topic (e.g. 'capitals' holds
Norway/Canada, 'heating' holds up/down/thermostat, 'lights-on'
holds four rooms). This build preserves the writer's families as
the units, as briefed (20-25 families). Consequence: within-topic
families hold different-answer prompts, so a within-family
cross-match (e.g. a cached Norway-capital answer served to a
Canada-capital query) would count safe under the v3 scorer's
unsafe definition, which judges cacheable/TTL/denylist, not answer
correctness. A dev/holdout split by topic-family is a stronger
generalisation test than a per-question split; the parent decides
whether to keep topic families or re-split per question.

## Method notes

- **Real-traffic half:** audit log unchanged since v3 (569 rows, mtime
  22 Nov 17:40 UTC); shadow 23 Nov is a replay of the same rows;
  cache_hits/store yielded only demo fixtures; bus envelopes yielded
  the 16 unused bodies. Full inventory in `V4-CANDIDATE-REPORT.md`.
- **Timestamps:** real-traffic prompts keep real timestamps (bus
  sent_utc, demo created_at 22 Nov 05:28 UTC, fastpath file mtime
  4 Nov, day-granular). Fresh prompts use the v3 two-wave scheme
  anchored 23 Nov 2026 00:00 UTC: wave 1 (34 prompts) spread over
  day 0, wave 2 (71 prompts) spread over days 3–6 (26–29 Nov), so
  the 7-day stable TTL is exercised and ttl24 entries go stale
  between waves. Overall ts range 4 Nov → 29 Nov 2026.
- **Screening:** bus bodies contain internal Spark file paths and
  portfolio figures; no credential values. Keep this file on the
  Spark eval dir + VM workspace only; never public without review.
- **Verification:** after merging, the file was re-checked from disk:
  0 fresh prompts collide with v3 or the simulation set by
  normalised text; 81 fresh prompts / 21 families kept.

## Hard-rule compliance

- Labels are PROPOSED only; the parent agent labels v4 and splits
  dev/holdout. Nothing is frozen.
- No scoring was done (neither v4 nor dev). The retired v3 holdout
  was NOT re-scored. v3 holdout scores/failures were not used.
- No live routing changes, no dispatcher changes, no code changes.
  Shadow only.
- v4 gets exactly one scoring, after the parent has labelled and
  frozen it.

## Files

Spark (`[spark-home]/team/gateway-shadow-trial/eval/v4/`):

- `eval_set_v4.json` - the v4 set (105 prompts, 34 families,
  proposed labels + reasoning + source per prompt)
- `eval_set_v4_candidate.json` - the real-traffic-only candidate
  (24 prompts, 13 families) it was built from
- `build_eval_set_v4.py` - the merge builder (reproducible from
  `inputs/`); `build_eval_set_v4_candidate.py` - the real-traffic
  builder
- `V4-REPORT.md` - this report; `V4-CANDIDATE-REPORT.md` - the
  real-traffic-half report
- `audit_snapshot_2026-11-23.jsonl` - audit baseline snapshot

VM mirror (`[workspace]/v4/`): same files, md5-verified identical,
plus `inputs/` (source extracts: audit snapshot, shadow JSON,
cache_hits log, cache_store + backup, demo prompts, fastpath
dry-run, bus tarball, v4-fresh-prompts.json, simulation workload
for the contamination check only, v2 set, v3 build script).

## Neatness (kept vs deleted)

- Kept (Spark eval/v4 + VM [workspace]/v4): v4 JSON, candidate JSON,
  both builders, both reports, audit snapshot, and (VM only) inputs/.
- Deleted: /tmp scratch copies (audit, shadow, cache_hits, store,
  bus tarball + extracted bus dir, v2/v3 read copies) after the
  Spark copy was md5-verified. Nothing was created on the Spark
  outside eval/v4.
