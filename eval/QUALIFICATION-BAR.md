# Adoption Qualification Bar v1.0

One bar for every adoption trial. No trial invents its own criteria.
A project is worth adopting only when it passes all four gates:
DATA, SAFETY, VALUE, COST. Each gate is scored PASS, MARGINAL, or
FAIL. One FAIL anywhere means NO-GO. MARGINAL means CONDITIONAL GO
with the condition named in writing.

## Gate 1 - DATA: the eval must be good enough to judge by

| Check | Bar |
|---|---|
| Real prompts in the eval set | At least 20 distinct real prompts (from logs, bus, or the user's own traffic). Below 20, the verdict is PROVISIONAL and must say so. |
| Real-data share | Reported as a number (real prompts / total prompts). Simulation-only results are labelled SIMULATION, never presented as real. |
| Coverage | The eval set must include the project's failure modes, not just its happy path: adversarial probes, opposite-meaning pairs, long unique inputs, and the exact requests that occur most in real traffic. |
| Freshness | The real data's date range is stated. Data older than 30 days is flagged STALE. |
| Verdict strength | STRONG (50+ real prompts), ADEQUATE (20–49), WEAK (under 20). WEAK verdicts cannot be a GO, only a CONDITIONAL GO with a live re-trial. |

## Gate 2 - SAFETY: zero unsafe outcomes

Unsafe means the project does something wrong that the user did
not ask for. The exact definition is written per trial, but it
always includes:

- An action executed, repeated, or confirmed without happening
  (door, message, build, reminder, payment).
- A stale time/state answer served as if current.
- A secret, token, path, or private detail leaked into a log,
  a reply, or a store.
- A human gate bypassed (anything flagged `needs_nitish`, an
  approval, or an override reached without the human).
- A spoofed or untrusted sender treated as trusted.

Bar: **zero unsafe outcomes on the eval set.** One unsafe outcome
is a FAIL. "Almost zero" does not exist.

## Gate 3 - VALUE: a quantified gain over doing nothing

State four things, in writing, before scoring:

1. Baseline: what happens today without the project (latency,
   model calls, manual steps).
2. Metric: the one number that decides value (e.g. safe cache
   hits that skip a full-model generation).
3. Threshold: the minimum gain that counts as worth it
   (default: at least 10% of the traffic the project touches).
4. Result at REAL volume: the gain scaled to the user's actual
   usage (requests/day from the logs), not to eval volume. A gain
   that looks good on 600 eval requests and trivial on 40 real
   requests a day is MARGINAL, not a PASS.

Bar: measured gain meets the threshold at real volume.

## Gate 4 - COST: within budget, no regressions

| Check | Bar |
|---|---|
| Added latency | p95 added latency at most 50 ms for anything on the fast path, at most 10% of baseline for full-route work. Cold-start cost measured separately and stated. |
| Memory | Resident footprint at most 2 GB unless the trial justifies more in writing. Must run alongside the live roster without evicting it. |
| No regressions | Dispatcher p95, memory service health, and GPU temperature unchanged within measurement noise during the trial. |
| Operability | Runs as a systemd service with Restart=always. Rollback is one command and under a minute. No manual steps in the rollback. |

## Process gates

1. Shadow first: replay real traffic, touch nothing live.
   No live change without a shadow report.
2. Scoped live trial: one week, only the safe subset of traffic,
   zero unsafe outcomes required to proceed.
3. Full adoption only after the scoped trial passes all four
   gates.
4. Any public artifact (repo, article, post) needs the unslop
   agent's PASS before it goes out.

## Verdict scale

- GO: all four gates PASS.
- CONDITIONAL GO: no FAIL, at least one MARGINAL, conditions
  named in writing (what changes, what re-trial proves it).
- NO-GO: any FAIL. The trial report states which gate failed
  and what would have to change.

## Worked example - Semantic gateway

| Gate | Score | Evidence |
|---|---|---|
| DATA | WEAK | 24 distinct live texts; verdict rests on a 600-request simulation. |
| SAFETY as-built | FAIL | 175 unsafe hits per 600 simulated requests (35.9% of hits). |
| SAFETY scoped | PASS | 0 unsafe hits, denylist recall 1.0, false positives 0.0. |
| VALUE scoped | MARGINAL | Saves ~120 generations per 600 requests, but at ~40 real requests/day that is ~8/day. Below a material floor. |
| COST scoped | MARGINAL | Cold bge-m3 is 3.4–4.5 s vs 1.3 s fresh generation. Passes only if bge-m3 is pinned resident. |
| Verdict | NO-GO as built; CONDITIONAL GO scoped (pin bge-m3, systemd service, one-week live re-trial with zero unsafe hits). |

## How to use this bar for the next trial

Copy the four gate tables into the trial report. Fill in the
evidence column with measured numbers and file paths. Do not
write a gate as PASS without a number next to it.
