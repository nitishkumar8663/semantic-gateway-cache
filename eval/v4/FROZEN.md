# Eval set v4 - FROZEN (semantic gateway)

**Version:** v4. **Status: FROZEN 23 Nov 2026 by the parent agent (Muse).**
Labels final. Dev may be scored for sanity (detail allowed). Holdout
scored exactly once, summary only, no detail. Holdout failures are
never read during iteration, never added to the denylist or the seed,
and never used to change the code. A code change after the holdout
scoring needs a new fresh holdout (v5).

**Source:** candidate `eval_set_v4.json` (105 prompts, 34 families,
built by subagent workstream 2, 23 Nov 2026) + parent labelling below.
Candidate file kept as the pre-labelling record.

**Framing (Nitish, 23 Nov 2026): eval traffic is good traffic.** The
v4 verdict stands on the v4 scoring as a whole; the real vs synthetic
split is factual reporting, not a discount. A full GO from the v4
scoring is a full GO.

## Labelling decisions (parent, 23 Nov 2026)

1. **Routes are the real dispatcher's decisions.** Each prompt's route
   is `tier1.route()` (the live Tier 1 routing function) run on its
   text, with two overrides. Bus bodies are forced full (they are not
   dispatcher traffic; tier1's fast hits on 2KB texts are keyword
   artefacts). v4-047 "is the dishwasher done?" is forced full (a PARA
   keyword artefact; it is a state question, not a PARA question).
   v4-080 "what did I say about the car insurance?" stays fast (a
   genuine PARA question; tier1 agrees). Result: 1 fast, 104 full.
   Consequence recorded honestly: the dispatcher's narrow fast
   handlers (exact greeting, narrow time/status, PARA keywords,
   door HA) match almost none of the fresh prompts, so nearly all
   of v4 reaches the gateway. That is what the dispatcher does, not
   a choice to make the test harder.
2. **Bus bodies are cacheable=never, not stable.** Departs from the
   v3 BUS precedent (stable). A bus body is a unique, non-repeatable
   task text; any cache hit on one is a false positive and must count
   unsafe. A hit counting safe under stable would hide false
   positives.
3. **Must_block is true for lights-on and lights-off only.** They are
   the direct analogues of the v3 R-A3 / NM-A lights must-block
   cases (same task frame, new rooms). All other families false,
   including D6 (a conditional action, not a denylist escape).
4. **Stable factual topic families are re-split per question.**
   v3 families are per-question (same family means same answer).
   The fresh writer's topic families (capitals, planets, cooking,
   translations, authors, science) hold different-answer prompts,
   so a within-topic cross-match (Norway's answer served to a
   Canada question) would count as a safe hit although the answer is
   wrong. Re-split into 17 per-question families (paraphrases stay
   together). Never and fast topic families are kept as-is: any hit
   on a never prompt is unsafe regardless of family, and fast
   prompts never reach the gateway, so no correctness blind spot
   there.
5. **Bus is 6 task-literal families (V4-B2..B7), not one BUS family.**
   Each thread is a distinct task. Splitting them puts real traffic
   in both dev (B2, B3, B7) and holdout (B4, B5, B6). Departs from
   the v3 single-BUS-family simplification; recorded here.
6. **Lists stays one family, full/never.** Mixed mutation/query, but
   the worst-case label (never) covers both: a cached list answer
   goes stale as soon as the list changes.

## Counts

| | Prompts | Families |
|---|---|---|
| Total | 105 | 45 |
| Dev | 70 | 29 |
| Holdout | 35 | 16 |
| Real (bus envelopes) | 16 | 6 |
| Synthetic / eval-derived | 89 | 39 |
| Fresh eval prompts | 81 | 38 (21 topic + 17 re-split) |
| Demo / test fixtures | 8 | 7 |

Routes: fast 1, full 104. Cacheable: stable 30, never 67, ttl24 8.
Holdout: 6 real prompts (bus B4, B5, B6), 4 ttl24 prompts
(memory-lookup), 4 must_block prompts (lights-on).

## Split method

By family, seeded shuffle per category (seed 20261123),
ceil(n/3) families to holdout, stratified by category. One parent
adjustment: the shuffle put both ttl24 families (smalltalk,
memory-lookup) in holdout, leaving dev with no ttl24 items, so
smalltalk was moved to dev. Holdout families (16): action
lights-on, door-unlock; agent-task B4, memory-lookup, B5, B6;
factual cooking-chicken, science-sea, D2, planets-mercury,
science-rainbow, D5, authors-1984, translations-german;
perception appliance-state; time time-now.

## Pass criteria

Same four gates as `eval/v3/PASS_CRITERIA.md` (AGREED 23 Nov 2026,
Nitish in writing). No threshold changed, so no version bump to the
criteria. Applied to v4: DATA is the v4 set above (holdout 35
prompts / 16 families, 6 real); SAFETY is 0 unsafe dev and holdout
(unweighted and traffic-weighted), denylist recall 1.0, FP 0.0 on
gateway traffic, must-block all blocked, 0 never items stored;
VALUE is non-seed safe hits at least 10% of full-route traffic;
COST is p95 at most 50 ms fast path / 10% full-route, resident at
most 2 GB, no regressions, systemd + rollback under a minute. All
four gates conjunctive: one FAIL anywhere is NO-GO. MARGINAL is
CONDITIONAL GO with the condition named in writing.

## Files

- `eval_set.json` - the frozen v4 set (all 105, labelled, with split)
- `eval_set_dev.json` - dev split (70 prompts, 29 families)
- `eval_set_holdout.json` - holdout split (35 prompts, 16 families)
- `FROZEN.md` - this file
- `eval_set_v4.json`, `V4-REPORT.md` - the candidate and its report
  (pre-labelling record, kept alongside)

## Public split note

This is the public copy of the frozen v4 set. It differs from the private frozen original:

- Prompts v4-004 and v4-020 in the holdout (same two in the full set) are redacted: their text is replaced with a redaction note. One held personal financial detail, one held home-security detail. Their labels are kept.
- Rewordings applied to the public copy: em dashes removed, an unlock example reworded, internal project references removed (including a demo source label).
- The reported scores were measured on the private frozen originals.

Original (private) md5s:

- `eval_set.json`: 9d6e9ada7fc5760bcd3a2b3ed6603982
- `eval_set_dev.json`: f37ead8ffffea80758b6b08b56805107
- `eval_set_holdout.json`: 136bf650beb0d1fd28a77041020141c5

Public copy md5s (at the time this note was written; they change if the public copy is re-cleaned):

- `eval_set.json`: ed525b6431b95dbbc460ae7dddbae252
- `eval_set_dev.json`: dc82fd713769ab52378c395efe31c1aa
- `eval_set_holdout.json`: 4a469a30f60cad7647f3aacd09ff4d32
