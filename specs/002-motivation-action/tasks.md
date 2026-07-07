---
description: "Task list for the motivation and action layer"
---

# Tasks: Motivation and Action Layer

**Input**: Design documents from `/specs/002-motivation-action/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅ (seams.md, cli.md, config.md)

**Tests**: INCLUDED — the spec's success criteria are test-shaped (byte-identity, immutability, T7), quickstart.md maps every scenario to a test file, and the user's global CLAUDE.md mandates "all tests pass, none skipped". Tests are written before the implementation they cover where practical.

**Organization**: Grouped by user story (spec.md): US1 (P1, MVP), US2 (P1), US3 (P2), US4 (P2), US5 (P3).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: parallelizable (different files, no dependency on an incomplete task)
- Every task names an exact file path

## Path Conventions

Single Python project extending feature 001: source under `src/pra/`, tests under `tests/`, repo root `/Users/calmera/Work/personal/pra`, everything through the repo `.venv`.

---

## Phase 1: Setup

**Purpose**: Package skeleton for the two new components.

- [x] T001 Create `src/pra/motivation/__init__.py` and `src/pra/action/__init__.py` subpackage markers (docstrings naming the Doc 01 components they implement)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Config, the two seams with their defaults, and Engine integration — everything every user story depends on. The byte-identity rules (research R1/R2) are load-bearing here.

**⚠️ CRITICAL**: No user story is testable until this phase completes.

- [x] T002 Extend `src/pra/config.py` with the drive block (`drive_weights={"curiosity":1.0}`, `w_progress=1.0`, `w_novelty=1.0`, `lp_recent_window=60`, `lp_baseline_window=600`, `novelty_memory_size=200`) and the policy block (`policy_mode="random"`, `exploration_epsilon=0.1`, `lookahead_min_age_cycles=2`) per contracts/config.md — frozen, construction-time validation (weights ≥ 0 and non-empty, `lp_baseline_window > lp_recent_window`, `exploration_epsilon ∈ [0,1]`, `policy_mode ∈ {random, curiosity}`), defaults leave every existing mode untouched
- [x] T003 [P] Implement `src/pra/motivation/context.py` (`DriveContext`: observation, recent_pred_errors, observation_memory, step_index — read-only view) and `src/pra/motivation/drive.py` (`Drive` Protocol with `id()`/`value(context)`; `CuriosityDrive` with frozen params + mutable bookkeeping FIFOs, windowed learning progress `max(0, mean(baseline)−mean(recent))` gated on ≥ `lp_recent_window` baseline samples, min-distance novelty with empty-memory ⇒ 1.0, `value = w_progress·LP + w_novelty·novelty`, bookkeeping updated after valuation; `WeightedDriveSet` with fixed-order accumulation and one-to-one weight/id validation) per data-model §2 and research R5
- [x] T004 [P] Implement `src/pra/action/policy.py`: `PolicyContext` (observation, n_actions, best_frame info, `predict_decoded(action)`, `drive_value_of(obs)`), `Policy` Protocol, `RandomPolicy` (exactly one `rng.integers(n_actions)` draw — the pinned baseline, research R1), `CuriosityLookaheadPolicy` (ε-gate draw first; random when exploring / no best frame / `age < lookahead_min_age_cycles`; else argmax over ascending actions of drive-valued decoded predictions, ties to lowest index, no further draws) per data-model §3 and research R6
- [x] T005 Integrate in `src/pra/core/engine.py` + `src/pra/telemetry/recorder.py`: Engine accepts a `policy` seam (default `RandomPolicy`) and, in agency mode (`policy_mode="curiosity"` or an injected drive set), builds `DriveContext`/`PolicyContext` per step (best-frame predict→decode via the existing FrameStore/scorer machinery), records the per-step value signal and directed-action fraction, and replaces the inline `rng.integers(n_actions)` with `policy.select_action(...)`; `PerSeedRunSummary` gains the **conditional** agency block (value_signal_mean/final, learning_progress_mean, novelty_mean, directed_fraction) serialized **only when present** so baseline bytes are unchanged (research R2, data-model §4) — depends on T002–T004

### Foundational verification tests

- [x] T006 [P] Unit test `tests/unit/test_curiosity_drive.py`: LP ≈ 0 on flat-low (mastered) and flat-high (noise) histories, LP > 0 on a falling history; novelty = 1.0 on empty memory, low for familiar, high for unfamiliar observations; value finite from an empty context; bookkeeping bounded at configured sizes
- [x] T007 [P] Unit test `tests/unit/test_lookahead_policy.py`: argmax selection against a scripted drive; tie-break to lowest action index; ε-gate draws random; maturity gate (young/no best frame ⇒ random); RNG draw order fixed (one uniform, then integer only when random path taken)
- [x] T008 [P] Contract test `tests/contract/test_drive_contract.py`: a substitute constant drive is accepted unchanged and the weighted sum is exact; `value()` consumes no RNG (generator state unchanged); drive parameter mutation attempts raise (frozen)
- [x] T009 [P] Contract test `tests/contract/test_policy_contract.py`: a substitute always-action-0 policy is accepted by the Engine unchanged; `RandomPolicy` reproduces the validated reference seed-1 summary values exactly (early 0.4465 / late 0.1574 / checkpoints (3,19)/(3,24)/(4,27)); curiosity-mode runs are byte-identical on re-run

**Checkpoint**: Both seams work, defaults pinned, baseline untouched, all foundational tests green.

---

## Phase 3: User Story 1 — The system acts on its own initiative (Priority: P1) 🎯 MVP

**Goal**: One command runs the curious agent end-to-end: random at cold start, directed once matured, value signal finite from step one, byte-identical re-runs.

**Independent Test**: `pra-validate agency --seeds 1` completes with policy-selected actions, finite per-step value signal, and deterministic re-run.

- [x] T010 [P] [US1] Integration test `tests/integration/test_agency_determinism.py`: a curiosity-mode run completes end-to-end; the recorded value signal exists from the first step and is finite throughout; two runs of the same seed serialize byte-identically; the summary carries the agency telemetry block (SC-001, SC-002)
- [x] T011 [US1] Implement `src/pra/harness/agency.py`: `run_agency(config, workers)` — per seed, two full predictive runs with the **same seed** (identical world, equal experience): curious arm (`CuriosityLookaheadPolicy` + drive set) and random arm (`RandomPolicy`), returning an `AgencyRun` (curious/random summary lists paired by seed, failed_seeds surfaced, per-seed wall) with parallel workers per the 001 pattern (research R7, data-model §4)
- [x] T012 [US1] Add the `agency` command to `src/pra/harness/cli.py` (`--seeds/--true-dim/--config/--json/--strict/--workers`; single-seed FOR-DEBUGGING-ONLY banner) rendering the curious arm's telemetry; wire `build_agency_report` scaffolding in `src/pra/harness/report.py` (contracts/cli.md) — verdict content lands in US3

**Checkpoint**: The agent runs, observable and reproducible. MVP demoable.

---

## Phase 4: User Story 2 — The validated core is untouched (Priority: P1)

**Goal**: Prove byte-identity of every existing mode with the validated build.

**Independent Test**: the suite passes T1–T6 with a reference seed's summary byte-identical to the recorded validated values.

- [x] T013 [P] [US2] Integration test `tests/integration/test_baseline_unchanged.py`: a default-config Engine run (policy seam at its default) reproduces the validated reference seed-1 values exactly; a baseline summary's canonical serialization contains **no** agency fields; the determinism check still PASSes; `evaluate_suite` on a small baseline run emits no T7 (SC-003, FR-008)

**Checkpoint**: The regression gate is provably frozen.

---

## Phase 5: User Story 3 — Directed exploration measurably not worse than random (Priority: P2)

**Goal**: The T7 verdict — honest, per-seed, majority-judged.

**Independent Test**: `pra-validate agency` emits T7 with the per-seed margin table; PASS at the reference config.

- [x] T014 [P] [US3] Integration test `tests/integration/test_agency_t7.py`: engineered summary pairs where curious ≥ random in a majority ⇒ PASS, and where it loses the majority ⇒ FAIL with per-seed margins present (never a mean alone); at a small real config the evaluator runs end-to-end (FR-009)
- [x] T015 [US3] Add the T7 evaluator to `src/pra/harness/acceptance.py` (claim, criterion "curious improvement ≥ random improvement in a strict majority of seeds", per-seed `t7_detail` margins, NOT_AVAILABLE handling) per data-model §4
- [x] T016 [US3] Extend `src/pra/harness/report.py` (+ JSON) to render T7 with the per-seed table and the agency telemetry; wire into the `agency` command's output (contracts/cli.md)

**Checkpoint**: The load-bearing claim has an honest verdict; reference-config PASS is measured (SC-004).

---

## Phase 6: User Story 4 — The drive cannot be corrupted or gamed (Priority: P2)

**Goal**: Immutability and self-limiting curiosity, explicitly proven.

**Independent Test**: mutation attempts fail; mastered/noise/improving histories yield ~0/~0/positive learning progress.

- [x] T017 [P] [US4] Extend `tests/contract/test_drive_contract.py`: attempts to set any drive parameter, weight, or the Config drive fields raise; the drive roster cannot be altered at runtime (SC-005, FR-003)
- [x] T018 [P] [US4] Extend `tests/unit/test_curiosity_drive.py` with the three named histories (mastered flat-low, unlearnable flat-high, genuinely-improving) asserting ~0 / ~0 / positive learning progress with the default windows (US4 acceptance scenarios 2–4)

**Checkpoint**: The mandatory safety invariant and the self-limiting property are locked by tests.

---

## Phase 7: User Story 5 — Counter-drive by configuration only (Priority: P3)

**Goal**: The multi-drive mechanism works without code change.

**Independent Test**: a second trivial drive configured with fixed weights yields the exact weighted sum.

- [x] T019 [P] [US5] Integration test `tests/integration/test_multi_drive.py`: a constant second drive registered via configuration produces `value = w1·curiosity + w2·constant` exactly; the base configuration runs with curiosity only; weight/id mismatches are rejected at construction (SC-006, FR-002)

**Checkpoint**: The Doc 05 §5 escape hatch exists as configuration.

---

## Phase 8: Polish & Cross-Cutting Concerns

- [x] T020 [P] Walk quickstart.md end-to-end (`agency`, `suite`, `determinism`) confirming outputs match the documented shape; assert the only disk artifacts are requested reports
- [x] T021 [P] Propagate to the living specs: record T7 (claim, criterion, reference measurement) in `design/validate/PRA-02-validation-specification.md`; update `design/05-motivation-action.md` status tags for what is now built/validated; note the new parameters in `design/07-configuration-reference.md`; update `README.md` with the `agency` command
- [x] T022 Run the reference T7 measurement (8 seeds, parallel) and record the honest result in the spec + feature docs — whatever it is (SC-004 expects PASS; a FAIL is reported as a finding, not hidden)
- [x] T023 Quality gate (MUST be green, none skipped): `./.venv/bin/ruff format --check .` && `./.venv/bin/ruff check .` && `./.venv/bin/pytest -q`

---

## Dependencies & Execution Order

- **Setup (P1)** → **Foundational (P2)**: T002 first (config), then T003/T004 in parallel, then T005 (engine) after both; tests T006–T009 in parallel once their targets exist. Foundational **blocks all stories**.
- **US1 (P3)**: needs Foundational. T010 (test) before/with T011 (runner) → T012 (CLI).
- **US2 (P4)**: needs only Foundational (T013 independent of US1).
- **US3 (P5)**: needs US1's runner (T011); T014 with T015 → T016.
- **US4 (P6)**, **US5 (P7)**: need only Foundational; independent of each other and of US1/US3.
- **Polish (P8)**: T020–T022 after all stories; T023 last.

### Parallel opportunities

- T003 ∥ T004 (different packages); T006–T009 all ∥; T010 ∥ T013 ∥ T017 ∥ T018 ∥ T019 across stories once Foundational lands.

## Implementation Strategy

MVP = Phase 1 + 2 + US1 (the agent runs, reproducibly). Then US2 (prove the gate frozen) before anything else touches main. US3 delivers the verdict; US4/US5 lock invariants; Polish measures the reference T7 and propagates specs. Commit after each phase or logical group; sign commits; never `git add -A`.
