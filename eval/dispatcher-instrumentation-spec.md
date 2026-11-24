# Dispatcher instrumentation spec (E2) - SPEC ONLY, NOT APPLIED

**Status:** specification only. Nothing in this file has been applied
to the live dispatcher. Applying it is a dispatcher code change
(config + audit writer), not part of the v3 eval build, and must not
be done as a side effect of eval work. It is written here because
E2 found the VALUE gate cannot be decided without a dated volume
number, and the audit log currently has no timestamps at all.

## The gap it closes

The dispatcher audit log (`services/tier1-dispatcher/audit.jsonl`,
569 rows) has no timestamp field and records no route-decision
config version. Consequences, all measured in the eval audit:

- Daily volume cannot be derived. "~40 requests/day" has no dated
  source; the plausible span (119 live rows over ~3 weeks) suggests
  ~6/day. The VALUE gate rests on an assumed number.
- A text's route can change silently between runs (config edits),
  so a label in the eval set can go stale without any record.
- The 24h TTL cannot be measured on real data, because entry age
  needs request times.

## Fields to add to each audit row

| Field | Type | Meaning |
|---|---|---|
| `ts` | float | Epoch seconds when the request was received. The missing field. |
| `config_version` | string | Dispatcher config version (or git SHA) in force for this request, so a route decision is traceable to the config that made it. |
| `route_decision` | string | The route taken (fast / full), kept as `route` is today; add `route_reason` already exists as `reason`. No change needed beyond `config_version`. |
| `cache_status` | string or null | Null when the request never consults the gateway. Otherwise one of `hit-safe`, `hit-unsafe-never`, `hit-unsafe-stale-ttl24`, `miss-stored`, `miss-expired`, `blocked-denylist`, `blocked-route`. Same vocabulary as the eval trace schema v3.0. |
| `cache_similarity` | float or null | Best cosine similarity for the request, when consulted. |
| `cache_matched_entry_id` | string or null | `seed-N` or `workload-N` style id of the matched entry, when there is a match. |
| `cache_entry_age_s` | float or null | Age of the matched entry in seconds, when there is a match. |

## Gateway log change (same patch)

`cache_hits.log.jsonl` (gateway side) gains the same three fields
per lookup: `matched_entry_id`, `matched_entry_age_s`,
`cache_status`. The gateway already logs `ts`, `hit`,
`latency_ms`, `similarity`, `text`.

## What applying this enables

- A dated requests/day number, split live vs dry-run, from the log
  itself. The VALUE gate then uses a measured volume, and the
  sensitivity table (6/20/40/86 per day) collapses to one number.
- TTL evidence on real data: entry age is recorded, so stale hits
  are countable without a simulation.
- Route-label freshness: eval sets can be rebuilt from the log with
  the config version attached, and a label that no longer matches
  the live config is detectable.

## What it must not do

- Must not change routing, thresholds, or any live behaviour. It
  is a logging-only change.
- Must not log prompt text beyond what the audit already logs
  (it already logs `text`).
- Must not be applied from the eval harness or as part of a
  scoring run. It belongs to a dispatcher change with its own
  review.

## How to verify after applying

- New rows carry `ts` and `config_version`; old rows keep their
  shape (no backfill).
- Rebuild the eval set from the log: `real_live_n` per prompt and
  the requests/day number both come from dated rows.
- The v3 VALUE sensitivity table is replaced by the measured
  volume in the next eval version.
