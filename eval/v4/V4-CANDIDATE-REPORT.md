# Holdout v4 CANDIDATE set - semantic gateway

**Date:** 23 Nov 2026 (evening). **Order:** Nitish, 23 Nov 2026 -
"Need a full go, so need more changes" (data half). **Author:** subagent
(workstream 2). **Status: CANDIDATE, NOT frozen, NOT labelled.**

## Verdict: NOT BIG ENOUGH - do not score a holdout from this set

- **Fresh real families: 0** under the v3-consistent reading (every bus
  body is the BUS family, already in v3 dev), **6** under the generous
  per-task reading (16 unused bus envelopes in 6 task threads).
- A 1/3 holdout split of 6 families gives **2 holdout families**, far
  below the 10–15 target in ENH-REPORT.md Section 8.
- The reason is not a thin build: every available traffic source was
  inventoried. The audit log has not grown since the v3 build (still
  569 rows, mtime 22 Nov 17:40 UTC), the only shadow file is a replay
  of those same 569 rows, and everything else not already in v3 is a
  demo fixture or a test fixture, not real traffic.
- **No invented prompts were added.** Only real traffic counts as fresh,
  and there is almost none that is new.

## Counts

| Item | Value |
|---|---|
| Prompts in the candidate file | 24 |
| Families in the candidate file | 13 |
| Real-sourced prompts / families (task-literal) | 16 / 6 |
| Real-sourced families (v3-consistent) | 0 |
| Eval-derived prompts / families (NOT fresh) | 8 / 7 |
| Families available for a holdout split (~1/3) | 0 (v3-consistent) or 2 (generous) |
| Target holdout families | 10–15 |

### Families by category (proposed)

| Category | Families | Prompts |
|---|---|---|
| agent-task | 6 | 16 |
| factual | 6 | 7 |
| action | 1 | 1 |
| generative / chatter / para / time-state / perception / greeting | 0 | 0 |

### Families by proposed cacheable label

| Proposed cacheable | Families | Prompts |
|---|---|---|
| stable | 12 | 23 |
| never | 1 | 1 |
| ttl24 | 0 | 0 |

No ttl24 family survived: the only ttl24-flavoured traffic (greetings,
jokes, PARA/time questions) is entirely inside v3 already.

## What was examined (all sources, all on the Spark)

| Source | Size | Survivors after v3 exclusion | Verdict |
|---|---|---|---|
| Dispatcher audit log `services/tier1-dispatcher/audit.jsonl` | 569 rows, 58 unique texts, mtime 22 Nov 17:40 UTC | 2 texts: `''` (14 rows) and `'/new'` (1 row) | Both unusable. 56/58 unique texts already in v3. Log unchanged since v3 was built. |
| Shadow `eval/v3/shadow/shadow_2026-11-23.json` | 555 requests, replay of the same 569 audit rows | 0 (`'/new'` only) | Newly stored 13 prompts all in v3 except `'/new'`. Paraphrase hits (8) all v3 texts. No new day yet: next replay 24 Nov 06:00 UTC. |
| Gateway log `cache_hits.log.jsonl` | 1692 rows, 77 unique texts, 22–23 Nov | 13 texts | All demo fixtures or eval-replay artefacts (see below). |
| Store `cache_store.json` (29 entries) + backup (16 entries) | 29 entries | 8 prompts | All demo fixtures (subset of the 13 above). The 16 backup entries are the demo seed store, created 22 Nov 05:28 UTC. |
| demo set `demo/prompts.json` | 20 prompts | 11 texts not in v3 | Demo fixtures, not real traffic. |
| Bus envelopes `team/bus/` | 22 envelopes, 5–12 Nov | 16 envelopes (6 task threads) | Real Muse↔Vidyut agent-task texts. Same population as v3 family BUS. Family question is ambiguous (see below). |
| Fastpath dry-run `scripts/fastpath/fastpath-audit-dryrun.jsonl` | 2 rows, 4 Nov | 1 text: `unlock a door if it is raining` | Test fixture (ambiguity-guard), not real traffic. |
| Memory service request log | - | - | None exists (per the v2 builder). No other dispatcher prompt log exists on the Spark. |

Union of distinct prompt texts examined across audit + cache_hits: 79.
Live-mode distinct texts in the audit: 24, all in v3. HTTP-channel
distinct texts: 15, all in v3.

## The 13 families (proposed labels only - the parent labels v4)

### Real-sourced: bus task threads (16 prompts, 6 proposed families)

Proposed label for all six: **agent-task / full / stable**,
must_block false. Reasoning: follows the v3 BUS precedent - a long
unique agent-task text that never traverses the dispatcher, expected
0 hits, any hit is a false-positive finding; route full is the worst
case (the text reaches the gateway).

| Family | Thread | Envelopes | First seen |
|---|---|---|---|
| V4-B2 | Stage 1 step 4 + qwen3.8 reload + plugin investigation | mv-003, mv-004, mv-005 | 5 Nov |
| V4-B3 | before_dispatch plugin build/install/test (held for Nitish) | mv-006, mv-007, mv-008, mv-010, outbox mv-011 | 5 Nov |
| V4-B4 | Bad-cop review: draft Workplace post | mv-009 | 5 Nov |
| V4-B5 | Portfolio review after the 5 Nov sell-off | mv-012, mv-014 | 6 Nov |
| V4-B6 | Bad-cop review: Gate 5 Medium draft (+ title + graphics) | mv-015, mv-016, mv-017 | 7 Nov |
| V4-B7 | Self-improvement nightly reports (7 Nov and 12 Nov runs) | outbox mv-20261107-016, outbox mv-20261112-001 | 7 Nov |

**AMBIGUOUS - family definition (all six bus families).** Two readings:
(a) v3-consistent: every bus body is one BUS family, already in v3 dev,
so these 16 envelopes add prompts to an existing family and count as
**0 fresh families**. (b) Task-literal: each distinct task thread is its
own family ("same question/task, paraphrases together"), giving **6 fresh
families**. The parent decides. Second tension, also for the parent: the
v3 BUS label is cacheable=stable although the expected outcome is 0 hits;
a hit on a 2 KB task body would count safe under that label.
V4-B7 is the weakest thread: its two variants are different nightly
reports 5 days apart sharing only the task frame.

Muse's own Spark interactions, as tasked: they are the bus envelopes
(`team/bus/`, Muse↔Vidyut task bus, protocol v1.2). 6 were already used
as v3 family BUS (adoption test 001/002, health check 09-001/09-002,
portfolio re-send 013, Workplace review 010-vidyut-review). The 16
unused ones are inventoried above. No other record of Muse's Spark
interactions as dispatcher traffic exists: the audit log's actor is
always `tier1`, and its HTTP rows are the live test battery, all in v3.

### Eval-derived: demo / test fixtures (8 prompts, 7 would-be families)

Listed for transparency with provenance. **fresh=false. Do NOT count
toward the holdout target.** They are the only non-v3 texts found
outside the bus, and none is real traffic.

| Family | Text(s) | Proposed label | Provenance |
|---|---|---|---|
| V4-D0 | How do I reset my Wi-Fi router? / How can I restart my Wi-Fi router? | factual / full / stable | demo seed 1 + paraphrase, created 22 Nov 05:28 UTC |
| V4-D1 | What is the capital of Spain? | factual / full / stable | demo different-intent negative (near-miss of R-F1) |
| V4-D2 | How do I reset my Wi-Fi password? | factual / full / stable | demo different-intent negative (near-miss of router) |
| V4-D3 | What is the best way to fry an egg? | factual / full / stable | demo different-intent negative (near-miss of F6 boil-egg) |
| V4-D4 | Explain cellular respiration in one sentence. | factual / full / stable | demo different-intent negative (near-miss of F5 photosynthesis) |
| V4-D5 | What is 17 multiplied by 6? | factual / full / stable | demo unrelated negative |
| V4-D6 | unlock a door if it is raining | action / full / never, must_block false | Fastpath dry-run fixture, 4 Nov (ambiguity-guard) |

V4-D6 is flagged ambiguous: a single test-fixture case, and whether a
conditional action belongs with the never action families is for the
parent to confirm. must_block is proposed false: it is not a denylist
escape and no denylist pattern covers it.

## Excluded (with reasons)

- **Same-family demo paraphrases** (belong to v3 families, not new
  families): 'Which city is the capital of France?' (R-F1),
  'Compose a haiku about rain in autumn.' (G2), 'What is the best
  method for boiling an egg?' (F6), 'Describe photosynthesis in a
  single sentence.' (F5).
- **Perception-alert near-miss variant** in cache_hits (frame-020,
  right side, "appears"): NM-A family material, not a new family.
- **Unusable texts:** `''` (14 audit rows, empty) and `'/new'`
  (a session command, in audit + store + shadow). Neither is a prompt.
- **Everything else in every source:** already in v3 by normalised
  text (56/58 audit texts; all 15 HTTP texts; all 24 live texts;
  all 68 shadow hit-row texts).

## Method notes

- **Snapshot/diff:** the ENH plan asked for daily audit snapshots so
  each prompt's first-seen day is known. No earlier snapshot exists
  and the log has no timestamps, so no first-seen day can be assigned
  to audit rows (all on/before 22 Nov). This build takes the snapshot
  (`inputs/audit_snapshot_2026-11-23.jsonl`, sha256
  `38429ab78bb546d357b1583dc3f02e53d1801c7bfcdd2da51471744a5486fe9e`)
  as the baseline, so future builds CAN diff by day. Bus envelopes
  carry real `sent_utc` timestamps; demo entries carry real
  `created_at`; the fastpath ts is a file mtime (day-granular).
- **Waves:** wave 1 = first variant of each family, wave 2 = later
  variants, on their real dates (not the v3 synthetic day 3–6 spread).
  Only V4-B7 spans more than a day (7 → 12 Nov); the other bus
  threads are same-day, so the 7-day TTL is barely exercised by this
  set. Another reason it is not holdout-ready.
- **Screening:** bus bodies were screened for secrets. No credential
  values found ("HA token" occurs as words only, and mv-003 states
  "No token in any bus file, ever"). They DO contain internal Spark
  file paths (`[home]/...`) and portfolio figures, as do v3's
  BUS prompts. This file stays on the Spark eval dir + VM workspace
  only; never public without review.
- **Dedup:** families by embedding similarity was not needed: the
  surviving population is 24 prompts and every grouping above was
  checked by hand against the v3 family list. The demo paraphrases
  and near-misses were matched to their v3 families by their seed /
  anchor texts (recorded in the builder).

## How to get more real traffic (to reach 10–15 holdout families)

1. **Extend the shadow window.** The shadow timer runs daily 06:00 UTC
   from 24 Nov; each day's replay adds newly stored prompts, and the
   audit log grows only when the dispatcher is actually used. Re-run
   this build (the builder + snapshot baseline are in place) after the
   shadow week, or when the audit log passes ~700 rows, and diff
   against `audit_snapshot_2026-11-23.jsonl` for first-seen days.
2. **More live dispatcher use.** The audit log's live rows are 119 of
   569 and mostly a fixed test battery (14x repeats); genuinely
   user-like live prompts are ~13 texts, all already in v3. Fresh
   families need fresh live requests, not more dry-run repeats.
3. **Apply the dispatcher instrumentation spec**
   (`eval/dispatcher-instrumentation-spec.md`: timestamps on audit
   rows) so future first-seen days are exact, not day-granular.
4. Do NOT lower the bar by padding with demo/test fixtures or invented
   prompts. The 7 eval-derived would-be families above stay excluded
   from the fresh count unless the parent explicitly reclassifies them.

## Hard-rule compliance

- Labels are PROPOSED only; the parent agent labels v4. Nothing is
  frozen.
- No scoring was done (neither v4 nor dev). The retired v3 holdout was
  NOT re-scored. v3 holdout scores/failures were not used for anything.
- No prompts were invented. No live routing changes, no dispatcher
  changes, no code changes. Shadow only.
- The v4 candidate gets exactly one scoring, after the parent has
  labelled and frozen it.

## Files

Spark (`[spark-home]/team/gateway-shadow-trial/eval/v4/`):

- `eval_set_v4_candidate.json` - the candidate set (24 prompts,
  13 families, proposed labels + reasoning + source per prompt)
- `build_eval_set_v4_candidate.py` - the builder (reproducible from
  `inputs/`)
- `V4-CANDIDATE-REPORT.md` - this report
- `audit_snapshot_2026-11-23.jsonl` - audit baseline snapshot for
  future diffs

VM mirror (`[workspace]/v4/`): same files, md5-verified identical,
plus `inputs/` (source extracts used by the builder).

## Neatness (kept vs deleted)

- Kept (Spark eval/v4 + VM [workspace]/v4): candidate JSON, builder,
  report, audit snapshot, and (VM only) the inputs/ source extracts.
- Deleted: /tmp/v4work scratch copies of the audit log, shadow JSON,
  cache_hits log, cache_store, bus tarball + extracted bus dir, and
  the v2/v3 read copies, after the Spark copy was md5-verified.
  Nothing was created on the Spark outside eval/v4.
