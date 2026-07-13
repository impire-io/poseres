# Data Model: Continuous Operation

Phase 1 of `plan.md`. Entities, fields, validation, and state.

## Config additions (inert by default — FR-002)

| Field | Type / default | Meaning | Validation (FR-009) |
|---|---|---|---|
| `episode_mode` | `str = "episodic"` | `episodic` (pinned validated behavior) \| `continuous` (boot once, virtual episodes) | must be one of the two |

No other dials: virtual episodes reuse `steps_per_episode`, warmup reuses
`warmup_episodes`, consolidation reuses `episodes_per_cycle` (research
R2/R3 — the segmentation exists to preserve validated meanings).
Existing validation already rejects degenerate schedules
(`steps_per_episode >= 1`, `episodes_per_cycle >= 1`, non-empty
checkpoints), which covers FR-009's "zero virtual episodes".
`episode_mode` rides in snapshots via the existing config-in-force.

## Engine state (continuous mode only)

- `pending: np.ndarray` — the observation carried across a virtual
  boundary: set by the boot (`world.reset()`, called exactly once), then
  overwritten at each span's end with the trailing observation of the
  last step (which episodic mode discards). Never `None` after boot.
- Boot bookkeeping: the engine tracks that boot has happened
  (`booted: bool`) so the single-call guarantee is engine logic, not
  world tolerance (FR-001). On resume, `booted` restores as true and no
  reset is issued — the world state comes from the snapshot (below).

Episodic mode allocates none of this; its code path is untouched
(byte-identity by construction, guarded by the frozen-baseline tests).

## World-state capture protocol (optional, duck-typed — research R5)

```
state_dict() -> dict          # mutable run state only, JSON/array-safe
load_state_dict(state) -> None
```

- **`SensorimotorWorld`**: `{"latent": array | None, "obj": int | None}` —
  the only mutable fields; constructed arrays (objects, emissions,
  actions) are seed-derived and rebuilt at boot.
- **Ladder worlds**: the same two fields, plus L1's occupancy counters
  (`steps_in_region`, `steps_total`) and L3's distractor latent
  (`d_latent`). Masked actions / construction state: seed-derived, not
  captured.
- **`Body` (anatomy)**: delegates capture to its mounted environment when
  that environment implements the protocol — the body itself is
  stateless between steps apart from its pending-tool queue, which is
  already part of the engine's resize story, not world state.
- External worlds (Gymnasium, hardware): do not implement it — snapshot
  capture in continuous mode raises with a message naming the protocol
  (FR-005); ROADMAP B5 owns the rest.

## Snapshot blob (additive, backward-compatible)

`SystemState` gains one optional field:

| Field | Type / default | Written when | Decode behavior |
|---|---|---|---|
| `world_state` | `dict \| None = None` | continuous mode AND the world implements capture; carries `{"world": <state_dict>, "pending": <array>}` | absent/None → old and episodic blobs decode unchanged, bit-identical (FR-002) |

Format version stays `1`: the addition is optional-with-absent-default in
both directions (an old decoder never sees the key in episodic blobs — the
only blobs it could have produced; a new decoder tolerates absence).
Resume in continuous mode: rebuild the world from the seed prefix as
today (construction draws), then `load_state_dict(world_state["world"])`
and restore `pending` — the same restore-over-reconstruct pattern the rng
state already uses (research R4/R5).

## Test instruments

- **`SingleBootWorld`** (test-shipped wrapper, FR-007/R8): wraps any
  `EventSource`; `reset()` increments a boot counter and raises
  `RuntimeError("SingleBootWorld: already booted")` on the second call;
  delegates `step`/`obs_dim`/`n_actions`; exposes the counter for
  assertions.
- **Boundary probes** (SC-004): tests assert, on a continuous run, that
  chain-break/window/cap-projection effects occur exactly at stream
  positions `k × steps_per_episode` — implemented against observable
  consequences (e.g., capped-norm projection points, EMA-advance
  positions) rather than private state where possible.

## Lifecycle summary

Boot (once) → virtual episodes of `steps_per_episode` steps (trailing
observation carried, chain break + window restart + cap projection at
each boundary) → offline cycle every `episodes_per_cycle` spans (spawn /
evict / resize / C4 snapshot, unchanged) → summary. Resume: rebuild from
seed prefix → overwrite rng state → `load_state_dict` + `pending` →
continue without reset.
