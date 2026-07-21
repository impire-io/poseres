# Data Model: Brain Telemetry & Introspection Dashboard (feature 029)

All payloads use the canonical wire form (`subjects.to_bytes`: fixed key
order by construction, compact separators, ascii) and carry **no
wall-clock time** — ordering facts are `seq` (the tap's single mirrored
sequence) and the run's own counters. All three families are run-scoped:
`pra.v1.run.<run_id>.brain.<leaf>`.

## AnatomyMeta — `brain.anatomy`

Published once at world construction and re-published on the view
heartbeat clock (late attachers catch it within one period, ≤5 s default).

```json
{
  "run": "c1",
  "seq": 17,
  "obs_dim": 14,
  "n_actions": 8,
  "groups": [
    {"id": "pose",   "start": 0,  "width": 5},
    {"id": "vitals", "start": 5,  "width": 2},
    {"id": "env",    "start": 7,  "width": 4},
    {"id": "blocks", "start": 11, "width": 3}
  ],
  "actuators": [
    {"id": "control", "action": 0, "label": "forward"},
    {"id": "control", "action": 7, "label": "idle"}
  ]
}
```

- `groups`: ordered, contiguous, non-overlapping; `start` is the slice
  offset into the observation vector; `sum(width) == obs_dim` for a body
  that names everything (a partial body may cover a prefix — consumers
  label uncovered dims generically).
- `groups[i].labels` (optional): per-channel names within the group,
  `len(labels) == width` when present.
- `actuators`: one entry per action id, `action` ∈ [0, n_actions);
  `label` is the human name (preset keys `+`-joined; empty preset →
  `idle`; Gymnasium/generic bodies may use `a<n>`).
- Validation: a world's `anatomy_meta()` returning a malformed dict is a
  bug surfaced by the unit tests, not silently repaired by the tap; the
  tap publishes what the body declares (single source of truth).

## FrameRow list — `brain.frames`

Published by the census walk, same cadence (default 0.5 s), same
torn-read guard. The aggregate `tele.census` payload is unchanged; this
subject carries the rows it aggregates.

```json
{
  "run": "c1",
  "seq": 421,
  "steps": 5240,
  "population": 9,
  "best_frame": 3,
  "rows": [
    {"id": 3, "dim": 3, "age": 41, "cand": false,
     "recon": 0.081, "pred": 0.104, "effort": 0.22, "score": 0.291}
  ]
}
```

- `rows` is **complete** (bounded by `max_frames` by construction — no
  truncation; if a future config ever forces a cap, the payload MUST gain
  `dropped: <n>` — the no-silent-caps rule).
- `population == len(rows)`; `best_frame` is the id the same walk chose
  (ties by ascending id, the store's own rule) — consumers can
  cross-check against `tele.census` (SC-002).
- `age` is `age_cycles`; `cand` is the store's is_candidate (still inside
  the protection window); `score` is the engine's own
  `WeightedSumScorer.combine` result for the row.

## LifecycleEvent — `brain.events`

Mirrored on the engine thread by the tap's Bus wrapper; drained in order
with the rest of the mirrored family (drops derive from seq gaps, as for
every mirrored event).

```json
{"run": "c1", "seq": 388, "event": "spawn", "frame": 17, "steps": 5211}
{"run": "c1", "seq": 512, "event": "evict", "frame": 4,  "steps": 6480}
```

- `event` ∈ {`spawn`, `evict`} — the fixed vocabulary. `spawn` = the
  frame joined the live population **including boot and snapshot-restore
  registration** (stated; this makes `spawns − evicts == population`
  exact from any attach point). `evict` = it left (the engine's single
  decay/threshold/cap path).
- `steps` is the tap's step counter at mirror time (0 at boot).
- Invariant (SC-003): over any window observed gap-free, each engine
  register/unregister appears exactly once, in seq order.

## Dashboard model state (consumer-side, bounded)

| Field | Source | Bound |
|-------|--------|-------|
| `brain_meta` | latest `brain.anatomy` | 1 (latest wins) |
| `frames_latest` | latest `brain.frames` | 1 (latest wins) |
| `events` | `brain.events` append | deque maxlen 512 |
| `steps_window` | existing `tele.step` handler | deque maxlen 600 |

`steps_window` entries: `{step, stream, action, obs}` — the decoded
channel log and strip charts and the schematic's live activity all derive
from this one window client-side; nothing else retains observations.
State payload additions are exactly these four keys (pure consumer:
everything on screen is derivable from the subjects by any third party).

## Relationships

```
anatomy_meta (per run) ──labels──▶ steps_window.obs slices  (charts, log, schematic)
                       ──labels──▶ actuators → action ids   (schematic highlight)
brain.frames.rows ──rows==census──▶ tele.census aggregates  (SC-002 cross-check)
brain.events ──Σspawn−Σevict──▶ population                  (SC-003 reconciliation)
```
