# Contracts: The Watchable Rover World

The binding interface promises of feature 006. Everything here is
testable without a browser, and every MUST maps to a functional
requirement in `spec.md`.

## 1. World contract

- `RoverWorld(config, rng, *, telemetry=None, step_delay=0.0)` MUST be
  constructible from the engine's `(Config, rng)` calling convention and
  MUST consume the seeded generator in the documented fixed order
  (data-model: construction → obstacles then spawns; reset → index +
  noise; step → noise only) so runs are byte-reproducible per
  `(config, seed)` (FR-004).
- `reset()` MUST begin a new episode at a freshly drawn spawn pose and
  clear the bump flag — per-episode semantics mirroring the reference
  world (FR-004).
- Movement MUST be a pure function of (pose, action): blocked moves leave
  the pose unchanged and set the bumper; turns never bump (FR-001).
- An unsatisfiable layout (spawn sampling exceeding its attempt budget)
  MUST raise at construction with a message naming the constraint, never
  hang (FR-011).
- `layout()` is **harness/viewer-only**: the engine MUST NOT call it, and
  nothing on the body's system-visible surface may expose pose, map, or
  layout (FR-005).
- `step_delay > 0` MUST change wall-clock behavior only — no draw, no
  float on run state — byte-identical summaries with any delay (FR-009).

## 2. Anatomy contract

- `make_rover_body(config, rng, ...) → Body` MUST compose exactly the
  named parts in the documented fixed order (`rays`, `compass`, `gps`,
  `bump`; actuator `drive`) onto the standard Doc 02 `Body`, yielding
  `obs_dim == 10` and `n_actions == 4` (FR-002/FR-003).
- The returned body MUST satisfy the `EventSource` protocol and run on
  the **unchanged** engine via the existing `world_factory` parameter,
  producing the standard `PerSeedRunSummary` (FR-003).
- A config whose `obs_dim`/`n_actions` disagree with the rover anatomy
  MUST be rejected at mount time with a message naming both widths
  (FR-011).
- Sensors MUST be RNG-free, idempotent reads of the world's cached
  emission (reading before the first emission raises); the actuator
  returns nothing — feedback arrives only via observations (Doc 02 §4.2).

## 3. Telemetry-tap contract (non-perturbation)

- Run-path writes (`record_reset`, `record_step`, `bus_factory`, layout
  attach, `finish`) MUST consume no randomness, perform no
  floating-point computation, and take no locks — plain value copies and
  assignments only (FR-007).
- `bus_factory(processor)` MUST return the standard
  `InMemorySyncBus(processor)`; the engine's delivery semantics are
  untouched (FR-007).
- `snapshot()` MUST be safe to call from any thread at any time — before
  the run, mid-run, after the run — never raising and never mutating run
  state; concurrent-mutation races fall back to the last good reading
  (spec edge case).
- Every learning quantity served MUST be an existing defined quantity
  (frame EMAs, the real scorer's score, population, best_dim) computed
  on copies off the run path (SC-006).
- **The binding proof**: a run with the tap attached and its endpoints
  polled throughout MUST serialize byte-identically to the same
  `(config, seed)` run with no tap (SC-003) — integration-tested with
  live HTTP traffic during the run.

## 4. HTTP contract

- `start_viewer(tap, port) → (server, url)`: serves `/` (the
  self-contained page), `/layout` (static geometry JSON), `/state` (the
  snapshot JSON) on `127.0.0.1`; anything else is 404 (FR-006).
- The page MUST reference no external resources — it renders entirely
  from `/layout` + `/state` (FR-006).
- `/state` MUST answer coherently at every run phase: before the first
  step (null pose, empty trail, zero counters), mid-run, and after
  completion (`done: true` + the final canonical summary) (spec edge
  cases).
- Port 0 MUST bind an ephemeral port with the true URL returned; a busy
  port MUST surface a clear error naming the port (FR-011).
- Serving threads are daemons; `shutdown()` + `server_close()` MUST leave
  no lingering sockets (test-enforced via the warnings-as-errors gate).

## 5. CLI contract

```
pra-rover [--seed N] [--port N] [--fps N] [--config PATH]
          [--json PATH] [--no-open] [--exit-when-done]
```

- MUST print the viewer URL before the run starts, run to completion,
  print the honest end-of-run summary **with the single-seed caveat**,
  and exit 0 (FR-008; assumptions).
- MUST attempt `webbrowser.open` only in an interactive terminal and
  never when `--no-open` is set; a failed open is never fatal (FR-008,
  spec edge case).
- `--fps` maps to the world's `step_delay` (0 = unthrottled) and MUST NOT
  change any byte of the results (FR-009).
- `--json` writes the canonical per-seed summary — the byte-reproducible
  example-run artifact (SC-002).
- `--exit-when-done` returns after the run; otherwise the command holds
  the server open until interrupted, shutting down gracefully.
- An unusable port exits 2 with a message; no partial run starts.

## 6. Regression contract

The feature is purely additive: no module outside `pra.examples` is
edited except `pyproject.toml` (new console script + package-data —
inert for every existing entry point). Every existing test, recorded
reference value, and validated mode stays byte-identical;
`tests/integration/test_baseline_unchanged.py` and the full suite remain
the gate (FR-010, SC-004). The feature adds zero runtime dependencies
(SC-005).
