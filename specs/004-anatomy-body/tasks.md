---
description: "Task list for anatomy and body"
---

# Tasks: Anatomy and Body

**Input**: Design documents from `/specs/004-anatomy-body/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅
**Tests**: INCLUDED.

## Phase 1: Setup
- [ ] T001 Create `src/pra/anatomy/__init__.py` (component docstring)

## Phase 2: Foundational
- [ ] T002 Implement `src/pra/anatomy/body.py`: `Sensor`/`Actuator` protocols, `AnatomyError`, `Body` (ordered composition + width checks, disjoint-union routing, EventSource-compatible reset/step, pending-tool queue + `register_sensor`/`register_actuator`/`deregister`/`list_tools`/`apply_pending_tools`), `WorldSensor`, `WorldActuator`, `ConstantSensor` (research R1/R2/R4, data-model §1–§2)
- [ ] T003 Implement `FrameStore.resize(new_obs_dim, new_n_actions, rng)` in `src/pra/core/frame.py` per data-model §3: bit-preservation, trailing growth at §8.8 effective scales, trailing shrink, fixed draw order, current-dims + effective-lr update; births/`results_for` use current dims (research R3)
- [ ] T004 Engine hook in `src/pra/core/engine.py`: at offline-cycle top, duck-typed `apply_pending_tools()` → `store.resize(...)`; inert for plain worlds (research R4)

## Phase 3: US1 — composed body, byte-identical (P1) 🎯 MVP
- [ ] T005 [P] [US1] Unit `tests/unit/test_body_composition.py`: fixed-order concat, widths, wrong-width `AnatomyError` naming the sensor, routing table incl. boundaries, range check, duplicate-id + last-part rejection
- [ ] T006 [P] [US1] Contract `tests/contract/test_anatomy_contract.py`: substitute sensor/actuator accepted unchanged; `Body` satisfies `EventSource`; actuators return None (feedback only via sensors)
- [ ] T007 [US1] Integration `tests/integration/test_anatomy_growth.py::test_world_through_body_is_byte_identical`: mounted vs direct summaries byte-equal (SC-001)

## Phase 4: US2 — growth without forgetting (P1)
- [ ] T008 [P] [US2] Unit `tests/unit/test_frame_resize.py`: obs growth (shapes, bit-preserved old slices, fresh nonzero new slices, zero biases), action growth, shrink discards, deterministic draws (same seed twice), effective-lr update
- [ ] T009 [US2] Integration `test_anatomy_growth.py`: mid-run `ConstantSensor` + no-op actuator registration at cycle k — deferred to slow loop (SC-005), shapes/dims grow, pre-registration weights bit-equal, run completes, byte-identical re-run (SC-002)

## Phase 5: US3 — baseline untouched (P1)
- [ ] T010 [P] [US3] `test_anatomy_growth.py::test_baseline_unchanged`: reference seed values exact with the anatomy layer present and unused (SC-003)

## Phase 6: Polish
- [ ] T011 [P] Propagate: Doc 02 build-status note; README layout line; JOURNEY.md chapter (required by AGENTS.md)
- [ ] T012 Quality gate: ruff format/check + full pytest green, none skipped

## Dependencies
Setup → T002→T003→T004 (T003 ∥ T002 partially) → tests T005–T010 (∥) → Polish. MVP = T001–T007.
