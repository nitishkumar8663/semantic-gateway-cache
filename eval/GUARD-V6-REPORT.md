# Guard v2.4 (guard v2.0) - report

**Semantic gateway, round 1 of the loop Nitish ordered
23 Nov 2026 ("execute in a loop till it is a go").** v2.4-guard is
built, dev-validated, deployed to shadow on :18795, rollback-tested,
and verified live. The v6 candidate eval set is a separate
deliverable (`[workspace]/v6/eval_set_v6.json`, see
`[workspace]/v6/V6-REPORT.md`); it is a candidate only, not scored.

## What changed (v2.4-guard vs v2.3-guard)

A genuinely stronger MECHANISM, not a patch for specific v5 holdout
items. The v5 verdict (NO-GO) showed guard v1.0 catches easy never
items but misses hard ones that rely on Rule C alone (imperative
verbs not in Rule A's class; question forms not in Rule B). v2.4
widens each layer so the hard forms are caught by form rules
(precise, FP 0.0 on dev) instead of by the embedding margin.

| Layer | Change | Dev effect |
|---|---|---|
| Denylist v1.3 | Bare `\btemperature\b` narrowed to live-temperature question forms (`what('s\| is) the temperature`, `temperature (outside\|now\|today\|here\|in)`, `how (hot\|cold) is it`, `temp`). A pattern-class fix, not a per-item patch. | FP 0.105 -> 0.0 on v5 dev; the 4 stable boil/freeze questions are no longer blocked; live-temp never items still caught (4/98 never vs 3/98 before). |
| Rule A v2 | Verb class expanded: boil, preheat, play, boost, brew, cook, bake, wash, dry, clean, vacuum, mop, charge, iron, sweep, dust. Plus a `make <beneficiary> <article>` form ("make me a coffee") with an article constraint so "make me laugh" (chatter) and "make a video" (creative) do not match. "make" alone stays out of the verb class. | Rule A recall 0.487 -> 0.590 on regex-missed dev never (FP 0.0). |
| Rule B v2 | Live entities expanded (tumble dryer, dryer, coffee machine, robot vacuum, vacuum, sprinklers, hose); state words expanded (finished, done, ready); interrogatives expanded (has, have); three new general forms: stock ("are we out of", "do we have any"), delivery/location ("where is my/our"), daily-count ("how many ... have I done today"). | Rule B recall 0.231 -> 0.333 on regex-missed dev never (FP 0.0). A+B v2 combined: 0.923 (36/39), FP 0.0. |
| Rule C | The "what is the temperature outside" action prototype REMOVED (it caused the Rule C FP on temperature factual questions: freeze margins +0.23). Live-temp never items are caught by the regex, so Rule C does not need it. Margin stays 0.20. Action prototypes 34 -> 33; safe prototypes stay 17. | Freeze margins +0.23 -> +0.07; boil +0.13 -> +0.07. All four fall well below 0.20. |

## Rejected direction: nearest-centroid classifier

Tried and REJECTED. A small embedding-based classifier trained on
dev labels (nearest centroid per class, margin threshold). In-sample
at margin 0.00: recall 0.969, FP 0.171. Leave-one-family-out CV at
0.00: recall 0.969, FP 0.229; at 0.05: recall 0.714, FP 0.114.
Separation is WORSE than the prototype margin (centroid CV medians
+0.086 never vs -0.062 safe; prototype margin medians +0.212 vs
-0.114). Do not adopt it. Details:
`guard-v6-build/classifier_experiment.py`.

## Dev results (v3 + v4 + v5 dev, 239 prompts)

Driver: `drive_gateway_v3.py`, `gateway_v6.py`, threshold 0.90 /
factual 0.85 / generative 0.85, TTL 24h / 168h, seed store
`cache_store_backup_20261123.json` (16 entries). Temp stores for
all runs; the live store was never poisoned. Run files:
`eval/v3/v24_dev_{seed,empty}.json`, `eval/v4/v24_dev_{seed,empty}.json`,
`eval/v5/v24_dev_{seed,empty}.json` (plus `.jsonl` detail).

| Metric | v3 seed | v3 empty | v4 seed | v4 empty | v5 seed | v5 empty | Bar |
|---|---|---|---|---|---|---|---|
| Denylist recall | 1.0 (31/31) | 1.0 (31/31) | 1.0 (46/46) | 1.0 (46/46) | 1.0 (21/21) | 1.0 (21/21) | 1.0 |
| Must-block | 5/5 | 5/5 | 4/4 | 4/4 | 2/2 | 2/2 | all |
| Never stored | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Unsafe hits | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| FP (gateway) | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Non-seed safe rate | 0.2432 | 0.2568 | 0.0429 | 0.0571 | 0.2712 | 0.2712 | >= 0.10 |
| Median total check | 16.6 ms | 16.5 ms | 14.3 ms | 13.6 ms | 16.6 ms | 13.9 ms | - |
| p95 total check | 30.2 ms | 21.5 ms | 25.1 ms | 22.9 ms | 27.9 ms | 18.9 ms | <= 50 ms |

Combined dev (239 prompts): recall **1.000 (98/98)**, must-block
**11/11**, never stored **0**, unsafe **0**, FP **0.0** (driver
definition; the 3 v3 bus bodies blocked by the pre-existing regex
message/send/unlock patterns are agent-task items, excluded from
the driver's "gateway traffic" FP and a v3 labelling artefact: v4
labels bus bodies "never", so under the current convention they are
not FPs at all). v4+v5 dev FP is 0.0 by any definition.

Comparison with v2.3-guard on dev: recall 0.929 -> 1.000, FP 0.067
-> 0.000 (driver) / 0.029 (counting the v3 bus bodies). The v5 dev
temperature FP (0.1053) is fixed. The v4 dev value rate (0.043 /
0.057) is unchanged from v2.3 and below the 0.10 bar, but that is a
property of the v4 dev set (few paraphrase repeats), not the guard;
the value bar applies to the holdout.

Cost: p95 check 18.9-30.2 ms across all 6 runs, all under the
50 ms budget. (Max per-request ~436-464 ms is a single cold-start
outlier, the first embed of each run warming bge-m3; p95 is the
robust metric.)

## Unit tests

`test_gateway_v6.py`, run on the Spark from the eval dir:
**22 tests, all pass** (3.6 s). Extends the v5 suite (18 tests) with:
a denylist v1.3 temperature class (boil/freeze not blocked,
live-temp still blocked), Rule A v2 home-action verbs + make-for
(including the "make me laugh" / "make a video" non-matches), Rule B
v2 live-state forms (stock, where-is-mine, daily-count, tumble
dryer / coffee machine / vacuum, finished/done/ready, has/have),
and the v3+v4+v5 dev form-rule assertions (36 caught, 0 FP;
regex+form 95/98, the 3 remaining are Rule C's). The live Rule C
test (`test_real_margin_separates_dev`, real bge-m3) passes: the
full guard blocks every dev never item and no dev safe item.

## Deploy (shadow :18795)

- **Deployed 23 Nov 2026 22:30:46 UTC** via `eval/deploy_gateway_v6.sh`
  (mirrors the v2.3 deploy pattern). Backed up v2.3-guard code +
  config (`gateway_v5_guard_20261123.py`,
  `config_v2_3_guard_20261123.json`); store kept live (30 entries,
  no snapshot; v2.4 adds no entry fields, so the store is
  forward/backward compatible). Config unchanged: threshold 0.90,
  upstream stub, TTL 24h/168h, factual 0.85, generative 0.85,
  generative_ttl true, frame_strip false, legacy_backfill false,
  guard_enabled true, guard_margin 0.20.
- **Live /health (verified 22:30 UTC):**
  `{"ok": true, "service": "semantic-gateway-cache", "gateway_version":
  "v2.4-guard", "threshold": 0.9, "threshold_factual": 0.85,
  "threshold_generative": 0.85, "frame_strip_factual": false,
  "legacy_backfill": false, "generative_ttl": true, "denylist":
  "v1.3", "guard": "v2.0", "guard_enabled": true, "guard_margin":
  0.2, "guard_action_prototypes": 33, "guard_safe_prototypes": 17,
  "ttl_hours": 24.0, "ttl_stable_hours": 168.0, "normalise": true,
  "exact_match": true, "keep_alive": "24h", "embedder_warmed": true}`
- **Live probes (verified):** "Play the radio in the bedroom." ->
  blocked `denylist:guard-rule-a:play`, cache_status
  blocked-denylist, 0 embed calls (blocked pre-embed). "At what
  temperature does water boil?" -> NOT blocked, miss-stored
  (STUB-OUTPUT), blocked_by null. The probe's stored entry was
  removed afterwards and the store restored to 30 entries.
- **Rollback tested:** `rollback_gateway_v5.sh` (in the gateway project dir)
  restored v2.3-guard (verified /health: v2.3-guard, denylist v1.2,
  guard v1.0, 34 action prototypes), then v2.4-guard was re-deployed
  and re-verified live. Deeper fallbacks intact: rollback_gateway_v4.sh
  (v2.2-enh), rollback_gateway_v3.sh (v2.1-enh), rollback_gateway_v2.sh
  (v2.0-c1c6), rollback_gateway.sh (as-built).

## Known limits

- **Rule C is the thin layer.** On dev, 3 never items are caught
  only by Rule C (the v4 bus body, "make it warmer in here",
  "Show me the front door camera."). The bus body relies on a
  margin of +0.236, only 0.036 above the 0.20 threshold. If a
  holdout item lands in the same band, Rule C is the deciding
  factor and it is the least precise layer.
- **The v6 candidate set has 8 form-rule misses** (never items the
  form layers do not catch; see `[workspace]/v6/V6-REPORT.md`).
  They are the same failure modes Rule C must cover: novel verbs
  (run, mow), perception with no state word (door camera, alarm
  armed), live events (doorbell), non-covered time windows (last
  night), weather forms (raining), location with "where are".
- **Dev is not holdout.** v2.4 reaches recall 1.0 on dev, but dev
  is 239 prompts the mechanism was designed against. The v6
  holdout is the generalisation test. The v5 holdout failures
  (preheat, play jazz) were NOT the tuning target; the mechanism
  was built from v5 DEV failures and general forms only.
- **Value on v4 dev stays low (0.043/0.057).** A property of the
  v4 dev set, not the guard. If the v6 holdout value is also low,
  the cause is likely the set's paraphrase structure, not the
  guard (the guard does not affect value except through FP).
- **No new real traffic.** The v6 set is blind-writer fresh, not
  real traffic (audit log and shadow replays are thin). The DATA
  gate stays marginal.

## How to iterate (for the next round)

The guard is modular: each layer is a separate function with its
own unit tests, so a next round can strengthen one layer without
touching the others.

- **Denylist** (`DENYLIST`, `denied()`): regex patterns, layer 1.
  Add a pattern only for a general class (a verb, a form, a
  structure), never for a single item. Narrow a pattern when it
  causes an FP (as v1.3 did for temperature).
- **Rule A** (`_ACTION_VERBS`, `_RULE_A_RE`, `_RULE_A_MAKE_RE`,
  `guard_rule_a()`): the imperative verb class. Add verbs that
  head actions; keep information/creative verbs out. The make-for
  form is the template for a constrained construction (verb +
  beneficiary + article).
- **Rule B** (`_LIVE_ENTITIES`, `_STATE_WORDS`, `_RULE_B_*_RE`,
  `guard_rule_b()`): live-state question forms. Add entities,
  state words, interrogatives, or whole new forms (stock,
  where-is-mine, daily-count are the v2.4 templates).
- **Rule C** (`ACTION_PROTOTYPES`, `SAFE_PROTOTYPES`,
  `guard_margin_check()`): the embedding margin. Prototypes are
  general canonical phrases; the source of truth is
  `eval/prototypes.json` + `eval/safe_prototypes.json`, and the
  unit tests assert the module constants match those files. Drop a
  prototype when it causes an FP (as v2.4 did for temperature).
- **Do NOT** lower the global margin below 0.20 (FP rises steeply:
  0.03 at 0.10, 0.16 at 0.00 on dev) and do NOT add item-specific
  prototypes (that is patching, not generalising).

## Next round's most promising lever (if v6 still fails)

**A per-category Rule C margin.** The margin that separates
never/safe differs by prompt type: short imperatives cluster near
0 (the bus body +0.18, "make it warmer" +0.05, "steps today"
+0.004), while long factual questions sit near -0.1. A single
global 0.20 threshold is too blunt for the short-imperative band
and too lax for the factual band. The lever: compute the margin
separately per prompt class (imperative / question / statement,
from the form rules' own classification) and set a lower margin
for the imperative class (e.g. 0.10) and keep 0.20 for questions.
Validate on dev first: it must keep FP 0.0 on v3+v4+v5 dev (the
imperative band is where the safe chatter lives, so the FP risk
is real). The second lever, if per-category margin does not
separate enough, is a second embedding model for the guard only
(a model trained for intent, not retrieval), but that adds a
dependency and load time, so it is the fallback, not the first
move. Do NOT pre-build a v7; this is a direction for the next
round's parent to authorise.

## Files (md5-verified VM vs Spark)

| File | md5 |
|---|---|
| `guard-v6-build/gateway_v6.py` = `eval/gateway_v6.py` = live `semantic_gateway/gateway.py` | 09e960b243b14045ba3cd7529bf18cf2 |
| `guard-v6-build/test_gateway_v6.py` = `eval/test_gateway_v6.py` | 34963fce85975e9fadff9fef584a16df |
| `guard-v6-build/prototypes.json` = `eval/prototypes.json` | c86f4bca0b30a463ab739728a6a17e50 |
| `guard-v6-build/deploy_gateway_v6.sh` = `eval/deploy_gateway_v6.sh` | 003ebaf18ccc78d2557a48fe131c672a |
| `v6/eval_set_v6.json` = `eval/v6/eval_set_v6.json` | 2baf1474fc1560971b34e45536989242 |
| `v6/V6-REPORT.md` | 8bf2be19cd3668fb18dbfbd5736e6b52 |

Audit trail (VM `[workspace]/guard-v6-build/`, Spark mirror in
`eval/`): `probe_v6.py`, `probe_v6.json`, `probe_v6_embs.json`,
`probe_v6_combined.json`, `classifier_experiment.py`,
`validate_v24_rules.py`, `test_rulec_prototype.py`,
`combined_validate.py`, `p95.py`, `collision_check_v6.py`,
`collisions_v6.json`, `build_v6_set.py`, `eval_set_v6_draft.json`,
`v6_form_miss_check.py`, `finalise_v6_set.py`. Dev run JSONs +
detail: `eval/v3/v24_dev_{seed,empty}.json{,l}`,
`eval/v4/v24_dev_{seed,empty}.json{,l}`,
`eval/v5/v24_dev_{seed,empty}.json{,l}`. Rollback:
`rollback_gateway_v5.sh` (restores v2.3-guard). The `/tmp` probe
scripts on both VM and Spark were removed after use (neatness).
