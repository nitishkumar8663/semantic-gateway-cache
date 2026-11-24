# FROZEN manifest - eval case v3 (semantic gateway)

**Frozen:** 23 Nov 2026. **Status:** frozen. Nothing below changes
without a version bump (v3.1, v4, ...) and a new freeze entry.
"Settled" is a version, not a permanent state: fresh traffic must
refill the holdout on a cadence (see the EDD assessment), and any
change to the set, the scorer, the threshold, or the pass criteria
bumps the version.

## Freeze entry v3.1 - threshold 0.98 to 0.90 (23 Nov 2026, C4)

- **What changed:** the frozen threshold only, 0.98 to **0.90**.
  The v3 dataset (154 prompts, 47 families), the scorer v3.0, and
  the pass criteria are unchanged; no data file was modified.
- **Why:** the C4 sweep on the fixed gateway (C1+C2+C3, dev only,
  0.90/0.93/0.95/0.98, with-seed and empty-store) found zero unsafe
  at every threshold, and 0.90 gives the best safe-hit rate
  (non-seed full-route 0.0811, 6/74; seed-inclusive 0.0946, 7/74).
  No threshold meets the pre-registered VALUE bar (0.10), so no
  threshold "passes"; 0.90 is the deployed setting because it
  maximises safe hits at zero unsafe on dev. The threshold is a
  mechanism accompaniment, not the fix by itself: safety on dev
  comes from denylist v1.2 + TTL + route scoping, which hold at
  every threshold swept.
- **Driver:** `eval/drive_gateway.py v1.0` (replays the frozen
  workload through the real gateway code; the frozen scorer v3.0
  cannot judge denylist v1.2). C4 run summaries:
  `eval/v3/c4_t090_dev_seed.json`, `c4_t093_dev_seed.json`,
  `c4_t095_dev_seed.json`, `c4_t098_dev_seed.json` (+ `_empty`).
- **Holdout validation for v3.1 is still pending** at the time of
  this entry; it runs at threshold 0.90 on the final code.

## Dataset v3

| Item | Value |
|---|---|
| Version | v3 |
| Built | 2026-11-23, `eval/build_eval_set_v3.py` |
| Source | v2 (144 prompts) + NM-A/NM-C near-miss families (10 prompts) |
| Total | 154 prompts, 47 families, 63 real-sourced |
| Dev | 110 prompts, 33 families (`eval/v3/eval_set_dev.json`) |
| Holdout | 44 prompts, 14 families (`eval/v3/eval_set_holdout.json`) |
| Split | By family, stratified by category, deterministic seed 20261123. ~30% of families in holdout. |
| Timeline | Two-wave synthetic timeline, anchored to the real seed creation time (22 Nov 05:28 UTC). Wave 1 (first variant of each family) over day 0 (23 Nov); wave 2 (remaining variants) over days 3-6. Every prompt carries `ts`. |
| Seed duplicates | 8 prompts word-for-word identical to seed entries, labelled `seed_duplicate` |
| Must-block | 5 prompts flagged `must_block` (the denylist escapes) |
| Near-miss probes | NM-A (8) and NM-C (2); similarities measured with bge-m3, recorded in `eval/v3/near_miss_probe.md` |

### File hashes (sha256)

| File | sha256 |
|---|---|
| `eval/v3/eval_set.json` | ddf6bd5709c9e391a4957c87fee6e596b7265ae63ac58139ea23fd4b381b8f09 |
| `eval/v3/eval_set_dev.json` | ea6358b88725fbc05ac563258c10862a249786d4160fdb8f76a05ff8562ac2f9 |
| `eval/v3/eval_set_holdout.json` | 0f8a014248fcaa6c14628a0b8d967cc9f05edc264038dd49704e185c2bdd620b |

### Forced to dev (documented exceptions to the random split)

- R-PA, R-A3, INJ: the must-block families (the named failure modes being fixed).
- NM-A, NM-C: the near-miss probes are sweep inputs (dev only).
- R-GR: only greeting family. BUS: agent-task guard.

Holdout families: F5, G3, R-A1, R-A2, R-A7, R-C1, R-C3, R-F2, R-G2,
R-P4, R-P6, R-Q2, R-T1, R-T6.

### Holdout rule

Holdout is scored twice only: baseline (E6) and final validation.
Holdout failures are NEVER read during iteration. A holdout
failure's text is never added to the denylist or the seed. Breaking
this rule burns the holdout and requires a refill from fresh
traffic.

## Scorer v3.0

| Item | Value |
|---|---|
| File | `eval/score.py` (sha256 51c036b1dee3b1b15276c79b4437c0fe7a9be2518d6962630d4131a078d62f43) |
| Version | v3.0 (previous: v2, archived as `eval/score_v2.py`) |
| Denylist | v1.1, unchanged (the denylist is part of the system under test) |
| Changes vs v2 | Stale ttl24 hits count unsafe; family_recall fixed (cannot exceed 1.0); denylist FP split by population (gateway vs BUS); traffic-weighted reporting; seed entries use real `created_at` timestamps; trace fields on every detail row; must-block reporting; never-items-stored metric; `--threshold`, `--normalise`, `--seed-mode`, `--shuffle-seed` flags; Wilson 95% CIs; lookup norm precomputation |
| Regression check | Scorer v3.0 on v2 reproduces v2 exactly (asbuilt 17 hits / 1 unsafe; scoped 16 hits / 0 unsafe; weighted 112/70 asbuilt, 29/0 scoped; recall 0.8276; FP 0.046) |

## Threshold (frozen)

**0.90** - set by the C4 sweep on the fixed gateway (v3.1, 23 Nov
2026). Was 0.98 (the shipped value) under v3.0.

The E5 sweep (dev only, scoped, 0.90/0.93/0.95/0.98 x
normalisation off/on) found NO threshold satisfying the
pre-registered rule (zero unsafe AND safe-hit rate at or above
10% of full-route traffic). Best config: 0.90 with normalisation,
1 unsafe hit, 0.0946 safe-hit rate. The single unsafe hit (NM-A
alert-3b vs real alert 1, sim 0.9976) is threshold-independent.
**The mechanism fails per the pre-registered rule.** 0.98 is
frozen as the baseline setting, not as a passing setting. See
`eval/v3/SWEEP.md`. Any future threshold change requires a
version bump and a re-freeze.

The C4 sweep (fixed code C1+C2+C3, dev only, same four
thresholds, with-seed and empty-store) found zero unsafe at every
threshold and the best non-seed full-route safe-hit rate at 0.90
(0.0811, 6/74). Still below the 0.10 bar, so no threshold passes;
0.90 is the deployed setting. See the v3.1 freeze entry above.

## Pass criteria

`eval/v3/PASS_CRITERIA.md`. **Status: AGREED 23 Nov 2026 by Nitish in
writing (chat: "Agree the pass criteria, start C1-C6"). No numbers
changed, so no version bump.** Code changes (C1-C6) are judged against
them. If he changes any number, this manifest is updated and the
version bumped.

## Baseline

`eval/v3/BASELINE.md` (E6): as-built code on dev + holdout, with
seed and empty store, plus the noise floor (shuffled-order re-run).
The baseline is the reference every code change is compared
against.

## Known limits of this frozen case (stated, not hidden)

- Real data is thin: 63 real-sourced prompts, 24 distinct live
  texts; most live rows are a test battery. DATA gate is WEAK on
  holdout alone (17 real prompts); the verdict rests on dev +
  holdout together and must say so.
- The workload timeline is synthetic (two-wave), anchored to a
  real seed time. TTL behaviour is measured under that timeline;
  continuous production traffic would refresh entries and give a
  higher safe-hit rate. The safety findings are not affected by
  this caveat.
- Volume ("~40 requests/day") has no dated source. The VALUE
  threshold is expressed as a rate (10% of full-route traffic)
  so it does not depend on the volume number; saved/day is
  reported as a sensitivity table until E2 instrumentation lands.
- The audit log has no timestamps and no route config version;
  the patch is specified in
  `eval/dispatcher-instrumentation-spec.md` (spec only, not
  applied).

## Public split note

This is the public copy of the frozen v3 set. It differs from the private frozen original:

- Prompts v3-145 and v3-146 in the dev set are redacted: their text is replaced with a redaction note. One held personal financial detail, one held home-security detail. Their labels are kept.
- Rewordings applied to the public copy: em dashes removed, an unlock example reworded, internal project references removed.
- The reported scores were measured on the private frozen originals.

Original (private) md5s:

- `eval_set.json`: 05815b5bc97e57419dc87316d0cfd6fb
- `eval_set_dev.json`: c88e55453a2fbba83fb1b30b568d7514
- `eval_set_holdout.json`: 281f12491ac6c2166de17d10360d207e

Public copy md5s (at the time this note was written; they change if the public copy is re-cleaned):

- `eval_set.json`: 332531b5fe68a1945470e838e98cbdaa
- `eval_set_dev.json`: 028240e18d86a4a2c5d1ea517be2faa5
- `eval_set_holdout.json`: f8303eef863bd7c65601b8ec4e72603c
