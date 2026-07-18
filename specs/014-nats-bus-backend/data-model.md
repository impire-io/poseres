# Data Model: The External Bus Backend (NATS at the Seams)

Phase 1 of `plan.md`. Entities, wire payloads, and state machines. All
wire forms are canonical JSON (fixed key order, compact separators,
`ensure_ascii=True` — the recorder's discipline) and carry **no
wall-clock time** (research R3): ordering facts are sequence numbers
and the run's own counters.

## 1. Run identity

- **`run_id`**: token naming one live run on the bus. User-supplied or
  default `run-<8 hex>` (uuid4 — OS entropy, never the engine
  generator). Validation: nonempty, no `.` `*` `>` whitespace (NATS
  subject atoms); violations raise `ValueError` at tap construction.
- Appears in every run-scoped subject and every payload (`run` key).

## 2. Subjects (the scheme, `subjects.py`)

| Constant | Subject | Direction |
|---|---|---|
| `status_subject(run_id)` | `pra.v1.run.<run_id>.status` | tap → world |
| `step_subject(run_id)` | `pra.v1.run.<run_id>.tele.step` | tap → world |
| `episode_subject(run_id)` | `pra.v1.run.<run_id>.tele.episode` | tap → world |
| `census_subject(run_id)` | `pra.v1.run.<run_id>.tele.census` | tap → world |
| `snapshot_subject(run_id)` | `pra.v1.run.<run_id>.tele.snapshot` | tap → world |
| `control_subject(run_id)` | `pra.v1.run.<run_id>.ctrl` | request/reply |
| `DISCOVER_SUBJECT` | `pra.v1.discover` | request/reply, all runs answer |

`pra.v1.brain.*` is reserved, unimplemented (the inter-brain horizon).
A scheme change is a `v2` root; `v1` names never mutate.

## 3. Telemetry payloads (tap → world, fire-and-forget)

- **StepEvent** (`tele.step`): `{run, seq, stream, episode, step,
  action, obs}` — `seq` is the tap-wide monotone sequence; `stream` is
  the world's construction index (0..K−1); `episode`/`step` are the
  mirrored counters; `action` is the routed action index; `obs` is the
  post-step observation as a float list (a copy taken at mirror time —
  never a live reference).
- **EpisodeEvent** (`tele.episode`): `{run, seq, stream, episode,
  kind}` with `kind ∈ {"boot", "reset"}` — boot is a continuous-mode
  single boot; reset is an episodic world reset.
- **Census** (`tele.census`): `{run, seq, population, dims, best_dim,
  best_score, pred_err_ema, steps, episodes}` — the viewer's
  `_learning()` reading (frame states scored on copies with the run's
  own scorer; `dims` maps dim → count, keys sorted ascending), plus the
  tap's mirrored counters at derivation time. Absent until the first
  successful derivation; a torn read repeats the last good reading.
- **SnapshotNotice** (`tele.snapshot`): `{run, seq, snapshot_id,
  step, cycle, population, format_version}` — the engine's own write
  metadata, minus the wall-clock timestamp, plus the id the store
  returned.
- **Status** (`status`): `{run, seq, state, ...}` where
  `state ∈ {"started", "completed"}`; `started` carries
  `{obs_dim, n_actions, n_streams, episode_mode}` (the mounted
  anatomy's public numbers); `completed` carries
  `{summary: <canonical per-seed summary object>}` via `tap.finish()`.

## 4. Control payloads (request/reply, `control.py`)

Request: `{cmd, ...}`. Reply: `{ok: true, ...}` or
`{ok: false, error: "<what and why>"}`. The run never observes a
malformed request (error replies come from the tap's listener thread).

| `cmd` | Request extras | Success reply |
|---|---|---|
| `inspect` | — | `{ok, run, state, steps, episodes, census, counters}` — `state ∈ {"running","paused","completed"}`; `counters` is §6 |
| `pause` | — | `{ok, state: "paused", position}` — position = mirrored steps at gate arm time; idempotent (`already paused` noted in reply) |
| `resume` | — | `{ok, state: "running"}`; idempotent |
| `snapshot` | — | `{ok, snapshot_id, step, cycle}` — sent when the next C4 write is observed (deferred fulfillment, research R5) |

Error replies (exact conditions, all contract-tested): unknown `cmd`;
non-JSON or non-object request; `snapshot` with no store injected or
`snapshot_every_n_cycles == 0` (names the missing configuration);
`snapshot` when the run completed before the next boundary; any command
after `completed` (except `inspect`, which reports it).

**Discover** (`pra.v1.discover`): request `{}` (payload ignored); every
live tap replies `{run, state, subjects: {status, step, episode,
census, snapshot, ctrl}}` — a consumer discovers runs without guessing
names.

## 5. The tap's internal state (`tap.py`)

- **Mirror buffer**: `collections.deque(maxlen=buffer_size)` (default
  4096) of ready-to-serialize tuples. Run thread appends only;
  publisher thread drains only. Drop-oldest on overflow; drops are
  derived from sequence gaps, never counted on the run path.
- **Sequence counter**: one tap-wide monotone int, assigned at mirror
  time (run thread). Also stamps census/snapshot/status messages
  (publisher/listener side) — one total order per run, gaps meaningful
  only within `tele.step`/`tele.episode` (the mirrored family).
- **Pause gate**: `threading.Event` (set = running). Checked at wrapped
  `step()`/`reset()` entry. `ControlState` (below) is the only writer.
- **Captured references**: the `FrameStore` (from `bus_factory`), the
  inner snapshot store (from `wrap_store`), the run's scorer config —
  all read-only from the publisher thread, viewer discipline.

## 6. Counters (outside the learning surface, FR-012)

On the tap object, plain ints read by `inspect` and tests:
`events_mirrored`, `events_published`, `events_dropped` (derived),
`publish_failures`, `reconnects`, `census_published`,
`control_requests`, `control_errors`. None are ever read by the engine,
a drive, a scorer, or a world.

## 7. State machines

**Run state** (as the control plane reports it):
`running ⇄ paused` (pause/resume), `running|paused → completed`
(`tap.finish()`; terminal). Pause requests during `completed` → error
reply; inspect always answers.

**Pending snapshot request**: `none → pending` (accepted `snapshot`
cmd) `→ fulfilled` (next observed store write; reply sent with id)
or `→ failed` (run completed first; error reply sent). At most one
pending request per requester reply-inbox; concurrent requests each
get their own fulfillment from the same write.

**Transport health** (`NatsTransport` and fake alike): `up ⇄ down`;
publishes in `down` count `publish_failures`, transitions to `up`
count `reconnects`; requests/store ops in `down` raise loudly (they
are explicit operations).

## 8. The store backend (`store.py`)

- **Object**: name = `snapshot_id` (existing `snapshot_id_for(metadata)`
  — one id scheme project-wide); bytes = the encoded blob, unmodified.
- **Metadata**: canonical JSON of the engine's metadata dict, stored in
  the object description; parsed back verbatim on `list`/`read`.
- **`list()`**: newest-first by metadata `timestamp` (the
  `FileSnapshotStore` contract, matched exactly).
- **Bucket**: configurable name, default `pra-snapshots`; `write`
  creates it if absent; a store with no bucket yet lists `[]` (an
  empty store, like a fresh directory) and `delete` is idempotent.
- **Failures**: a missing snapshot id on `read` raises `KeyError` (the
  file store's grammar, matched); any transport/server error surfaces
  as `RuntimeError` naming store, operation, and id — never a hang
  (bounded timeout), never a silent success.
