---
description: "Task list for PRA Validation Harness implementation"
---

# Tasks: PRA Validation Harness

**Input**: Design documents from `/specs/001-validation-harness/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅ (cli.md, seams.md, config.md, report-schema.json)

**Tests**: INCLUDED. The feature plan enumerates a full `tests/` tree, quickstart.md maps every acceptance scenario to a specific test file, and the user's CLAUDE.md mandates "all tests pass, none skipped." Test tasks are therefore generated and, where practical, written before the implementation they cover.

**Organization**: Tasks are grouped by user story (from spec.md) to enable independent implementation and testing. Priorities: US1 (P1, MVP), US2 (P1), US3 (P2), US4 (P2), US5 (P3).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependency on an incomplete task)
- **[Story]**: Which user story the task serves (US1–US5); Setup/Foundational/Polish carry no story label
- Every task names an exact file path

## Path Conventions

Single Python project (library + CLI). Source under `src/pra/`, tests under `tests/`, both at the repository root `/Users/calmera/Work/personal/pra`. Run everything through the repo-root `.venv` (Python 3.14, numpy 2.4.6; PEP 668 blocks the system interpreter).

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project skeleton, packaging, and the quality-gate toolchain (research R10).

- [x] T001 Create the package and test skeleton with empty `__init__.py` files per plan.md: `src/pra/{__init__,config}.py`, `src/pra/world/__init__.py`, `src/pra/core/__init__.py`, `src/pra/telemetry/__init__.py`, `src/pra/harness/__init__.py`, and the `tests/contract/`, `tests/integration/`, `tests/unit/` directories each with `__init__.py`
- [x] T002 Author `pyproject.toml` at repo root: package metadata, `numpy>=2.4` as the sole runtime dependency, `[dev]` extra (`pytest`, `ruff`), `[project.scripts]` console entry `pra-validate = "pra.harness.cli:main"`, plus `[tool.ruff]` (format + lint) and `[tool.pytest.ini_options]` config (research R10)
- [x] T003 Install editable into the repo venv (`./.venv/bin/python -m pip install -e ".[dev]"`) and confirm `./.venv/bin/ruff`, `./.venv/bin/pytest`, and `./.venv/bin/pra-validate --help` all resolve (quickstart §1)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build the in-memory PRA-01 core (the system-under-test), its five swappable seams, the batched `dim`-grouped kernel, and the telemetry recorder — everything required to run one seed and produce a `PerSeedRunSummary`. No verdicts are produced yet.

**⚠️ CRITICAL**: No user story (no acceptance verdict) can be evaluated until this phase is complete. SC-005 (real T1–T6 PASS) and SC-006 (runnable T-SCALE) are unsatisfiable without a conforming, batched core.

### Core data contracts & components

- [x] T004 Implement `src/pra/core/contracts.py`: `SensorimotorEvent`, `FrameResult`, `GlobalPose`, and `FrameState` dataclasses with their null-rules (prev-obs/action null only on first event of an episode; `local_pose`/`recon_error` null iff `mapped == false`; `pred_error`/`effort` null when no previous observation) per data-model §2 / PRA-01 §3
- [x] T005 [P] Implement `src/pra/config.py`: frozen `Config` dataclass exposing every PRA-01 §8 parameter with its spec default plus harness-only `horizon_checkpoints=(18,30,50)`; construction-time validation rejecting out-of-range values (`ema_decay∉[0,1)`, `max_frames<min_frames`, `initial_dim_max<initial_dim_min`, empty `seeds`, `horizon_checkpoints` non-ascending or any entry `<1`, etc.); expose `effective_n_cycles = max(n_cycles, max(horizon_checkpoints))` so the run always reaches the last checkpoint (50 at default — resolves the §8 `n_cycles=18` vs 18/30/50-checkpoint mismatch) per data-model §1 and contracts/config.md
- [x] T006 [P] Implement `src/pra/world/event_source.py`: `EventSource` Protocol + `SensorimotorWorld` — `n_objects` objects (start `Normal(0,1)[true_dim]`, emission `Normal(0,1)[obs_dim,true_dim]`), `n_actions` displacements scaled by `action_scale`, nonlinear `emit = tanh(E_k·latent)+noise`, fixed draw order (objects start→emission per index, then actions), scaled configs; MUST NOT expose `true_dim`/latents/matrices to any telemetry (contracts/seams.md §5, PRA-02 §1, research R4)
- [x] T007 [P] Implement `src/pra/core/bus.py`: `Bus` Protocol + `InMemorySyncBus` — `register`/`unregister`/`publish`/`subscribers`; delivery-only, exactly-once, synchronous, ascending-`frame_id` order, no gating/scoring/learning/birth (contracts/seams.md §1, PRA-01 §4)
- [x] T008 [P] Implement `src/pra/core/scorer.py`: `Scorer` Protocol + `WeightedSumScorer` = `w_explain·recon + w_predict·pred + w_effort·effort + w_complexity·dim` (parsimony), vectorized over a FrameGroup, ties broken by ascending `frame_id` (contracts/seams.md §2, research R4)
- [x] T009 [P] Implement `src/pra/core/policies.py`: `ProposalPolicy` (biased: prob `exploit_prob`→`max(1,best_dim±1)`, else explore `uniform_int(1,best_dim+explore_dim_max_offset)`) + `DecayPolicy` (population-scaled threshold that **divides** by `1+coeff·max(0,n−baseline)`, soft-evict worst-first never below `min_frames`, hard cap to `max_frames`, young frames `age_cycles<min_age_cycles` exempt) (contracts/seams.md §3/§4, research R6)
- [x] T010 [P] Implement `src/pra/core/frame.py`: homogeneous frame kernel + `FrameGroup` (one per distinct `dim`) with weights stacked on a leading frame axis (encoder/decoder/transition tensors per data-model §3); batched `np.einsum`/matmul encode/decode/transition/fit/gradient-update over the `F` axis, per-element `gradient_clip`, birth = append row, eviction = delete row, derived `fit_quality`/`prediction_error` (observation space)/`effort`; NO per-frame branching (research R1/R2, PRA-01 §7.2)
- [x] T011 [P] Implement `src/pra/telemetry/recorder.py`: `PerStepRecord` (`map_fraction`, `mean_pred_error`, post-warmup `loss_flag`), `PerCycleRecord` (`population_size`, `dims_alive`, `best_frame`, `removed`), and `PerSeedRunSummary` (early/late pred-error with the ≥50-samples not-available rule, per-checkpoint `{best_dim,population_size}` snapshots, `still_growing` flag, the run's own `improvement = pred_error_early − pred_error_late`, `observation_steps`, `throughput`); each run yields **one** summary, so the T3 ablation produces a second summary the runner pairs by seed (not a single combined record — data-model §4); deterministic byte-identical serialization with fixed key order, fixed float formatting, and a pinned reduction (single-threaded BLAS, fixed order) so re-runs are byte-identical (FR-010, SC-007, data-model §4, PRA-02 §3, research R3/R8)
- [x] T012 Implement `src/pra/core/engine.py`: `Engine` with zero-start lifecycle — warmup, online episodes (coverage-fair EMA updates on **every** exposure, learning gated on mapped events), `config.effective_n_cycles` offline cycles (spawn via ProposalPolicy, age, evict via DecayPolicy), `best_dim`/population snapshot at **each** horizon checkpoint — every checkpoint is guaranteed reached because the run length is `effective_n_cycles = max(n_cycles, max(checkpoints))` (T005) — single seeded `numpy.random.Generator` consumed in the fixed PRA-01 §7.1 order (pinned reduction order, single-threaded BLAS for byte-identical telemetry), observation-space prediction; dispatches events to FrameGroups and reassembles `FrameResult`s per ascending `frame_id` (PRA-01 §5/§6, research R3/R4) — depends on T004–T011

### Foundational verification tests (gate the core before any verdict logic)

- [x] T013 [P] Contract test `tests/contract/test_bus_contract.py`: identical seed ⇒ byte-identical event/result sequence; a recording double substitutes without touching collaborators; delivery-only (no scoring/birth); and the default `InMemorySyncBus` preserves per-`frame_id` ascending order **while delegating delivery to the Engine's `dim`-grouped FrameGroups** (the batched path — seams.md §1 note / research R2) (contracts/seams.md §1)
- [x] T014 [P] Contract test `tests/contract/test_scorer_contract.py`: a substitute Scorer (error-only, no parsimony) changes which frame is "best" with no other edit (contracts/seams.md §2)
- [x] T015 [P] Contract test `tests/contract/test_policies_contract.py`: default threshold decreases as population grows; young frames never evicted; a high-dim proposal substitute is accepted by the Engine unchanged (contracts/seams.md §3/§4)
- [x] T016 [P] Contract test `tests/contract/test_event_source_contract.py`: identical seed ⇒ identical observation stream; substitute source accepted unchanged; no `true_dim`/latent/matrix leaks into any `FrameResult`/telemetry (contracts/seams.md §5)
- [x] T017 [P] Unit test `tests/unit/test_frame_kernel.py`: encode/decode/transition math + per-element gradient clipping on a small fixed seed (data-model §3)
- [x] T018 [P] Unit test `tests/unit/test_batched_equivalence.py`: the batched `dim`-group path equals a straightforward reference per-frame loop on a fixed seed (the §7.2 optimization changed no behavior) (research R1)
- [x] T019 [P] Unit test `tests/unit/test_scorer.py`: weighted sum + parsimony term, tie-break by ascending `frame_id` (contracts/seams.md §2)
- [x] T020 [P] Unit test `tests/unit/test_world.py`: nonlinear (`tanh`) emission, hidden latent never exposed, identical-seed determinism (PRA-02 §1)

**Checkpoint**: One seed runs end-to-end and yields a deterministic `PerSeedRunSummary`; all core/contract/unit tests green. User-story verdict work can now begin.

---

## Phase 3: User Story 1 - Trustworthy go/no-go on the behavioral claims (Priority: P1) 🎯 MVP

**Goal**: One command runs the whole suite across all seeds and emits, for each of T1–T6, a PASS/FAIL with the measured aggregate (mean ± std) and the exact criterion — failures shown honestly, never hidden or smoothed.

**Independent Test**: Run `pra-validate suite` at the default config and confirm a PASS/FAIL line for each of T1–T6 with its measured aggregate and pass criterion; at the validated reference config all of T1–T6 PASS (SC-001, SC-004, SC-005).

### Tests for User Story 1 ⚠️ (write first; expect FAIL before implementation)

- [x] T021 [P] [US1] Integration test `tests/integration/test_reference_config.py`: at the validated reference config T1–T6 all PASS, reproducing v4 reference behavior (SC-005) — capstone test; fully green once US2 (T4 detail) and US4 (T5 detail) land
- [x] T022 [P] [US1] Integration test `tests/integration/test_edge_cases.py`: not-available (too few pred-error samples ⇒ literal "not available"), seed-error (the failed seed is reported and the aggregate is flagged not-complete, never silently dropped), warmup-births (warmup losses not counted against T6) (Edge Cases, FR-008)
- [x] T023 [P] [US1] Unit test `tests/unit/test_aggregation.py`: across-seed mean/std plus the full per-seed `best_dim` spread; assert a mean is never returned where a spread is required (FR-003, data-model §4)

### Implementation for User Story 1

- [x] T024 [US1] Implement `src/pra/harness/acceptance.py` — `AcceptanceTest`/`VerdictReport`/`measured` dataclasses and the evaluator registry binding each test id to its claim, criterion, measure, and verdict (data-model §5, report-schema.json)
- [x] T025 [US1] Implement `src/pra/harness/runner.py` — multi-seed orchestration (run every configured seed for `effective_n_cycles`, capture each `PerSeedRunSummary`, surface `failed_seeds`); for T3, also run each seed's effort-only ablation (`seed+9999`, equal experience) and keep the predictive/ablation summary **pair** joined by seed; build `AcrossSeedAggregate` (mean/std for every field a test uses, plus per-seed spreads) (FR-001, data-model §4, research R7)
- [x] T026 [US1] Add T1 (mean `mean_map_fraction` < 0.99), T2 (`pred_error_late < pred_error_early` in a majority of seeds), and T6 (mean post-warmup `loss_fraction` < 0.15) evaluators to `src/pra/harness/acceptance.py` (PRA-02 §4)
- [x] T027 [US1] Add the T3 effort-only ablation evaluator to `src/pra/harness/acceptance.py`: for each seed read the predictive/effort-only summary **pair** the runner produced (T025) — the ablation is a *separate* run (fresh world from `seed+9999`, `scoring_mode=effort_only`, equal total experience, recording the true observation-space `pred_error`); PASS if `improvement(predictive) > improvement(effort_only)` in a majority of seeds, where each `improvement = pred_error_early − pred_error_late` from its own summary (no single summary holds both — they are joined by seed) (PRA-02 §2, research R7)
- [x] T028 [US1] Add the T4 evaluator (`|best_dim−true_dim|≤1` in a strict majority at **every** horizon checkpoint, judged on the per-seed spread never the mean) and the T5 evaluator (mean `final_population < max_frames` **and** no seed still strictly increasing over its final third) to `src/pra/harness/acceptance.py` (PRA-02 §4, research R5/R6) — completes the six-verdict suite; FAIL-paths proven in US2/US4
- [x] T029 [US1] Implement `src/pra/harness/report.py` human-readable renderer: per test, the measured aggregate (mean ± std), the exact criterion, and PASS/FAIL; failing tests rendered with the numbers that explain them; never a mean where a spread is required (FR-002/003/007/008)
- [x] T030 [US1] Extend `src/pra/harness/report.py` with the optional JSON renderer conforming to `contracts/report-schema.json` (schema_version, mode, run_metadata, tests[]) (FR-007)
- [x] T031 [US1] Implement `src/pra/harness/cli.py` `suite` command (and `main` dispatch): flags `--seeds/--true-dim/--obs-dim/--checkpoints/--config/--json/--strict`; single-seed runs labelled "FOR DEBUGGING ONLY — not a validation of a behavioral claim"; exit 0 even when tests FAIL unless `--strict` (contracts/cli.md, FR-012)

**Checkpoint**: `pra-validate suite` emits an honest six-test verdict with measure + criterion; reference config all-PASS. MVP is demoable.

---

## Phase 4: User Story 2 - Dimensionality result that cannot be a lucky snapshot (Priority: P1)

**Goal**: T4 is judged across multiple horizon checkpoints with the full per-seed `best_dim` spread, so a result that agrees early but drifts later is correctly reported FAIL.

**Independent Test**: Run a config whose dimensionality drifts with horizon and confirm the harness prints the per-seed spread at each checkpoint and reports T4 FAIL when the within-one majority does not hold at every checkpoint (SC-002).

### Tests for User Story 2 ⚠️

- [x] T032 [P] [US2] Integration test `tests/integration/test_t4_horizon_drift.py`: an engineered config that meets the within-one majority at an early checkpoint but not a later one ⇒ T4 FAIL; the per-seed spread is reported at each checkpoint (US2, SC-002)

### Implementation for User Story 2

- [x] T033 [US2] In `src/pra/harness/acceptance.py` + `report.py`, emit the T4 `HorizonCheckpointReading` per checkpoint — full `best_dim_per_seed`, `within_one_count`, `exact_count`, `n_seeds` — and write `horizon_readings[]` to the JSON report; assert the verdict requires the within-one majority at **every** checkpoint (FR-003/FR-004, SC-002, report-schema.json)
- [x] T034 [US2] In `src/pra/harness/cli.py`, render the `suite` T4 section as a per-checkpoint table showing the per-seed `best_dim` list with within-one/exact counts (contracts/cli.md)

**Checkpoint**: T4 cannot pass on a single lucky horizon; the spread is always visible.

---

## Phase 5: User Story 3 - Reproducibility you can trust (Priority: P2)

**Goal**: A determinism mode runs one seed twice and asserts the two run summaries are byte-identical, so any failure is attributable to one cause rather than hidden randomness.

**Independent Test**: Invoke `pra-validate determinism --seed 1` and confirm the two summaries compare identical to the byte; an injected divergence reports a hard FAIL pointing at the first difference (SC-003, SC-007).

### Tests for User Story 3 ⚠️

- [x] T035 [P] [US3] Integration test `tests/integration/test_determinism.py`: running one seed twice yields byte-identical summaries; an injected divergence is reported as a determinism FAILURE pointing at the differing field (FR-006, SC-003, SC-007)

### Implementation for User Story 3

- [x] T036 [US3] Add the determinism mode to `src/pra/harness/runner.py`: run one seed twice (pinned single-threaded BLAS + fixed reduction order so float ops are byte-stable — research R3 risk), byte-compare the deterministically serialized summaries, and locate the first difference (FR-006, research R3)
- [x] T037 [US3] Implement the `determinism` command in `src/pra/harness/cli.py` (`--seed/--true-dim/--config`): print PASS if byte-identical, else FAIL with a pointer to the first differing summary/field, and write `determinism_check` to JSON (contracts/cli.md, report-schema.json)

**Checkpoint**: Reproducibility is provable; nondeterminism is a hard failure, never averaged away.

---

## Phase 6: User Story 4 - Self-limiting, not merely capped (Priority: P2)

**Goal**: T5 passes only when the population genuinely self-limits (eviction keeps pace with growth), not merely because it hit a hard ceiling.

**Independent Test**: Run a config whose population grows at the spawn rate up to the cap and confirm T5 reports FAIL despite a finite final count (US4).

### Tests for User Story 4 ⚠️

- [x] T038 [P] [US4] Integration test `tests/integration/test_t5_still_growing.py`: a config below the cap but still strictly increasing over the final third of cycles ⇒ T5 FAIL (US4)

### Implementation for User Story 4

- [x] T039 [US4] In `src/pra/harness/acceptance.py` + `report.py`, surface the T5 `t5_detail`: per-seed `still_growing` flag (strictly increasing over the final third), `final_population` mean/std, `max_frames`, and a `capped` marker for a population pinned at the cap; write `t5_detail` to JSON (FR-005, research R6, report-schema.json)
- [x] T040 [US4] Add the capped-population case to `tests/integration/test_edge_cases.py`: a run pinned at the hard cap is reported as `capped` and FAILs the self-limiting clause, distinct from a genuinely self-limiting population (Edge Cases)

**Checkpoint**: T5 distinguishes self-limiting from capped; runaway growth can no longer hide behind a finite number.

---

## Phase 7: User Story 5 - The scale question is runnable and measured (Priority: P3)

**Goal**: The investigatory scale test runs at large true dimensionality and emits the per-seed dimensionality spread, throughput, and wall-clock, labelled investigatory — never scored as a build pass/fail.

**Independent Test**: Run `pra-validate scale --true-dims 20,35,50` and confirm it emits the per-seed `best_dim` spread, throughput, and wall-clock, labelled INVESTIGATORY, without ever being a build failure (SC-006).

### Tests for User Story 5 ⚠️

- [x] T041 [P] [US5] Integration test `tests/integration/test_scale_runnable.py`: the scale test emits the per-seed `best_dim` spread + `throughput` + wall-clock, labelled INVESTIGATORY, and a poor dimensionality result is never reported as a build failure (SC-006)

### Implementation for User Story 5

- [x] T042 [US5] Support scaled configs in `src/pra/config.py`/`src/pra/world/event_source.py`: `true_dim ∈ {20,35,50}` with `obs_dim ≥ 3·true_dim` and a lengthened run schedule so `observation_steps` per seed reaches the millions (PRA-02 §1.3, research R9)
- [x] T043 [US5] Add a high-dimensionality `ProposalPolicy` variant in `src/pra/core/policies.py`, substitutable via the seam with no change to other components (PRA-01 §6.5, contracts/seams.md §3, research R9)
- [x] T044 [US5] Add the T-SCALE evaluator to `src/pra/harness/acceptance.py`: always INVESTIGATORY (never PASS/FAIL), reporting per-`true_dim` `best_dim` spread, `throughput`, and wall-clock; write `scale_detail[]` to JSON (FR-009, SC-006, report-schema.json)
- [x] T045 [US5] Implement the `scale` command in `src/pra/harness/cli.py` (`--true-dims/--seeds/--config/--json`): emit the INVESTIGATORY section; `--strict` has no effect here (contracts/cli.md)

**Checkpoint**: The open research question is runnable and measured on a single machine via batched evaluation.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Verify the whole, lock the quality gate, and confirm the performance budget.

- [x] T046 [P] Walk quickstart.md §2–§4 end-to-end (`suite`, `determinism --seed 1`, `scale --true-dims 20,35,50`) and confirm the outputs match the documented shape and the scenario→check table (quickstart §6); assert that the **only** files created on disk are the requested report summaries — no frame/model state is persisted (FR-011)
- [x] T047 [P] Add README / module docstrings documenting how to run the harness, the honest-summary governing principle (FR-008), and the v4 behavioral-oracle note (`design/validate/pra_sim_v4.py`)
- [x] T048 Performance check: the full default suite — 8 seeds × 2 runs each (predictive + T3 effort-only ablation) × 50 effective offline cycles (16 runs total) — completes in single-digit minutes; the batched core must beat the pure-Python v4's ~3.5 min single-seed-50-cycle figure by enough to absorb all 16 runs and must not regress it; record the reported `throughput` (plan Performance Goals)
- [x] T049 Quality gate (MUST be green, none skipped — CLAUDE.md / research R10): `./.venv/bin/ruff format --check .` && `./.venv/bin/ruff check .` && `./.venv/bin/pytest -q`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies — start immediately.
- **Foundational (Phase 2)**: depends on Setup. **BLOCKS every user story** — no verdict can be computed without the core + telemetry. Within it: T004 (contracts) precedes T005–T012; T012 (engine) depends on T005–T011; the foundational tests (T013–T020) depend on the components they cover.
- **User Stories (Phases 3–7)**: all depend on Foundational completion.
  - US1 (Phase 3) is the harness backbone (runner, aggregate, report, CLI dispatch, acceptance registry). US2–US5 extend that backbone, so in practice they follow US1.
  - Given the P1/P1/P2/P2/P3 priorities, the delivery order is US1 → US2 → US3 → US4 → US5.
- **Polish (Phase 8)**: depends on all targeted user stories being complete.

### User Story Dependencies

- **US1 (P1)**: depends only on Foundational. Delivers the MVP suite + backbone.
- **US2 (P1)**: builds on US1's acceptance/report/CLI to harden T4 across horizons. Independently testable via `test_t4_horizon_drift.py`.
- **US3 (P2)**: builds on US1's runner/CLI to add determinism mode. Independently testable via `test_determinism.py`.
- **US4 (P2)**: builds on US1's acceptance/report to harden T5 self-limiting. Independently testable via `test_t5_still_growing.py`.
- **US5 (P3)**: builds on US1's acceptance/CLI + the policies/world seams to add the investigatory scale run. Independently testable via `test_scale_runnable.py`.

> Note: US1's capstone `test_reference_config.py` (all of T1–T6 PASS) exercises the full integrated suite and is fully green only once US2's T4 detail and US4's T5 detail land. Each story's *own* independent test is satisfiable within that story.

### Within Each User Story

- Tests are written first and expected to FAIL before implementation.
- Dataclasses/registry before evaluators; runner/aggregate before report; report before CLI.
- Tasks touching the same file (e.g. several US1 tasks edit `acceptance.py`) are sequential, not `[P]`.

### Parallel Opportunities

- Setup: T002 then T003 are sequential; T001 precedes both.
- Foundational: after T004, the components **T005–T011 all run in parallel** (`[P]`, distinct files); only T012 (engine) must wait for them. The eight foundational tests **T013–T020 run in parallel** once their targets exist.
- Each user story's test task(s) (`T021/T022/T023`, `T032`, `T035`, `T038`, `T041`) are `[P]` — distinct files.
- Polish: T046 and T047 are `[P]`; T048 and T049 follow.

---

## Parallel Example: Foundational components (Phase 2)

```bash
# After T004 (contracts.py) lands, launch the five seams + kernel + recorder together:
Task: "T005 Config dataclass in src/pra/config.py"
Task: "T006 SensorimotorWorld in src/pra/world/event_source.py"
Task: "T007 InMemorySyncBus in src/pra/core/bus.py"
Task: "T008 WeightedSumScorer in src/pra/core/scorer.py"
Task: "T009 Proposal/Decay policies in src/pra/core/policies.py"
Task: "T010 FrameGroup batched kernel in src/pra/core/frame.py"
Task: "T011 Telemetry recorder in src/pra/telemetry/recorder.py"

# Then the foundational tests in parallel once components exist:
Task: "T013 Bus contract test in tests/contract/test_bus_contract.py"
Task: "T016 EventSource contract test in tests/contract/test_event_source_contract.py"
Task: "T018 Batched-equivalence test in tests/unit/test_batched_equivalence.py"
```

## Parallel Example: User Story 1 tests (Phase 3)

```bash
# Launch all US1 test tasks together (distinct files):
Task: "T021 Reference-config all-PASS test in tests/integration/test_reference_config.py"
Task: "T022 Edge-cases test in tests/integration/test_edge_cases.py"
Task: "T023 Aggregation/spread test in tests/unit/test_aggregation.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 + the T4 guarantee)

1. Complete Phase 1 (Setup) and Phase 2 (Foundational core + tests) — CRITICAL, blocks everything.
2. Complete Phase 3 (US1): the honest six-test suite with measure + criterion.
3. Complete Phase 4 (US2): the horizon-robust T4 (both are P1).
4. **STOP and VALIDATE**: `pra-validate suite` at the reference config — T1–T6 PASS, T4 holds across every checkpoint.

### Incremental Delivery

1. Setup + Foundational → one seed runs deterministically.
2. + US1 → honest six-verdict suite (MVP).
3. + US2 → T4 cannot be a lucky snapshot.
4. + US3 → byte-identical reproducibility check.
5. + US4 → T5 self-limiting, not merely capped.
6. + US5 → investigatory scale run, measured.
7. Polish → quickstart walk-through, performance budget, green quality gate.

### Definition of Done (PRA-02 §6, mapped)

- World + ablation + telemetry exact (Foundational T004–T012, T027).
- Harness runs all seeds, determinism check, per-test verdicts with required detail (US1–US3).
- **T1, T2, T3, T6 PASS and T4 PASS at default `true_dim=3`** (US1 + US2); **T5 PASS** at default (US1 + US4).
- **T-SCALE runnable and measured** at `true_dim ∈ {20,35,50}` reaching millions of observation steps via batched evaluation (US5).
- `ruff format --check`, `ruff check`, `pytest` all green, none skipped (T049).

---

## Notes

- `[P]` = different files, no dependency on an incomplete task.
- `[Story]` label maps each task to its user story for traceability; Setup/Foundational/Polish carry none.
- Tests are written before their implementation and expected to FAIL first.
- The behavioral oracle is `design/validate/pra_sim_v4.py`; the new batched core must reproduce its T1–T6 verdicts at the default config (enforced by T018 + T021).
- Honest-summary is the governing principle (FR-008): where a tidy report and a faithful one conflict, the faithful one wins.
- Commit after each task or logical group; sign commits (CLAUDE.md).
