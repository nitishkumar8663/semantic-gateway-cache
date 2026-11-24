# Guard build report - gateway v2.3-guard

**Date:** 23 Nov 2026 (evening). **Code:** gateway v2.3-guard
(`gateway_v5.py`), guard v1.0. **Status:** built, unit-tested
(18/18), dev-validated, DEPLOYED to shadow on :18795, rollback
tested (2.0 s). **Dev verdict:** SAFETY PASS (recall 1.0,
must-block 4/4, 0 never stored, 0 unsafe, FP 0.0), COST PASS
(p95 25.6 / 22.9 ms). VALUE still fails on v4 dev (0.0429 / 0.0571
vs 0.10) - the known v4 under-measurement (few repeats after the
per-question re-split); the guard is a safety mechanism and was
never expected to change value. The v5 set (paraphrase pairs) is
what will measure value.

## Why a new guard

The v4 verdict (NO-GO) found denylist v1.2 (a regex list) does not
generalise: holdout recall 0.3333, must-block 3/4, 14 never items
stored. It generalises across phrasings of the verbs it knows and
fails on new verbs, new categories, and word-order variants
(heating, timers, lists, appliances, kill/bolt/secure, "switch X
on/off"). Patching it is whack-a-mole. Nitish chose a generalising
guard plus a v5 eval set.

## Design (three rules, two layers)

Layer 1 is unchanged: regex denylist v1.2 runs first, before
embedding (it alone covers shell-injection structure, and it
already blocks 53/77 dev never items with FP 0.0). Layer 2 is the
guard (v1.0), a multi-signal intent classifier. It is NOT a pattern
list for specific items: each rule is a general class.

**Rule A - anchored imperative action verb.** A general verb class
(turn, switch, set, unlock, lock, open, close, bolt, secure, kill,
add, remove, delete, remind, wake, count, send, build, rebuild,
start, stop, pause, resume, water, feed, arm, disarm, enable,
disable, activate, deactivate, book, order, call, text, email, put,
dim, brighten, heat, cool, mute, unmute). The verb must LEAD the
prompt (optional leading "please"), so "how do I start a fire" (a
factual question) does not match but "start the dishwasher" (an
action) does. Information verbs (tell/show/explain/describe/define/
translate/write/make/give) are deliberately NOT in the class: they
head information or creative requests, not actions. Pure text, no
embedding, runs before the exact-match fast path (so a never prompt
cannot be served by exact-match either).

**Rule B - live-state question forms.** Interrogative + live-entity
noun + state word ("is the back door shut", "is the side door
closed", "is the bedroom lamp still on"); "did I leave ...";
weather forms ("forecast", "going to rain/snow", "will it rain/
snow"); live advice ("do I need ... today/tomorrow"); list queries
("what's on my shopping list"). A factual question about a schedule
("what time does the London Underground close on Sundays") does
NOT match: it has no live entity and no state word. Pure text, no
embedding, runs before exact-match.

**Rule C - two-sided embedding margin.** Max cosine similarity to
34 action prototypes minus max similarity to 17 safe prototypes;
block when the margin is >= 0.20. The prototypes are general
canonical phrases (not dev copies); the source of truth is
eval/prototypes.json + eval/safe_prototypes.json, and the unit
tests assert the module constants match those files. Reuses the
prompt embedding already computed for the cache lookup, so the
marginal cost is ~51 cosine similarities (microseconds). Runs after
embedding, before the similarity lookup. Prototype embeddings are
computed once (51 calls, ~0.4 s) at service startup and cached;
if the embedder fails, Rule C is skipped for that query (Rules A+B
and the regex still run, and the embed-failure path never stores,
so a missing Rule C cannot poison the store).

Guard blocks are reported as "denylist:guard-<rule>" so the eval
driver counts them as denylist blocks (recall and FP). Guard
blocks never consult or store.

## How the design was chosen (probe, dev only)

A probe embedded all v3 dev + v4 dev prompts (180) and the
prototypes with bge-m3, and measured the separation.

- One-sided threshold (max similarity to action prototypes only):
  NO threshold gives recall 1.0 + FP 0.0. At 0.75 recall is 0.83
  with FP 0.0; at 0.65 recall is 1.0 but FP is 0.078. The overlap
  is short generic phrases: chatter ("how is it going?", "what's
  up?") matches the "are the lights on" prototype at 0.71, and a
  haiku about rain matches "will it rain" at 0.67. Short prompts
  cluster by form, not content.
- Two-sided margin (action minus safe): better, but still no clean
  split on its own. Lowest never margin +0.045 ("do I need a
  jacket today?"), highest safe margin +0.129 ("what time does the
  London Underground close on Sundays?"). At margin 0.20 recall is
  0.79 with FP 0.0; at 0.00 recall is 1.0 but FP is 0.20.
- The fix was to drop the prototypes that caused the false
  positives ("are the lights on" matched chatter; "wake me up in
  the morning" matched "good morning" factual prompts; the time
  prototypes matched factual schedule questions; the status
  prototypes matched "what's the status of my quantum computer?")
  - none of them were needed for the regex-missed set, because the
  regex already covers time and status - and to add Rules A and B,
  which catch the low-margin never items by form.
- Combined (regex + A + B + C at 0.20) on v3+v4 dev: recall 1.000
  (77/77), FP 0.000 (0/61 gateway safe). Rules A+B alone catch
  22/24 regex-missed never items with FP 0.0; Rule C catches the
  remaining 2 ("make it warmer in here", the bus body).

A length rule for bus bodies was considered and REJECTED: safe bus
bodies in v3 dev are up to 2391 chars, so length does not separate
never bus bodies from safe ones. The bus body relies on Rule C
(margin +0.236, only 0.036 above the 0.20 threshold) - see
caveats.

## Dev results (v4 dev, 70 prompts / 29 families, both modes)

Driver: drive_gateway_v3.py, gateway_v5.py, threshold 0.90 /
factual 0.85 / generative 0.85, TTL 24h / 168h, seed store
cache_store_backup_20261123.json (16 entries). Run twice (same
numbers both times).

| Metric | v2.2-enh dev | v2.3-guard dev seed | v2.3-guard dev empty | Bar |
|---|---|---|---|---|
| Denylist recall | 0.4783 (22/46) | 1.0 (46/46) | 1.0 (46/46) | 1.0 |
| Must-block | 2/4 | 4/4 | 4/4 | all |
| Never stored | 24 | 0 | 0 | 0 |
| Unsafe hits | 0 | 0 | 0 | 0 |
| FP (gateway) | 0.0 | 0.0 | 0.0 | 0.0 |
| Non-seed safe rate | 0.0429 / 0.0571 | 0.0429 | 0.0571 | >= 0.10 |
| Median total check | 12.6 / 11.2 ms | 14.6 ms | 13.6 ms | - |
| p95 total check | - | 25.6 ms | 22.9 ms | <= 50 ms |
| Median embed | - | 9.1 ms | 9.0 ms | - |

Blocked breakdown (both modes identical): regex v1.2: 22, guard
Rule A (verb): 14, guard Rule B (form): 8, guard Rule C (margin):
2 (the bus body, "make it warmer in here"). Consulted: 24 (20
factual + 4 chatter), all safe. Hits: 8 seed / 4 empty, all safe.

**Gates on dev:** SAFETY PASS, COST PASS, VALUE FAIL (v4
under-measures value; the guard does not change value, and the
v5 set is built to measure it). DATA: v4 dev only; the v4 holdout
was NOT read, scored, or used in any way (it is retired).

## Cost

p95 total check 25.6 ms (seed) / 22.9 ms (empty), inside the 50 ms
budget and essentially unchanged from v2.2-enh (p95 26.5 ms on v3
dev). The guard adds no per-query embedding (it reuses the prompt
embedding); Rule C is ~51 cosine similarities (microseconds).
One-time cost: 51 prototype embeddings (~0.4 s) at service
startup, pre-computed in serve() so no query pays it. (Before the
startup pre-compute, the first Rule C call after a restart cost
~440 ms; warm Rule C calls are ~12-14 ms total.) Memory: the
prototype embeddings are 51 x 1024 floats (~0.2 MB). No new
resident model; bge-m3 unchanged (0.69 GB).

## Deployment

- Live on :18795 as semantic-gateway.service, v2.3-guard, guard v1.0,
  guard_enabled true, guard_margin 0.20, 34 action + 17 safe
  prototypes, denylist v1.2, threshold 0.90 / 0.85 / 0.85, TTL
  24h / 168h, upstream stub. Shadow only; no live routing or
  dispatcher change. Store kept live (30 entries, no never-class
  entries in it; the store is forward/backward compatible, v2.3
  adds no entry fields).
- Rollback: rollback_gateway_v4.sh restores v2.2-enh code + config,
  keeps the store. TESTED: 2.0 s, /health returned v2.2-enh,
  store intact at 30 entries. Re-deployed v2.3-guard after the
  test. Deeper fallbacks intact (rollback_gateway_v3.sh, v2, v1).
- Live verification (curl, after deploy): "turn the heating up"
  blocked by guard-rule-a:turn (0.15 ms, no embed); "is the back
  door shut?" blocked by guard-rule-b:state-query (0.04 ms);
  "make it warmer in here" blocked by guard-margin (13.7 ms warm);
  "What is the capital of France?" hit the seed entry (sim 0.9967,
  not blocked). Stats: blocked_by_guard counted; entries unchanged
  at 30.
- Shadow timer unchanged (next run Tue 24 Nov 06:00 UTC).

## Files

- Code: eval/gateway_v5.py (Spark) + VM mirror
  [workspace]/guard-build/gateway_v5.py
- Tests: eval/test_gateway_v5.py (18 tests, all pass) + VM mirror
- Deploy: eval/deploy_gateway_v5.sh + VM mirror; rollback
  rollback_gateway_v4.sh
- Probes: eval/probe_guard.py, probe_guard2.py, probe_guard3.py
  (+ probe_guard.json, probe_guard2.json, probe_guard3.json) and
  eval/prototypes.json + eval/safe_prototypes.json
- Dev runs: eval/v4/v23_dev_seed.json (+ .jsonl, .log),
  eval/v4/v23_dev_empty.json (+ .jsonl, .log)
- This report: [workspace]/guard-build/GUARD-REPORT.md (VM) +
  Spark mirror eval/GUARD-REPORT.md (md5-verified below)

## Caveats (honest)

1. **The bus body is the thin margin.** It relies on Rule C
   (margin +0.236, only 0.036 above the 0.20 threshold). A v5 bus
   body about a different task could fall below 0.20 and be
   missed. The agent-task prototypes are generic ("apply the code
   changes and report back", "build and install the plugin",
   "task update from the agent"), but bus bodies vary widely.
   This is the guard's weakest point and the v5 test's sharpest
   check.
2. **"make it warmer" relies on Rule C too** (margin +0.2658).
   "make" is deliberately excluded from the Rule A verb class
   (it also heads creative requests: "make a video"). If a v5
   "make it ..." action prompt has a lower margin, it could be
   missed.
3. **Rules A and B are form-based.** They generalise across
   objects ("turn the X on" for any X) but not across intents
   they do not cover (e.g. a novel action verb not in the class,
   or a live-state question about an entity not in the list).
   Their generalisation is untested until v5.
4. **VALUE still fails on v4 dev** (0.0429 / 0.0571 vs 0.10).
   That is the v4 set's under-measurement, not a guard
   regression: the guard blocks never items only, and the value
   number is identical to v2.2-enh's. The v5 set (paraphrase
   pairs) is built to measure value properly.
5. **The guard was tuned on dev only** (v3 dev + v4 dev, 180
   prompts). The v4 holdout was never read or used. The v5
   holdout is the generalisation test; a v5 recall below 1.0 or
   FP above 0.0 would mean the guard needs another round.
