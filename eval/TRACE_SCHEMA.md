# Trace schema v3.0 (E2)

The trace fields every scorer v3.0 run records per request, in the
`--detail` JSONL output (one JSON object per line, in run order).
This is the schema the evals are scored from. The live dispatcher
does not log these fields yet; the patch that would add them is
specified in `dispatcher-instrumentation-spec.md` (spec only, not
applied).

## Detail row fields

| Field | Type | Meaning |
|---|---|---|
| `i` | int | Original prompt index in the workload file. Stable across runs and shuffles. |
| `order` | int | Position in this run. Differs from `i` only when `--shuffle-seed` is used. |
| `text` | string | Prompt text, truncated to 160 chars. |
| `group` | string | Paraphrase family id. |
| `category` | string | factual / generative / chatter / para / action / time-state / perception / greeting / agent-task. |
| `cacheable` | string | stable / ttl24 / never. |
| `route` | string | fast / full (dispatcher route label). |
| `request_ts` | float or null | Epoch seconds of the request on the workload timeline. Null in v1/v2 (no timestamps); set for every v3 prompt. |
| `consulted` | bool | Whether the request reached the cache lookup. False when route-scoped or denylist-blocked. |
| `blocked_by` | string or null | `route:fast-path-first` or `denylist:<pattern>`. |
| `hit` | bool | Best similarity >= threshold. |
| `cache_status` | string | One of: `blocked-route`, `blocked-denylist`, `hit-safe`, `hit-unsafe-never`, `hit-unsafe-stale-ttl24`, `miss-stored`, `miss-expired`. |
| `route_decision` | string | The route label that decided consultation (same as `route` in the eval; in production this is the dispatcher's decision with its config version). |
| `similarity` | float or null | Best cosine similarity, 4 dp. Null when not consulted. |
| `matched_prompt` | string or null | Best-matching stored prompt text, truncated to 120 chars. |
| `matched_entry_id` | string or null | `seed-N` for a seed entry, `workload-N` for an entry stored during the run. |
| `matched_entry_ts` | float or null | Epoch seconds the matched entry was created (seed `created_at`) or stored (request ts at store time). |
| `matched_entry_age_s` | float or null | `request_ts - matched_entry_ts`. Null when either ts is missing. This is what the TTL and the stale-unsafe rule are computed from. |
| `entry_source` | string or null | `live-store-seed` or `shadow-workload`. |
| `unsafe_kind` | string or null | `never` (cacheable never) or `stale-ttl24` (ttl24 hit on an entry older than the TTL). Null when safe or not a hit. |
| `expired_miss` | bool | A match existed but only lost to TTL expiry (scoped only). |
| `must_block` | bool | True for the 5 named denylist-escape cases. |
| `real_live_n` | int | Live audit rows for this exact text (0 for synthetic). |
| `weight` | int | Traffic weight = max(1, real_live_n). |
| `embed_ms` | float | Embedding latency for this request. First value in a run is the cold-load cost. |
| `lookup_ms` | float | Store lookup latency (excludes embedding). |
| `total_ms` | float | embed + lookup. |
| `store_size` | int | Store entries after this request. |

## Summary fields added in scorer v3.0

- `scorer_version`, `trace_schema_version`, `threshold` (actual),
  `normalise`, `seed_mode`, `shuffle_seed`.
- `stale_ttl24_hits`, `never_items_stored`.
- `full_route_requests`, `full_route_safe_hits`,
  `full_route_safe_hit_rate` (the VALUE numerator).
- `weighted_requests`, `weighted_hits`, `weighted_hit_rate`,
  `weighted_safe_hits`, `weighted_unsafe_hits`,
  `weighted_unsafe_rate`.
- `denylist_false_positive_gateway_traffic`,
  `denylist_false_positive_bus_bodies` (split of the old combined FP).
- `must_block_total`, `must_block_blocked`, `must_block_hit`,
  `must_block_unsafe`, `must_block_detail`.
- `hit_rate_ci95`, `unsafe_rate_ci95` (Wilson 95% CIs).
- `seed_ts_min`, `seed_ts_max` (real seed creation times).
