# Data Model: The Gymnasium Adapter

Phase 1 of `plan.md`. The adapter adds no persistent data and no config
fields; its "model" is two classes, one seed scheme, and a validation
table. Everything lives in `src/pra/anatomy/gymnasium_body.py`.

## GymnasiumWorld (EventSource over a `gymnasium.Env`)

| Field | Type | Meaning |
|---|---|---|
| `_env` | `gymnasium.Env` | the wrapped environment (owned; `close()` forwards) |
| `_entropy` | `int` | seed-sequence entropy `E` — pure function of the run seed (R3) |
| `_reset_index` | `int` | `k`, incremented on **every** env reset: PRA episode starts and respawns alike |
| `_action_start` | `int` | the Discrete space's `start` label offset |
| `_obs_dim` | `int` | element count of the Box observation space (flattened width) |
| `_n_actions` | `int` | the Discrete space's `n` |
| `_started` | `bool` | guards `step()` before the first `reset()` |
| `resets` | `int` (read-only property) | total env resets so far (== `_reset_index`) |
| `respawns` | `int` (read-only property) | mid-episode resets caused by `terminated`/`truncated` — the FR-004 counter, never read by the engine |

**Construction** (`__init__(env, *, rng=None, seed=None)`):

1. Import guard: gymnasium importable, else `ImportError` naming
   `pip install "poseres[gym]"` (FR-006).
2. Space validation (FR-007, order fixed): action space must be
   `Discrete` (else `AnatomyError` naming the space); observation space
   must be `Box` (else `AnatomyError` naming the space).
3. Entropy: exactly one of `rng`/`seed` (else `AnatomyError`).
   From `rng`: pure read of the PCG64 state integer — **no draw**; a
   generator without that state shape → `AnatomyError` directing to
   `seed=`. From `seed`: used as `E` directly.
4. No env interaction at construction (no reset, no draw) — mounting is
   free until the engine starts the first episode.

**Surface** (the `EventSource` protocol, nothing more crosses it —
FR-002):

- `obs_dim` / `n_actions` — sizes only.
- `reset()` → seeds with `_next_seed()`, resets the env, returns the
  flattened observation.
- `step(a)` → `env.step(_action_start + a)`; on `terminated or
  truncated`: increment `respawns`, reset with `_next_seed()`, and
  return the **fresh** observation (terminal observation discarded —
  R2); otherwise return the step observation. Reward, flags, and info
  never leave the adapter.
- `step()` before the first `reset()` → `AnatomyError`.

**Flattening rule** (FR-002): `np.asarray(obs, dtype=np.float64).ravel()`
— C-order, so a multi-dimensional Box has a defined channel order;
width = `prod(shape)`.

## The seed scheme (R3, FR-005)

```
E        = PCG64 state integer of the run generator at mount time   (pure read)
           — or the explicit seed= argument (standalone use)
seed_k   = int(np.random.SeedSequence(E, spawn_key=(k,))
               .generate_state(1, dtype=np.uint32)[0])              (k = 0, 1, 2, …)
reset k  = env.reset(seed=seed_k)
```

One counter `k` covers every reset — PRA episode starts and respawns —
so the sequence of env states is a pure function of `(run seed, action
sequence)`, and the action sequence is a pure function of the run seed
(the engine's own determinism). Byte-identical summaries follow
(SC-001). The engine generator is read once and never drawn from: its
stream is bit-identical to a run without the adapter mounted.

## GymnasiumBody (Body subclass — composition, no new mechanics)

| Member | Meaning |
|---|---|
| `__init__(env, *, rng=None, seed=None, sensor_id="gym", actuator_id="gym")` | builds a `GymnasiumWorld`, wires `WorldSensor(world, sensor_id)` + `WorldActuator(world, sensor, actuator_id)` into `Body.__init__` — the proven 004 composition path (R1) |
| `world` | the underlying `GymnasiumWorld` (read-only property) |
| `resets` / `respawns` | forwarded counters (outside the learning surface) |
| `close()` | forwards to `env.close()` |
| `factory(env_or_id, *, sensor_id, actuator_id, **make_kwargs)` (classmethod) | returns an Engine-ready `world_factory(cfg, rng)`; accepts an env id string (fresh `gymnasium.make(id, **make_kwargs)` per call — each run/seed gets its own env) or a zero-argument callable returning an env; validates `cfg.obs_dim`/`cfg.n_actions` against the mounted body and raises `AnatomyError` naming **both** numbers on mismatch (FR-007) |

Everything else (`reset`, `step`, `obs_dim`, `n_actions`, routing,
tool registration) is inherited from `Body`, unmodified.

## Validation table (constraint → error, all at mount time)

| Constraint | Error |
|---|---|
| gymnasium not installed | `ImportError`: names `gymnasium` and `pip install "poseres[gym]"` |
| action space not `Discrete` | `AnatomyError`: names the actual space (Box-action support is a documented v1 non-goal) |
| observation space not `Box` | `AnatomyError`: names the actual space |
| neither or both of `rng`/`seed` | `AnatomyError`: exactly one source of determinism |
| generator without a readable PCG64 state | `AnatomyError`: directs to explicit `seed=` |
| factory: `cfg.obs_dim` ≠ body width or `cfg.n_actions` ≠ body actions | `AnatomyError`: names config value and environment value, both axes |
| `step()` before `reset()` | `AnatomyError` |

## Sequences

**PRA episode on a self-terminating env** (`steps_per_episode = 6`,
env terminates after 4 live steps):

```
engine reset ── env.reset(seed_0) ─→ obs
step 1..3    ── env.step(a)       ─→ obs (live transitions)
step 4       ── env.step(a) → terminated
             └─ env.reset(seed_1) ─→ fresh obs   [respawn #1: this obs is step 4's outcome]
step 5..6    ── env.step(a)       ─→ obs (live transitions of the new life)
engine reset ── env.reset(seed_2) ─→ obs         [next PRA episode]
```

The engine never observes the boundary — it sees six observations, all
float64 width-`obs_dim`, exactly as on any other world. The respawn
count records that step 4's outcome was a teleport (R2's documented
learning consequence).

## What deliberately does not exist

- No config fields, no snapshot fields, no telemetry fields: the
  adapter adds zero state to any serialized artifact (FR-008).
- No reward path, no termination flags on the surface (FR-002).
- No env pooling or reuse across runs: the factory builds a fresh env
  per `world_factory` call, keeping seeds-in-parallel runs independent.
