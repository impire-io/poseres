---
description: "Task list for multi-stream experience"
---

# Tasks: Multi-Stream Experience

**Input**: Design documents from `/specs/009-multi-stream/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅
**Tests**: INCLUDED (repo rule: all green, none skipped).

## Phase 1: Setup

- [ ] T001 `Config.n_streams` (default 1) + validation incl. the B5 guard
      (`n_streams > 1` rejects `snapshot_every_n_cycles > 0`) in
      `src/pra/config.py` (FR-008, research R6/R7)

## Phase 2: US1 — K explorers, one brain, deterministic (P1) 🎯 MVP

- [ ] T002 [US1] Engine K-stream branch in `src/pra/core/engine.py`:
      identical-construction worlds + per-stream generator reseed (R2),
      stream_rngs from spawn keys (R1), episode scheduler `e mod K` with
      merged-episode cadence (R3), per-stream pending + single boot each in
      continuous mode; policy draws from the acting stream's generator;
      K=1 path untouched
- [ ] T003 [US1] Integration `tests/integration/test_multistream.py`:
      K=1 byte-identity vs pre-feature; K=4 determinism on re-run;
      structure sharing (streams' worlds identical structure, different
      exploration); snapshot loud-fail at K>1
- [ ] T004 [US1] Unit `tests/unit/test_multistream.py`: validation
      rejections; spawn-key seeding distinct per stream and deterministic;
      scheduler/cadence math

## Phase 3: US2 — regime is mechanism-safe (P1)

- [ ] T005 [US2] Placement tests: consolidation positions (total
      observation count) identical K=1 vs K=4 on the same schedule
      (SC-003); continuous composition — each of K streams boots exactly
      once (guard worlds) and runs deterministic (SC-005)

## Phase 4: US3 — the exit reading (P1)

- [ ] T006 [US3] Run the pre-registered exit protocol (R5): reference
      world, seeds 1–8, K ∈ {1, 2, 4}, equal experience, paired margins +
      noninferiority verdicts; plus the investigatory continuous-rover
      reading (K ∈ {1, 4}, seeds 1–3); record
      `specs/009-multi-stream/reading.md` whichever way it lands

## Phase 5: Polish

- [ ] T007 [P] Propagate: Doc 07 `n_streams` entry; PRA-01 §6.6 note;
      GETTING-STARTED paragraph; ROADMAP B4; JOURNEY chapter + "Where
      things stand"; memory
- [ ] T008 Quality gate → merge to main → push

## Dependencies

T001 → T002 → (T003 ∥ T004) → T005 → T006 → T007 → T008. MVP = T001–T004.
