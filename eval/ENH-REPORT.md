# Semantic gateway enhancement - E1 + E3 (v2.1-enh)

**Date:** 23 Nov 2026 (evening). **Order:** Nitish, 23 Nov 2026 -
"we have to make it hit the bar". **Author:** subagent (enhancement task).

## Outcome

- The fixed gateway (v2.0-c1c6) failed VALUE at 0.0811 (dev) / 0.0833
  (holdout) against the 0.10 bar. The enhancement (v2.1-enh) clears
  the bar on dev with margin: **non-seed full-route safe-hit rate
  0.1757 seed mode (13/74) and 0.1892 empty mode (14/74)**.
- SAFETY unchanged: **0 unsafe on dev** (unweighted and weighted),
  denylist recall 1.0, gateway-traffic FP 0.0, must-block 5/5,
  0 never items stored.
- COST unchanged: p95 check 19–37 ms (embed-noise dominated),
  bge-m3 0.69 GB, qwen3.8 resident, rollback tested at 2.0 s.
- **Deployed to shadow** as v2.1-enh on :18795 (semantic-gateway.service),
  v2.0-c1c6 intact with a tested one-command rollback.
- **Verdict: CONDITIONAL GO.** No gate FAILs on dev, but the DATA
  gate is MARGINAL: the frozen holdout was already scored twice
  (budget spent) and was NOT scored again, so the holdout SAFETY /
  VALUE are unmeasured. The condition is the fresh-holdout
  validation (Section 7): a fresh holdout built from shadow-week
  traffic, scored once against the frozen v2.1-enh, must pass all
  gates for a full GO.

## 1. What was built (gateway v2.1-enh)

Two mechanism changes, both in `gateway_v3.py` (deployed as
`gateway.py`). Denylist stays v1.2, threshold stays 0.90.

### E1 - Family-aware TTL (the main lever)

- A stable factual question keeps its cached answer for **7 days**
  (`ttl_stable_hours` 168.0) instead of 24h; every other prompt
  keeps 24h.
- The TTL class is assigned **at write time** from the prompt text
  (`is_stable_factual`, a whitelist classifier on normalised text):
  interrogatives (what/who/which/where/when/why, how do/how many…),
  "tell me the/about", and translate/explain/define/describe.
  Everything else (generative, chatter, agent-task, declarative
  fragments) is not stable-factual and keeps 24h. The classifier is
  designed from general principles, not tuned to dev texts.
- Entries loaded from disk without a class (**legacy**, including
  the demo seed) keep the conservative 24h TTL, so a TTL change
  rolls out without a backfill migration and entries rotate
  naturally.
- The TTL is a property of the **stored answer**, not of the
  incoming question's phrasing: a stable fact stays correct however
  it is asked. There is deliberately **no query-side TTL cap**
  (see Section 3 for why the first version, which had one, was
  reverted).
- Entries carry `ttl_class` (`stable` / `standard` / `legacy`) and
  `ttl_seconds`; `/health` and `/stats` report `ttl_stable_hours`
  and the `ttl_classes` counts.

### E3 - Per-category threshold 0.85 for factual questions

- When a query is classified stable-factual, the similarity
  threshold is **0.85** (`threshold_factual`) instead of 0.90.
  Every other prompt keeps 0.90. The factual classifier is the
  second guard: only factual questions get the lower bar, so the
  BUS wrong-match (0.8033) and the generative near-misses stay
  misses.
- The wrong-fact risk (a factual query matching a *different* fact
  at 0.85–0.90) is bounded because the best match wins and the
  correct entry is present in replay; the daily shadow replay's
  paraphrase-review list monitors it live.

### What was tried and reverted

- **E1 with a query-side cap (min(entry TTL, query TTL)).** First
  version: a long-TTL serve required both the stored answer and the
  incoming question to be stable-factual. It scored 7/74 seed
  (0.0946, below the bar) and 8/74 empty (0.1081). The cap blocked
  declarative factual questions ("Jupiter has how many moons?",
  "Pride and Prejudice was written by whom?", "best way to boil an
  egg?", "London Underground Sunday closing time?") from matching
  days-old stable entries, costing 4 dev hits, while adding no
  safety on dev: the ttl24 queries that reach the gateway (ping,
  two jokes) score 0.41–0.54 against factual entries, far below
  threshold. Reverted to entry-side TTL only. The cap code was
  removed, not left dormant.

### What was evaluated and declined

- **E2 - request-frame stripping in normalisation (C2b).**
  Stripping "tell me the" / "what is the" so "Tell me the capital
  of France." canonicalises to the same key as "what is the capital
  of France?" would recover that one hit as an exact match. But E3
  already recovers it (0.8822 at the 0.85 factual bar), and the
  remaining near-misses after E1+E3 are generative rephrases
  (R-G1 0.8919/0.8936, G2 "write me a haiku about rain" 0.8751,
  G4 0.8305) whose recovery would need a lower bar for generative
  prompts, where the topic-mismatch risk lives. Changing
  normalisation globally would move every similarity score, a
  larger regression surface than the remaining gain justifies.
  Not built. If a future mechanism needs it, it is a separate
  ablation with a full dev re-run.

## 2. Per-candidate dev scores (frozen v3.1, threshold 0.90, dev only)

Non-seed full-route safe-hit rate is the VALUE metric (bar 0.10).
Seed = 16-entry backup seed; empty = no seed. The frozen holdout
was NOT scored (both allowed scorings used).

| Candidate | Seed mode | Empty mode | Unsafe | Notes |
|---|---|---|---|---|
| As-built v2.0-c1c6 (C4 t090) | 6/74 = 0.0811 | 6/74 = 0.0811 | 0 | baseline, VALUE FAIL |
| E1 + query-side cap | 7/74 = 0.0946 | 8/74 = 0.1081 | 0 | reverted (cap cost 4 hits) |
| E1 entry-side only (E1b) | 11/74 = 0.1486 | 12/74 = 0.1622 | 0 | clears the bar |
| **E1 + E3 (v2.1-enh, deployed)** | **13/74 = 0.1757** | **14/74 = 0.1892** | **0** | **clears the bar with margin** |

Full detail per run (all seed mode unless noted):

| Run | Hits | Safe | Unsafe | Stale ttl24 | Exact | Paraphrase | Expired miss | Never stored | Weighted safe | Weighted unsafe |
|---|---|---|---|---|---|---|---|---|---|---|
| As-built seed | 7 | 7 | 0 | 0 | 1 | 6 | 15 | 0 | 19 | 0 |
| As-built empty | 6 | 6 | 0 | 0 | 0 | 6 | 8 | 0 | 18 | 0 |
| E1 cap seed | 8 | 8 | 0 | 0 | 3 | 5 | 14 | 0 | 20 | 0 |
| E1 cap empty | 8 | 8 | 0 | 0 | 3 | 5 | 6 | 0 | 20 | 0 |
| E1b seed | 12 | 12 | 0 | 0 | 3 | 9 | 10 | 0 | 24 | 0 |
| E1b empty | 12 | 12 | 0 | 0 | 3 | 9 | 2 | 0 | 24 | 0 |
| **E1+E3 seed** | **14** | **14** | **0** | **0** | **3** | **11** | **10** | **0** | **26** | **0** |
| **E1+E3 empty** | **14** | **14** | **0** | **0** | **3** | **11** | **2** | **0** | **26** | **0** |

Denylist (all runs, both modes): recall 1.0, FP on safe 0.0455
(the known BUS-body FP, identical to as-built), FP on gateway
traffic 0.0, FP on BUS bodies 0.5, must-block 5/5. The enhancement
does not touch the denylist and does not change any of these.

## 3. Hit inspection (every recovered hit, semantically checked)

E1b recovered 5 (seed) / 6 (empty) hits over as-built; E3 added 2
more in each mode. Every one was inspected as a matched pair, not
just by the eval's safe label. All are the same question asked a
second time; no wrong-fact match, no topic mismatch.

E1b recovered (seed mode; empty mode identical plus R-F1 #1):

| Query | Matched entry | Sim | Age | Correct? |
|---|---|---|---|---|
| how many moons does jupiter have | How many moons does Jupiter have? | 1.0000 | 5.07 d | yes, same question |
| Jupiter has how many moons? | How many moons does Jupiter have? | 0.9882 | 5.10 d | yes, same question |
| who wrote pride and prejudice | Who wrote Pride and Prejudice? | 1.0000 | 5.12 d | yes |
| Pride and Prejudice was written by whom? | Who wrote Pride and Prejudice? | 0.9816 | 5.16 d | yes |
| how do I boil an egg | What is the best way to boil an egg? | 0.9506 | 5.23 d | yes, same how-to |
| best way to boil an egg? | What is the best way to boil an egg? | 0.9834 | 5.26 d | yes |
| London Underground Sunday closing time? | What time does the London Underground close on Sundays? | 0.9637 | 5.32 d | yes, same schedule |
| translate good morning to japanese | Translate 'good morning' into Japanese. | 0.9767 | 5.37 d | yes, same translation |

E3 added (both modes):

| Query | Matched entry | Sim | Age | Correct? |
|---|---|---|---|---|
| Tell me the capital of France. | what is the capital of France? | 0.8822 | 0.15 d (seed) / 3.16 d (empty) | yes |
| how do you say good morning in japanese | Translate 'good morning' into Japanese. | 0.8941 | 5.33 d | yes, same translation |

Notes:

- The haiku topic-mismatch worry from the miss analysis did not
  materialise: "write a haiku about summer heat" exactly matches
  the seed's summer-heat entry (sim 1.0, not a mismatch), and the
  autumn-rain entry scores below 0.80 against a summer-heat query.
  Generative entries stay 24h, so no haiku is served days old.
- The BUS wrong-match ("This is a small health-check task…"
  0.8033 vs "Adoption test, read-only…") stays a miss: it is
  agent-task, keeps the 0.90 bar, and is below 0.85 anyway.
- Remaining expired misses are the wave-1 queries against legacy
  seed entries (by design: legacy keeps 24h) and the generative
  R-G1 #3 (0.8907) / G2 #3 (0.8687), whose entries stay 24h.

## 4. Classifier validation (dev, gateway-flow only)

`is_stable_factual` was validated against the dev labels with route
scoping and the denylist applied first (only the 40 items that reach
the classifier). Factual groups F3/F4/F6/F7/F8/R-F1/R-Q1: 18
stable, 4 not-stable. The 4 not-stable are declarative-fragment
queries that hit via fresh entries, so their class is irrelevant.
ttl24 items reaching the classifier: 0 stable / 3 not-stable.
Never items reaching the classifier: 0. Other stable items
(generative / agent-task): 0 stable / 15 not-stable, by design
(factual-only TTL). The personal-state false positives found in a
first naive pass ("where is my PARA?", balcony-plan questions) are
all route=fast, so they never reach the gateway; the classifier
never sees them.

## 5. Verdict per gate (agreed pass criteria, PASS_CRITERIA.md)

All four gates are conjunctive. The verdict rule is pre-registered:
GO needs all four gates PASS on dev AND holdout; CONDITIONAL GO
means no FAIL and at least one MARGINAL, conditions named in
writing; NO-GO means any FAIL.

| Gate | Dev | Holdout | Verdict |
|---|---|---|---|
| DATA | frozen v3.1 dev, 110 prompts / 33 families | spent (scored twice); NOT re-scored | **MARGINAL** - fresh holdout needed (Section 7) |
| SAFETY | 0 unsafe (unweighted + weighted), recall 1.0, FP gw 0.0, must-block 5/5, 0 never stored | not measured | **PASS on dev; unmeasured on holdout** |
| VALUE | 0.1757 seed / 0.1892 empty vs bar 0.10 | not measured | **PASS on dev; unmeasured on holdout** |
| COST | p95 check 19–37 ms, bge-m3 0.69 GB, qwen3.8 resident, rollback 2.0 s | n/a (same deployment) | **PASS** |

**Overall: CONDITIONAL GO.** The condition is the fresh-holdout
validation in Section 7: a fresh holdout built from shadow-week
traffic, scored once against the frozen v2.1-enh, must pass all
gates for a full GO. Nothing is claimed about the holdout that was
not measured.

At real volume (sensitivity): the 23 Nov shadow replay saw 81
full-route requests. At the dev rate 0.1757 that is ~14 saved
generations/day; at 40/day it is ~7/day; at 20/day ~4/day. The
daily shadow replays from 24 Nov onward measure the live rate
directly (the replay's `full_route_hit_rate`).

## 6. Cost evidence

- Latency (driver, 40 consulted queries): median total check
  10.6–15.1 ms; p95 total check 19.0–37.4 ms. As-built p95 was
  28.4 ms. The E3 seed p95 (37.4 ms) is one 104 ms embed outlier
  on a long BUS body (embed median 10.0 ms, p95 23.1 ms); E3 adds
  no compute (a threshold comparison). Within measurement noise.
- Memory: bge-m3 0.69 GB resident; qwen3.8:27b-mtp-q8_0 29.05 GB
  resident (not evicted). No new model, no new resident process.
  The classifier is a few regexes on a short string.
- Operability: semantic-gateway.service active, Restart=always.
  Rollback `rollback_gateway_v2.sh` tested: **2.0 s**, restores v2.0-c1c6
  code + config, keeps the live store (v2 ignores the v3 ttl
  fields, so no learned entries are lost), /health verified
  v2.0-c1c6, then v2.1-enh re-deployed and verified. The deeper
  as-built fallback `rollback_gateway.sh` is left intact.
- Disk: 262 GB free (916 GB total).

## 7. Deploy (shadow only)

- `deploy_gateway_v3.sh` installed gateway v2.1-enh as the live
  `gateway.py` on :18795 (config: threshold 0.90, upstream stub,
  ttl_stable_hours 168.0, threshold_factual 0.85). Backups:
  `gateway_v2_c1c6_20261123.py`, `config_v2_c1c6_20261123.json`.
  The live store (29 entries) was kept, not snapshotted; it loads
  as legacy (24h) and new entries get their TTL class at write time.
- `/health` verified: v2.1-enh, threshold 0.90,
  threshold_factual 0.85, ttl_stable_hours 168.0, denylist v1.2,
  embedder warmed. `/stats`: 29 entries, all legacy.
- Smoke test (live): "What is the capital of France?" hit the
  replay-stored "what's the capital of France?" at 0.9967 (32 min
  old), latency 40 ms; repeat hit again at 0.9967, 25.8 ms. Store
  unchanged at 29 entries (both were hits, nothing stored).
- Shadow timer `gateway-shadow-replay.timer` still enabled; next run
  Tue 24 Nov 2026 06:00 UTC. No dispatcher or routing changes.
  No live routing changes of any kind.

## 8. Fresh-holdout validation plan (the condition for a full GO)

The frozen v3 holdout is retired: it was scored twice (E6 baseline
+ C1-C6 final validation), its families are known, and reusing it
would be training on the test. A fresh holdout must be built from
shadow-week traffic and scored once against the frozen v2.1-enh.

### Sources (all on the Spark)

- Dispatcher audit log
  (`[spark-home]/services/tier1-dispatcher/audit.jsonl`):
  the raw traffic text + route. Append-only, rows in time order,
  but no timestamps. 569 rows / 58 unique texts / 29 unique
  full-route texts as of 23 Nov 2026 - most of it is the v3 eval
  traffic itself, not fresh real traffic.
- Daily shadow JSONs (`eval/v3/shadow/shadow_YYYY-MM-DD.json`):
  per-day hit rows (text, matched prompt, similarity), paraphrase
  flags, newly stored prompts, risky stored prompts.
- Gateway log (`cache_hits.log.jsonl`): timestamped (replay time)
  record of every gateway query, including blocked ones.
- Store snapshots (`cache_store.json`): entries with `created_at`.

### Build steps (after the shadow week ends, 30 Nov 2026)

1. Snapshot the audit log daily (or diff by `audit_id`) so each
   prompt's first-seen DAY is known. Assign synthetic timestamps
   by first-seen day: a family's first variant on its first-seen
   day (wave 1), later variants on later days (wave 2), preserving
   the day gaps so the 7-day TTL is exercised. Document that the
   timestamps are day-granular, not exact.
2. Deduplicate into families (same question/task, paraphrases
   together) by embedding similarity plus manual review. Exclude
   the v3 eval prompts themselves (they are already in the frozen
   set and must not be re-used as fresh data).
3. Label each family: `cacheable` (stable / ttl24 / never),
   `category` (factual / generative / chatter / agent-task /
   action), `route` (full / fast), `must_block` for never items
   that must be blocked. Labelling is done by the parent agent
   (not by the subagent that built the code), with Nitish
   confirming any ambiguous family. A family whose label is
   genuinely ambiguous is dropped, not guessed.
4. Split by family into dev (about 2/3) and holdout (about 1/3).
   The holdout families are never read during any further
   iteration. Freeze the set as v4 (new FROZEN.md + PASS_CRITERIA
   reference, same gates), with the dev/holdout split recorded.
5. Score the frozen v2.1-enh against the new holdout **once**
   (summary only, no detail read). Score dev first for a sanity
   check; the holdout scoring is the single allowed one.

### Size caveat (honest)

- The audit log's unique full-route count (29 texts) is far below
  v3's scale (154 prompts / 47 families). The fresh holdout's size
  depends on how much genuinely new real traffic arrives during
  the shadow week. Target: at least 10–15 holdout families. If the
  unique family count is below that on 30 Nov, extend the shadow
  window (keep v2.1-enh in shadow, keep collecting) until the
  target is met, rather than scoring a holdout too small to mean
  anything. Do not pad the holdout with invented prompts; only
  real traffic (audit log) counts as fresh.
- The dev/holdout split and the labels must be built AFTER v2.1-enh
  is frozen. No code change may be made in response to the fresh
  holdout's failures; if it fails, the failure is reported and the
  next mechanism change starts a new dev iteration with a new
  holdout.

### What can be claimed without a fresh holdout scoring

- Dev only: VALUE 0.1757 / 0.1892, SAFETY 0 unsafe, COST as in
  Section 6. Nothing about holdout SAFETY or VALUE can be claimed
  until the fresh holdout is scored. The daily shadow replays give
  a live (unlabelled) signal - full-route hit rate, paraphrase
  hits to review, risky stored prompts - but that is monitoring,
  not a labelled holdout verdict.

## 9. Files

Spark (`[spark-home]/team/gateway-shadow-trial/eval/`):

- `gateway_v3.py` - v2.1-enh (E1 + E3), deployed as `gateway.py`
- `drive_gateway_v2.py` - driver v1.0 + `--ttl-stable-hours`,
  `--threshold-factual`
- `test_gateway_v3.py` - 24 tests, all passing (see Section 10)
- `run_e1_dev.sh`, `run_e3_dev.sh` - dev run scripts
- `deploy_gateway_v3.sh` - deploy script (run 23 Nov 18:48 UTC)
- `validate_classifier.py` - classifier validation (VM copy in
  enhance-build; run on the VM against the dev set)
- `analyse_misses.py`, `repro_baseline.sh`, `enh_e1.log`,
  `enh_e1b.log`, `enh_e3.log` - harness + run logs
- `v3/e1_t090_dev_{seed,empty}.{json,jsonl}`,
  `v3/e1b_t090_dev_{seed,empty}.{json,jsonl}`,
  `v3/e3_t090_dev_{seed,empty}.{json,jsonl}` - run outputs

Project (`semantic_gateway/`):

- `gateway.py` - v2.1-enh (live)
- `gateway_v2_c1c6_20261123.py`, `config_v2_c1c6_20261123.json` -
  v2.0-c1c6 backups
- `rollback_gateway_v2.sh` - one-command rollback to v2.0-c1c6
  (tested 2.0 s, store kept). `rollback_gateway.sh` (as-built) intact.
- `config.json` - threshold 0.90, stub, ttl_stable_hours 168.0,
  threshold_factual 0.85

VM mirror (`[workspace]/enhance-build/`): same files as the Spark
eval dir, md5-verified identical (see Section 11). Run outputs in
`runs/v3/`.

## 10. Tests

`test_gateway_v3.py`: **24/24 pass** on the Spark (20 pure
FakeEmbedder tests + 1 live bge-m3 test + 3 E3 tests). Covers:
classifier confusion cases (interrogatives / how-forms / tell-me /
transforms are stable; generative / chatter / agent-task /
declarative fragments are not), TTL expiry per class (stable 7d,
standard 24h, legacy 24h), entry TTL independent of query
phrasing, exact-path TTL behaviour, stats reporting, E3 threshold
branching (factual uses 0.85, generative keeps 0.90, None means
the same bar), and a live bge-m3 check that a different fact
(France vs Spain) scores below 0.90.

## 11. Verification (VM mirror)

- `gateway_v3.py`, `drive_gateway_v2.py`, `test_gateway_v3.py`,
  `run_e1_dev.sh`, `run_e3_dev.sh`, `deploy_gateway_v3.sh`,
  `validate_classifier.py`, `ENH-REPORT.md` - md5-verified
  identical between `[workspace]/enhance-build/` and the Spark
  eval dir (checked after the final copy).
- Run outputs (`v3/e1*`, `v3/e1b*`, `v3/e3*` JSON + JSONL) mirrored
  in `[workspace]/enhance-build/runs/v3/`.

## 12. What could not be built as specified

- Nothing in the core task is unbuilt. Two things were scoped
  down with reasons recorded: E2 (frame-stripping normalisation)
  was evaluated and declined (Section 1); the fresh holdout is a
  plan, not a built artefact, because the shadow week has not
  finished and the traffic volume is not yet known (Section 8).
- The frozen v3 holdout was not scored, by the hard rule. No
  holdout failure was read, and nothing from holdout was added to
  the denylist or the seed.

## 13. Neatness (kept vs deleted)

- Kept (Spark eval dir + VM mirror): the v3 gateway, driver,
  tests, run scripts, deploy script, classifier validation, the
  report, and all run outputs (JSON + JSONL + stdout logs).
- Deleted: the failed first E1 run's partial outputs were
  overwritten by the corrected re-run (same paths); the driver's
  temp store/log directories are removed by the driver itself
  after each run; the Spark `__pycache__` from test runs is
  left (regenerated on import, harmless). No raw downloads or
  intermediate clones were created on the Spark for this task.
- The VM `/tmp` copies of the three files used for scp staging
  were removed after copying.
