# Eval set v3 - frozen (23 Nov 2026)

The frozen eval case for the semantic gateway,
built under eval-driven development: settle the eval case first,
then use it to make the code better. See the assessment at
`[workspace]/eval-driven-development-assessment-2026-11-23.md`
(VM) and the freeze manifest `FROZEN.md` in this directory.

## What is frozen

- **Dataset v3** - `eval_set.json` (154 prompts, 47 families),
  `eval_set_dev.json` (110 prompts, 33 families),
  `eval_set_holdout.json` (44 prompts, 14 families). Built by
  `eval/build_eval_set_v3.py` from v2. Split by family,
  stratified by category, deterministic seed 20261123.
- **Scorer v3.0** - `eval/score.py`. Changes vs v2: stale ttl24
  hits count unsafe; family_recall fixed; denylist FP split by
  population; traffic-weighted reporting; seed entries use real
  `created_at` timestamps; trace fields on every detail row;
  must-block reporting; never-items-stored metric; `--threshold`,
  `--normalise`, `--seed-mode`, `--shuffle-seed` flags; Wilson
  95% CIs.
- **Threshold 0.98** - the current shipped value. The E5 sweep
  found NO threshold satisfying the pre-registered rule, so the
  mechanism fails per that rule; 0.98 is frozen as the baseline
  setting, not as a passing setting. See `SWEEP.md`.
- **Pass criteria** - `PASS_CRITERIA.md`. PROPOSED, not yet agreed
  by Nitish. Do not judge code changes against them until he
  agrees them in writing.

## Files in this directory

| File | What it is |
|---|---|
| `eval_set.json` | Full v3 set (dev + holdout). |
| `eval_set_dev.json` | Dev split. Iterate against this. |
| `eval_set_holdout.json` | Holdout split. Score twice only (baseline, final). |
| `FROZEN.md` | The freeze manifest: versions, hashes, threshold, limits. |
| `PASS_CRITERIA.md` | Pass criteria from the bar (PROPOSED). |
| `SWEEP.md` | E5 threshold sweep results (dev only). |
| `BASELINE.md` | E6 baseline: as-built code on dev + holdout, noise floor. |
| `near_miss_probe.md` | Measured bge-m3 similarities for the NM-A/NM-C probes. |
| `sweep_scoped_*.json` / `.jsonl` | Sweep runs (8 configs). |
| `baseline_*.json` / `.jsonl` | Baseline runs (10 runs). |
| `validation_asbuilt_t*.json` | Scorer-validation runs (stale-ttl24 rule). |
| `run_sweep.sh`, `run_baseline.sh` | The exact commands that produced the sweep and baseline. |

## The holdout rule (read this before running anything)

Holdout is scored twice only: baseline (done, see BASELINE.md)
and final validation. **Holdout failures are NEVER read during
iteration.** Do not open `eval_set_holdout.json` to look at what
failed, do not add a holdout failure's text to the denylist or
the seed, do not tune the threshold on holdout. Breaking this
rule burns the holdout and requires a refill from fresh traffic.

## How to run

```bash
cd [spark-home]/team/gateway-shadow-trial
# Score a code change on DEV (the only split you iterate on):
python3 eval/score.py --workload eval/v3/eval_set_dev.json \
    --variant scoped --threshold 0.98 --seed-mode with-seed \
    --out eval/v3/run_dev_scoped.json --detail eval/v3/run_dev_scoped.jsonl
# Compare against the baseline in BASELINE.md, paired, with CIs.
# Validate the winner ONCE on holdout, at the end, same command
# with eval_set_holdout.json.
```

## What the frozen case already decided

- **E5 sweep (dev, scoped):** no threshold in 0.90-0.98 with
  normalisation on/off clears zero-unsafe AND 10% safe-hit rate.
  Best: 0.90 + normalisation, 1 unsafe, 0.0946. The single unsafe
  hit (NM-A alert-3b vs real alert 1, sim 0.9976) is
  threshold-independent. Mechanism fails per the pre-registered
  rule; the next step is code (C1-C6), not a lower threshold.
- **E6 baseline:** as-built fails SAFETY on dev (3 unsafe) and on
  holdout weighted (68 unsafe per 113 weighted requests).
  Scoped fails SAFETY on dev (1 unsafe) and VALUE everywhere.
  Cold embed 3028.7 ms (fifth measurement, range 3.0-4.5 s).
- **Noise floor:** unsafe count stable under shuffling (3 dev, 0
  holdout), but the identity of one dev unsafe hit changes with
  order. Claims about counts are stable; claims about a specific
  unsafe prompt must be checked in both orders.

## E2 instrumentation (spec only)

- `eval/TRACE_SCHEMA.md` - the trace fields scorer v3.0 records.
- `eval/dispatcher-instrumentation-spec.md` - the patch that
  would add timestamps, config version, and cache fields to the
  live dispatcher audit log. SPEC ONLY, NOT APPLIED. Do not apply
  it from eval work.
