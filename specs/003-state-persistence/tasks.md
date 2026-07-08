---
description: "Task list for state persistence"
---

# Tasks: State Persistence

**Input**: Design documents from `/specs/003-state-persistence/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: INCLUDED (success criteria are test-shaped; CLAUDE.md mandates green, none skipped).

## Phase 1: Setup

- [ ] T001 Create `src/pra/persistence/__init__.py` (component docstring) and add `snapshot_every_n_cycles: int = 0` (≥ 0 validation) to `src/pra/config.py`

## Phase 2: Foundational

- [ ] T002 Add `state_dict()` / `load_state_dict()` to `src/pra/core/frame.py` FrameStore: per-dim identity records + all 12 weight tensors + `next_id`; load reconstructs groups exactly
- [ ] T003 Implement `src/pra/persistence/snapshot.py`: `SystemState` (data-model §2), `capture(...)` from engine internals, `encode(state) → bytes` / `decode(bytes) → SystemState` (versioned npz + JSON meta, `allow_pickle=False`), `SnapshotVersionError`, `SnapshotCompatibilityError`, body-compat check (research R3/R6)
- [ ] T004 [P] Implement `src/pra/persistence/store.py`: `SnapshotStore` protocol, `FileSnapshotStore` (temp + `os.replace`, `list()` newest-first parsing committed blobs only), `InMemorySnapshotStore` (research R5)
- [ ] T005 Integrate in `src/pra/core/engine.py`: `snapshot_store` param + cycle-cadence capture hook (end of offline cycle only, C4); `run(seed, resume_from=...)` — version/compat checks, world from seed prefix, RNG state overwrite, frames/counters/accumulators/agency applied, warmup + done cycles skipped (research R1/R4) — depends on T002–T004

## Phase 3: US1 — byte-identical continuation (P1) 🎯 MVP

- [ ] T006 [US1] Integration test `tests/integration/test_snapshot_resume.py`: uninterrupted vs snapshot@k+resume summaries byte-identical — random mode AND curiosity mode (drive FIFOs survive); empty-population snapshot resumes; resume starts with a fresh sensing episode (SC-001)

## Phase 4: US2 — safe artifacts (P1)

- [ ] T007 [P] [US2] Unit test `tests/unit/test_snapshot_blob.py`: state round-trip is exact (arrays, config, counters, FIFOs, RNG state); doctored version → `SnapshotVersionError` naming it; metadata carries all five fields; file store: temp files invisible to `list`/`read`, delete removes exactly one, newest-first ordering (SC-002, SC-005)

## Phase 5: US3 — validated behavior untouched (P1)

- [ ] T008 [P] [US3] Extend `tests/integration/test_snapshot_resume.py`: reference seed-1 values reproduce with persistence code present and disabled; default-config run creates zero files (tmp_path scan); snapshots appear only at cycle boundaries at the configured cadence (SC-003)

## Phase 6: US4 — compatibility rejection (P2)

- [ ] T009 [P] [US4] Extend `tests/integration/test_snapshot_resume.py`: snapshot at `obs_dim=10` restored under `obs_dim=60` → `SnapshotCompatibilityError` naming field + values; compatible restore succeeds (SC-004)

## Phase 7: Contract

- [ ] T010 [P] Contract test `tests/contract/test_snapshot_store_contract.py`: `InMemorySnapshotStore` passes identical write/read/list/delete semantics; engine accepts the substitute unchanged; blobs opaque (store never parses)

## Phase 8: Polish

- [ ] T011 [P] Propagate: Doc 06 build-status note; Doc 07 §7/§8 parameter row; README snippet; quickstart walk
- [ ] T012 Quality gate: `ruff format --check` + `ruff check` + `pytest -q` all green, none skipped

## Dependencies

Setup → Foundational (T002→T003→T005; T004 ∥ T003) → US tests T006–T010 (∥ once T005 lands) → Polish. MVP = T001–T006.
