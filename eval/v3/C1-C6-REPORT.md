# C1-C6 report - semantic gateway

**Date:** 23 Nov 2026. **Gateway:** v2.0-c1c6, denylist v1.2,
threshold **0.90** (eval case v3.1, see FROZEN.md).
**Driver:** `eval/drive_gateway.py` v1.0 (replays the frozen workload
through the real gateway code; the frozen scorer v3.0 simulates the
gateway and hardcodes denylist v1.1, so it cannot judge v1.2 - it
stays untouched as the baseline reference).
**Pass criteria:** AGREED 23 Nov 2026 by Nitish in writing
(`eval/v3/PASS_CRITERIA.md`). Gates are conjunctive: one FAIL = NO-GO.

## Verdict: NO-GO (VALUE fails; SAFETY and COST pass)

| Gate | Result | Numbers |
|---|---|---|
| SAFETY | **PASS** | Zero unsafe on dev AND holdout, unweighted and weighted. Denylist recall 1.0, FP 0.0 on gateway traffic. Must-block 5/5 (dev; holdout has 0 must-block items by design). 0 never items stored, dev and holdout. |
| VALUE | **FAIL** | Non-seed full-route safe-hit rate: dev best 0.0811 (6/74 at 0.90), holdout 0.0833 (2/24). Bar is 0.10. No threshold passes. |
| COST | **PASS** | p95 check 28.4 ms warm (bar 50 ms fast path / ~131 ms = 10% of full-route). Memory: bge-m3 0.69 GB + gateway process ~16 MB peak, well under 2 GB. qwen3.6 not evicted by bge-m3. Rollback 2.1 s (bar under 60 s). No regressions: 31/31 tests pass. |

The C1-C6 fixes made the mechanism **safe** (the as-built code had
3 unsafe hits on dev and 68 weighted unsafe hits on holdout; the
fixed code has 0 on both), but it does not save enough to meet the
10% bar. The threshold is not the fix: safety holds at every
threshold swept (0.90-0.98), and no threshold reaches 0.10.

## What was built

- **C1 - exact-match fast path.** Normalised string equality checked
  before any embedding; exact repeats never pay the embedding cost.
  Verified by test: a case/punctuation variant adds 0 embed calls.
- **C2 - text normalisation before embedding.** Lowercase, strip
  punctuation/whitespace; identical to the scorer v3.0 function.
  Adds 2 safe hits at 0.98 on dev (6 vs 4 hits with-seed), 0 unsafe.
- **C3 - route / denylist / TTL in the gateway itself.**
  Denylist v1.2 (perception-alert patterns, verb-object lights
  phrasings, shell-injection patterns; the v1.1 status false
  positive on "what's the status of my quantum computer?" fixed);
  TTL 24 h enforced on lookup and on the exact path; route
  scoping (route != "full" never consults/stores); denied and
  route-blocked items are never stored. Covers all 9 known v1.1
  escapes (5 must-block + alert-3b + alert-3c + "turn the lights
  on!" + "turn the lights off").
- **C4 - threshold retune on dev only.** Sweep 0.90/0.93/0.95/0.98
  on the fixed code, with-seed and empty-store. Best is 0.90
  (non-seed rate 0.0811); no threshold meets 0.10. Threshold
  0.98 to 0.90 recorded as eval-case v3.1 (FROZEN.md re-freeze
  entry; v3 data files untouched).
- **C5 - keep-alive on bge-m3.** Embedder sends `keep_alive: 24h`
  plus best-effort warmup at startup. Cold first embed 2,675 ms
  (model unloaded) / 1,833 ms (after a qwen3.6 load evicted it);
  warm median 8.6 ms, p95 12.1 ms. p95 total check 28.4 ms.
  bge-m3 0.69 GB resident; gateway process ~16 MB peak.
  Co-residency verified: after bge-m3 reloads, qwen3.6 (38.15 GB)
  is still resident; both coexist at 38.83 GB total.
  Caveat: loading qwen3.6 evicts bge-m3 (Ollama policy); it
  self-heals on the next embed (~1.8 s). bge-m3 does not evict
  qwen3.6.
- **C6 - wiring + shadow week.** Fixed gateway installed as the
  permanent user service `semantic-gateway.service` (Restart=always,
  :18795), replacing the transient scope. One-command rollback
  `rollback_gateway.sh` tested: 2.1 s, /health back to as-built
  (threshold 0.98). Live store migrated (16 entries re-embedded
  from normalised text, backup first). Daily shadow replay via
  user timer 06:00 UTC; first (baseline) replay 23 Nov 2026
  18:15 UTC. Shadow only: no dispatcher changes, no live routing.

## Per-fix dev scores (frozen v3 dev, 110 prompts, threshold 0.98)

| Config | Seed | Hits | Safe | Unsafe | Weighted unsafe | Full-route safe | Non-seed rate | Denylist recall | FP (gw) | Must-block | Never stored |
|---|---|---|---|---|---|---|---|---|---|---|---|
| C1 only | seed | 4 | 3 | 1 | 2 | 3/74 | 0.0270 | 0.0 | 0.0 | 0/5 | 43 |
| C1 only | empty | 3 | 2 | 1 | 2 | 2/74 | 0.0270 | 0.0 | 0.0 | 0/5 | 43 |
| C1+C2 | seed | 6 | 5 | 1 | 2 | 5/74 | 0.0541 | 0.0 | 0.0 | 0/5 | 43 |
| C1+C2 | empty | 5 | 4 | 1 | 2 | 4/74 | 0.0541 | 0.0 | 0.0 | 0/5 | 43 |
| C1+C2+C3 | seed | 5 | 5 | 0 | 0 | 5/74 | 0.0541 | 1.0 | 0.0 | 5/5 | 0 |
| C1+C2+C3 | empty | 4 | 4 | 0 | 0 | 4/74 | 0.0541 | 1.0 | 0.0 | 5/5 | 0 |

C3 is the step that takes unsafe to zero (1 to 0) and never-stored
to zero (43 to 0). C1 alone loses hits vs the as-built baseline
(18 hits) only because the frozen case binds the 24 h TTL: 14 of
the as-built hits are matches on entries older than TTL.

## C4 threshold sweep (fixed code, dev only)

| Threshold | Seed | Hits | Safe | Unsafe | Weighted unsafe | Non-seed rate |
|---|---|---|---|---|---|---|
| 0.90 | seed | 7 | 7 | 0 | 0 | 0.0811 (6/74) |
| 0.90 | empty | 6 | 6 | 0 | 0 | 0.0811 (6/74) |
| 0.93 | seed | 6 | 6 | 0 | 0 | 0.0676 (5/74) |
| 0.95 | seed | 5 | 5 | 0 | 0 | 0.0541 (4/74) |
| 0.98 | seed | 5 | 5 | 0 | 0 | 0.0541 (4/74) |
| 0.98 | empty | 4 | 4 | 0 | 0 | 0.0541 (4/74) |

Zero unsafe at every threshold (safety comes from denylist v1.2 +
TTL + route scoping, not the threshold). 0.90 chosen: best safe-hit
rate at zero unsafe. Reproducibility: the 0.98 sweep rerun matches
the C1+C2+C3 run exactly (5/5/0 seed, 4/4/0 empty).

## Driver validation

The driver reproduces the frozen scorer's scoped baseline modulo
the intended changes (denylist v1.1 to v1.2, normalisation on).
Scoped baseline (seed): consulted 48, blocked-deny 26, hits 4,
safe 3, unsafe 1, never-stored 8, deny recall 0.7097, FP 0.0167.
Fixed code (seed, 0.98): consulted 40, blocked-deny 34, hits 5,
safe 5, unsafe 0, never-stored 0, deny recall 1.0, FP 0.0.
The +8 denylist blocks are exactly +9 never items blocked (the
v1.1 escapes) minus 1 safe false positive fixed (the quantum
computer status question). The +2 safe hits are the normalisation
gain the E5 sweep predicted.

## Final holdout validation (v3.1, threshold 0.90, summary only)

Second and last allowed holdout scoring (E6 baseline used the first).
No holdout detail was read; no holdout text was added to the
denylist or seed.

| | With-seed | Empty-store |
|---|---|---|
| Requests | 44 | 44 |
| Consulted | 18 | 18 |
| Blocked (denylist / route) | 6 / 20 | 6 / 20 |
| Hits / safe / unsafe | 2 / 2 / 0 | 2 / 2 / 0 |
| Weighted unsafe (of 113) | 0 | 0 |
| Full-route safe | 2/24 (0.0833) | 2/24 (0.0833) |
| Non-seed full-route safe | 2 (0.0833) | 2 (0.0833) |
| Denylist recall / FP (gw) | 1.0 / 0.0 | 1.0 / 0.0 |
| Never items stored | 0 | 0 |
| Median total check | 16.0 ms | 10.2 ms |

E6 holdout baselines for comparison: as-built seed 1 hit / 1 safe /
0 unsafe unweighted but **68 weighted unsafe hits** (store
poisoning: "unlock a door" stored once, hit 42 times); scoped
seed 0 hits / 0 unsafe / 0 saved. Fixed code: 2 safe hits, 0 unsafe,
weighted unsafe 0.

## Shadow run (running, started 23 Nov 2026 18:15 UTC)

- Daily replay of `[spark-home]/services/tier1-dispatcher/audit.jsonl`
  (569 rows; no timestamps, so a daily batch score, not time-ordered)
  through the deployed gateway; timer `gateway-shadow-replay.timer`,
  06:00 UTC daily for one week; summaries in `eval/v3/shadow/`.
- Baseline 23 Nov: 555 requests, 81 consulted (full-route),
  372 route-blocked, 102 denylist-blocked, 68 hits (60 exact +
  8 paraphrase), full-route hit rate 0.8395, 13 newly stored,
  store 16 to 29, median check 11.6 ms, p95 23.9 ms.
  The 8 paraphrase hits are one benign pair ("what is the capital
  of France? Answer in one short sentence." to "what's the capital
  of France?", sim 0.901). The only risky-flagged newly stored
  prompt is "what's the status of my quantum computer?", the safe
  question v1.2 deliberately unblocks. No alert/lights/door/
  temperature prompt was stored or hit.
- Note: the shadow hit rate is dominated by within-log repeats
  (the audit log is mostly a repeated test battery), so it
  measures repeat-serving, not fresh-traffic value; the frozen
  eval remains the value authority. Day-over-day TTL churn
  (entries stored day 1 expire by day 3) is the signal to watch.
- Shadow upstream is a stub (placeholder outputs stored, never
  served to a user). A production deploy would wire the real
  upstream (dispatcher); that step is not done and not claimed.

## What could not be built as specified

- **VALUE gate not met.** No threshold reaches 10% non-seed
  full-route safe hits on dev (best 0.0811) or holdout (0.0833).
  The mechanism is safe but the saving is below the bar. This is
  a verdict, not a build failure: nothing in C1-C6 was left
  unbuilt. The next step, if Nitish wants it, is a mechanism
  change (e.g. a longer TTL for stable factual families, or an
  intent classifier for the near-miss band), not another
  threshold move.
- **Holdout must-block gate rests on dev alone.** All must-block
  families were forced into dev by the split design, so holdout
  has 0 must-block items; the 5/5 result is dev-only.
- **DATA gate is WEAK on holdout alone** (17 real prompts);
  the verdict rests on dev + holdout together (FROZEN.md).
- **bge-m3 residency is best-effort in Ollama**, not pinned:
  loading qwen3.6 evicts it (self-heals on next embed, ~1.8 s).
  The 24 h keep-alive holds only until another large model load.
- **Shadow replay is a batch, not live traffic.** The audit log
  has no timestamps and the replay uses live time for every row,
  so TTL ageing across days is approximate.

## Files (Spark + VM mirror, md5-verified identical)

- Gateway: `semantic_gateway/gateway.py`
  (= `gateway_v2.py`, md5 `09c629e3c4f2bad23345195e580b9fc5`),
  `config.json` (threshold 0.9, upstream stub), `rollback_gateway.sh`,
  backups `gateway_asbuilt_20261123.py`, `config_asbuilt_20261123.json`,
  `cache_store_backup_20261123.json`. Service `semantic-gateway.service`.
- Harness: `team/gateway-shadow-trial/eval/drive_gateway.py`
  (md5 `272546540568f072f10ef83a4884848b`), `shadow_replay_daily.py`.
- Tests: `tests/test_gateway_v2.py`
  (31 tests, all pass incl. 2 live bge-m3).
- Scores: `eval/v3/c1_dev_{seed,empty}.json`,
  `c1c2_dev_{seed,empty}.json`, `c1c2c3_dev_{seed,empty}.json`,
  `c4_t0{90,93,95,98}_dev_{seed,empty}.json`,
  `c1c6_holdout_{seed,empty}.json`,
  `eval/v3/shadow/shadow_2026-11-23.json`.
- Eval case: `eval/v3/FROZEN.md` (v3.1 re-freeze entry, threshold 0.90),
  md5 `f7e60893a4ff1a01e2efff2dc45375e5`.
- VM mirror: `[workspace]/c1c6-build/` (code, driver, tests, run
  summaries under `runs/v3/`, deploy/rollback/shadow scripts,
  this report).

## Neatness (Spark)

- Kept: the files listed above (deliverables + service + backups).
- Deleted at end of task: `/tmp/gwtest`, `/tmp/c5_measure.py`,
  `/tmp/c5_coresidency.py`, `/tmp/c5_coresidency.log`,
  `/tmp/c1c6-runs.tgz`, `/tmp/c1c6-final.tgz`, `/tmp/deploy_gateway_v2.sh`,
  `/tmp/setup_shadow_timer.sh`, `/tmp/deploy2.log`, `/tmp/deploy3.log`.
  (Driver temp stores were removed by the driver itself per run.)
