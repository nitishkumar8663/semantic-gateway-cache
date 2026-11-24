# Guard v2.9-guard (guard v2.5) - round-6 build report

Date: 24 Nov 2026 (build ~00:30-00:45 GMT)
Gateway version: v2.9-guard, guard v2.5, denylist v1.5
Live: shadow only, :18795, semantic-gateway.service, upstream stub
Dev base: 536 prompts (v3 dev 110, v4 dev 70, v5 dev 59, v6 dev 56, v7 dev 51,
v8 dev 62, v9 dev 58, v10 dev 70). Must-block total 21.

## Verdict on dev: PASS on all gates, every set, both modes

| set | mode | req | recall | must-block | never stored | unsafe | FP (gateway) | non-seed safe rate | median ms | p95 ms |
|-----|------|-----|--------|------------|--------------|--------|--------------|--------------------|-----------|--------|
| v3 | empty | 110 | 1.0000 | 5/5 | 0 | 0 | 0.00 | 0.2568 | 15.0 | 21.5 |
| v3 | seed | 110 | 1.0000 | 5/5 | 0 | 0 | 0.00 | 0.2432 | 15.5 | 30.5 |
| v4 | empty | 70 | 1.0000 | 4/4 | 0 | 0 | 0.00 | 0.0571 | 13.2 | 19.8 |
| v4 | seed | 70 | 1.0000 | 4/4 | 0 | 0 | 0.00 | 0.0429 | 14.3 | 24.8 |
| v5 | empty | 59 | 1.0000 | 2/2 | 0 | 0 | 0.00 | 0.2712 | 13.7 | 18.5 |
| v5 | seed | 59 | 1.0000 | 2/2 | 0 | 0 | 0.00 | 0.2712 | 15.5 | 28.5 |
| v6 | empty | 56 | 1.0000 | 2/2 | 0 | 0 | 0.00 | 0.0714 | 13.7 | 18.2 |
| v6 | seed | 56 | 1.0000 | 2/2 | 0 | 0 | 0.00 | 0.0714 | 15.2 | 27.8 |
| v7 | empty | 51 | 1.0000 | 2/2 | 0 | 0 | 0.00 | 0.0588 | 13.5 | 16.6 |
| v7 | seed | 51 | 1.0000 | 2/2 | 0 | 0 | 0.00 | 0.0588 | 15.2 | 24.9 |
| v8 | empty | 62 | 1.0000 | 2/2 | 0 | 0 | 0.00 | 0.0645 | 13.7 | 23.6 |
| v8 | seed | 62 | 1.0000 | 2/2 | 0 | 0 | 0.00 | 0.0645 | 15.4 | 32.7 |
| v9 | empty | 58 | 1.0000 | 2/2 | 0 | 0 | 0.00 | 0.0345 | 13.7 | 15.7 |
| v9 | seed | 58 | 1.0000 | 2/2 | 0 | 0 | 0.00 | 0.0345 | 15.6 | 23.1 |
| v10 | empty | 70 | 1.0000 | 2/2 | 0 | 0 | 0.00 | 0.0429 | 14.2 | 17.5 |
| v10 | seed | 70 | 1.0000 | 2/2 | 0 | 0 | 0.00 | 0.0429 | 15.3 | 24.1 |

SAFETY: recall 1.0, must-block 21/21, never stored 0, unsafe 0, FP 0.0 on
gateway traffic, all 16 runs. VALUE: non-seed safe rates unchanged from
v2.8 on v3-v9 (v10 dev 0.0429; dev value is not the gate, holdout is).
COST: p95 15.7-32.7 ms, all under the 50 ms budget (p95 recomputed from
the .jsonl detail, consulted rows only; the JSON summaries carry no p95
field). Median 13.2-15.6 ms. Cold-embed max ~430-450 ms on the first
consulted row of most runs (model load), same pattern as v2.8.

v10 dev, the round-5 failure set, is fully fixed: recall 0.8621 -> 1.0,
must-block 0/2 -> 2/2, never stored 4 -> 0. All 4 v10 dev escapes are now
caught by form layers: sun-go-down -> rule-b:live-fact-when, post-arrived
-> rule-b:state-query, car-charged -> rule-b:state-query, calendar-tomorrow
-> rule-b:calendar.

v3 FP caveat, unchanged: the v3 FP on safe is still 0.0455 (3/66 safe, long
bus-body artefacts v3-143/145/146), pre-existing and identical under v2.5,
v2.6, v2.7 and v2.8. Gateway-traffic FP is 0.0 on all 16 runs.

Unit tests: 51 tests, all OK in 18.6 s on the Spark (including the live
bge-m3 test_real_margin_separates_dev). Honest note: the first run was 50/51
with one failure, test_v29_new_forms_do_not_block_factual, on "when does
the sun rise in the east" matching the new live-fact-when form. That is a
direction fact, not a time question, so the form gained a negative
lookahead for "in the east/west/north/south" and the re-run passed 51/51.

## Mechanism

No denylist, prototype, threshold or margin change. No dispatcher, routing
or live-serving change. Shadow only.

### Rule B v7 widening (general pattern classes, not per-prompt)

(a) Live-fact forms: _RULE_B_LIVE_FACT_WHEN_RE ("when does the sun/moon
go down/go up/rise/set/come up") and _RULE_B_LIVE_FACT_TIME_DOES_RE
("what time does the sun/moon go down/go up/rise/set/come up"),
_Rule_B_TIDE_WHEN_RE ("when is high/low tide", "when does the tide come
in/go out"). The when-form carries a negative lookahead so direction
facts ("when does the sun rise in the east") do not FP; a date-dependent
time ("when does the sun rise in summer") still blocks, same reasoning as
"what time is sunset".

(b) Delivery entities: _LIVE_ENTITIES += post, mail, letter, car, laptop,
tablet. "has the post arrived today?" is now form-blocked
(rule-b:state-query).

(c) "Charged enough" form: _RULE_B_ENOUGH_RE ("enough charge/battery/
power/fuel/petrol"). "is the car charged enough to drive tomorrow?" is now
form-blocked (state-query via car + charged; the enough form covers
"enough charge" phrasings directly).

(d) "Check if" form: _RULE_B_CHECK_IF_RE ("check if" + a live entity +
a state word). "check" stays out of the action verb list. "can you check
if the oven is still on?" blocks; "check if the capital of France is
Paris" does not FP (no live entity + state word in the subordinate
clause). Verified in the factual test.

(e) Calendar form: _RULE_B_CALENDAR_RE and _RULE_B_CALENDAR_DAY_RE
("what is on my/our calendar/schedule/agenda/diary", with a day-marker
variant for "the"). "what is on my calendar tomorrow?" blocks.

(f) Progressive states: _STATE_WORDS += charging, drying, washing,
cooking, baking, brewing, boiling. "is my phone charging" blocks via
rule-b:state-query.

Form-layer recall (regex + Rules A/B, never route=full, 536 dev prompts):
v3 43/44, v4 43/46, v5 20/21, v6 23/23, v7 21/21, v8 24/24, v9 23/23,
v10 29/29 (was 25/29 under v2.8). Counts probe (test's own logic): form-
caught 129 of 133 regex-missed (v2.8: 125), FP 0, blocked 214 of 218
(v2.8: 210). The only form-layer misses are the same 4 Rule C reachers as
v2.8 (v4-015, v4-023 long bus bodies; v4-065 "make it warmer in here";
v5-058 "Show me the front door camera."). Form FP on cacheable: v3 6
(pre-existing bus-body artefacts, unchanged), v4-v10 0. Zero new FPs
from v2.9.

### One deliberate scope change in the tests

"at what time does the sun set in summer" was removed from
test_v28_new_forms_do_not_block_factual. It is now correctly blocked by
the live-fact-time-does form: a sunset time is date-dependent and a cached
answer would be stale (same class as "what time is sunset", already blocked
under v2.8). Documented in the test comment.

### What was declined and why

- Fine-tuned embedding model: NOT attempted. Form widening reached dev
  recall 1.0 with FP 0.0, so the fallback was not needed. It stays the
  fallback if v11 still fails.
- Intent classifier: stays declined (round-3 LOFO CV: best honest point
  recall 4/9 at FP 0).
- Any per-prompt pattern for a specific v10 prompt: none added. Every new
  form is a general class (live-fact forms, entity/state words, check-if,
  calendar, enough-charge).

## Deploy and rollback

- Deploy script: deploy_gateway_v11.sh (Spark eval/). Backs up v2.8 code/config
  (gateway_v10_guard_20261124.py, md5 f125f34adedff26b33a617d8c43eae12;
  config_v2_8_guard_20261124.json), installs gateway_v11.py, config
  unchanged, store kept live (34 entries).
- Rollback script: rollback_gateway_v10.sh (written by the deploy script).
  ROLLBACK TESTED 24 Nov ~00:36 GMT: /health returned v2.8-guard, guard
  v2.4, embedder warmed. v2.9 then re-deployed; /health verified
  v2.9-guard, guard v2.5, denylist v1.5, threshold 0.90/0.85/0.85,
  guard_margin 0.2/0.1, 33 action + 17 safe prototypes, embedder warmed.
- Live probes on :18795 (8 queries, all OK): the 4 v10 dev escapes blocked
  by their new forms (sun-go-down -> rule-b:live-fact-when, post-arrived
  -> rule-b:state-query, car-charged -> rule-b:state-query,
  calendar-tomorrow -> rule-b:calendar); "write a birthday message for my
  mum" unblocked (exact hit, similarity 1.0, Rule C exemption intact);
  "send a message to mum" blocked (regex \bsend\b); "what is the capital
  of France" unblocked (hit, similarity 0.9967); "who wrote The Hobbit"
  unblocked (miss, similarity 0.414, below threshold, correct).

## The v11 candidate set (summary; full detail in V11-REPORT.md)

106 prompts, 95 families: stable 44, never 42, ttl24 20. Two blind writer
batches (100 + 50). Collisions removed: batch 1 33 (v8 11, v10 6, v6 5,
v5 4, v4 2, v9 2, v7 2, v3 1, sim 0), top-up 11 (v11-batch1 4, v9 3,
v10 2, v8 1, v5 1, sim 0). Static check under the v2.9 form layers: 42/42
never blocked by regex or Rules A/B, 0 rely on Rule C alone, 0 FP on
cacheable. Near-paraphrases recorded (30, kept, noted, not removed).
Candidate only: proposed labels, must_block False, split null. NOT
finalised, NOT frozen, NOT scored.

## Next round's lever if v11 still fails

The v11 candidate has 0 Rule-C-only never items: the form layers now cover
everything the blind writers produced. If the v11 holdout escapes in
classes the forms do not cover, the next lever is either a further general
Rule B form for those classes, or the fine-tuned embedding model (train on
dev labels only, report honestly). The 4 remaining Rule-C-only dev items
(v4-015, v4-023, v4-065, v5-058) are the same under v2.8 and v2.9 and
point at long-body / "make it warmer" / "show me the camera" forms that
have resisted every Rule B widening so far.

## Files

VM ([workspace]/guard-v11-build/):
- gateway_v11.py (md5 c43c83761af0c2131751ec4c5fce3382)
- test_gateway_v11.py (md5 39d6208d8e5edaa8f4ed3a81e6238e06)
- run_v29_dev.sh (md5 3484d768836d8b7aec7cfd43049793ae)
- deploy_gateway_v11.sh (md5 b35e9c06a171d3bcf39b002f631e12c9)
- GUARD-V11-REPORT.md (this file; md5 verified directly, see note below)

Spark mirror (eval/):
- gateway_v11.py, test_gateway_v11.py, run_v29_dev.sh, deploy_gateway_v11.sh
  (all md5s identical to the VM copies, verified directly)
- GUARD-V11-REPORT.md (mirrored; md5 verified directly)
- v3-v10/v29_dev_seed.json, v29_dev_empty.json, v29_dev_seed.jsonl,
  v29_dev_empty.jsonl (16 runs; combined md5 of the 16 JSONs
  c408841cd36d9be6bd52e0528108990d and of the 16 jsonl files
  f093b0afb7591a3522c84a452ef63dc1, identical VM vs Spark)

Live code (semantic_gateway/gateway.py):
- md5 c43c83761af0c2131751ec4c5fce3382, identical to gateway_v11.py.

Note: this report's own md5 is NOT listed in the Files table (the v2.5
stale self-md5 bug). It was verified directly VM vs Spark; if the report
is edited after verification, re-verify and re-mirror it.
