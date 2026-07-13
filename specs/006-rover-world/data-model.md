# Data Model: The Watchable Rover World

Phase 1 of `plan.md`. Entities, constants, draw order, threading rules,
and wire formats.

## World constants (module-level, stated — research R1)

| Constant | Value | Meaning |
|---|---|---|
| `ARENA_HALF` | 1.0 | arena is the square [−1, 1] × [−1, 1] |
| `N_OBSTACLES` | 5 | circular obstacles per map |
| `OBSTACLE_R_MIN / _MAX` | 0.12 / 0.22 | obstacle radius range |
| `OBSTACLE_SPREAD` | 0.7 | obstacle centers drawn in [−0.7, 0.7]² |
| `ROVER_RADIUS` | 0.06 | collision radius of the rover |
| `MOVE_STEP` | 0.08 | forward displacement per action |
| `REVERSE_FACTOR` | 0.5 | reverse speed = 0.5 × MOVE_STEP |
| `TURN_STEP` | π/6 | heading change per turn action (30°) |
| `RAY_ANGLES` | (−π/2, −π/4, 0, π/4, π/2) | rangefinder directions, relative to heading |
| `RAY_MAX` | 1.0 | rangefinder cap; readings are d / RAY_MAX ∈ [0, 1] |
| `N_SPAWNS` | 8 | precomputed collision-free start poses |
| `SPAWN_ATTEMPTS` | 1000 | total rejection-sampling budget (then a constraint-naming error) |
| `SPAWN_SPREAD` | 0.85 | spawn positions drawn in [−0.85, 0.85]² |
| `ROVER_OBS_DIM / ROVER_N_ACTIONS` | 10 / 4 | the fixed anatomy widths `make_rover_body` enforces |

## `RoverWorld` (the environment)

- **Fixed structure (constructed from the seeded generator)**: obstacle
  list `[(cx, cy, r)] × 5`, spawn poses `[(x, y, θ)] × 8`.
- **Episode state**: pose `(x, y, θ)`, `bump` flag (last move blocked),
  cached sense vectors per part.
- **Construction draw order** (research R4): per obstacle — center
  (`uniform(−0.7, 0.7, size=2)`), radius (`uniform(0.12, 0.22)`); then
  per spawn attempt — position (`uniform(−0.85, 0.85, size=2)`), heading
  (`uniform(0, 2π)`), accepted iff collision-free; hard cap
  `SPAWN_ATTEMPTS`, exceeded → `ValueError` naming the constraint.
- **`reset()`**: one integer draw (spawn index) → pose := spawn, bump :=
  0; emit (one `standard_normal(10)` noise draw); record to the tap
  (`record_reset`); returns `None` (the Body composes from the sensors).
- **`apply(action)`** (called by the actuator): physics (no RNG) —
  0 forward / 1 reverse / 2 turn left / 3 turn right; a move whose new
  position collides (wall: |coord| > `ARENA_HALF − ROVER_RADIUS`;
  obstacle: distance < r + `ROVER_RADIUS`) leaves the pose unchanged and
  sets bump := 1, else bump := 0; turns never bump. Then emit (one noise
  draw), record to the tap (`record_step`), then optional
  `time.sleep(step_delay)` (pacing, research R8).
- **Emission**: clean 10-vector (table below) + `standard_normal(10) ×
  config.sensor_noise_std`, then sliced into per-part caches.
- **Harness/viewer-only surface** (never called by the engine, FR-005):
  `layout()` → static geometry dict (arena half-size, rover radius,
  obstacles, spawn poses, ray angles/max, action names, sensor order).

### Observation channels (fixed order — the order is semantic, Doc 02 §3.3)

| Channels | Part | Meaning | Range (clean) |
|---|---|---|---|
| 0–4 | `rays` | distance to nearest wall/obstacle along heading −90°, −45°, 0°, +45°, +90°, normalized d / RAY_MAX | [0, 1] |
| 5–6 | `compass` | cos θ, sin θ | [−1, 1] |
| 7–8 | `gps` | x / ARENA_HALF, y / ARENA_HALF | [−1, 1] |
| 9 | `bump` | 1.0 if the last move was blocked else 0.0 | {0, 1} |

## Anatomy (research R2)

| Part | Kind | id | width / actions |
|---|---|---|---|
| Rangefinder | Sensor | `rays` | 5 |
| Compass | Sensor | `compass` | 2 |
| Position beacon | Sensor | `gps` | 2 |
| Bumper | Sensor | `bump` | 1 |
| Drive | Actuator | `drive` | 4 (forward, reverse, left, right) |

`RoverSensor(world, part_id, width)` reads the world's cached part
vector (raises before the first emission, the `WorldSensor` precedent);
`RoverDrive(world)` applies the local action index via `world.apply`.
`make_rover_body(config, rng, *, telemetry=None, step_delay=0.0) → Body`
composes them in the table's order; it raises `AnatomyError` naming the
mismatch when `config.obs_dim != 10` or `config.n_actions != 4` (FR-011)
and hands `layout()` to the tap when one is attached.

## `RoverTelemetry` (the tap — research R5)

| Field | Writer (thread) | Content |
|---|---|---|
| `pose`, `bump`, `step`, `episode` | run (world) | current pose tuple, bump flag, counters — plain Python floats/ints |
| `trail` | run (world) | bounded deque of (x, y), cleared per episode |
| `_store` | run (bus factory, once) | the live `FrameStore` reference |
| `layout` | run (mount, once) | the world's static geometry dict |
| `done`, `final` | run (CLI, once) | completion flag + canonical summary dict |
| `_last_learning` | serving | last good learning block (torn-read fallback) |

- `bus_factory(processor)` — stores the reference, returns the standard
  `InMemorySyncBus(processor)` unchanged.
- `snapshot()` — **serving thread only**: copies pose/counters/trail
  (retry-on-`RuntimeError` for concurrent deque mutation, falling back to
  the last copy), then reads learning state via public read-only
  accessors — `frame_states()` scored with the run's own
  `WeightedSumScorer` on copies — producing population, per-dim
  histogram, best (dim, score), best frame's `pred_err_ema`; any
  concurrent-mutation error falls back to `_last_learning`. Never
  mutates run state, never draws randomness.

**Threading rule**: run-path methods only append/assign plain values; no
locks are ever taken on the run path; all float computation happens in
`snapshot()` (FR-007).

## HTTP surface (research R7)

| Route | Payload |
|---|---|
| `/` | `viewer.html` — single self-contained page (inline CSS/JS, canvas) |
| `/layout` | `{arena_half, rover_radius, obstacles: [[cx, cy, r]…], spawns: [[x, y, θ]…], ray_angles, ray_max, actions: [names], sensors: [ids]}` |
| `/state` | `{step, episode, pose: [x, y, θ]\|null, bump, trail: [[x, y]…], done, final: {…}\|null, learning: {population, dims: {dim: count}, best_dim, best_score, pred_err_ema}\|null}` |

`start_viewer(tap, port) → (server, url)`: `ThreadingHTTPServer`
(daemon threads) on `127.0.0.1`; port 0 binds ephemeral; the returned
URL carries the actual port; busy port → `OSError` surfaced with a
message naming the port. Any other route → 404. Request logging is
silenced.

## `pra-rover` CLI (research R9)

| Flag | Default | Meaning |
|---|---|---|
| `--seed N` | 1 | the run's seed |
| `--port N` | 8765 | viewer port (0 = ephemeral) |
| `--fps N` | 50 | pacing in steps/second (0 = unthrottled) |
| `--config PATH` | — | JSON overrides onto `Config()` (schedule dials etc.; widths must stay 10/4) |
| `--json PATH` | — | write the canonical per-seed summary |
| `--no-open` | off | never attempt to open a browser |
| `--exit-when-done` | off | shut the server down after the run instead of serving until Ctrl+C |

Flow: build config → tap → start viewer → print URL (+ estimated
duration) → maybe `webbrowser.open` (only interactive TTY and not
`--no-open`, failure non-fatal) → run engine (world_factory +
tap.bus_factory) → `tap.finish(summary)` → print honest summary with the
single-seed caveat → optional `--json` → hold serving (or exit) →
graceful shutdown on Ctrl+C. Exit 0 on success; 2 on an unusable port.

## Lifecycle

The rover world is constructed per run from `(Config, rng)` inside the
engine (world consumes the seed prefix exactly like the reference
family); the tap outlives the run and serves `done + final` afterwards.
No world internals persist anywhere; the `--json` artifact is the
existing canonical summary, byte-stable per `(config, seed)`.
