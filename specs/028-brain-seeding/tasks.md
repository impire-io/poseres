---
description: "Task list for Brain Seeding (feature 028)"
---

# Tasks: Brain Seeding

**Input**: Design documents from `specs/028-brain-seeding/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/seeding-cli.md, quickstart.md

**Tests**: INCLUDED — this repo's constitution is byte-identity and honest
measurement; degenerate-dial identity, the CLI contract, and chain resume are
gate-critical, so their tests are first-class tasks (not optional).

**Organization**: grouped by user story (US1 = transfer test, US2 = compounding
test, US3 = reproducibility & non-perturbation).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel (different files, no incomplete-task dependency)
- **[Story]**: US1 / US2 / US3
- Paths are repo-relative; single-project layout (`src/pra/`, `tests/`).

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: establish a green, byte-frozen baseline before any edits.

- [X] T001 Run the quality gate on a clean tree and confirm it is green, none skipped: `./.venv/bin/ruff format --check . && ./.venv/bin/ruff check . && ./.venv/bin/pytest -q` — record that `tests/integration/test_baseline_unchanged.py` (seed-1 byte guard) passes as the pre-edit reference. **DONE 2026-07-20: green (ruff format ok, lint passed, full suite passes). NOTE: worktree venv at `/Users/calmera/Work/personal/pra/.venv/bin`; run tests with `PYTHONPATH=$PWD/src` so the worktree's `src/pra` is used, not the main checkout's editable install.**

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: the opt-in config surface both new worlds depend on.

**⚠️ CRITICAL**: no user-story work begins until this is complete.

- [X] T002 **REVISED during implementation → cleaner seam.** The rover is an *example* world mounted via its own `make_rover_body` factory (not `Config.world`), so rover-specific dials belong as **factory parameters**, not core `Config` fields — this leaves the validated `Config` completely untouched (strictly more reference-preserving) and matches how the rover already differs from the ladder worlds. **DONE:** `make_rover_body`/`RoverWorld` gained `layout_seed`, `permute`, `permute_seed` kwargs; the seeding harness passes them via closure factories. No `Config` change.

**Checkpoint**: config carries the new dials, all defaults inert.

---

## Phase 3: User Story 1 - Transfer, and it is not maturity (Priority: P1) 🎯 MVP

**Goal**: hop A→B measured across three arms; seeded reaches θ_B sooner than fresh (B1) and than the maturity control (B2).

**Independent Test**: `pra-validate seeding --mode confirmatory` decides B1 and B2 at 24 seeds with spreads and reach-rates; the two new worlds' degenerate dials are byte-identical to today's rover.

### Tests for User Story 1

- [X] T003 [P] [US1] Byte-identity test for the layout-seed degenerate path in `tests/unit/test_rover_layout_seed.py`: `layout_seed=None` byte-identical to plain rover; distinct seeds → distinct maps; same seed → same map regardless of run rng; deterministic.
- [X] T004 [P] [US1] Byte-identity + learnability test for the permuted rover in `tests/unit/test_permuted_rover.py`: `permute=False` byte-identical; perm vectors are valid permutations; permuted world learnable (error falls) and distinct from the un-permuted map; permutation reindexes senses without redrawing the map.
- [X] T005 [P] [US1] Metric unit test in `tests/unit/test_seeding_metric.py`: trailing smoothing, τ first-crossing, censoring (incl. common-length), paired margin sign/pairing, ±1.9·SE superiority/noninferiority bounds.
- [X] T006 [P] [US1] Contract test in `tests/contract/test_seeding_cli.py`: pilot no bar verdict (calibration only); confirmatory B1/B2 + overall; readings carry `reached`/`n_censor`; margin sign convention; JSON shape; CLI `main` writes JSON. (Baseline byte-identity guarded by the full gate, which stays green.)

### Implementation for User Story 1

- [X] T007 [US1] Layout-seed plumbing (FR-001) in `src/pra/examples/rover/world.py`: `RoverWorld`/`make_rover_body` gained a `layout_seed` kwarg — the map (obstacles+spawns) draws from an independent generator while reset/emit stay on the brain's run rng; `layout_seed=None` byte-identical (smoke-verified).
- [X] T008 [US1] Permuted rover (FR-002) in `src/pra/examples/rover/world.py`: `permute`/`permute_seed` kwargs draw action + sensor permutations from an independent generator, applied in `apply()`/`_emit()`; `permute=False` byte-identical; permuted world measured learnable (improvement 0.26) and distinct.
- [X] T009 [US1] Seeding orchestration core in `src/pra/harness/seeding.py`: pretrain→capture-snapshot→resume-with-extended-config, reading the trajectory from `SystemState.pred_errors`; maps A/B via `_layout_seed(seed, ...)`; maturity arm on the permuted rover. **Key mechanic learned & handled:** `effective_n_cycles=max(n_cycles, max(horizon_checkpoints))` — run length pinned via `horizon_checkpoints=(total,)`.
- [X] T010 [US1] Time-to-competence + margins in `src/pra/harness/seeding.py`: `W_smooth` trailing smoothing, τ with **common-length censoring** (shortest arm, so warmup-length never fakes a margin), `margin1`/`marginM`, the ±1.9·SE one-sided form (T7 precedent), reach-rates; bars B1, B2.
- [X] T011 [US1] `pra-validate seeding` subcommand in `src/pra/harness/cli.py`: `--seeds`, `--mode pilot|confirmatory`, `--json`, `--config`; human bar lines + JSON; pilot reports calibration only. Smoke-verified end-to-end (2 seeds: B1 +260, B2 +63.5, both PASS).

**Checkpoint**: US1 is independently runnable — B1/B2 decided, both worlds byte-clean.

---

## Phase 4: User Story 2 - The head start does not shrink across a body-growing hop (Priority: P2)

**Goal**: chain seeded A→B→(+1 sensor resize)→C; seeded-vs-fresh margin at C is superior and non-shrinking (C1).

**Independent Test**: hop 2 runs at 24 seeds; C1 decided with margin₁ and margin₂ reported per seed.

### Tests for User Story 2

- [X] T012 [P] [US2] `tests/unit/test_seeding_metric.py` + `tests/unit/test_rover_resize.py`: `_delta_margin` (paired m2−m1), the C1 combination (margin2 superiority AND delta non-shrink), and the resize world (native 11-dim, pending 10→11 growth, ungrown byte-identical, deterministic).

### Implementation for User Story 2

- [X] T013 [US2] Resize hop: `world.py` gains a clean RNG-free back-ray (`extra_ray` native 11-dim; `extra_ray_pending` grows 10→11 via `register_sensor` → `apply_pending_tools` → `FrameStore.resize`). `seeding.py` `_probe(grow=…)` + `_hop2` chain the seeded/maturity brains onto map C; fresh-C mounts the native 11-dim rover.
- [X] T014 [US2] `margin2`, `delta`, bar C1 (superiority AND non-shrink) in the report (human + JSON); overall `B1 ∧ B2 ∧ C1`; `--no-hop2` CLI flag. θ_C recalibrated on the 11-dim fresh curve → 0.33 (frozen before the hop-2 run).

**Checkpoint**: US1 and US2 both independently functional.

---

## Phase 5: User Story 3 - Reproducible and non-perturbing (Priority: P3)

**Goal**: the experiment reproduces byte-identically and never disturbs the reference.

**Independent Test**: seeded chain snapshot/resume across scramble + resize is byte-identical; the full existing suite passes untouched.

### Tests for User Story 3

- [X] T015 [P] [US3] Integration test `tests/integration/test_seeding_chain.py`: the full two-hop run reproduces byte-identically across two invocations (τ tables + all four margins), hop-2 readings grow the body, and the reference rover is unperturbed by the seeding machinery.
- [X] T016 [US3] Reference-suite guard stays green with all new code present (full gate: `test_baseline_unchanged.py` passes; no engine/core edits — orchestration only).

**Checkpoint**: all three stories independently functional; constitution intact.

---

## Phase 6: Experiment, Recording & Gate (Cross-Cutting)

**Purpose**: run the science, freeze it honestly, propagate, and gate.

- [ ] T017 Run the pilot (`pra-validate seeding --mode pilot`), choose θ_B/θ_C/`N_pretrain`/`N_probe`/`W_smooth`, and **freeze** them into the `_TBD (pilot)_` table in `design/validate/SEEDING-DIAGNOSIS.md`; commit the pre-registration BEFORE the confirmatory run.
- [ ] T018 Run the confirmatory 24-seed experiment (`--mode confirmatory`); append raw per-seed τ, the four margins, verdicts, and reach-rates to the Results section of `design/validate/SEEDING-DIAGNOSIS.md`.
- [ ] T019 [P] Record JOURNEY chapter 44 (honest outcome, including the reversal condition if triggered) and refresh "Where things stand"; update the ROADMAP seeding entry and Doc 06 §5b persistence guidance to match the verdict.
- [ ] T020 Run `quickstart.md` end-to-end and the full quality gate green, none skipped: `./.venv/bin/ruff format --check . && ./.venv/bin/ruff check . && ./.venv/bin/pytest -q`.

---

## Dependencies & Execution Order

- **Setup (T001)** → **Foundational (T002)** blocks all stories.
- **US1 (T003–T011)** is the MVP; depends only on T002.
- **US2 (T012–T014)** builds on the US1 harness (extends `seeding.py`); start after T009–T011.
- **US3 (T015–T016)** validates the chain built by US1+US2; start after T013.
- **Phase 6 (T017–T020)** depends on US1+US2 complete (needs a working `pra-validate seeding`); T017 (freeze) MUST precede T018 (confirmatory).

### Within US1

- Tests T003–T006 [P] written first (T003/T004 must pass immediately — byte-identity; T005/T006 drive the metric/CLI).
- Worlds T007, T008 (both edit `world.py` → sequential, not [P]).
- Harness T009 → T010 → T011 (same module, sequential).

### Parallel Opportunities

- T003, T004, T005, T006 [P] — distinct test files.
- T019 [P] — docs, independent of T020's gate run once results exist.

---

## Implementation Strategy

### MVP First (US1)

1. Phase 1 Setup → Phase 2 Foundational → Phase 3 US1.
2. **STOP and VALIDATE**: B1/B2 decided at 24 seeds; both worlds byte-clean.

### Incremental Delivery

1. US1 (transfer test) → the core seeding verdict lands.
2. US2 (compounding across resize) → the head-start-non-shrink verdict.
3. US3 (reproducibility guards) → constitution proven intact.
4. Phase 6 → pilot-freeze-confirmatory, record, gate.

---

## Notes

- No engine/core edits: the experiment is orchestration over unchanged
  `Engine.run(resume_from=…)`, `FrameStore.resize`, and the snapshot codec.
- Pre-registration boundary is hard: T017 (freeze θ/budgets, commit) strictly
  before T018 (confirmatory). No criterion tuned after the confirmatory data.
- Sign convention everywhere: positive margin = seeded faster (τ is lower-better).
- Commit after each logical group; sign commits; hold pushes until asked.
