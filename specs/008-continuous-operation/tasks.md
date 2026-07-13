---
description: "Task list for continuous operation"
---

# Tasks: Continuous Operation

**Input**: Design documents from `/specs/008-continuous-operation/`
**Prerequisites**: plan.md ✅, spec.md ✅ (SC-003 amended openly), research.md ✅, data-model.md ✅, contracts/ ✅
**Tests**: INCLUDED (repo rule: all green, none skipped).

## Phase 1: Setup

- [x] T001 `Config.episode_mode` (`"episodic"` default / `"continuous"`) +
      validation in `src/pra/config.py` (data-model table; FR-009)

## Phase 2: Foundational

- [x] T002 `SingleBootWorld` test instrument + unit tests in
      `tests/unit/test_continuous.py`: one boot allowed, second raises,
      counter exposed; config validation rejections (research R8, FR-007)

## Phase 3: US1 — a reset-less world runs to a faithful summary (P1) 🎯 MVP

- [x] T003 [US1] Engine continuous branch in `src/pra/core/engine.py`:
      boot-once + `pending` carry in the episode loop (one changed line per
      research R2), both `do_offline` paths; episodic path untouched
- [x] T004 [US1] Integration `tests/integration/test_continuous.py`:
      default-mode byte-equivalence (episodic ≡ pre-feature), single-boot
      full-schedule run over `SingleBootWorld` (boot counter == 1),
      continuous determinism on re-run and under workers (FR-001/002/005)

## Phase 4: US2 — every mechanism keeps its meaning (P1)

- [x] T005 [US2] Boundary-placement tests (SC-004): chain break, fair-judge
      window restart, and norm-cap projection fire exactly at
      `k × steps_per_episode` in continuous mode; stream gap-free and
      duplication-free by observation accounting (FR-003/004)
- [x] T006 [US2] World-state capture protocol: `state_dict`/
      `load_state_dict` on `SensorimotorWorld` + the three ladder worlds +
      `Body` delegation (additive methods only); unit round-trip tests
      (research R5, data-model)
- [x] T007 [US2] Snapshot support: optional `SystemState.world_state`
      (+ `pending`) in `src/pra/persistence/snapshot.py`, engine capture on
      C4 + restore on resume, loud `RuntimeError` for non-capturing worlds;
      integration: continuous resume byte-identity (SC-003), episodic blob
      bit-identity, old-blob decode tolerance (FR-005)
- [x] T008 [US2] Composition: continuous + drives, continuous + Body,
      continuous + ladder world — deterministic full runs, no special cases
      (research R7)

## Phase 5: US3 — the reading (P2)

- [x] T009 [US3] Run the investigatory episodic-vs-continuous reading
      (reference world, 8 seeds, standard schedule, random policy) and
      record `specs/008-continuous-operation/reading.md` with per-seed
      spreads — whichever way it lands (FR-008, research R9)

## Phase 6: Polish

- [x] T010 [P] Propagate: Doc 07 `episode_mode` entry; PRA-01 lifecycle
      note (virtual episodes); GETTING-STARTED continuous-mode paragraph;
      ROADMAP B3 done; JOURNEY chapter + "Where things stand"; memory
- [x] T011 Quality gate (`ruff format --check`, `ruff check`, full
      `pytest -q`, none skipped) → merge to main → push

## Dependencies

T001 → T002 → T003 → T004 → (T005 ∥ T006) → T007 → T008 → T009 →
T010 → T011. MVP = T001–T004.
