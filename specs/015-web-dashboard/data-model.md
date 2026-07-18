# Data Model: The Web Dashboard (One Face for Any Brain)

Phase 1 of `plan.md`. Wire additions (the view channel), the dashboard's
in-memory model, and the endpoint payloads. Wire forms follow B6's
discipline: canonical JSON, no wall-clock in tap-published payloads;
dashboard endpoint payloads MAY carry the dashboard's own derived ages
(liveness is the consumer's clock, not the run's).

## 1. Wire additions (the world-view channel, tap side)

| Subject | Payload |
|---|---|
| `pra.v1.run.<id>.tele.view.static` | `{run, seq, kind, static}` — `kind` names the view family (v1 ships `"rover"`); `static` is the kind-defined one-time part (rover: the `layout()` dict). Published on first drain after `attach_layout`, re-published on a slow heartbeat (default 5 s) so late attachers catch it. |
| `pra.v1.run.<id>.tele.view.live` | `{run, seq, kind, ...kind fields}` — rover: `{episode, x, y, theta, bump}` per `record_step`/`record_reset`. |

Both join the tap's existing mirrored seq family (buffer, pump, drop
derivation, no-backpressure — nothing new to get wrong). The adapter
object returned by `NatsTap.world_view(kind)` exposes exactly
`attach_layout(layout)`, `record_reset(*a)`, `record_step(*a)` — the
RoverTelemetry call surface, so `make_rover_body(..., telemetry=adapter)`
works unchanged. Kind-specific argument mapping lives in the adapter
(rover: reset → `(x, y, theta)`, step → `(x, y, theta, bump)`).

## 2. RunModel (dashboard-side, built from received payloads only)

- **Identity/state**: `run_id`; `state ∈ {running, paused, completed,
  unknown}` (from status/inspect payloads; `unknown` until anything
  arrives); `completed_summary` when published.
- **Liveness**: `last_seen` monotonic stamp per run → endpoint serves
  `age_seconds` (the consumer's clock; honest aging, never reset by the
  dashboard's own requests).
- **Census**: `latest` (the payload verbatim) + `history` (bounded deque,
  default 512, of `{seq, population, best_dim}`).
- **Counters**: the last-seen counters block from `inspect` replies plus
  wire-level `wire_errors` (malformed payloads counted, skipped) and
  `seq_gaps` (observed discontinuities in the mirrored family — rendered,
  not repaired).
- **Snapshots**: bounded list of received snapshot notices.
- **World view**: `kind`, `static` (latest), `live` (latest), plus the
  client-side capped trail (page state, not model state).
- **Anatomy**: the `started` status payload (obs_dim, n_actions,
  n_streams, episode_mode) when seen.

`DashboardModel` holds `{run_id: RunModel}` + the discovery list; runs
materialize from any observed `pra.v1.run.<id>.…` traffic or a discover
reply; never auto-evicted.

## 3. Endpoints (the page's and the tests' shared surface)

| Endpoint | Payload |
|---|---|
| `GET /` | the self-contained page (`text/html`). |
| `GET /runs` | `{runs: [{run, state, age_seconds, has_view}]}` sorted by run id. |
| `GET /run/<id>/state` | everything both modes render: `{run, state, age_seconds, anatomy, census, census_history, counters, snapshots, view: {kind, static, live} \| null, completed_summary}`. Unknown run → 404 with `{error}`. |
| `POST /run/<id>/ctrl` | body `{cmd, ...}` → forwarded via `transport.request` (5 s; snapshot 60 s) → the run's reply verbatim; transport failure/timeout → `{ok: false, error}`. Unknown run → 404. |

The page renders simple mode (state, liveness, plain census, SVG world
view when `view.kind == "rover"`, present-but-unrenderable note for other
kinds) and advanced mode (history charts, per-dim histogram from
`census.dims`, counters, snapshot list, control buttons) from the same
`/state` payload — one poll, two tabs.

## 4. State machines

- **RunModel.state**: `unknown → running|paused|completed` from payloads;
  control replies update it too (a pause reply ⇒ paused) — but payloads
  win (the run is the authority).
- **View static**: `absent → present(kind)`; heartbeat re-publishes are
  idempotent merges.
- **Ctrl POST**: request → verbatim reply | timeout-error; no dashboard
  retries (the human is the retry policy of an instrument).
