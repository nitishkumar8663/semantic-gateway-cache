# Guard v2.8-guard (guard v2.4) - round-5 build report

Date: 24 Nov 2026 (build done 23 Nov 2026, ~23:48-00:15 GMT)
Gateway version: v2.8-guard, guard v2.4, denylist v1.5
Live: shadow only, :18795, semantic-gateway.service, upstream stub
Dev base: 466 prompts (v3 dev 110, v4 dev 70, v5 dev 59, v6 dev 56, v7 dev 51,
v8 dev 62, v9 dev 58). Must-block total 19.

## Verdict on dev: PASS on all gates, every set, both modes

| set | mode | req | recall | must-block | never stored | unsafe | FP (gateway) | non-seed safe rate | median ms | p95 ms |
|-----|------|-----|--------|------------|--------------|--------|--------------|--------------------|-----------|--------|
| v3 | empty | 110 | 1.0000 | 5/5 | 0 | 0 | 0.00 | 0.2568 | 15.9 | 21.6 |
| v3 | seed | 110 | 1.0000 | 5/5 | 0 | 0 | 0.00 | 0.2432 | 15.5 | 30.2 |
| v4 | empty | 70 | 1.0000 | 4/4 | 0 | 0 | 0.00 | 0.0571 | 13.4 | 19.1 |
| v4 | seed | 70 | 1.0000 | 4/4 | 0 | 0 | 0.00 | 0.0429 | 14.3 | 25.1 |
| v5 | empty | 59 | 1.0000 | 2/2 | 0 | 0 | 0.00 | 0.2712 | 14.0 | 18.5 |
| v5 | seed | 59 | 1.0000 | 2/2 | 0 | 0 | 0.00 | 0.2712 | 16.6 | 27.4 |
| v6 | empty | 56 | 1.0000 | 2/2 | 0 | 0 | 0.00 | 0.0714 | 13.6 | 17.6 |
| v6 | seed | 56 | 1.0000 | 2/2 | 0 | 0 | 0.00 | 0.0714 | 15.3 | 27.1 |
| v7 | empty | 51 | 1.0000 | 2/2 | 0 | 0 | 0.00 | 0.0588 | 13.6 | 15.6 |
| v7 | seed | 51 | 1.0000 | 2/2 | 0 | 0 | 0.00 | 0.0588 | 15.1 | 24.7 |
| v8 | empty | 62 | 1.0000 | 2/2 | 0 | 0 | 0.00 | 0.0645 | 14.2 | 23.9 |
| v8 | seed | 62 | 1.0000 | 2/2 | 0 | 0 | 0.00 | 0.0645 | 15.2 | 32.3 |
| v9 | empty | 58 | 1.0000 | 2/2 | 0 | 0 | 0.00 | 0.0345 | 13.8 | 15.8 |
| v9 | seed | 58 | 1.0000 | 2/2 | 0 | 0 | 0.00 | 0.0345 | 15.3 | 22.1 |

SAFETY: recall 1.0, must-block 19/19, never stored 0, unsafe 0, FP 0.0 on
gateway traffic, all 14 runs. VALUE: non-seed safe rates unchanged from v2.7
(v9 dev 0.0345, still below the 0.10 holdout bar; dev value is not the gate,
holdout is). COST: p95 15.6-32.3 ms, all under the 50 ms budget (p95
recomputed from the .jsonl detail, consulted rows only; the JSON summaries
carry no p95 field). Median 13.4-16.6 ms.

v9 dev, the round-4 failure set, is fully fixed: recall 0.7826 -> 1.0,
must-block 0/2 -> 2/2, never stored 5 -> 0. v7 dev also improved (form
recall 20/21 -> 21/21) because "lower" joined the verb class.

v3 FP caveat, unchanged: the v3 FP on safe is still 0.0455 (3/66 safe, long
bus-body artefacts v3-143/145/146), pre-existing and identical under v2.5,
v2.6 and v2.7. Gateway-traffic FP is 0.0 on all 14 runs.

Unit tests: 48 tests, all OK in 14.1 s on the Spark (including the live
bge-m3 test_real_margin_separates_dev).

## Mechanism

No denylist, prototype, threshold or margin change. No dispatcher, routing or
live-serving change. Shadow only.

### 1. Rule C creative-draft exemption (the documented round-5 lever)

New `is_creative_draft()` in `guard_margin_check`. A prompt is exempt from
the Rule C margin block when it starts with a creative verb
(write, compose, draft, craft, pen, invent, imagine, create, with optional
"please" and optional "me") followed by a creative artefact noun (message,
poem, story, song, toast, speech, haiku, limerick, novel, letter, card,
lyrics, verse, tale, ode, sonnet, ballad, anthem, jingle, slogan, caption,
blog, essay, article, script, play, screenplay, chorus). "make" is
deliberately NOT a creative verb (same reason as the v1.5 regex guard:
"make it warmer in here" is an action). The exemption returns
blocked=False but still computes and returns the margin for observability.

Why it cannot let a messaging task through: "message to" is regex-blocked
before Rule C ever runs. "write a reminder" is not exempt (reminder is not
a creative artefact). "write a python function" is not exempt (function is
not a creative artefact).

Measured FP risk on dev, honestly: the exemption changes nothing on the
466 dev prompts. All 22 dev prompts starting with a creative verb are
cacheable (stable/ttl24), none is a never item, and none is a must-block.
The 5 Rule C reachers (v4-015, v4-023 bus bodies; v4-065 "make it warmer
in here"; v5-058 "Show me the front door camera."; v7-032 "Lower the
thermostat to 18 degrees.") are none of them creative drafts; v7-032 is
now form-blocked anyway (see below).

Live probe of the v7 holdout FP: "Write a birthday message for my mum" was
blocked live under v2.7 by denylist:guard-margin (margin 0.2574, sim_a
0.8343, sim_s 0.5769, class imperative, thr 0.20). Under v2.8 it is NOT
blocked (live probe: miss-stored, 17.02 ms). The FP is fixed.

### 2. Rule B v6 widening (general pattern classes, not per-prompt)

(a) Verb class: _ACTION_VERBS += lower, raise, cancel, change, adjust,
increase, decrease, reduce, move, schedule, reschedule, postpone, confirm.
"check" stays out (it heads information requests). This feeds both Rule A
and the softened-imperative form. Wh-word guard retained: genuine
questions ("can you tell me...", "could you explain...") do not FP.

(b) Completion-state form: _LIVE_ENTITIES += dinner, lunch, breakfast,
supper, meal, food, roast, soup, cake, bread, pasta, rice, clothes,
dishes, room. _STATE_WORDS += dry, wet, damp, clean, dirty, full, empty,
warm, cool, cooked, baked, frozen, fresh, stale.

(c) Live-fact forms: _RULE_B_LIVE_FACT_RE ("what time is sunset/sunrise/
moonrise/moonset/dawn/dusk/high tide/low tide/the tide", no day marker
needed) and _RULE_B_LIVE_FACT_DAY_RE ("what time is <noun>
today/tomorrow/tonight"). "what time is it in London" does not match.

All 5 v9 dev escapes are now caught by form layers (verified in the live
probes): lower-heating -> rule-b:softened-imperative, dinner-ready ->
rule-b:state-query, cancel-dentist -> rule-b:softened-imperative,
washing-dry -> rule-b:state-query, sunset-time -> rule-b:live-fact.
"Lower the thermostat to 18 degrees." is now Rule A:lower.

Form-layer recall (regex + Rules A/B, never route=full, 466 dev prompts):
v3 31/31, v4 43/46, v5 20/21, v6 23/23, v7 21/21, v8 24/24, v9 23/23.
The only form-layer misses are the 4 Rule C reachers (v4-015, v4-023,
v4-065, v5-058). Form FP on cacheable: v3 6/66 (pre-existing bus bodies
plus v3-007, v3-008, v3-065), v4-v9 0. A v2.7 comparison probe gave an
identical v3 FP list: zero new FPs from v2.8.

### 3. What was declined and why

- Fine-tuned embedding model: NOT attempted. Form widening + the Rule C
  exemption reached dev recall 1.0 with FP 0.0, so the fallback was not
  needed. It stays the fallback if v10 still fails.
- Safe-prototype tuning for the birthday-message FP: NOT done. The
  creative-verb exemption fixes the FP class generally without touching
  the prototypes, which would have moved the margin for all prompts.
- Intent classifier: stays declined (round-3 LOFO CV: best honest point
  recall 4/9 at FP 0).
- Any per-prompt pattern for a specific v9 prompt: none added. Every new
  form is a general class (verb class, entity/state words, live-fact
  forms).

## Deploy and rollback

- Deploy script: deploy_gateway_v10.sh (Spark eval/). Backs up v2.7 code/config,
  installs gateway_v10.py, config unchanged, store kept live (33 entries).
- Rollback script: rollback_gateway_v9.sh (written by the deploy script).
  ROLLBACK TESTED 24 Nov 00:04 GMT: /health returned v2.7-guard, guard
  v2.3, embedder warmed. v2.8 then re-deployed; /health verified
  v2.8-guard, guard v2.4, denylist v1.5, threshold 0.90/0.85/0.85,
  guard_margin 0.2/0.1, 33 action + 17 safe prototypes, embedder warmed.
- Live probes on :18795 (13 queries, all OK): the 5 v9 dev escapes blocked
  by their Rule B v6 forms (0.04-0.09 ms); the birthday message unblocked
  (miss-stored, 17.02 ms); "send a message to mum" blocked (regex);
  "Lower the thermostat to 18 degrees." blocked (Rule A:lower); "At what
  temperature does water boil?", "What is the weather like on Mars?", "Is
  anyone at the party?", "Write a haiku about autumn rain.", "What is the
  capital of France?" all unblocked (hit-safe). Live store 34 entries
  (33 + the birthday message stored by the probe).

## The v10 candidate set (summary; full detail in V10-REPORT.md)

108 prompts, 101 families: stable 40, never 44, ttl24 24. Two blind writer
batches (100 + 50). Collisions removed: batch 1 35 (v3 2, v4 2, v5 9, v6 6,
v7 8, v8 5, v9 3), top-up 7 (v6 2, v7 2, v8 1, v10-batch1 2). Static check
under the v2.8 form layers: 38/44 never blocked by regex or Rules A/B, 6
rely on Rule C alone, 0 FP on cacheable. Candidate only: proposed labels,
must_block False, split null. NOT finalised, NOT frozen, NOT scored.

## Next round's lever if v10 still fails

The 6 v10 never items that rely on Rule C alone point at the next widening
classes, if the v10 holdout escapes in the same forms:
- Live-fact variants: "When does the sun go down today?" (a "when does
  the sun go down" form, not "what time is sunset"); "Has the post
  arrived today?" (entity "post" missing from _LIVE_ENTITIES).
- Presence/state questions: "Is the car charged enough for tomorrow?"
  (entity "car", "charged enough" form); "Can you check if the oven is
  still on?" ("check if" form, "check" is deliberately not an action
  verb); "Is my phone charging in the bedroom?" (progressive "charging",
  not the state word "charged").
- Agent-task with no form: "What is on my calendar tomorrow?" (same class
  as v9-068).
If those classes still do not generalise, the fine-tuned embedding model is
the next lever (train on dev labels only, report honestly).

## Files

VM ([workspace]/guard-v10-build/):
- gateway_v10.py (md5 f125f34adedff26b33a617d8c43eae12)
- test_gateway_v10.py (md5 c4fa245884f126219749feb36e119acb)
- run_v28_dev.sh (md5 eb8a1a20886a675bfad09e8f83f28c71)
- deploy_gateway_v10.sh (md5 afa245d3f05836b889f77111669ab691)
- GUARD-V10-REPORT.md (this file; md5 verified directly, see note below)

Spark mirror (eval/):
- gateway_v10.py, test_gateway_v10.py, run_v28_dev.sh, deploy_gateway_v10.sh
  (all md5s identical to the VM copies, verified directly)
- GUARD-V10-REPORT.md (mirrored; md5 verified directly)
- v3-v9/v28_dev_seed.json, v28_dev_empty.json, v28_dev_seed.jsonl,
  v28_dev_empty.jsonl (14 runs; all 14 JSON md5s verified identical to the
  VM mirror, sorted comparison)

Live code (semantic_gateway/gateway.py):
- md5 f125f34adedff26b33a617d8c43eae12, identical to gateway_v10.py.

Note: this report's own md5 is NOT listed in the Files table (the v2.5
stale self-md5 bug). It was verified directly VM vs Spark; if the report
is edited after verification, re-verify and re-mirror it.
