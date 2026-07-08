# Phase 1 Data Model: Anatomy and Body

## 1. Anatomy entities

| Entity | Fields / behavior |
|---|---|
| `Sensor` (protocol) | `id() -> str`, `width() -> int`, `read() -> float[width]` |
| `Actuator` (protocol) | `id() -> str`, `action_count() -> int`, `apply(local) -> None` |
| `WorldSensor` | mounts the synthetic world's observation (width = world.obs_dim); caches the world's last emission |
| `WorldActuator` | mounts the world's action space (count = world.n_actions); `apply` steps the world |
| `ConstantSensor` | fixed vector, no RNG — the growth-demo/tool part |
| `Body` | ordered `sensors`, ordered `actuators`, mounted `environment`; pending-tool queue; derived `obs_dim`/`n_actions`; EventSource-compatible `reset`/`step` |

Validation: widths checked on every composition (`AnatomyError` names the
offender); duplicate tool ids rejected; deregistering the last sensor/actuator
rejected; global action index range-checked.

## 2. Pending tool change

`(kind: sensor|actuator|deregister, part_or_id)` — queued by the registry
methods, applied only by `apply_pending_tools()` (slow loop), which returns the
new `(obs_dim, n_actions)` iff anything changed.

## 3. FrameStore resize (Doc 03 §7)

Inputs: `new_obs_dim`, `new_n_actions`, the run's generator.
Per group (ascending `dim`), preserving all existing entries bit-for-bit:

| Tensor | obs growth ΔO | action growth ΔA | shrink |
|---|---|---|---|
| `W1[F,H,O]` | +ΔO columns ~ N(0,(s·√(10/O_new))²) | — | trailing columns dropped |
| `Dc2[F,O,H]` | +ΔO rows ~ N(0,(s·√(12/H))²) | — | trailing rows dropped |
| `dc2[F,O]` | +ΔO zeros | — | trailing dropped |
| `T1[F,A,H,D]` | — | +ΔA slices ~ N(0,s²) | trailing slices dropped |
| `tb1[F,A,H]` | — | +ΔA zero slices | trailing dropped |
| `T2[F,A,D,H]` | — | +ΔA slices ~ N(0,(s·√(12/H))²) | trailing dropped |
| `tb2[F,A,D]` | — | +ΔA zero slices | trailing dropped |

Draw order: per group ascending `dim` → `W1` then `Dc2` (obs) → `T1` then `T2`
(actions); one sequence from the single generator. Post-conditions: store's
current `obs_dim`/`n_actions` updated (used by births and `results_for`);
effective learning rate re-derived at the new `obs_dim` (§8.8).

## 4. Engine hook

At the top of each offline cycle:
`apply = getattr(world, "apply_pending_tools", None)`; if present and it
returns new dims → `store.resize(new_obs, new_A, rng)`. Plain worlds: one
getattr, nothing else (FR-008).

## 5. Out of scope (recorded)

Tool self-invention [O]; continuous actions [O]; hardware timeouts (config
declared, not enforced in-process); snapshot/restore of resized runs (Doc 06
format-version follow-up — restore's body-compat check fails loudly).
