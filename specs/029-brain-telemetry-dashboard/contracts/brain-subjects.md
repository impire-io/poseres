# Wire Contract: the `brain.*` subject family (feature 029)

Additive extension of the pra.v1 scheme (feature 014, data-model §2/§3).
Everything here is run-scoped, canonical wire form, no wall-clock time.
A consumer that ignores this family loses nothing that exists today.

## §1 Subjects

| Subject | Cadence | Content |
|---------|---------|---------|
| `pra.v1.run.<id>.brain.anatomy` | once at world construction + view-heartbeat republish (default 5 s) | AnatomyMeta (data-model.md) |
| `pra.v1.run.<id>.brain.frames`  | census cadence (default 0.5 s) | complete per-frame rows |
| `pra.v1.run.<id>.brain.events`  | on population change (mirrored, drained ≤ drain interval) | one spawn/evict per event |

The discover reply (`run_subjects`) gains the three keys `brain_anatomy`,
`brain_frames`, `brain_events` — consumers never guess subject names.

## §2 Semantics

1. **Ordering**: `seq` values come from the tap's single mirrored
   sequence, shared with steps/episodes/views/snapshots — any one
   subject's seqs legitimately skip; gaps are measured on the union
   (the dashboard's existing rule). `brain.events` are mirrored on the
   engine thread and drained in order; `brain.anatomy` heartbeats and
   `brain.frames` are publisher-thread emissions stamped with the
   current seq (census pattern).
2. **Late attach**: a consumer that attaches mid-run has AnatomyMeta
   within one heartbeat, current rows within one census interval, and
   sees lifecycle events from its attach point onward. It reconciles
   population from `brain.frames` (or `tele.census`) — it never invents
   missed history.
3. **Vocabulary**: `event` ∈ {`spawn`, `evict`}, fixed. `spawn` includes
   boot and snapshot-restore registration (the frame *joined the live
   population*); `evict` is the engine's single removal path
   (decay/threshold/cap). From any gap-free attach point:
   Σspawn − Σevict = current population.
4. **Completeness**: `rows` is the whole population (bounded by
   `max_frames`). Any future bound MUST add `dropped: <n>` — silent
   truncation is forbidden (constitution II).
5. **Consistency**: `brain.frames.population == len(rows)` always;
   `best_frame` equals the same walk's aggregate census choice (ties by
   ascending frame id).
6. **Absence**: a run whose world publishes no `anatomy_meta()` simply
   never emits `brain.anatomy` — consumers label dims generically from
   the `started` status (`obs_dim`/`n_actions`). A run without a tap
   emits nothing at all (unchanged).
7. **Degradation**: consumers MUST tolerate any subset of the family
   (metadata without events, rows without metadata, …) — panels light up
   per-subject.

## §3 Body self-description (`anatomy_meta()`)

Optional world method, read once by the tap at world construction
(one `getattr`, one deep copy — run-path budget preserved):

```python
def anatomy_meta(self) -> dict:
    return {
        "obs_dim": self.obs_dim,
        "n_actions": self.n_actions,
        "groups": [{"id": ..., "start": ..., "width": ...}, ...],
        "actuators": [{"id": ..., "action": ..., "label": ...}, ...],
    }
```

Implementors in this feature: `Ros2Body` (live sensors/actuators — serves
ROS2 and Minecraft, correct after grown tools because it reads the live
lists), the rover world (`SENSOR_PARTS` + action names), `GymnasiumWorld`
(structural groups, generic labels). The bare reference world implements
nothing. The tap publishes what the body declares — the body is the
single source of truth, malformed declarations are unit-test bugs, not
tap repairs.

## §4 Dashboard endpoint additions (`/run/<id>/state`)

Four new keys, exactly mirroring the model's bounded state:
`brain_meta` (latest AnatomyMeta or null), `frames_latest` (latest rows
payload or null), `events` (bounded recent window, oldest first),
`steps_window` (bounded recent steps: step/stream/action/obs). The page's
Brain tab renders only from these — a third-party consumer of the raw
subjects can reproduce every pixel (FR-011).
