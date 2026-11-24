# Pass criteria - semantic gateway (v3 eval case)

**Status: AGREED 23 Nov 2026. Nitish agreed these criteria in writing
(chat, 23 Nov 2026: "Agree the pass criteria, start C1-C6"). No numbers
were changed, so no version bump.** Code changes (C1-C6) are judged
against these criteria. If he changes any number below, the FROZEN.md
manifest must be updated and the version bumped.

Source: the qualification bar (`eval/QUALIFICATION-BAR.md` v1.0)
plus the EDD assessment (E7). All four gates are conjunctive: one
FAIL anywhere means NO-GO. MARGINAL means CONDITIONAL GO with the
condition named in writing.

## Gate 1 - DATA

| Check | Bar |
|---|---|
| Eval set | v3, frozen (see FROZEN.md). Dev 110 prompts / 33 families, holdout 44 prompts / 14 families. |
| Real prompts | 63 real-sourced in v3 (46 dev, 17 holdout). Verdict strength ADEQUATE (20-49 real prompts in holdout terms: 17 real in holdout is WEAK on its own; the dev+holdout total is what the verdict rests on, and it must say so). |
| Holdout discipline | Holdout scored twice only (baseline and final). Holdout failures are NEVER read during iteration. A holdout failure's text is never added to the denylist or the seed. |
| Freshness | Real data spans 5-12 Nov 2026 (bus) and the audit log (undated, no timestamps). Data older than 30 days is flagged STALE. Fresh traffic must refill the holdout on a cadence; "settled" is a version, not a permanent state. |

## Gate 2 - SAFETY (zero unsafe outcomes)

| Check | Bar |
|---|---|
| Unsafe hits, dev | 0, unweighted AND traffic-weighted. Unsafe = cacheable `never` hit, OR `ttl24` hit on an entry older than 24h. |
| Unsafe hits, holdout | 0, unweighted AND traffic-weighted. Same definition. |
| Denylist recall | 1.0 over never items that reach the denylist (route=full). |
| Denylist false positives | 0.0 on gateway traffic. BUS bodies are reported separately and are not in the denominator. |
| Must-block cases | 5/5 blocked (the denylist escapes: "turn the lights on", "lights on in the living room", both real perception alerts, "hi'; echo PWNED; '"). |
| Store poisoning | 0 never items stored in a scoped run. (Follows from recall 1.0; reported as its own check because a stored never item is a future unsafe hit.) |

## Gate 3 - VALUE (quantified gain over doing nothing)

| Check | Bar |
|---|---|
| Baseline | Without the gateway, every full-route request costs a full-model generation (~1,310 ms warm). |
| Metric | Safe cache hits that skip a full-model generation, as a share of full-route traffic. |
| Threshold | At least 10% of full-route traffic saved. Non-seed safe hits are reported separately; seed-matched hits do not count toward the threshold. |
| Result at real volume | Saved generations/day reported at measured real volume. Volume is currently an ASSUMPTION ("~40 requests/day", no dated source); the sensitivity table (6/20/40/86 per day) is reported alongside until E2 instrumentation lands and the volume is measured. A gain that clears 10% on the eval set but is trivial at real volume is MARGINAL, not PASS. |

## Gate 4 - COST (within budget, no regressions)

| Check | Bar |
|---|---|
| Added latency | p95 added latency at most 50 ms for anything on the fast path, at most 10% of baseline for full-route work. Cold-start cost measured separately and stated. |
| Memory | Resident footprint at most 2 GB. Must run alongside the live roster without evicting it (bge-m3 0.69 GB; qwen3.6 must stay resident). |
| No regressions | Dispatcher p95, memory service health, and GPU temperature unchanged within measurement noise during the trial. |
| Operability | Runs as a systemd service with Restart=always. Rollback is one command and under a minute. No manual steps in the rollback. |

## Process gates

1. Shadow first: the frozen v3 eval case is the shadow report. No live change without it.
2. Scoped live trial: one week, only the safe subset of traffic, zero unsafe outcomes required to proceed. 0 unsafe in 280 requests gives a 95% upper bound of 1.1% on the true unsafe rate (rule of three).
3. Full adoption only after the scoped trial passes all four gates.
4. Any public artifact (repo, article, post) needs the unslop agent's PASS before it goes out.

## Verdict rule (pre-registered)

- GO: all four gates PASS on dev AND holdout.
- CONDITIONAL GO: no FAIL, at least one MARGINAL, conditions named in writing.
- NO-GO: any FAIL. The trial report states which gate failed and what would have to change.
- Mechanism-fail rule (E5): if no threshold clears zero-unsafe AND the 10% value bar on dev, the mechanism (raw cosine on bge-m3) fails and the verdict is NO-GO for that mechanism. The next step is a different mechanism (exact match plus normalisation only, or a different similarity signal), not a lower threshold.
