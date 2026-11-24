# Guard v2.5 (guard v2.1) - report

**Semantic gateway, round 2 of the loop Nitish ordered
23 Nov 2026 ("execute in a loop till it is a go").** v2.5-guard is
built, dev-validated on all four dev sets, deployed to shadow on
:18795, rollback-tested, and verified live. The v6 holdout was NOT
read, scored, or used for tuning in this round (it is retired); the
only tuning signal was the four DEV sets (295 prompts) and the v6
dev failures named in the verdict. The v7 candidate eval set is a
separate deliverable for the parent to authorise; it is not built
here. No v8 was pre-built.

## What changed (v2.5-guard vs v2.4-guard)

A genuinely stronger MECHANISM, not a patch for specific items.
Each v6 dev failure is fixed by a general pattern class:

| Layer | Change | Dev effect |
|---|---|---|
| Denylist v1.4 | The bare `\bmessage\b` pattern is narrowed to messaging-action forms only: a send/text/forward/share/pass/leave/drop/deliver/reply verb within 40 chars before "message", "message to/for <recipient>" (12-char window), or "message <recipient>" as a verb (maa/mama/papa/nimu/reema/me/him/her/them/us). | The v6 dev FP ("finds a message in a bottle") is unblocked; messaging actions ("send a message to mum", "message Maa ...") are still blocked. One v4 dev bus body whose ONLY blocker was `\bmessage\b` (v4-015, "the plain message") is now caught by the Rule C statement margin instead (see below). |
| Rule A v3 | Yard-work verbs join the class (mow, rake, prune, weed - "trim" stays OUT: it also heads video edits) and the messaging verb "message". Plus a question guard: Rule A does not fire when the prompt contains a wh-word (what/who/whom/whose/which/where/when/why/how) or the raw text ends with "?" (checked on the raw text: normalisation strips "?"). | "Mow the lawn this afternoon." now blocked by Rule A (was Rule C's miss at margin +0.0084). "Water boils at what temperature ...?" and "Count the continents ..., how many are there?" no longer blocked. "Water the plants ..." (a real action) still blocked. |
| Rule B v3 | Where-form takes "are" as well as "is" ("where are my car keys"); daily-count form takes the wider time windows "last night / last week / this morning / last month / this month / this year / last year" ("how many hours did I sleep last night"); new weather-now form ("is it raining / snowing"). | "Where are my car keys?", "How many hours did I sleep last night?", "Is it raining outside right now?" now blocked by form rules. |
| Rule C | PER-CATEGORY margin (guard v2.1): imperative 0.20, question 0.20, statement 0.10. The class comes from the prompt's own form (wh-word / aux-leading / trailing "?" = question; first word a generic imperative verb = imperative; else statement). Prototypes UNCHANGED (33 action + 17 safe). | The statement margin catches the two statement-form agent-task bodies that reach Rule C (v4-015 at +0.1093, the self-improvement body at +0.2360). |

## The per-category probe: the documented guess was refuted in its imperative form

Before building, a probe (`probe_v7.py`, real bge-m3, all 295 dev
prompts) measured sim_action / sim_safe / margin per prompt class:

- Imperative margin 0.10 would FP on "write a python function to
  sort a list" (+0.1070). The never imperatives that reach Rule C
  sit at +0.21/+0.27 (already caught at 0.20) or +0.0084 ("mow the
  lawn", uncatchable by any margin that keeps FP 0.0: safe
  imperatives reach +0.107). **Lowering the imperative margin buys
  nothing and costs an FP. It was NOT adopted.**
- Question margin: safe questions reach +0.1202 ("when does the
  tube close on sundays"); the question never items are form-fixed
  or already caught at 0.20. **Question margin stays 0.20.**
- Statement: safe statements max +0.0889; statement-form
  agent-task bodies sit at +0.1093/+0.2360. **Statement margin
  0.10 separates with FP 0.0 on dev.** This is the only class
  where the margin moves, and it is load-bearing for exactly one
  dev item (v4-015). Its gap to the highest safe statement is
  0.02 - thin, and named below as the known limit.
- Candidate agent-task prototypes were tried and REJECTED
  (`probe_v7b.py`): adding "install the plugin and run the live
  test" and "dispatch the message to the agent" moved the v4-015
  margin by exactly 0.0000 (sim_action unchanged at 0.5865).
  No prototype change is justified.

## Dev results (v3 + v4 + v5 + v6 dev, 295 prompts)

Driver: `drive_gateway_v3.py`, `gateway_v7.py`, threshold 0.90 /
factual 0.85 / generative 0.85, TTL 24h / 168h, seed store
`cache_store_backup_20261123.json` (16 entries, same as the v2.4
runs). Temp stores for all runs; the live store was never
poisoned. Run files: `eval/v3/v25_dev_{seed,empty}.json{,l}`,
`eval/v4/v25_dev_{seed,empty}.json{,l}`,
`eval/v5/v25_dev_{seed,empty}.json{,l}`,
`eval/v6/v25_dev_{seed,empty}.json{,l}`. Every number below was
read from the run JSONs (and the .jsonl detail for p95), not from
a script summary.

| Metric | v3 seed | v3 empty | v4 seed | v4 empty | v5 seed | v5 empty | v6 seed | v6 empty | Bar |
|---|---|---|---|---|---|---|---|---|---|
| Requests / consulted / blocked | 110 / 40 / 34 | 110 / 40 / 34 | 70 / 24 / 46 | 70 / 24 / 46 | 59 / 38 / 21 | 59 / 38 / 21 | 56 / 33 / 23 | 56 / 33 / 23 | - |
| Denylist recall | 1.0 (31/31) | 1.0 (31/31) | 1.0 (46/46) | 1.0 (46/46) | 1.0 (21/21) | 1.0 (21/21) | 1.0 (23/23) | 1.0 (23/23) | 1.0 |
| Must-block | 5/5 | 5/5 | 4/4 | 4/4 | 2/2 | 2/2 | 2/2 | 2/2 | all |
| Never stored | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Unsafe hits | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| FP (gateway traffic) | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| FP (all safe, incl. bus bodies) | 0.0455 | 0.0455 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | - |
| Non-seed safe rate (value) | 0.2432 | 0.2568 | 0.0429 | 0.0571 | 0.2712 | 0.2712 | 0.0714 | 0.0714 | >= 0.10 (holdout) |
| Median total check | 15.8 ms | 16.0 ms | 14.1 ms | 13.6 ms | 16.1 ms | 14.0 ms | 14.8 ms | 13.6 ms | - |
| p95 total check | 30.4 ms | 21.5 ms | 24.3 ms | 18.8 ms | 28.0 ms | 19.7 ms | 26.7 ms | 19.0 ms | <= 50 ms |
| Max total check | 413.1 ms | 462.2 ms | 29.0 ms | 440.3 ms | 418.1 ms | 441.0 ms | 419.5 ms | 436.0 ms | - |

Combined dev (295 prompts): recall **1.000 (121/121 never,
route=full)**, must-block **13/13**, never stored **0**, unsafe
**0**, FP gateway **0.0** (all 8 runs).

Comparison with v2.4-guard on dev: v3/v4/v5 identical (recall 1.0,
FP 0.0, same value rates); v6 recall 0.8696 -> **1.000**,
must-block 0/2 -> **2/2**, never stored 3 -> **0**, FP gateway
0.0606 -> **0.0**, value 0.0536 -> **0.0714** (the unblocked
"Water boils ..." question now hits its seed paraphrase at
0.9891). The v3 FP-all 0.0455 is unchanged from v2.4: the same 3
agent-task bus bodies are blocked (by the narrowed message
pattern via "reply ... the message", `\bsend\b`, and
`\bunlock\b`); they are excluded from the gateway-traffic FP by
the agreed definition.

Cost: p95 check 18.8–30.4 ms across all 8 runs, all under the
50 ms budget. Max per-request ~413–462 ms is a single first-query
outlier per run (order 0 in the detail; second-highest is at most
28.8 ms): the fresh driver process pays the one-time lazy
prototype-embedding cost (~50 embeds) on its first Rule C query.
The live service pre-computes prototype embeddings at startup,
so live traffic never pays it. (The v2.4 report attributed the
same outlier to first-embed warming; the detail shows total_ms
far above embed_ms + lookup_ms on that first query, which is the
prototype warm-up, not the prompt embed.)

Dev detail (v6 seed run, verified in the .jsonl): "Mow the lawn
this afternoon." blocked `denylist:guard-rule-a:mow`; "How many
hours did I sleep last night?" blocked `denylist:guard-rule-b:
daily-count`; "Where are my car keys?" blocked
`denylist:guard-rule-b:where-is-mine`; "Is it raining outside
right now?" blocked `denylist:guard-rule-b:weather-now`;
"Water boils at what temperature at sea level?" consulted, HIT
(sim 0.9891); "Write a short story about a lighthouse keeper who
finds a message in a bottle." consulted, miss-stored (sim
0.4862). Rule C blocks on dev (seed runs): v4-015 and the
self-improvement body (statement margin), "make it warmer in
here" and "Show me the front door camera." (imperative margin
0.20). No safe item is blocked by Rule C on any dev set.

Value note (same as v2.4): the v4/v6 dev value rates (0.043–
0.071) stay below the 0.10 bar, but that is a property of those
dev sets (few paraphrase repeats), not the guard; the value bar
applies to the holdout, and the guard affects value only through
FP, which is 0.0.

## Unit tests

`test_gateway_v7.py`, run on the Spark from the eval dir:
**34 tests, all pass** (5.5 s). Extends the v6 suite (22 tests)
with: denylist v1.4 message class (story not blocked, messaging
actions still blocked, plain-message noun not blocked), Rule A v3
yard verbs + message verb + question guard (including "trim the
video" staying unblocked), Rule B v3 where-are / wider
daily-count windows / weather-now, prompt-class classification
and per-class margin thresholds, the statement-margin synthetic
test (+0.15 margin blocked for statement, not for imperative or
question), the 4-dev-set form-rule assertions (regex 60 +
form 57 = 117 of 121 never; 4 left for Rule C; FP 0), the v6 dev
failure/FP assertions, and the live Rule C test (`test_real_
margin_separates_dev`, real bge-m3) passing on all four dev sets.
(33 pass + 1 live test skipped on the VM, no Ollama there.)

## Deploy (shadow :18795)

- **Deployed 23 Nov 2026 22:55:50 UTC** via
  `eval/deploy_gateway_v7.sh` (mirrors the v2.4 deploy pattern).
  Backed up v2.4-guard code + config
  (`gateway_v6_guard_20261123.py` - md5 09e960b243b14045ba3cd7529bf18cf2,
  the v2.4 guard md5 from GUARD-V6-REPORT.md -
  `config_v2_4_guard_20261123.json`); store kept live (30 entries,
  no snapshot; v2.5 adds no entry fields, so the store is
  forward/backward compatible). Config: threshold 0.90, upstream
  stub, TTL 24h/168h, factual 0.85, generative 0.85,
  generative_ttl true, frame_strip_factual false,
  legacy_backfill false, guard_enabled true, guard_margin 0.20,
  **guard_margin_statement 0.10** (new).
- **Live /health (verified 22:55 UTC, and again after the final
  restart):**
  `{"ok": true, "service": "semantic-gateway-cache", "gateway_version":
  "v2.5-guard", "threshold": 0.9, "threshold_factual": 0.85,
  "threshold_generative": 0.85, "frame_strip_factual": false,
  "legacy_backfill": false, "generative_ttl": true, "denylist":
  "v1.4", "guard": "v2.1", "guard_enabled": true, "guard_margin":
  0.2, "guard_margin_statement": 0.1,
  "guard_action_prototypes": 33, "guard_safe_prototypes": 17,
  "ttl_hours": 24.0, "ttl_stable_hours": 168.0, "normalise": true,
  "exact_match": true, "keep_alive": "24h", "embedder_warmed": true}`
- **Live probes (verified):** "Mow the lawn this afternoon." ->
  blocked `denylist:guard-rule-a:mow`, cache_status
  blocked-denylist, 0 embed calls (blocked pre-embed). "Water
  boils at what temperature at sea level?" -> NOT blocked,
  miss-stored (STUB-OUTPUT), blocked_by null. "Write a short
  story about a lighthouse keeper who finds a message in a
  bottle." -> NOT blocked, miss-stored (STUB-OUTPUT). The two
  probe entries were removed afterwards and the store restored to
  30 entries; the service was restarted so the live process
  reloaded the restored store (verified /stats: 30 entries,
  /health still v2.5-guard).
- **Rollback tested:** `rollback_gateway_v6.sh` (in the gateway project dir)
  restored v2.4-guard (verified /health: v2.4-guard, denylist
  v1.3, guard v2.0, 30 entries), then v2.5-guard was re-deployed
  and re-verified live. Deeper fallbacks intact:
  rollback_gateway_v5.sh (v2.3-guard), rollback_gateway_v4.sh (v2.2-enh),
  rollback_gateway_v3.sh (v2.1-enh), rollback_gateway_v2.sh (v2.0-c1c6),
  rollback_gateway.sh (as-built).

## Known limits

- **The statement margin 0.10 is thin.** Its gap to the highest
  safe statement on dev is 0.02 (+0.0889 vs 0.10), and it is
  load-bearing for exactly one dev item (v4-015 at +0.1093). A
  fresh safe statement-form prompt (a long code request, a
  declarative factual statement) landing above +0.10 would FP;
  a fresh agent-task body landing below +0.10 would escape. The
  margin is the least precise layer, and this round spent its
  precision budget on the statement class.
- **Rule A question guard has a known residual risk:** an action
  request phrased as a question ("Play the radio?") would no
  longer be caught by Rule A and must rely on the regex (which
  covers turn/switch/lights but not play) or Rule C. No such item
  exists in dev; the guard was still adopted because both v6 dev
  FPs need it and the alternative (first-word matching regardless
  of part of speech) is the proven failure.
- **Deliberately NOT done (holdout discipline):** no form was
  added for the v6 holdout failures (doorbell, "who is at the
  front door", "is the alarm armed", "run the dishwasher").
  "armed" was NOT added to Rule B state words, "run" was NOT
  added to Rule A, and no doorbell prototype was added - those
  would be tuning to the retired holdout. The mechanism must
  generalise to them via the form rules + margins above.
- **Dev is not holdout.** v2.5 reaches recall 1.0 and FP 0.0 on
  dev, but dev is 295 prompts the mechanism was designed against.
  The v7 holdout is the generalisation test.
- **Value on v4/v6 dev stays low (0.043–0.071).** A property of
  those dev sets, not the guard (see above).
- **No new real traffic.** The DATA gate stays marginal (same as
  v2.4).

## How to iterate (for the next round)

The guard is modular: each layer is a separate function with its
own unit tests, so a next round can strengthen one layer without
touching the others.

- **Denylist** (`DENYLIST`, `denied()`): regex patterns, layer 1.
  Add a pattern only for a general class (a verb, a form, a
  structure), never for a single item. Narrow a pattern when it
  causes an FP (as v1.4 did for message).
- **Rule A** (`_ACTION_VERBS`, `_QUESTION_WORD_RE`, `_RULE_A_RE`,
  `_RULE_A_MAKE_RE`, `guard_rule_a()`): the imperative verb class
  plus the question guard. Add verbs that head actions; keep
  information/creative verbs out. The question guard is the
  template for a form-level exception (a question is not an
  imperative even when its first word is a verb).
- **Rule B** (`_LIVE_ENTITIES`, `_STATE_WORDS`, `_RULE_B_*_RE`,
  `guard_rule_b()`): live-state question forms. Add entities,
  state words, interrogatives, or whole new forms (where-are,
  daily-count windows, weather-now are the v2.5 templates).
- **Rule C** (`ACTION_PROTOTYPES`, `SAFE_PROTOTYPES`,
  `prompt_class()`, `guard_margin_for_class()`,
  `guard_margin_check()`): the embedding margin, now per class.
  Prototypes are general canonical phrases; the source of truth
  is `eval/prototypes.json` + `eval/safe_prototypes.json`, and the
  unit tests assert the module constants match those files.
  Margins per class live in `guard_margin_for_class()` with
  config overrides `guard_margin` (imperative/question) and
  `guard_margin_statement` (statement). Do NOT lower the
  imperative/question margin below 0.20 (probe: safe imperatives
  reach +0.107, safe questions +0.120) and do NOT add
  item-specific prototypes (candidate prototypes moved the
  bus-body margin by exactly 0.0000; see probe_v7b.py).
- **Do NOT** tune to the retired v6 holdout, and do NOT pre-build
  a v8; the next round's parent authorises the v7 candidate set
  and the next guard from the v7 verdict.

## Next round's most promising lever (if v7 still fails)

**A second embedding model for the guard only (a model trained
for intent, not retrieval).** The probe showed the bge-m3 margin
cannot separate short everyday never forms from safe prompts in
the imperative/question classes at all (mow +0.0084, sleep
-0.0093 sit below every safe maximum), and the statement margin
is spent at a 0.02 gap. The form rules have now covered the
failure classes dev can show; the next hard miss will be a form
Rule C alone must catch, and bge-m3 retrieval similarity is the
wrong signal for that job - it measures topical closeness, not
action intent. An intent-trained embedding (or a small intent
classifier on top of bge-m3, NOT the rejected nearest-centroid
classifier - its CV FP was 0.23) is the mechanism change that
could separate the band. It adds a dependency and load time, so
it is the fallback, not the first move. The cheaper lever, if the
v7 verdict shows a new form-rule miss class, is widening Rule B
to that class (the v2.5 templates show how) - but that is
form-rule breadth, not a new signal, and it does not fix the
margin band.

## Files (md5-verified VM vs Spark)

| File | md5 |
|---|---|
| `guard-v7-build/gateway_v7.py` = `eval/gateway_v7.py` = live `semantic_gateway/gateway.py` | 0c35f614fa4dd4190451ee5fa412d92a |
| `guard-v7-build/test_gateway_v7.py` = `eval/test_gateway_v7.py` | 6dd12836c1b17f93976f2294fa95c835 |
| `guard-v7-build/deploy_gateway_v7.sh` = `eval/deploy_gateway_v7.sh` | a4739fe794833a7d9027e6a95aed83f0 |
| `guard-v7-build/probe_v7.py` = `eval/probe_v7.py` | 844b64676b6b2c8ae679cf88bd77f889 |
| `guard-v7-build/probe_v7b.py` = `eval/probe_v7b.py` | de565da0fa93924acefc6c27756b74f3 |
| `guard-v7-build/probe_v7.json` (VM `spark_src/`) = `eval/probe_v7.json` | a07f695bd013a07a02a4c6b6687de5d4 |
| `guard-v7-build/run_v25_dev.sh` = `eval/run_v25_dev.sh` | 5a27121f2f87bb03d13be5112c59b741 |
| `eval/v3/v25_dev_seed.json` | 79efec89d12b4812b67c891867ee66ee |
| `eval/v3/v25_dev_empty.json` | 9c26626aa97688912cbf6fade229cdde |
| `eval/v3/v25_dev_seed.jsonl` | 8c0f7dd52bd2074140835e5f178beabe |
| `eval/v3/v25_dev_empty.jsonl` | a51b15b4cbae4b72a84c5ca0a8a7729e |
| `eval/v4/v25_dev_seed.json` | 40e706037c35336c5b1179d6c21e0cd8 |
| `eval/v4/v25_dev_empty.json` | 9d7cd7b83bd75f40181ff764a3ebe432 |
| `eval/v4/v25_dev_seed.jsonl` | 524688dc7e9f43ebe0feaacab3effe51 |
| `eval/v4/v25_dev_empty.jsonl` | 190657620cca66d9af77c0a9fb5a16b9 |
| `eval/v5/v25_dev_seed.json` | 03d77420a4a6f8619d9a85e5e2042d39 |
| `eval/v5/v25_dev_empty.json` | c41b8a65e02e1fdac080d7e5d32e3544 |
| `eval/v5/v25_dev_seed.jsonl` | b068ece07eb480dbe2925e1e3206c2c8 |
| `eval/v5/v25_dev_empty.jsonl` | 6304e7e9e4fd69c8f36f4ac4474223d8 |
| `eval/v6/v25_dev_seed.json` | 1e3457e047f133f7c22bf3999c5a0ccb |
| `eval/v6/v25_dev_empty.json` | c8ea2a19a40928464915900b4272cdf3 |
| `eval/v6/v25_dev_seed.jsonl` | ad1d09621482f6aa356ab2d708c766d2 |
| `eval/v6/v25_dev_empty.jsonl` | 38b181d036e72493a591205f4042b2a7 |
| `guard-v7-build/GUARD-V7-REPORT.md` = `eval/GUARD-V7-REPORT.md` | 8a3c7aa8f7255c35d97444b86956a760 |

Audit trail (VM `[workspace]/guard-v7-build/`, Spark mirror in
`eval/`): `probe_v7.py`, `probe_v7.json`, `probe_v7b.py`,
`run_v25_dev.sh`, `restore_store.py` (VM only: one-shot store
restore after the live probes), `spark.sh` (VM only: SSH helper),
`spark_src/` (VM only: v2.4 sources + the four dev sets as pulled
for analysis). Dev run JSONs + detail + logs:
`eval/v3/v25_dev_{seed,empty}.json{,l,.log}`,
`eval/v4/v25_dev_{seed,empty}.json{,l,.log}`,
`eval/v5/v25_dev_{seed,empty}.json{,l,.log}`,
`eval/v6/v25_dev_{seed,empty}.json{,l,.log}`. Rollback:
`rollback_gateway_v6.sh` (restores v2.4-guard; tested). The `/tmp`
test dir on the VM was removed after use (neatness).
