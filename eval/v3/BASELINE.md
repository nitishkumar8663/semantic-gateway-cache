# E6 baseline - as-built gateway code on v3 (frozen)

**Date:** 23 Nov 2026. **Scorer:** v3.0. **Threshold:** 0.98 (frozen;
see FROZEN.md - frozen as the baseline setting, not as a passing
setting). **Normalisation:** off (as-built behaviour). **Shadow
only.** The baseline is the reference every code change (C1-C6) is
compared against.

## Runs

| Run | Split | Variant | Seed | Hits | Safe | Unsafe | Weighted unsafe | Full-route safe rate | Recall | FP (gw) | Never stored |
|---|---|---|---|---|---|---|---|---|---|---|---|
| dev_asbuilt_seed | dev | asbuilt | with-seed | 18 | 15 | 3 | 4 | 0.2027 | - | - | 41 |
| dev_asbuilt_empty | dev | asbuilt | empty | 10 | 7 | 3 | 4 | 0.0946 | - | - | 41 |
| holdout_asbuilt_seed | holdout | asbuilt | with-seed | 1 | 1 | 0 | 68 | 0.0417 | - | - | 21 |
| holdout_asbuilt_empty | holdout | asbuilt | empty | 0 | 0 | 0 | 68 | 0.0 | - | - | 21 |
| dev_scoped_seed | dev | scoped | with-seed | 4 | 3 | 1 | 1 | 0.0405 | 0.7097 | 0.0167 | 8 |
| dev_scoped_empty | dev | scoped | empty | 3 | 2 | 1 | 1 | 0.0270 | 0.7097 | 0.0167 | 8 |
| holdout_scoped_seed | holdout | scoped | with-seed | 0 | 0 | 0 | 0 | 0.0 | 1.0 | 0.0 | 0 |
| holdout_scoped_empty | holdout | scoped | empty | 0 | 0 | 0 | 0 | 0.0 | 1.0 | 0.0 | 0 |

Noise floor (same runs, `--shuffle-seed 7`):

| Run | Hits | Safe | Unsafe | Same unsafe set as file order? |
|---|---|---|---|---|
| dev_asbuilt_seed_shuf7 | 18 | 15 | 3 | NO (see below) |
| holdout_asbuilt_seed_shuf7 | 1 | 1 | 0 | yes |

Scorer-validation runs (not part of the frozen baseline; they
exercise the new stale-ttl24 rule, E1a):

| Run | Hits | Safe | Unsafe | of which stale-ttl24 |
|---|---|---|---|---|
| asbuilt dev with-seed, threshold 0.90 | 40 | 23 | 17 | 3 |
| asbuilt dev with-seed, threshold 0.95 | 26 | 17 | 9 | 2 |

## Findings

**1. As-built fails SAFETY on dev (3 unsafe, all NM-A probes).**
The 3 unsafe hits are the near-miss probes doing their job:
alert-3b (0.9976 vs alert 1), alert-3c (0.9915 vs alert 1), and
"is the door locked?" (0.9873 vs "is the door locked"). All three
are `never` items served from the cache. The same 3 unsafe hits
appear with an empty store, so they are not seed artefacts.

**2. As-built fails SAFETY on holdout in weighted terms (68 unsafe).**
Unweighted holdout unsafe is 0, which hides the danger. Weighted
by real traffic, 68 of 113 weighted requests (60.2%) would get a
stale action/time answer: "unlock a door" (43 live rows) is
stored on first occurrence and its 42 repeats hit it; "lock the
door" (14 rows) and "what's the temperature" (14 rows) add 13
each. This is store poisoning quantified, and it is why E1d
(weighted reporting) exists. The unweighted holdout number (0
unsafe) must never be quoted without the weighted number (68).

**3. Value is seed-dominated and thin without the seed.**
Dev asbuilt with-seed: 15 safe hits, of which 13 matched seed
entries. Non-seed safe hits: 2/110 = 1.8%. Empty-store: 7 safe
hits (all non-seed, by definition), full-route safe rate 0.0946.
Holdout asbuilt with-seed: 1 safe hit, and it matched a seed
entry ("Explain photosynthesis in one sentence.", sim 1.0).
Empty-store holdout: 0 hits. Cold start is the honest value
number, and it is 0-7 safe hits, not 15.

**4. Scoped is safe on holdout and saves nothing anywhere.**
Holdout scoped: 0 hits, 0 unsafe, recall 1.0, FP 0.0, 0 never
items stored - in both seed modes. It is safe because the
denylist catches every reached never item on holdout and the TTL
expires the rest. It saves nothing because the TTL empties the
store between waves (see the SWEEP.md caveat). Dev scoped: 1
unsafe (the alert pair), recall 0.7097, FP (gateway) 0.0167.

**5. Noise floor: counts stable, identity not.**
Re-running dev asbuilt with-seed in shuffled order gives the same
counts (18 hits, 15 safe, 3 unsafe) but a different third unsafe
hit: file order has "is the door locked?" (NM-A), shuffled order
has "is the door locked" (R-T4-1) instead. The two alerts are the
same in both orders. Holdout is identical in both orders (1 safe,
0 unsafe). So the unsafe COUNT is robust to order, but WHICH
prompt is unsafe is order-dependent for one of the three. Any
claim about a specific unsafe prompt must be checked in both
orders; claims about the count are stable.

**6. The stale-ttl24 rule works (validation runs).**
Asbuilt at 0.90: 3 stale-ttl24 unsafe hits ("what is my balcony
plants plan", 85.8h old; "Hi", 109.3h; "thank you", 114.2h). At
0.95: 2 stale hits. At 0.98: 0, because no ttl24 paraphrase
reaches 0.98. The rule is implemented and exercised; it bites
exactly where the sweep predicted (lower thresholds trade safety
for paraphrase hits).

**7. Cold embed, fifth measurement: 3028.7 ms.**
Measured on the first scorer run of the day (regression asbuilt).
Range across all trials: 3.0-4.5 s. Warm median total check time
in these runs: ~9.3 ms. The cold cost is a COST-gate fact, not a
scorer artefact.

## Wilson 95% CIs (headline rates)

| Run | Hit rate | Unsafe rate |
|---|---|---|
| dev asbuilt, with-seed | 0.1636 [0.1061, 0.2439] | 0.0273 [0.0093, 0.0771] |
| dev asbuilt, empty | 0.0909 [0.0501, 0.1593] | 0.0273 [0.0093, 0.0771] |
| holdout asbuilt, with-seed | 0.0227 [0.0040, 0.1181] | 0.0 [0.0, 0.0803] |
| holdout asbuilt, empty | 0.0 [0.0, 0.0803] | 0.0 [0.0, 0.0803] |
| dev scoped, with-seed | 0.0364 [0.0142, 0.0898] | 0.0091 [0.0016, 0.0497] |
| holdout scoped, with-seed | 0.0 [0.0, 0.0803] | 0.0 [0.0, 0.0803] |

## Value at real volume (sensitivity)

Full-route share of live traffic: 33.6% (40/119 live audit rows).
Non-seed safe-hit rate on full-route traffic, scoped, with-seed:
0.98 no-norm 2/74 = 2.7%; 0.90 with normalisation 6/74 = 8.1%
(sweep best). Saved full-model generations per day:

| Requests/day | 2.7% rate | 8.1% rate |
|---|---|---|
| 6 | 0.05 | 0.16 |
| 20 | 0.18 | 0.54 |
| 40 | 0.37 | 1.10 |
| 86 | 0.78 | 2.34 |

The bar's VALUE threshold is 10% of full-route traffic (1.34
saved/day at 40/day). Neither rate clears it. Volume is an
assumption ("~40/day", no dated source) until E2 instrumentation
lands; the rate is volume-independent and is the number that
matters.

## Baseline verdict (against PASS_CRITERIA.md, proposed)

- SAFETY: FAIL (asbuilt 3 unsafe dev, 68 weighted unsafe
  holdout; scoped 1 unsafe dev).
- VALUE: FAIL (best non-seed rate 8.1% < 10%; 0 on holdout).
- DATA: WEAK (holdout has 17 real prompts; verdict rests on dev
  + holdout together).
- COST: not measured in this baseline (latency/memory are code
  properties, measured in the C5/C6 trials). Cold embed 3.0 s is
  recorded as the cost to beat.

**Overall: NO-GO as built; CONDITIONAL GO scoped is not earned
on this baseline either** (scoped fails SAFETY on dev and VALUE
everywhere). The code fixes C1-C6 are judged against this
baseline: each must move its metric without regressing the others,
gated on dev, validated once on holdout.
