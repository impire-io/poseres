---
description: "Task list for the Gymnasium adapter"
---

# Tasks: The Gymnasium Adapter

**Input**: Design documents from `/specs/007-gymnasium-adapter/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅
**Tests**: INCLUDED (repo rule: all green, none skipped).

## Phase 1: Setup

- [x] T001 Add the optional dependency surface to `pyproject.toml`:
      `[project.optional-dependencies] gym = ["gymnasium>=1.0"]` and
      `gymnasium>=1.0` appended to `dev` (FR-006; research R5) —
      reinstall the worktree venv so the gate exercises it

## Phase 2: US1 — mount a Gymnasium world, deterministically (P1) 🎯 MVP

- [x] T002 [US1] Create `src/pra/anatomy/gymnasium_body.py`:
      module docstring (adapter role, termination semantics, seed scheme,
      v1 scope, snapshot deferral — data-model), lazy import helper with
      the `poseres[gym]` ImportError (R5), and `GymnasiumWorld` —
      space validation per the data-model validation table, entropy from
      pure PCG64 state read or explicit `seed=` (R3), `_next_seed()` via
      `SeedSequence(E, spawn_key=(k,))`, C-order float64 flattening,
      Discrete `start` mapping, `resets`/`respawns` counters, `close()`
      (FR-001..FR-005, FR-007)
- [x] T003 [US1] Same module: `GymnasiumBody(Body)` — wires
      `WorldSensor`/`WorldActuator` around a `GymnasiumWorld` (R1),
      forwards `world`/`resets`/`respawns`/`close`, plus
      `GymnasiumBody.factory(env_or_id, **make_kwargs)` returning an
      Engine-ready `world_factory` with fresh-env-per-call and the
      both-numbers config mismatch error (FR-007)
- [x] T004 [P] [US1] Unit `tests/unit/test_gymnasium_world.py`
      (scripted fake envs, no real gymnasium env needed): seed scheme is
      the documented closed form and reproducible across instances;
      explicit-seed vs rng-derived entropy; engine generator state
      bit-identical before/after mount and across resets (no draws);
      flattening (multi-dim Box → C-order float64, width = element
      count); Discrete `start` offset applied
- [x] T005 [P] [US1] Contract `tests/contract/test_gymnasium_contract.py`:
      `GymnasiumWorld` satisfies `EventSource`; `GymnasiumBody` is a
      `Body` and the composed surface is float64 at declared width;
      nothing but the observation vector crosses `step`; every rejection
      path from the validation table (Box action space, Discrete
      observation space, rng+seed both/neither, unreadable generator
      state, step-before-reset, factory size mismatch naming both
      numbers, missing gymnasium via monkeypatched import handle —
      never a skip) (FR-006, FR-007, SC-004)
- [x] T006 [US1] Integration `tests/integration/test_gymnasium_cartpole.py`
      (real CartPole-v1, small schedule): same `(config, seed)` twice →
      byte-identical `serialize()`; different seed → different summary;
      run through `GymnasiumBody.factory("CartPole-v1")` end-to-end
      (SC-001)

## Phase 3: US2 — the termination boundary, explicit and tested (P2)

- [x] T007 [US2] Unit (same file as T004): scripted env terminating
      after N live steps — respawn resets immediately with the next
      sequence seed, the step returns the *fresh* observation (terminal
      observation demonstrably discarded), `respawns` increments,
      `truncated` takes the same path, and one shared reset counter
      covers episode starts + respawns (FR-004; R2; data-model sequence)
- [x] T008 [US2] Integration (same file as T006): a real CartPole run
      under the pinned random policy finishes with `respawns > 0` — the
      semantics is exercised, not just implemented (FR-010, US2/AS2)

## Phase 4: US3 — the worked example (P3)

- [x] T009 [US3] `examples/cartpole.py`: heavily commented single file —
      builds the adapter via `GymnasiumBody.factory("CartPole-v1")`,
      runs the reference schedule on seed 1, prints a plain-language
      summary (early → late prediction error, population, respawns),
      re-runs seed 1 and prints the byte-identity verdict; under one
      minute total; ruff-clean (FR-009, SC-003; R6)
- [x] T010 [P] [US3] Integration (same file as T006): body ≡ world —
      an engine run mounted through `GymnasiumBody` is byte-identical
      to the same run mounted on `GymnasiumWorld` directly (the 004 R1
      equivalence replayed; contracts §2)

## Phase 5: Polish & gate

- [x] T011 Stage the parallel-work doc edits (no shared files touched):
      `specs/007-gymnasium-adapter/journey-chapter.md` (proposed
      JOURNEY.md chapter, template-conformant) and
      `specs/007-gymnasium-adapter/docs-propagation.md` (proposed
      GETTING-STARTED §4/§7 + README pointers, ROADMAP B2 exit note)
- [x] T012 Quality gate, all green, none skipped:
      `./.venv/bin/ruff format --check . && ./.venv/bin/ruff check . &&
      ./.venv/bin/pytest -q` — including the untouched reference suite
      (`test_baseline_unchanged` byte-identity) and a timed example run
      (< 1 minute, SC-003)

## Dependencies

- T001 → everything (the dev venv must carry gymnasium for tests)
- T002 → T003 → {T004, T005, T006} (T004/T005 parallel)
- T007 needs T002; T008 needs T006's harness file
- T009/T010 need T003; T011/T012 last

## Notes

- No task touches `core/`, `world/`, `harness/`, `config.py`,
  `anatomy/body.py`, or any shared narrative file — the byte-frozen
  reference is protected by construction, and parallel-session files
  (`JOURNEY.md`, `ROADMAP.md`, `GETTING-STARTED.md`, `README.md`) are
  reached only through the staged proposals of T011.
