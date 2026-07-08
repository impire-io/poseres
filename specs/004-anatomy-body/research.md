# Phase 0 Research: Anatomy and Body

## R1 — The Body implements the EventSource seam

**Decision.** `Body` satisfies the existing `EventSource` protocol
(`reset`/`step`/`obs_dim`/`n_actions`): `reset()` begins an episode on the
mounted environment and composes the first observation; `step(global_action)`
routes to `(actuator, local)` — the world actuator advances the environment —
then composes all sensors' reads. With the world mounted as a single
sensor/actuator pair, delegation is 1:1 (same calls, same order, no extra RNG),
so runs are **byte-identical** to the direct connection (SC-001).

**Rationale.** The whole stack (Engine, harness, tests) already depends on the
EventSource seam; mounting the body there means zero changes to composition
consumers and makes byte-equivalence provable rather than hoped.
**Alternatives.** A new Engine "body mode" (rejected: churn in the hot loop and
a second code path to keep byte-frozen); making Body wrap the Engine (rejected:
Doc 05 §7 wires the policy inside the loop — the body must sit below it).

## R2 — Fixed-order composition and disjoint-union routing

**Decision.** `Body` stores sensors/actuators as ordered lists.
Observation = `np.concatenate([s.read() ...])` in declared order, with a width
check per sensor (wrong width → `AnatomyError` naming the sensor, FR-003).
Action routing: cumulative offsets over `action_count()` in declared order;
global index → binary-search-free linear scan (n_actuators is tiny) to
`(actuator, local)`. `obs_dim`/`n_actions` are derived properties.

**Rationale.** Doc 02 §3.3/§4.2 verbatim. **Alternatives.** Dict-keyed parts
(rejected: order is semantic — "changing it changes the meaning of every
observation dimension").

## R3 — Frame I/O resize (Doc 03 §7), made precise

**Decision.** `FrameStore.resize(new_obs_dim, new_n_actions)`:
- **Observation growth** (`ΔO > 0`): for every group, `W1[F,H,O]` gains columns
  `W1_new[F,H,ΔO]`, `Dc2[F,O,H]` gains rows, `dc2[F,O]` gains zeros; existing
  entries preserved bit-for-bit. New entries ~ `Normal(0, (s·f)²)` with the
  §8.8 effective factors at the **new** `obs_dim` (`f = √(10/obs_dim_new)` for
  `W1`; `f = √(12/H)` for `Dc2`; biases zero) — the reference-preserving
  reading of "Normal(0, init_weight_scale²)".
- **Observation shrink**: trailing columns/rows discarded (Doc 03 §7
  "removed ... discarded"); no draws.
- **Action growth** (`ΔA > 0`): `T1[F,A,H,D]`, `tb1[F,A,H]`, `T2[F,A,D,H]`,
  `tb2[F,A,D]` gain per-action slices (weights at effective scale — raw for
  `T1` (pose fan-in), `√(12/H)` for `T2`; biases zero). **Action shrink**:
  slices for removed trailing actions discarded.
- **Draw order (determinism, FR-006):** groups in ascending `dim`; within a
  group, per frame in row order, tensors in the fixed order `W1, Dc2, T1, T2`
  (observation first, then actions); a single documented sequence from the
  run's generator.
- The store updates its **current dims** (used by subsequent births and
  `results_for`), and re-derives the effective learning rate at the new
  `obs_dim` (FR-007, §8.8).

**Rationale.** Doc 03 §7 verbatim, with the two open readings pinned: trailing
(= declared-order) growth/shrink because composition order is semantic, and
effective-scale initialization because raw 0.3 at obs 60 was proven to saturate
newborn weights (SCALE-DIAGNOSIS layer 3) — fresh slices must join the regime
the surviving weights live in.
**Alternatives.** Re-initializing whole tensors (rejected: destroys learning —
the point is growth); interleaved insertion positions (rejected: sensors append
in declared order, so trailing is exact).

## R4 — The slow-loop hook, inert by construction

**Decision.** Registrations queue on the Body (`register_sensor/actuator`,
`deregister`) and take effect only in `apply_pending_tools()`, which the Engine
calls at the **top of each offline cycle** (before aging/eviction/spawn and
before any snapshot — Doc 06 §5 ordering) via a duck-typed lookup:
`apply = getattr(world, "apply_pending_tools", None)`. Plain worlds lack the
attribute → one `getattr` per cycle, no RNG, no float work → baseline bytes
frozen (FR-008). When it returns changed dims, the Engine calls
`store.resize(...)` with the run's generator.

**Rationale.** C4 (Doc 02 §5.2) and byte-identity. **Alternatives.** A new
first-class Engine seam for the body (rejected for now: EventSource already is
the seam; a `runtime_checkable` protocol adds ceremony without safety).

## R5 — What demonstrates growth honestly

**Decision.** Integration test grows the body mid-run with a `ConstantSensor`
(fixed vector — contributes no RNG) and a second `WorldActuator`-like no-op
actuator, at a chosen cycle; asserts: shapes, bit-preservation of old slices,
run completion with sane telemetry, byte-identical re-run. Byte-equivalence of
the mounted world (SC-001) is its own test.

**Rationale.** A constant sensor isolates the resize mechanics from new
stochastic input; determinism of the whole schedule is the strongest honest
check. **Alternatives.** A noise sensor (rejected: would consume world RNG and
complicate the determinism claim without adding coverage).

## Resolved unknowns

| Unknown | Resolution |
|---|---|
| How the body mounts without touching the loop | R1: Body implements EventSource |
| Where new dims live mid-run | R3: FrameStore tracks current dims; config stays boot record |
| Resize init scale | R3: §8.8 effective factors at new widths |
| Draw order for resize | R3: dims ascending, fixed tensor order |
| How the hook stays byte-inert | R4: duck-typed getattr, cycle-top |
| Growth demo without RNG contamination | R5: ConstantSensor + no-op actuator |
