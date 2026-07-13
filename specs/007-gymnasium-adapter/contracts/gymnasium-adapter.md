# Contracts: The Gymnasium Adapter

The binding interface promises of feature 007. Everything here is
testable, and every MUST maps to a functional requirement in `spec.md`.

## 1. World contract (`GymnasiumWorld`)

- **MUST** satisfy the `EventSource` protocol exactly as the reference
  world does — `reset() → obs`, `step(action) → obs`, `n_actions`,
  `obs_dim` — and nothing else may cross that surface: no reward, no
  `terminated`/`truncated` flags, no info dict (FR-001, FR-002).
- **MUST** return, from both `reset` and `step`, a one-dimensional
  float64 vector of exactly `obs_dim` elements — multi-dimensional Box
  observations flattened in C order (FR-002).
- **MUST** map PRA's local action index `i ∈ [0, n_actions)` to the
  environment action `space.start + i`, so index 0 is always the
  space's first action (FR-003).
- **MUST**, on a step where the environment reports `terminated` or
  `truncated`, immediately reset the environment with the next seed in
  the deterministic sequence and return the fresh reset observation as
  that step's outcome; the terminal observation is discarded; the
  respawn is counted (FR-004).
- **MUST** seed every environment reset — PRA episode starts and
  respawns alike, one shared counter `k` — with
  `SeedSequence(E, spawn_key=(k,))`-derived uint32 values, where `E` is
  a pure function of the run seed obtained **without drawing from** the
  engine's generator (FR-005). The engine generator's state after
  mounting MUST be bit-identical to its state before.
- **MUST** reject at construction, with a message naming the offense:
  a non-`Discrete` action space, a non-`Box` observation space, zero
  or two determinism sources (`rng`/`seed`), a generator whose state
  cannot be read purely, and `step()` before the first `reset()`
  (FR-007). Missing gymnasium MUST raise `ImportError` naming the
  package and `pip install "poseres[gym]"` (FR-006).
- **MUST** expose `resets` and `respawns` as read-only counters outside
  the `EventSource` surface; the engine never reads them (FR-004).

## 2. Body contract (`GymnasiumBody`)

- **MUST** be a `Body` (Doc 02): composed of the existing `WorldSensor`
  and `WorldActuator` around a `GymnasiumWorld`, so `reset`/`step`/
  `obs_dim`/`n_actions`, action routing, width enforcement, and tool
  registration behave exactly as feature 004 validated (FR-001).
- Engine runs mounted through `GymnasiumBody` **MUST** produce run
  summaries byte-identical to the same runs mounted on the underlying
  `GymnasiumWorld` directly (the 004 R1 equivalence, replayed on the
  adapter).
- `GymnasiumBody.factory(env_or_id, ...)` **MUST** return a
  `world_factory(cfg, rng)` that builds a **fresh** environment per
  call and validates `cfg.obs_dim`/`cfg.n_actions` against the mounted
  body at mount time, raising `AnatomyError` naming both the config
  value and the environment value on mismatch (FR-007).
- `close()` **MUST** forward to the wrapped environment.

## 3. Determinism contract

- Same `(config, seed)` on a seeded Gymnasium environment → serialized
  run summaries byte-identical across repeated runs (SC-001); different
  seeds → different summaries (the seed demonstrably reaches the
  environment).
- Scope: guaranteed for environments whose stochasticity flows through
  the Gymnasium seeding convention (`env.reset(seed=...)`); stated in
  the docs (spec Assumptions).

## 4. Regression contract

- Purely additive: no edits to `core/`, `world/`, `harness/`,
  `config.py`, or `anatomy/body.py`; the adapter is a leaf module
  (FR-008).
- The full existing suite passes with recorded reference values
  byte-identical; the core install remains numpy-only — `gymnasium`
  appears only in the `gym` and `dev` extras (FR-006, SC-002).
- No test is skipped: the dev environment always carries gymnasium;
  the missing-dependency path is tested by monkeypatching (FR-006).

## 5. Example contract

- `examples/cartpole.py` exists, runs on `pip install "poseres[gym]"`
  (or dev) in under one minute, and prints: a plain-language per-seed
  summary, the respawn count, and a byte-identity verdict from
  re-running its own seed (FR-009, SC-003).
- The script is lint-clean under the repo's ruff configuration and
  contains the termination-semantics and discarded-reward notes a
  newcomer needs to interpret what they see (FR-010).
