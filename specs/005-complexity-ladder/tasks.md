---
description: "Task list for the complexity ladder"
---

# Tasks: The Complexity Ladder

**Input**: Design documents from `/specs/005-complexity-ladder/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅
**Tests**: INCLUDED (repo rule: all green, none skipped).

## Phase 1: Setup

- [x] T001 Add ladder config surface to `src/pra/config.py`: `world`,
      `region_noise_std`, `factor_dims`, `distractor_dim`,
      `distractor_channels`, `distractor_mode` — inert defaults, validation
      per data-model table (constraint-naming messages, FR-011)

## Phase 2: Foundational

- [x] T002 Create `src/pra/world/ladder.py`: module docstring stating the
      draw-order discipline (research R7) and `make_world(cfg, rng)` routing
      `world="reference"` to `SensorimotorWorld` (worlds land per story)
- [x] T003 [P] `run_suite` optional `world_factory` pass-through in
      `src/pra/harness/runner.py` (default `None` — byte-identical; same
      opt-in pattern as `proposal_factory`; threads into `_run_seed_group`)
- [x] T004 [P] Pre-register `design/validate/LADDER-CRITERIA.md`: L1/L2/L3
      criteria exactly as research R6 states them (paired-twin survival +
      occupancy sanity band; churn-matched persistence + census envelope;
      controllable-`true_dim` horizon rule), result sections empty —
      committed before any recorded result (FR-007)

## Phase 3: US1 — the non-uniform world (P1) 🎯 MVP

- [x] T005 [US1] `NonUniformWorld` in `src/pra/world/ladder.py`: half-space
      region `latent[0] > 0`, per-step in-region transition noise
      `N(0, region_noise_std²I)` drawn after displacement lookup, occupancy
      counters, harness-only `ladder_readings()`; degenerate dial draws
      nothing extra (data-model §NonUniformWorld)
- [x] T006 [P] [US1] Unit `tests/unit/test_ladder_worlds.py`: config
      validation rejections; region membership math; draw order (noise only
      when in-region and dial > 0); occupancy counts every step once;
      `make_world` routing
- [x] T007 [P] [US1] Contract `tests/contract/test_ladder_contract.py`:
      `NonUniformWorld` satisfies `EventSource`; the system-visible surface
      (`reset`/`step`/`obs_dim`/`n_actions`) exposes no ground truth
      attribute; `ladder_readings()` exists and is never called by the
      engine (SC-005)
- [x] T008 [US1] Integration `tests/integration/test_ladder.py`: degenerate
      dial engine summary byte-identical to `SensorimotorWorld` same
      config/seed (FR-012); non-degenerate run deterministic across re-run
      and workers (FR-005)
- [x] T009 [US1] Harness rung L1 in `src/pra/harness/ladder.py`:
      `run_ladder(base, rungs, seeds, workers)` skeleton + L1 — engine runs
      across seeds, paired same-seed degenerate-twin runs, occupancy
      readout, `RungReading` rows (paired deltas of improvement/best_dim);
      integration-test the pairing and readings at tiny budgets

## Phase 4: US2 — the compositional world (P2)

- [x] T010 [US2] `CompositionalWorld` in `src/pra/world/ladder.py`:
      `factor_dims` groups, action displacement drawn as reference then
      masked to group `a mod K` (mask-after-draw keeps construction draws
      byte-equal, research R3), reference joint emission;
      `ladder_readings()` reports groups + assignment
- [x] T011 [P] [US2] Tests for L2 across the three test files: unit (mask
      math, `sum(factor_dims) == true_dim` validation, single-group no-op),
      contract (EventSource + hiding), integration (degenerate
      `factor_dims=(true_dim,)` byte-identity; determinism)
- [x] T012 [US2] Harness rung L2 in `src/pra/harness/ladder.py`: quartet
      arms via `run_suite(cfg, world_factory=make_world, with_matched=True,
      proposal_factory=None)` on the compositional config + end-of-run
      census via the in-memory snapshot codec (stable frames' dims vs
      `factor_dims`/`Σd_k`); readings rows; tiny-budget integration test

## Phase 5: US3 — the distractor world (P3)

- [x] T013 [US3] `DistractorWorld` in `src/pra/world/ladder.py`:
      autonomous fixed-drift latent + own tanh emission appended as
      `distractor_channels` (structured mode) or fresh unit-normal channels
      (noise mode); construction draws after reference draws in documented
      order; `obs_dim` property reports total width; `ladder_readings()`
      reports the split (data-model §DistractorWorld)
- [x] T014 [P] [US3] Tests for L3 across the three test files: unit (append
      math both modes, channel-count validation, total-width property),
      contract (EventSource + hiding), integration (degenerate
      `distractor_channels=0` byte-identity; determinism both modes)
- [x] T015 [US3] Harness rung L3 in `src/pra/harness/ladder.py`: runs at
      the configured mode(s), per-checkpoint `best_dim` vs controllable
      `true_dim` readings rows; tiny-budget integration test

## Phase 6: US4 — the ladder as one instrument (P4)

- [x] T016 [US4] `build_ladder_report` + text/JSON rendering blocks in
      `src/pra/harness/report.py` (mode `"ladder"`, per-rung
      `AcceptanceVerdict` L1/L2/L3 judged per LADDER-CRITERIA, per-seed
      reading tables in `run_metadata`, single-seed debug banner preserved)
- [x] T017 [US4] CLI `pra-validate ladder` in `src/pra/harness/cli.py`
      (`--rungs l1,l2,l3` default all, `--seeds`, `--config`, `--json`,
      `--workers`; exit 0 always — FR-009/FR-010) + integration CLI test in
      `tests/integration/test_ladder.py` (report text, JSON artifact shape,
      only-artifact-on-disk)

## Phase 7: Polish & first recorded results

- [x] T018 Run the R9 first-results grid (reference-scale dials, pinned
      random policy, 8 seeds: L1 mild/strong, L2 (3,3)/(2,2,2), L3 both
      modes) and fill the result sections of
      `design/validate/LADDER-CRITERIA.md` — verdicts, spreads, occupancy,
      census, including failures (SC-003). Done: 3 PASS / 3 FAIL as
      written; L1 occupancy clause amended openly (drift-dominated
      occupancy refuted the ≈½ assumption); channel-noise robustness named
      as the new open problem (L3 noise-mode FAIL)
- [x] T019 [P] Propagate: ROADMAP A3 status + JOURNEY.md chapter + "Where
      things stand" refresh (required by AGENTS.md); GETTING-STARTED
      pointer to `pra-validate ladder`. Amendment: the ladder dials are
      world configuration, which Doc 07 does not carry (it is the *system*
      config reference — the reference world's dials are not there
      either); they are documented in PRA-02 §1.5 instead, which is the
      normative home of validation-world configuration
- [x] T020 Quality gate: `ruff format --check`, `ruff check`, full
      `pytest -q` green, none skipped; baseline byte-frozen test untouched

## Dependencies

T001 → T002 → (T003 ∥ T004) → US1: T005 → (T006 ∥ T007 ∥ T008) → T009 →
US2: T010 → (T011) → T012 → US3: T013 → (T014) → T015 → US4: T016 → T017 →
Polish: T018 → (T019) → T020.

US2/US3 depend only on Phase 2 plus their own world task (stories are
independently testable); they are sequenced only because `ladder.py` and
the test files are shared. MVP = T001–T009 (US1 alone satisfies the A4
gate). T018 depends on T004's criteria being committed first (FR-007).

## Implementation strategy

US1 first and complete (worlds → tests → harness) — it is the A4 gate and
the MVP; each later story lands as an independent increment on the same
scaffold; results recording (T018) happens once, after all rungs and the
CLI exist, so the recorded artifact is produced by the shipped instrument.
