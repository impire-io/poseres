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

- [ ] T003 [P] [US1] Byte-identity test for the layout-seed degenerate path in `tests/unit/test_rover_layout_seed.py`: rover with `rover_layout_seed=None` (and layout_seed==run_seed single stream) produces a byte-identical observation stream to today's rover for seeds 1–3; plus a test that two distinct layout seeds yield distinct layouts while the brain seed is fixed.
- [ ] T004 [P] [US1] Byte-identity + learnability test for the permuted rover in `tests/unit/test_permuted_rover.py`: identity permutation ⇒ byte-identical to plain rover; a non-identity permutation is still learnable (prediction error falls) and its learned mapping does not match the un-permuted world (sanity: action/sensor vectors permuted).
- [ ] T005 [P] [US1] Metric unit test in `tests/unit/test_seeding_metric.py`: time-to-competence τ = first checkpoint where `W_smooth`-smoothed error ≤ θ; right-censoring at `N_probe` sets `reached=false`, `tau=N_probe`; `_margins_vs`-style paired margins with the ±1.9·SE superiority form; sign of margin follows "positive = seeded faster".
- [ ] T006 [P] [US1] Contract test in `tests/contract/test_seeding_cli.py` per `contracts/seeding-cli.md`: pilot prints no bar verdict; confirmatory prints B1/B2/C1 + overall; readings carry `reached`; JSON shape matches; running it leaves the byte-frozen baseline green.

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

- [ ] T012 [P] [US2] Extend `tests/unit/test_seeding_metric.py` (or a sibling) with `margin2` and `delta = margin2 − margin1`, and the C1 compound bar: superiority of `margin2` AND non-shrink (`mean(delta) ≥ −1.9·SE`).

### Implementation for User Story 2

- [ ] T013 [US2] Resize-hop orchestration in `src/pra/harness/seeding.py`: after hop 1, grow the seeded (and maturity) chain by one sensor (obs_dim 10→11) via `register_sensor` → `apply_pending_tools` → `FrameStore.resize`, applied identically at the same boundary; then run on map C (`layout_seed = H(seed, "C")`, `θ_C`).
- [ ] T014 [US2] Add `margin2`, `delta`, and bar C1 to the report (human + JSON) in `src/pra/harness/seeding.py`; overall verdict `B1 ∧ B2 ∧ C1`.

**Checkpoint**: US1 and US2 both independently functional.

---

## Phase 5: User Story 3 - Reproducible and non-perturbing (Priority: P3)

**Goal**: the experiment reproduces byte-identically and never disturbs the reference.

**Independent Test**: seeded chain snapshot/resume across scramble + resize is byte-identical; the full existing suite passes untouched.

### Tests for User Story 3

- [ ] T015 [P] [US3] Integration test in `tests/integration/test_seeding_chain.py`: a seeded chain snapshotted mid-run resumes byte-identically across the permuted-world maturity training and the +1-sensor resize; a full seeding run is deterministic across two invocations (same seeds/mode/frozen table).
- [ ] T016 [US3] Confirm the reference-suite guard stays green with all new code present (`tests/integration/test_baseline_unchanged.py` unchanged and passing); no engine/core edits landed.

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
