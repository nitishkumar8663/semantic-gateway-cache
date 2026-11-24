# Semantic gateway enhancement round 2 - E5 + E6 (v2.2-enh)

**Date:** 23 Nov 2026 (evening). **Order:** Nitish, 23 Nov 2026 -
"Need a full go, so need more changes". **Author:** subagent
(enhancement round 2).

## Outcome

- v2.1-enh (E1 + E3) was CONDITIONAL GO at **0.1757 seed /
  0.1892 empty** on dev. v2.2-enh (E5 + E6, this round) widens
  the dev margin to **0.2432 seed (18/74) / 0.2568 empty (19/74)**,
  0 unsafe, COST PASS, 39/39 tests.
- Three candidates were evaluated and **declined with numbers**:
  E2 frame stripping (REGRESSES: 12/13), E3b factual threshold
  0.80 (no gain: 13/14), E4 legacy backfill (seed-mode VALUE
  collapses to 0.0135 - see Section 2).
- **Deployed to shadow** as v2.2-enh on :18795
  (semantic-gateway.service); v2.1-enh intact with a tested
  one-command rollback (2.0 s).
- **Verdict: CONDITIONAL GO, wider margin.** No gate FAILs on dev,
  but the DATA gate is still MARGINAL for the same reason as
  v2.1-enh: the frozen holdout was already scored twice (budget
  spent) and was NOT scored again, so holdout SAFETY / VALUE are
  unmeasured. The condition is unchanged: the fresh-holdout
  validation (ENH-REPORT §8, after the shadow week ends 30 Nov).
  A full GO cannot come from dev alone, however wide the margin.

## 1. What was built (gateway v2.2-enh)

Two mechanism changes, both in `gateway_v4.py` (deployed as
`gateway.py`). Denylist stays v1.2, threshold stays 0.90,
factual threshold stays 0.85, TTL stays 7d for stable entries.
Every candidate sits behind a config flag so each ablation is a
clean rerun (`drive_gateway_v3.py`: `--no-generative-ttl`,
`--threshold-generative`, `--frame-strip-factual`,
`--legacy-backfill`).

### E5 - Stable-generative TTL (the main lever, +2 per mode)

- A self-contained creative artefact keeps its cached answer for
  **7 days** like a stable fact: `is_stable_generative`
  (write/make/create/compose a haiku, a video, a piece of code).
  The TTL class is assigned at write time from the prompt text,
  stored on the entry as `ttl_class: stable-generative`.
- Source-dependent generative prompts keep 24h: summarise /
  summarize a report, explain a changing situation. Their source
  can change; a haiku cannot go stale.
- The principle: for generative prompts the risk is topic
  mismatch, not staleness, and that is guarded by the similarity
  threshold (E6), not by TTL. A generated artefact re-served days
  later is still a correct answer to the same request.
- Classifier guard found and fixed during validation: the first
  version matched the creative verb anywhere in the text and
  classified a long BUS agent-task body as generative, because
  "write" occurs at character 253 ("... and write your one-line
  reply to outbox/ ..."). That would have given a bus body a 7d
  TTL and the 0.85 bar - exactly the population the threshold
  protects. Fixed: the verb must appear in the first 40
  characters ("Using Remotion, write the code ..." still counts,
  verb at character 15). See Section 4.

### E6 - Per-category threshold 0.85 for stable-generative queries (+3 per mode)

- When a query is classified stable-generative, the similarity
  threshold is **0.85** (`threshold_generative`) instead of 0.90.
  Factual keeps 0.85, everything else keeps 0.90.
- The principle: a creative prompt has no single right answer, so
  a near-paraphrase artefact is an acceptable substitute; a
  factual question has exactly one right answer. The classifier
  is the second guard, as in E3.
- The one borderline hit this adds is inspected in Section 3
  (rain haiku served for a rain-haiku request) and judged
  acceptable; it is flagged here rather than hidden.

### What was evaluated and declined

- **E2 - factual-only frame stripping.** Stripping "tell me the" /
  "what is the" before embedding, factual queries only. It does
  not recover the one remaining factual near-miss ("when does the
  tube close on sundays", 0.7734 - a wording gap, tube vs
  Underground, not a frame gap; stripping lowers it to 0.7557
  by direct pair measurement) and it REGRESSES one hit: "What is
  the capital of France? Answer in one short sentence." falls
  from 0.9012 to 0.8446, below the 0.85 factual bar. Dev: 12/74
  seed, 13/74 empty (base 13/14). Not built into the shipped
  config (flag stays off; code kept for the ablation record).
- **E3b - factual threshold 0.80.** No gain on dev (13/14,
  identical to base): the only factual near-miss sits at 0.7734,
  below 0.80. A lower bar buys nothing and only consumes
  wrong-fact headroom, so it stays at 0.85. (Checked: the
  different-fact pair France vs Spain scores 0.7432 live, below
  0.80 - so 0.80 would not have caused a France/Spain wrong-fact
  hit either; it is declined for no-gain, not for a live risk.
  The live test now asserts France vs Spain < 0.80.)
- **E4 - legacy backfill.** Classifying entries loaded from disk
  without a TTL class at load (factual / generative -> 7d)
  instead of keeping 24h. It recovers the wave-1 expired misses
  against the demo seed (total hits 14 -> 21 in seed mode) but
  the VALUE metric collapses: seed-mode non-seed safe hits fall
  to **1/74 = 0.0135**. Reason: once wave-1 queries hit the seed
  entry, they never store a replay entry, so the wave-2 queries
  also hit the seed entry - and seed-matched hits do not count
  toward the bar. The backfill converts counted hits into
  uncounted ones. Empty mode is unchanged (16/74, same as E5:
  no seed to backfill). Declined: the agreed VALUE bar is the
  dev metric, and E4 fails it in seed mode. Note for the record:
  in production there is no demo seed, so this is an eval
  artefact, not a production defect - but the bar is the bar,
  and the live store rotates to classified entries within a week
  without a backfill.

## 2. Per-candidate dev scores (frozen v3.1, threshold 0.90, dev only)

Non-seed full-route safe-hit rate is the VALUE metric (bar 0.10).
Seed = 16-entry backup seed; empty = no seed. The frozen holdout
was NOT scored (both allowed scorings used).

| Candidate | Seed mode | Empty mode | Unsafe | Notes |
|---|---|---|---|---|
| v2.1-enh baseline (repro) | 13/74 = 0.1757 | 14/74 = 0.1892 | 0 | base run reproduces e3 exactly |
| E2 frame strip (factual-only) | 12/74 = 0.1622 | 13/74 = 0.1757 | 0 | REGRESSES 1 hit per mode |
| E3b factual threshold 0.80 | 13/74 = 0.1757 | 14/74 = 0.1892 | 0 | no gain |
| E4 legacy backfill (+E5) | 1/74 = 0.0135 | 16/74 = 0.2162 | 0 | seed VALUE collapses |
| E5 generative TTL 7d | 15/74 = 0.2027 | 16/74 = 0.2162 | 0 | +2 per mode |
| **E5 + E6 (v2.2-enh, deployed)** | **18/74 = 0.2432** | **19/74 = 0.2568** | **0** | **+5 per mode over v2.1** |

Wilson 95% CIs: base 13/74 [0.106, 0.278]; v2.2 seed 18/74
[0.160, 0.352], empty 19/74 [0.171, 0.367]. The absolute CIs
overlap, so the margin is not claimed as a statistically
separated win; the gain is paired (same 110 prompts, 5 new hits,
0 lost vs base), which is what makes the direction solid.
Full detail per run (all seed mode unless noted):

| Run | Hits | Safe | Unsafe | Weighted unsafe | Stale ttl24 | Expired miss | Never stored | Denylist recall | FP gw | Must-block |
|---|---|---|---|---|---|---|---|---|---|---|
| base seed | 14 | 14 | 0 | 0 | 0 | 10 | 0 | 1.0 | 0.0 | 5/5 |
| base empty | 14 | 14 | 0 | 0 | 0 | 2 | 0 | 1.0 | 0.0 | 5/5 |
| E2 seed | 13 | 13 | 0 | 0 | 0 | 10 | 0 | 1.0 | 0.0 | 5/5 |
| E2 empty | 13 | 13 | 0 | 0 | 0 | 2 | 0 | 1.0 | 0.0 | 5/5 |
| E3b seed | 14 | 14 | 0 | 0 | 0 | 10 | 0 | 1.0 | 0.0 | 5/5 |
| E3b empty | 14 | 14 | 0 | 0 | 0 | 2 | 0 | 1.0 | 0.0 | 5/5 |
| E4 seed | 21 | 21 | 0 | 0 | 0 | 3 | 0 | 1.0 | 0.0 | 5/5 |
| E4 empty | 16 | 16 | 0 | 0 | 0 | 0 | 0 | 1.0 | 0.0 | 5/5 |
| E5 seed | 16 | 16 | 0 | 0 | 0 | 8 | 0 | 1.0 | 0.0 | 5/5 |
| E5 empty | 16 | 16 | 0 | 0 | 0 | 0 | 0 | 1.0 | 0.0 | 5/5 |
| **E5+E6 seed** | **19** | **19** | **0** | **0** | **0** | **8** | **0** | **1.0** | **0.0** | **5/5** |
| **E5+E6 empty** | **19** | **19** | **0** | **0** | **0** | **0** | **0** | **1.0** | **0.0** | **5/5** |

Denylist (all runs, both modes): recall 1.0, FP on gateway
traffic 0.0, must-block 5/5, 0 never items stored. Unchanged
from v2.1-enh; v2.2 does not touch the denylist.

## 3. Hit inspection (every new hit, semantically checked)

E5 recovered 2 per mode; E6 added 3 more per mode. Identical
sets in seed and empty modes. Every one was inspected as a
matched pair, not just by the eval's safe label.

| Query | Matched entry | Sim | Age | Correct? |
|---|---|---|---|---|
| make a 10 second animated video of the chatter benchmark bars (E5) | make a 10-second animated video of the chatter benchmark bars | 0.9979 | 3.34 d | yes, near-exact same task |
| a haiku about autumn rain please (E5) | Write a haiku about autumn rain. | 0.9487 | 5.46 d | yes, same topic |
| Using Remotion, write the code for a 10-second animation of the chatter benchmark bars (E6) | make a 10-second animated video of the chatter benchmark bars | 0.8919 | 3.26 d | yes, same task, different phrasing |
| make an animated video of the chatter benchmark (E6) | make a 10-second animated video of the chatter benchmark bars | 0.8936 | 3.30 d | yes, same task |
| write me a haiku about rain (E6) | Write a haiku about autumn rain. | 0.8751 | 5.43 d | BORDERLINE, judged acceptable: autumn rain is rain; the served haiku is about rain. A summer-heat haiku for the same query (0.6924) stays a miss. |

Notes:

- The BUS wrong-match (0.8033) stays a miss: BUS bodies are
  agent-task, keep the 0.90 bar, and are below 0.85 anyway. The
  classifier tightening (§4) also keeps BUS bodies out of the
  generative class entirely.
- The G4 summaries (0.7366 / 0.8305) stay misses: summarise is
  not stable-generative (source-dependent, 24h TTL) and keeps
  0.90. The F7 tube question (0.7734) stays a miss under every
  candidate tried.
- Remaining expired misses in seed mode (8) are all wave-1
  queries against legacy seed entries (F3/F4/F6/F7/F8 factual,
  G2 haiku, R-F1 capital) - seed-matched by design, so they
  cannot count toward VALUE; E4 shows recovering them costs
  more counted hits than it gains. Empty mode has 0 expired
  misses left under v2.2.

## 4. Classifier validation (dev, gateway-flow only)

`is_stable_generative` was validated against the dev labels with
route scoping and the denylist applied first (same method as
ENH-REPORT §4). After the 40-char head fix: **8 items reaching
the gateway are classified generative, all 8 generative/stable;
0 agent-task, 0 ttl24, 0 never.** Factual classifier unchanged:
18 stable-factual reaching the gateway. The pre-fix version had
1 false positive (the BUS body, verb at character 253); the fix
is covered by a unit test with that exact body shape.
`validate_classifier_gen.py` reproduces these counts on the VM.

## 5. Verdict per gate (agreed pass criteria, PASS_CRITERIA.md)

All four gates are conjunctive. GO needs all four gates PASS on
dev AND holdout; CONDITIONAL GO means no FAIL and at least one
MARGINAL, conditions named in writing; NO-GO means any FAIL.

| Gate | Dev | Holdout | Verdict |
|---|---|---|---|
| DATA | frozen v3.1 dev, 110 prompts / 33 families | spent (scored twice); NOT re-scored | **MARGINAL** - fresh holdout needed (ENH-REPORT §8) |
| SAFETY | 0 unsafe (unweighted + weighted), recall 1.0, FP gw 0.0, must-block 5/5, 0 never stored | not measured | **PASS on dev; unmeasured on holdout** |
| VALUE | 0.2432 seed / 0.2568 empty vs bar 0.10 | not measured | **PASS on dev; unmeasured on holdout** |
| COST | p95 check 23–27 ms, bge-m3 0.69 GB, qwen3.8 resident, rollback 2.0 s | n/a (same deployment) | **PASS** |

**Overall: CONDITIONAL GO, wider dev margin.** The condition is
unchanged from v2.1-enh: a fresh holdout built from shadow-week
traffic, scored once against the frozen v2.2-enh, must pass all
gates for a full GO. Nothing is claimed about the holdout that
was not measured.

At real volume (sensitivity): the 23 Nov shadow replay saw 81
full-route requests. At the dev rate 0.2432 that is ~20 saved
generations/day; at 40/day ~10/day; at 20/day ~5/day (v2.1-enh:
~14 / ~7 / ~4). The daily shadow replays measure the live rate
directly (the replay's `full_route_hit_rate`).

## 6. Cost evidence

- Latency (driver detail, 40 consulted queries per run): v2.2
  median total check 12.6 ms seed / 10.6 ms empty; p95 total
  check 26.5 ms seed / 23.2 ms empty. v2.1 baseline p95 was
  29.3 / 19.4 ms. E5/E6 add no compute (a TTL class at write
  time, two threshold comparisons). Within measurement noise.
- Memory: bge-m3 0.69 GB resident; qwen3.8 resident (not
  evicted). No new model, no new resident process. Both
  classifiers are a few regexes on a short string.
- Operability: semantic-gateway.service active, Restart=always.
  Rollback `rollback_gateway_v3.sh` tested: **2.0 s**, restores
  v2.1-enh code + config, keeps the live store (30 entries),
  /health verified v2.1-enh, then v2.2-enh re-deployed and
  verified. The deeper fallbacks `rollback_gateway_v2.sh` (v2.0-c1c6)
  and `rollback_gateway.sh` (as-built) are left intact.
- Rollback caveat: v2.1 honours an entry's stored `ttl_seconds`,
  so entries written under v2.2 as stable-generative keep their
  7d TTL after a rollback until they rotate; new entries written
  after the rollback get v2.1 classes. Code and thresholds revert
  fully.
- Disk: not re-measured this round; 262 GB free at v2.1 deploy,
  no large files added (code + run outputs only).

## 7. Deploy (shadow only)

- `deploy_gateway_v4.sh` installed gateway v2.2-enh as the live
  `gateway.py` on :18795 (config: threshold 0.90, upstream stub,
  ttl_stable_hours 168.0, threshold_factual 0.85,
  threshold_generative 0.85, generative_ttl true,
  frame_strip_factual false, legacy_backfill false). Backups:
  `gateway_v3_enh_20261123.py`, `config_v2_1_enh_20261123.json`.
  The live store was kept, not snapshotted; its 29 entries load
  as legacy (24h) and new entries get their TTL class at write
  time.
- `/health` verified: v2.2-enh, threshold 0.90,
  threshold_factual 0.85, threshold_generative 0.85,
  ttl_stable_hours 168.0, denylist v1.2, embedder warmed.
  `/stats`: 29 entries, all legacy (before smoke test).
- Smoke test (live): "What is the capital of France?" hit the
  replay-stored "what's the capital of France?" at 0.9967,
  27 ms. "Write a haiku about autumn rain." missed at 0.5235
  (no live haiku entry within TTL) and stored as
  stable-generative, entries 29 -> 30 - the new TTL class works
  live. Store now 30 entries (29 legacy + 1 stable-generative).
- Shadow timer `gateway-shadow-replay.timer` still enabled; next run
  Tue 24 Nov 2026 06:00 UTC. No dispatcher or routing changes.
  No live routing changes of any kind.

## 8. Files

Spark (`[spark-home]/team/gateway-shadow-trial/eval/`):

- `gateway_v4.py` - v2.2-enh (E5 + E6 shipped; E2/E3b/E4 behind
  flags, off in the deployed config), deployed as `gateway.py`
- `drive_gateway_v3.py` - driver v1.1 + `--threshold-generative`,
  `--frame-strip-factual`, `--legacy-backfill`,
  `--no-generative-ttl`
- `test_gateway_v4.py` - 39 tests, all passing (see Section 9)
- `run_enh2_dev.sh` - ablation matrix (base|e2|e3b|e4|e5|e5e6)
- `deploy_gateway_v4.sh` - deploy script (run 23 Nov 21:05 UTC)
- `validate_classifier_gen.py` - generative classifier validation
- `ENH2-REPORT.md` - this report
- `v3/{base,e2,e3b,e4,e5,e5e6}_t090_dev_{seed,empty}.{json,jsonl}`
  (+ `.stdout.log`) - run outputs

Project (`semantic_gateway/`):

- `gateway.py` - v2.2-enh (live)
- `gateway_v3_enh_20261123.py`, `config_v2_1_enh_20261123.json` -
  v2.1-enh backups
- `rollback_gateway_v3.sh` - one-command rollback to v2.1-enh
  (tested 2.0 s, store kept). `rollback_gateway_v2.sh` (v2.0-c1c6)
  and `rollback_gateway.sh` (as-built) intact.
- `config.json` - threshold 0.90, stub, ttl_stable_hours 168.0,
  threshold_factual 0.85, threshold_generative 0.85,
  generative_ttl true, frame_strip_factual false,
  legacy_backfill false

VM mirror (`[workspace]/enhance2-build/`): same files as the Spark
eval dir, md5-verified identical (see Section 10). Run outputs in
`runs/v3/`.

## 9. Tests

`test_gateway_v4.py`: **39/39 pass** on the Spark (24 carried
over from v2.1 + 15 new: generative classifier positives /
negatives incl. the long BUS-body negative, generative TTL
expiry per class, summary still 24h, generative-TTL-off
behaviour, legacy backfill on/off, frame-strip unit behaviour,
E6 threshold branching incl. summary keeping 0.90, and a live
bge-m3 check that a different fact (France vs Spain) scores
below 0.80 - strengthened from 0.90, since the factual bar is
0.85 and the 0.80 ablation was tested).

## 10. Verification (VM mirror)

- `gateway_v4.py`, `drive_gateway_v3.py`, `test_gateway_v4.py`,
  `run_enh2_dev.sh`, `deploy_gateway_v4.sh`,
  `validate_classifier_gen.py`, `ENH2-REPORT.md` - md5-verified
  identical between `[workspace]/enhance2-build/` and the Spark
  eval dir (checked after the final copy).
- Run outputs (`v3/{base,e2,e3b,e4,e5,e5e6}_t090_dev_{seed,empty}`
  JSON + JSONL) mirrored in `[workspace]/enhance2-build/runs/v3/`.

## 11. What could not be built as specified

- Nothing in the core task is unbuilt: all five candidates in the
  brief were built behind flags and scored on dev (E2, E3b, E4,
  E5, E6). Three were declined with numbers (Section 1); the
  shipped version is E5 + E6.
- A full GO could not be delivered: it needs the fresh holdout
  scored once (ENH-REPORT §8), which cannot happen until the
  shadow week ends (30 Nov) and the traffic exists. Dev margin
  widened from 0.176/0.189 to 0.243/0.257 instead.
- The frozen v3 holdout was not scored, by the hard rule. No
  holdout failure was read, and nothing from holdout was added to
  the denylist or the seed.
- Overfitting note (honest): E5/E6 are the third mechanism round
  tuned against the same 110 dev prompts (C1-C6, then E1/E3,
  now E5/E6). Each mechanism is justified on general principles
  in Section 1, and every new hit was semantically inspected,
  but the dev number is now a tuned number: the fresh holdout
  is the only untainted check, and it must be scored once
  against the frozen v2.2-enh with no further code change in
  response to its failures.

## 12. Neatness (kept vs deleted)

- Kept (Spark eval dir + VM mirror): the v4 gateway, driver,
  tests, run scripts, deploy script, classifier validation, the
  report, and all run outputs (JSON + JSONL + stdout logs).
- Deleted: the VM `/tmp` probe script and the `/tmp` copies of
  three detail JSONLs after mirroring; the driver's temp
  store/log directories are removed by the driver itself after
  each run; the Spark `__pycache__` from test runs is left
  (regenerated on import, harmless). No raw downloads or
  intermediate clones were created on the Spark for this task.
- Live store note: the smoke test stored one haiku entry
  (stable-generative, STUB-OUTPUT), entries 29 -> 30. It is
  ordinary shadow learning (the replay stores stub outputs the
  same way) and was left in place; the rollback test confirmed
  it survives a rollback.
