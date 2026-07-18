# Tasks: Learned Channel Weighting (The L3-Noise Remedy)

**Input**: Design documents from `/specs/016-channel-weighting/`
**Prerequisites**: plan.md, research.md, data-model.md,
contracts/channel-weighting.md, and the arc trail
`design/validate/CHANNELWEIGHT-DIAGNOSIS.md` (P1 + E1 already recorded —
the gate is open; E2–E4 run *after* the mechanism ships, with binding stop
conditions).

**Tests**: included — the byte-identity and no-RNG contracts are the
feature's safety case (spec US2/US3), and the house gate forbids skips.

**Organization**: US1 = the rescue (mechanism + science), US2 = nothing
changes when off, US3 = the feature travels (snapshot/modes/resize).

## Phase 1: Foundational (blocking — the mechanism itself)

- [ ] T001 Add `channel_weight_floor` (default 0.0, 0 ≤ f ≤ 1) and
      `channel_stats_decay` (default 0.995, 0 ≤ β < 1) with validation and
      the house comment style in `src/pra/config.py`
- [ ] T002 Thread `w: np.ndarray | None = None` through
      `FrameGroup.encode / fit_quality / honest_pred_err / learn_placement
      / learn_transition` in `src/pra/core/frame.py` — `None` executes the
      textually-current expressions (contract C1); weighted forms per
      contract C2 (the E1 scratchpad instruments are the reference
      implementation)
- [ ] T003 Add the ChannelStats state (m/v/cov/n/w), per-step update,
      episode-start recompute (readiness `ceil(1/(1−β))`, max-normalized
      shaping, floor clip), and pass-through of `w` to every group call in
      `FrameStore.online_step` / `best_frame` / `best_frame_predictor` in
      `src/pra/core/frame.py` (zero `engine.py` edits — plan target)
- [ ] T004 Cover anatomy resize (grow → zeros + w=1, shrink → truncate) and
      `state_dict` / `load_state_dict` (`"channel_stats"` dict when on,
      fresh init when absent) in `src/pra/core/frame.py`
- [ ] T005 Pack/unpack `chanw__*` arrays + `meta["channel_stats"]` flag,
      additive-optional (world_state/streams pattern, no format bump) in
      `src/pra/persistence/snapshot.py`
- [ ] T006 Add the ON-only `channel_weighting` summary block
      (agency-fields byte-identity pattern) in `src/pra/telemetry/recorder.py`
      and echo the two params in the report config block when on in
      `src/pra/harness/report.py`

## Phase 2: User Story 2 — existing users see nothing change (P1)

**Goal**: feature present, disabled → byte-for-byte the pinned build.
**Independent test**: full existing suite green untouched + the new
identity tests.

- [ ] T007 [P] [US2] Unit tests in `tests/unit/test_channel_weighting.py`:
      estimator EMA arithmetic on constructed streams (known ρ̂), rank
      separation on synthetic static-vs-signal channels, all-ones `w`
      bit-equal to the unweighted path, single-zero `w` removes exactly
      that channel from numerator and denominator, readiness gating,
      resize grow/shrink, and the twin-engine no-RNG proof (same seed ON
      vs OFF → identical world observation streams and frame-birth draws;
      pattern of `tests/unit/test_scale_rules.py:100–122`)
- [ ] T008 [US2] Integration tests in
      `tests/integration/test_channel_weighting_runs.py`: explicit-inert
      config summary byte-equal to default `Config()` summary; existing
      byte-frozen family (`test_baseline_unchanged.py`,
      `test_determinism.py`, ladder streams) confirmed green with the
      feature code present

## Phase 3: User Story 3 — the feature travels with the brain (P2)

**Goal**: estimator state snapshots/resumes byte-identically; modes compose.
**Independent test**: ON round-trip equality; OFF blob format equality.

- [ ] T009 [US3] Extend `tests/integration/test_snapshot_completeness.py`:
      ON mid-run snapshot → resumed continuation byte-identical to
      uninterrupted; OFF blobs bit-identical to the pre-016 format; a
      pre-016-shaped blob loads with fresh estimator init (stated refill)
- [ ] T010 [US3] ON smoke coverage in
      `tests/integration/test_channel_weighting_runs.py`: L3 noise run
      with `channel_weight_floor=0.2` completes with the summary block
      present; multi-stream `n_streams=2` and `episode_mode="continuous"`
      ON smoke (runs, deterministic)

## Phase 4: Gate

- [ ] T011 Quality gate green and none skipped
      (`./.venv/bin/ruff format --check . && ./.venv/bin/ruff check . &&
      ./.venv/bin/pytest -q`); commit the mechanism + tests + trail
      "shipping shape" note as one signed commit

## Phase 5: User Story 1 — structure-finding survives static (P1, the science)

**Goal**: the pre-registered E-steps against the shipped code; bars and
exits from `design/validate/CHANNELWEIGHT-DIAGNOSIS.md` are binding.
**Independent test**: the trail doc's recorded verdicts.

- [ ] T012 [US1] E2 identification: scratchpad trace instrument over seeds
      1–8 × {noise σ_d ∈ {0.04, 0.1, 0.2, 0.5, 1.0}, structured,
      reference}; bars = rank separation by checkpoint 18 (≥ 7/8,
      sustained), margin monotone in dose, no core weight < 0.9 per the
      frozen clauses; STOP on X1 (two design revisions max) / X2
      (ship-block); record in the trail
- [ ] T013 [US1] E3 rescue: `pra-validate ladder --rungs l3 --config`
      overrides at the recorded rung dials, f = 0.2, β = 0.995 —
      exploratory seeds 1–8 × 5 doses; confirmatory seeds 1–24 at
      {0.5, 1.0} only if ≥ 5/8 at 1.0; primary = L3 noise PASS at
      σ_d = 1.0 (≥ 13/24 at every checkpoint, unchanged criterion form);
      secondaries (unweighted improvement ≥ 0.15/0.25, conveyor broken,
      learned-weights frozen surface) recorded with spreads; STOP on X3
      (honest FAIL, no amendment); evaluate D1(b); record in the trail
- [ ] T014 [US1] E4 no-harm: paired ON/OFF at σ_d = 0.04 + structured mode
      (drop ≤ 0.05 in ≥ 6/8), L1 + L2 + reference verdicts unchanged, ON
      snapshot round-trip, K=2 + continuous smoke — the OFF half is already
      permanent tests (T007–T009); STOP on X4/X5; record in the trail

## Phase 6: Outcome & propagation

- [ ] T015 Close the arc: trail Outcome section; dated L3 addendum in
      `design/validate/LADDER-CRITERIA.md` (original FAIL untouched);
      propagate design/03 + design/04 + design/07, PRA-01
      (§5.2/§5.4/§6.2/§8.4 + the §8.8 note), PRA-02 §1.5 pointer; forward
      pointer in `design/validate/CHANNELNOISE-DIAGNOSIS.md` Outcome §4;
      `ROADMAP.md` sequencing + C2-gate line; `JOURNEY.md` chapter 30 +
      "Where things stand"; final gate; merge `016-channel-weighting` to
      `main`

## Dependencies

- T001 → T002 → T003 → T004 → T005 → T006 (foundational chain; T005/T006
  depend on T004/T003 state shapes)
- US2 (T007–T008) and US3 (T009–T010) after T006; T007 parallelizable with
  T009/T010 authoring
- T011 gates everything after it; T012 → T013 → T014 → T015 in trail order
  (stop conditions may end the arc early at any of them — that is a valid
  completion per the pre-registration)

## Implementation strategy

Foundational chain first (T001–T006) exactly as the contracts state —
the scratchpad E1 instruments are the reference implementation for the
weighted math, already proven against the recorded anchors. Then both test
stories (the safety case), the gate commit, and only then the science
phases in pre-registered order. MVP = through T011: a shipped, inert,
fully-guarded mechanism; the arc's *claims* only exist once T012–T014
record their verdicts.
