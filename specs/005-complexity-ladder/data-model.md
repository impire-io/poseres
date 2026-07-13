# Data Model: The Complexity Ladder

Phase 1 of `plan.md`. Entities, dials, validation, and readings.

## Config additions (all inert by default — FR-006)

| Field | Type / default | Meaning | Validation (FR-011) |
|---|---|---|---|
| `world` | `str = "reference"` | world family selector: `reference` \| `nonuniform` \| `compositional` \| `distractor` | must be one of the four; rung dials non-inert only when their world is selected |
| `region_noise_std` | `float = 0.0` | L1: transition-noise scale inside the region (units of latent space; dial 0 = degenerate) | `>= 0`; `> 0` only with `world="nonuniform"` |
| `factor_dims` | `tuple[int, ...] = ()` | L2: factor-group sizes; `()` = degenerate (single group) | each `>= 1`; `sum == true_dim`; non-`()` only with `world="compositional"` |
| `distractor_dim` | `int = 0` | L3: autonomous latent size | `>= 0`; paired with `distractor_channels` |
| `distractor_channels` | `int = 0` | L3: extra observation channels the distractor emits into (0 = degenerate) | `>= 0`; `> 0` requires `distractor_dim > 0` and `world="distractor"` |
| `distractor_mode` | `str = "structured"` | L3: `structured` (drift dynamics) \| `noise` (fresh noise channels) | one of the two |

Notes: on L3 the world's total observation width is
`obs_dim + distractor_channels` — `obs_dim` keeps meaning the controllable
emission width so the degenerate dial is trivially reference-identical;
the *engine-visible* width is what the world's `obs_dim` property reports
(total). The harness reports both (spec edge case: scale rules key off
total). New fields ride in snapshots via the existing config-in-force
mechanism; defaults make old snapshots semantically unchanged (the
deferred Doc 06 format-version follow-up is unaffected).

## World entities

### `NonUniformWorld` (L1)

- **State**: reference state (objects, actions, current latent/object) —
  unchanged; plus occupancy counters `steps_in_region`, `steps_total`.
- **Region**: `latent[0] > 0` (fixed convention; documented).
- **Transition**: reference displacement; if the *pre-step* latent is in
  the region, add `ε ~ N(0, region_noise_std² I)` (one draw, after the
  displacement lookup, before emission — documented order).
- **Draws**: construction identical to reference. Per step: the extra
  `ε` draw happens **only** when `region_noise_std > 0` and in-region —
  at the degenerate dial the draw sequence is exactly the reference's.
- **Ground truth (harness-only)**: `ladder_readings()` → occupancy
  counters + dials. Never part of the `EventSource` surface.

### `CompositionalWorld` (L2)

- **State**: reference state; group boundaries from `factor_dims`
  (offsets precomputed at construction).
- **Actions**: displacement drawn as reference (full `true_dim` vector),
  then **masked to the action's group** (round-robin assignment: action
  `a` moves group `a mod K`). Masking after an identical draw keeps the
  construction draw sequence byte-equal to reference (R7); with `K = 1`
  the mask is a no-op.
- **Emission**: reference (one dense matrix over the full latent, tanh,
  standard normalization) — the composition never leaks through channels.
- **Ground truth (harness-only)**: `ladder_readings()` → `factor_dims`,
  group–action assignment.

### `DistractorWorld` (L3)

- **State**: reference state; plus distractor latent `z_d`
  (`distractor_dim`), fixed `drift` vector, distractor emission matrix
  (`distractor_channels × distractor_dim`).
- **Construction draws**: reference draws first, then (only if
  `distractor_channels > 0`): `z_d` start, drift, distractor emission —
  in that documented order.
- **Step**: reference transition and emission for the first `obs_dim`
  channels; distractor channels appended:
  - `structured`: `z_d ← z_d + drift`; channels =
    `tanh(E_d · z_d / norm_d)` (+ the world's sensor noise, same std).
  - `noise`: channels = fresh `N(0, 1)` draws (+ nothing else).
- **Surface**: `obs_dim` property reports the total width; `n_actions`
  unchanged. Degenerate dial appends nothing and draws nothing extra.
- **Ground truth (harness-only)**: `ladder_readings()` → channel split,
  mode, dims.

## Harness entities

### `RungReading` (per rung × seed)

- `rung`: `"l1" | "l2" | "l3"`; `seed`; configuration echo (dials, total
  vs learnable widths).
- Common: `best_dim`, `improvement`, `final_population`, checkpoint
  trajectory (from the existing per-seed summary — no recorder changes).
- L1: `occupancy` (share of steps in-region), paired twin's `best_dim` /
  `improvement` (same seed, degenerate dial), paired deltas.
- L2: quartet readings on the compositional world (predictive /
  effort-only / identity / churn-matched, reusing the T3 machinery) and
  the final census: stable frames' dims from an end-of-run snapshot.
- L3: `best_dim` vs controllable `true_dim` at every checkpoint;
  the same reading in the other mode when both are run.

### `LadderReport`

One `VerdictReport` (mode `"ladder"`): per rung an `AcceptanceVerdict`
(`L1`/`L2`/`L3`, criterion text from `LADDER-CRITERIA.md`, verdict
PASS/FAIL as data — investigatory at the build level, exit code 0), with
`run_metadata` carrying per-rung per-seed reading tables; rendered by the
existing text/JSON renderers (extended with a ladder block, same pattern
as the T3 quartet table).

## State transitions / lifecycle

Worlds are constructed per run from `(Config, rng)` by
`make_world(cfg, rng)` (the factory the harness passes as
`world_factory`) — same lifecycle as the reference world; occupancy
counters reset at construction, accumulate per step, and are read once
after the run. No persistence of world internals beyond what the seed
reconstructs (Doc 06's world-from-seed rule holds: the rng state in a
snapshot resumes the exact stream on every rung — fresh-noise draws
included).
