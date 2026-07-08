# Implementation Plan: Anatomy and Body

**Branch**: `004-anatomy-body` | **Date**: 2026-07-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-anatomy-body/spec.md`

## Summary

Build Doc 02's body layer: `Sensor`/`Actuator` protocols, a `Body` that
composes observations by fixed-order concatenation and routes a disjoint-union
action space, and a `ToolRegistry` whose registrations are deferred to the
slow loop and applied through the Doc 03 §7 **frame I/O resize** (learned
weights preserved bit-for-bit; new slices freshly initialized at the §8.8
effective scale; draws from the run's single generator in a fixed order).

The load-bearing integration trick keeps everything else untouched: **the Body
implements the existing `EventSource` seam** (`reset`/`step`/`obs_dim`/
`n_actions`), so it mounts through the Engine's `world_factory` with zero
engine-loop changes for composition — and a world-through-body run is
byte-identical to the direct run because delegation adds no RNG and no float
work. The only Engine addition is an inert slow-loop hook: if the world exposes
`apply_pending_tools()`, apply it at the top of the offline cycle (Doc 06 §5
ordering: resize before any snapshot) and resize the FrameStore. The Bus is
untouched (built + validated in 001).

## Technical Context

**Language/Version**: Python 3.14 (repo `.venv`)  **Dependencies**: numpy only
**Storage**: none (snapshots of resized runs are a documented follow-up — spec Edge Cases)
**Testing**: pytest — unit (composition, routing, resize math), contract (Sensor/Actuator/Body-as-EventSource substitutability), integration (byte-equivalence, mid-run growth, determinism, baseline)
**Project Type**: extends the `pra` package (`anatomy/` subpackage + FrameStore.resize + one engine hook)
**Performance**: composition is one concatenate per step (negligible); resize is O(population tensors) once per registration at the slow loop
**Constraints**:
- **Byte-identity** (FR-004/FR-008): Body delegates world calls 1:1 (same call order, no extra RNG); the engine hook is attribute-check-only for plain worlds; reference values re-verified.
- **Determinism** (FR-006): resize draws in fixed order — groups ascending by `dim`, tensors in the documented field order, growth before anything else in the cycle.
- **C4/slow-loop** (FR-005): registrations queue; `apply_pending_tools()` is called only at the offline-cycle top.
- **Scale rules** (FR-007): FrameStore tracks *current* dims; effective learning rate re-derived on resize; newborn frames use current dims.
**Scale/Scope**: reference-scale validation; growth demonstrated with synthetic extra sensors/actuators

## Constitution Check

Constitution remains the unfilled template; gating against project rules
(AGENTS.md) and the specs:

| Gate | Requirement | Status |
|---|---|---|
| Regression (FR-008) | Baseline byte-identical; hook inert without a body | PASS — duck-typed hook, no RNG/float on plain worlds (research R1/R4) |
| Byte-equal mounting (FR-004) | world-through-body ≡ direct world | PASS — Body implements EventSource by 1:1 delegation (research R1) |
| Resize honesty (FR-006) | preserve learned entries exactly; fresh slices at effective scale; fixed draw order | PASS — research R3, unit-tested bit-equality |
| C4 (FR-005) | changes only at slow-loop boundary | PASS — pending queue + cycle-top application (research R4) |
| Seam isolation | Sensor/Actuator/Body substitutable; Bus untouched | PASS — protocols + contract tests; no bus edits |
| Quality gate | ruff + pytest green, none skipped | PASS — gated in tasks |

## Project Structure

### Documentation (this feature)
```text
specs/004-anatomy-body/
├── plan.md, research.md, data-model.md, quickstart.md
├── contracts/seams.md      # Sensor/Actuator/Body/ToolRegistry contracts
└── tasks.md
```

### Source Code (repository root)
```text
src/pra/
├── anatomy/
│   ├── __init__.py
│   └── body.py             # Sensor/Actuator protocols; Body (EventSource-compatible,
│                           #   fixed-order composition + routing + ToolRegistry);
│                           #   WorldSensor/WorldActuator (mount the synthetic world);
│                           #   ConstantSensor (test/tool demo part)
└── core/
    ├── frame.py            # FrameStore.resize(new_obs_dim, new_n_actions) — Doc 03 §7;
    │                       #   store tracks current dims + effective lr
    └── engine.py           # inert slow-loop hook: apply_pending_tools() → store.resize

tests/
├── contract/test_anatomy_contract.py     # protocol substitutability; Body-as-EventSource
├── unit/test_body_composition.py         # order, widths, routing, rejections
├── unit/test_frame_resize.py             # preservation, fresh slices, draw order, shrink
└── integration/test_anatomy_growth.py    # byte-equivalence; mid-run growth; determinism; baseline
```

**Structure Decision**: `anatomy/` is its own subpackage per Doc 01's component
map. The Engine gains one duck-typed hook; the FrameStore gains `resize` beside
its existing membership operations. No harness/CLI changes — anatomy is an
engine-level capability exercised by its own tests (same posture as 003).

## Complexity Tracking

> No violations. Scope notes: tool self-invention stays [O] (interface only);
> continuous actions stay [O]; hardware timeouts are declared config without
> in-process enforcement; snapshots of resized runs are a documented Doc 06
> follow-up (the body-compat check fails loudly rather than corrupting).
