# Guard v2.7-guard build report (round 4)

Date: 2026-11-23. Gateway v2.7-guard, guard v2.3, denylist v1.5.
Built from gateway v2.6-guard (guard v2.2, denylist v1.5). Deployed to
shadow on :18795 at 2026-11-23 23:30:53 UTC. Rollback to v2.6-guard
tested and re-deployed.

## What changed (mechanism)

Rule B v5, five new general pattern classes, one per v8 failure class.
No denylist change, no Rule A change, no Rule C change, no prototype
change (33 action + 17 safe), no threshold change (0.90 / factual
0.85 / generative 0.85), no dispatcher/routing/live-serving change.

1. Uncontracted weather-like. "what is the weather like/doing" plus
   a live marker (outside / right now / at the moment / today / here /
   now / currently). v2.6 matched "what's" only. The live marker is
   the scope: "what is the weather like on Mars" stays unblocked.
2. Presence. "(is|are) (someone|anyone|somebody|anybody) ((at|in)
   (the|my|our)? <home location>|home)". The location must be a home
   noun (front door, door, kitchen, room, house, flat, home,
   apartment, lounge, living room, bedroom, garden, garage, hallway,
   porch). "is anyone at the party" does not match.
3. Softened imperative. "(can|could) you <action verb>" with no
   wh-word, firing even with a trailing "?". The action verb list is
   the Rule A verb set plus "book". The wh-word guard keeps genuine
   questions off: "can you tell me ..." (tell is not an action verb),
   "could you explain ..." (explain is not an action verb), "can you
   count how many ..." (wh-word present) do not match. This was the
   hardest class and the v2.5 report's named residual risk.
4. More completion state words. boiled, brewed, charged, downloaded,
   uploaded, printed join the state form ("has the kettle boiled").
   "phone", "battery" and "coffee" join the live entities ("is my
   phone charged", "has the coffee brewed").
5. "did i (put|lose|place)" form. "did i leave" keeps working with
   "the" ("leave the front gate open"). "put/lose/place" require a
   belonging ("my"/"our"), so "where did i put the emphasis" (a
   metaphor, not a live location) does not match. This narrowing was
   found during test writing: the first version matched "put the
   emphasis" and was fixed before the dev runs.

Form-layer probe on dev (408 prompts, live v2.7 module on the Spark,
before the driver runs): regex blocked 74 never, regex-missed 92,
form caught 87 of those, 5 left for Rule C (v4-015, v4-023, v4-065,
v5-058, v7-032). FP on gateway safe 0. Regex+form blocked 161 of 166
never with route=full. (The probe counted 166 never with route=full;
the driver counts 179 never in total, the difference being never
items whose route is not full.)

## Dev results (408 prompts, v3 dev 110 + v4 dev 70 + v5 dev 59 + v6 dev 56 + v7 dev 51 + v8 dev 62)

Driver drive_gateway_v3.py, scorer v3.0, thresholds 0.90 / 0.85 /
0.85, seed store cache_store_backup_20261123.json. p95 recomputed
from the .jsonl detail files (the run JSONs carry no p95 field).

| set | mode | req | recall | must-block | never stored | unsafe | FP | non-seed safe rate | median ms | p95 ms |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v3 | seed | 110 | 1.0 | 5/5 | 0 | 0 | 0.0455 | 0.2432 | 16.8 | 30.7 |
| v3 | empty | 110 | 1.0 | 5/5 | 0 | 0 | 0.0455 | 0.2568 | 15.4 | 21.9 |
| v4 | seed | 70 | 1.0 | 4/4 | 0 | 0 | 0.0 | 0.0429 | 14.7 | 27.3 |
| v4 | empty | 70 | 1.0 | 4/4 | 0 | 0 | 0.0 | 0.0571 | 13.6 | 22.3 |
| v5 | seed | 59 | 1.0 | 2/2 | 0 | 0 | 0.0 | 0.2712 | 16.0 | 32.5 |
| v5 | empty | 59 | 1.0 | 2/2 | 0 | 0 | 0.0 | 0.2712 | 14.1 | 23.2 |
| v6 | seed | 56 | 1.0 | 2/2 | 0 | 0 | 0.0 | 0.0714 | 14.9 | 28.0 |
| v6 | empty | 56 | 1.0 | 2/2 | 0 | 0 | 0.0 | 0.0714 | 13.4 | 19.0 |
| v7 | seed | 51 | 1.0 | 2/2 | 0 | 0 | 0.0 | 0.0588 | 14.8 | 24.7 |
| v7 | empty | 51 | 1.0 | 2/2 | 0 | 0 | 0.0 | 0.0588 | 13.6 | 23.0 |
| v8 | seed | 62 | 1.0 | 2/2 | 0 | 0 | 0.0 | 0.0645 | 15.3 | 33.8 |
| v8 | empty | 62 | 1.0 | 2/2 | 0 | 0 | 0.0 | 0.0645 | 14.5 | 24.6 |

Dev gates: recall 1.0 on all 6 sets, both modes. Must-block 17/17
blocked. Never stored 0. Unsafe 0. Cost p95 19.0-33.8 ms, all under
the 50 ms budget.

The v4 dev must-blocks that v2.6 missed are now blocked: v8-023
"Can you set an alarm for seven in the morning?" by
rule-b:softened-imperative, v8-031 "Has the kettle boiled?" by
rule-b:state-query. The other two v8 dev escapes (book-taxi-softened,
where-phone) are also blocked by their forms. v2.6 v8 dev recall was
0.8333 with must-block 0/2; v2.7 v8 dev recall is 1.0 with must-block
2/2.

FP note. v3 FP 0.0455 is 3 of 66 safe prompts, all long bus-message
bodies labelled stable (v3-143, v3-145, v3-146) that contain "send ...
message", "send" and "unlock". This FP is pre-existing and identical
under v2.5 and v2.6 (both 0.0455 on v3 seed). v2.7 introduces no new
FP. It is a data labelling artefact, not a guard defect: the bodies
are historical bus records, not genuine user prompts.

Value note. Non-seed safe rate on dev is below the 0.10 bar on v4,
v6, v7 and v8 (0.0429-0.0714) and above it on v3 and v5 (0.2432-
0.2712). Dev safe rate is not the gate; the gate is the v9 holdout.
The dev numbers say the guard is now safe enough that the value
question is decided by the fresh holdout, not by dev.

Unit tests: 43/43 pass on the Spark (test_gateway_v9.py), including
3 new v2.7 tests (new forms block, new forms do not block factual,
v8 dev failures fixed by form rules).

## Live service

semantic-gateway.service on :18795, shadow only. /health at deploy:
gateway v2.7-guard, guard v2.3, denylist v1.5, threshold 0.90 /
factual 0.85 / generative 0.85, guard_margin 0.20, guard_margin_
statement 0.10, 33 action + 17 safe prototypes, embedder warmed,
store 30 entries. Upstream stub. No live routing change.

Rollback tested: rollback_gateway_v8.sh restored v2.6-guard (verified on
/health: v2.6-guard, guard v2.2), then deploy_gateway_v9.sh re-deployed
v2.7-guard (verified on /health: v2.7-guard, guard v2.3). The store
was kept live through both (no snapshot; v2.7 adds no entry fields).

Live probes on :18795 after re-deploy (all blocked items show
latency 0.04-0.07 ms, i.e. 0 embeds, blocked before embedding):

- "Can you set an alarm for seven in the morning?" blocked by
  denylist:guard-rule-b:softened-imperative.
- "Has the kettle boiled?" blocked by denylist:guard-rule-b:state-
  query.
- "Could you book a taxi for tomorrow morning?" blocked by
  denylist:guard-rule-b:softened-imperative.
- "Where did I put my phone?" blocked by denylist:guard-rule-b:did-
  i-leave.
- "What is the weather like outside right now?" blocked by
  denylist:guard-rule-b:weather-like.
- "Is someone at the front door?" blocked by denylist:guard-rule-b:
  presence.
- "send a message to mum" blocked by denylist:\bsend\b.
- "At what temperature does water boil?" not denylist-blocked
  (served, STUB-OUTPUT).
- "What is the weather like on Mars?" not denylist-blocked.
- "Is anyone at the party?" not denylist-blocked.

Known residual FP, NOT fixed by this round. "Write a birthday
message for my mum" is still blocked live, by denylist:guard-margin
(Rule C). The v1.5 denylist regex exemption works: denied() and
guard_form_check() both return None for it (the creative verb "write"
before "message" skips the "message for" regex). The block is purely
Rule C, the embedding margin. This is the v7 holdout FP (v7-068),
not a dev item, and it was not a tuning target. It is a round 5
lever: a Rule C exemption for creative verbs, or safe-prototype
tuning for message-writing prompts.

## What was declined and why

- Fine-tuned embedding model. Not attempted. The Rule B widening
  reached dev recall 1.0 with FP 0.0 (except the pre-existing v3
  artefact) on all 6 dev sets, so the fallback condition did not
  trigger. It stays the fallback if a future round's form widening
  falls short.
- Intent classifier. Declined in round 3 (logistic regression on 50
  prototype sims, leave-one-family-out CV: best honest point recall
  4/9 at FP 0; no threshold gives recall 1.0 at FP 0). Not retried.
- Denylist change. None. The five v8 failure classes were all form
  classes, not denylist misses, and the v1.5 message to/for split
  already handles the creative-verb case at the regex level.
- Rule C margin change. None. The per-category margins (0.20 /
  0.20 / 0.10) are unchanged; the birthday-message FP is a Rule C
  margin issue, but changing the margin to fix one FP would risk
  recall on the 5 Rule C reachers (v4-015, v4-023, v4-065, v5-058,
  v7-032), which is the wrong trade on dev evidence alone.

## Next round's lever if v9 still fails

1. Rule C creative-verb exemption: a prompt whose leading verb is
   creative (write, compose, draft, invent, imagine) should not be
   blocked by the guard margin, or the safe prototypes should gain
   a message-writing prototype. This fixes the birthday-message FP
   without touching the denylist.
2. If v9 holdout shows new escape classes, widen Rule B to those
   classes the same way (general pattern, not per-prompt).
3. If form widening stops reaching dev recall 1.0 with FP 0.0, the
   fine-tuned embedding model is the fallback, trained on dev
   labels only.

## Files

All md5s verified VM vs Spark by direct comparison. The report's own
md5 is verified directly and is deliberately NOT listed in this
table (the v2.5 stale self-md5 bug).

- gateway_v9.py: fd65d5d23b9dcf514592bdbe9e8abb9c (VM and Spark)
- test_gateway_v9.py: 82445a4daa057fd30eb403d7a4555a46 (VM and Spark)
- run_v27_dev.sh: dec55d2fd5056e14a4cf9c3d516db0b0 (VM and Spark)
- deploy_gateway_v9.sh: ed1835d4ab2e68a50fb537a6019c14b9 (VM and Spark)
- Dev run JSONs (12): v3/v27_dev_seed.json
  2a49788d99bf09875f7c7e54a828e321, v3/v27_dev_empty.json
  b9ab091cfcadad2e9e11df78cbecb4c6, v4/v27_dev_seed.json
  a6622644b335a59d1d029ce24a693efd, v4/v27_dev_empty.json
  99aba015e05e5e047fa747e83062733a, v5/v27_dev_seed.json
  6348dbfdc3e14b1ee182af4e532916a4, v5/v27_dev_empty.json
  fb2861b1389d3894018ddb2aa1bf6c5b, v6/v27_dev_seed.json
  363696f275ae9526886f52014f031355, v6/v27_dev_empty.json
  84a84981720102f0d26c133c53a4f68a, v7/v27_dev_seed.json
  4f5299d9a2167fa9b09c836782dcb014, v7/v27_dev_empty.json
  b17f8d26fb99a07f2f9424a8a7497339, v8/v27_dev_seed.json
  93aa3c114a7dbf87e9a6290dc0930133, v8/v27_dev_empty.json
  7d5322410920bbe0360c97dc7f5f1288 (all VM and Spark identical).
  The .jsonl detail files are mirrored alongside each run JSON.
- v9 candidate eval set: [workspace]/v9/eval_set_v9.json
  65a51b64d732f9bfde284020f3ffe6f1 (see V9-REPORT.md).
