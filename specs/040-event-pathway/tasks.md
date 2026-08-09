# Tasks: The Event Pathway

**Input**: Design documents from `/specs/040-event-pathway/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/surface.md, quickstart.md

**Tests**: Included — the spec's acceptance explicitly demands them
(byte-identical-when-off, snapshot roundtrip/resume equivalence, policy
draw-order and completion-rule units, the surface guard).

**Organization**: Tasks grouped by user story; US1 (the head) is the MVP; US2
(the policy) makes it usable; US3 (the research closure) is the honesty
obligation that can only run last.

## Phase 1: Setup

- [ ] T001 Anchor the branch: run the full quality gate (`./.venv/bin/ruff format --check . && ./.venv/bin/ruff check . && ./.venv/bin/pytest -q`) on `040-event-pathway` and confirm green before any change

## Phase 2: Foundational (blocking prerequisites)

- [ ] T002 Add `event_head_eta: float = 0.0` to `src/pra/config.py` with validation `0 ≤ η < 2` (message per data-model.md) and the house-style comment block naming the off-default byte-identity promise and the G3 provenance
- [ ] T003 Add the defaulted `predict_event_delta` field (module-level `_no_event_delta` returning `None`) to `PolicyContext` in `src/pra/action/policy.py` — additive, keyword-only-legal (contracts/surface.md)

## Phase 3: User Story 1 — The brain can learn to expect events (P1) 🎯 MVP

**Goal**: The event head exists in the brain: config-gated, learning from
every executed transition, persisted, resize-safe, exposed to policies —
byte-identical everywhere when off.

**Independent Test**: `tests/integration/test_event_pathway.py` — off-path
summary and snapshot bytes equal the pre-feature build; on-path resume
equivalence; `tests/unit/test_event_head.py` — the math.

- [ ] T004 [US1] Implement the event head in `src/pra/core/frame.py`: store-owned state (`_eh_on`, `_eh_W`, `_eh_updates`) built in `FrameStore.__init__` iff `config.event_head_eta > 0`; methods `event_learn(prev_obs, action, obs)` (NLMS, data-model.md expressions), `event_predict(obs, action)`, an `event_head_on` property; resize handling inside `FrameStore.resize` (bit-preserving, zero-init growth, truncate shrink, no RNG); `state_dict`/`load_state_dict` additive-optional `event_head` key (absent → cold start, the channel_stats precedent)
- [ ] T005 [US1] Wire the engine in `src/pra/core/engine.py`: one guarded `store.event_learn(prev_obs, prev_a, obs)` at the end of each step-loop iteration (after `obs = w.step(prev_a)`, research.md D2); in the curiosity context construction add the `predict_event_delta` closure over the current observation (None-returning default untouched on the random-baseline path)
- [ ] T006 [US1] Persist the head in `src/pra/persistence/snapshot.py`: `encode` writes `eh__W` + `meta["event_head"] = {"updates": ...}` only when the state dict carries the key; `decode` restores it into `frame_store["event_head"]` when present — feature-off blobs bit-identical to the pre-040 format
- [ ] T007 [P] [US1] Unit tests in `tests/unit/test_event_head.py`: cold start predicts zero delta; NLMS converges on a known per-action linear dynamic; per-action separation (learning action 0 leaves action 1's predictions unchanged); update expression matches the G3 prototype arithmetic on a fixed example; resize preserves entries bit-for-bit, zero-inits growth, truncates shrink, draws no RNG (generator state unchanged); off store has no head attributes/work
- [ ] T008 [US1] Integration tests in `tests/integration/test_event_pathway.py`: (a) feature off — summary equality and snapshot byte-identity against default config on a reference run; (b) feature on — snapshot → resume equals uninterrupted run (the head's state travels); (c) old/feature-off blob resumed with the head enabled cold-starts and runs; (d) continuous-mode virtual-boundary transitions are learned (updates count equals executed transitions, not executed-minus-boundaries)

**Checkpoint**: US1 delivers the mechanism; gate green.

## Phase 4: User Story 2 — The completion itch is a shipped policy (P2)

**Goal**: `CompletionItchPolicy` ships with the measured semantics, honest
counters, and anatomy-derived channel constants.

**Independent Test**: `tests/unit/test_completion_itch_policy.py` against
stubbed contexts — no world, no engine.

- [ ] T009 [US2] Implement `CompletionItchPolicy` in `src/pra/action/policy.py` per data-model.md: constructor keywords, measured draw order (one ε uniform; one integer on the random path; none directed), frames candidate-skip, completion rule (`Δ̂[pocket] > threshold → progress_after = 1.0` else clipped), itch inert when `predict_event_delta` returns None, lowest-index ties, bounded watch (`completions_fired`, `false_completions` realized against the next observation, `progress_pred_error_ema` decay 0.99), `last_was_directed` telemetry, loud index validation on first selection
- [ ] T010 [P] [US2] Export `C1_MINING_INDEX` and `C1_POCKET_TOTAL_INDEX` from `src/pra/anatomy/minecraft/anatomy.py`, derived from `C1_SENSORS` widths/labels (never literals), re-exported in `src/pra/anatomy/minecraft/__init__.py`
- [ ] T011 [P] [US2] Unit tests in `tests/unit/test_completion_itch_policy.py`: draw-order parity with `CuriosityLookaheadPolicy` on the random path (same rng consumption); ε and maturity gates; completion rule fires at threshold; itch arithmetic on stubbed deltas with clipping; tie-break to lowest index; head-off degrades to pure drive+potential values; counters increment correctly incl. a false completion; index out of range raises at first selection; anatomy constants equal 14/15 and are derived (perturbation-resistant assertion via spec order)

**Checkpoint**: US1+US2 = the usable feature; gate green.

## Phase 5: User Story 3 — The research gate closes on the shipped build (P3)

**Goal**: Episode 0071's reversal condition answered on the record: the
shipped components reproduce Bar A at the G3 gate.

**Independent Test**: The rerun consumes only shipped head/policy plus the
existing harness instrumentation; bars recorded pass or fail.

- [ ] T012 [US3] Write the rerun runner in the session scratchpad (arc convention — not the repo): the G3 confirmatory protocol (24 P0 graduates, κ = 0.25, H = 5,000) with `event_head_eta = 0.5` in the resumed config and shipped `CompletionItchPolicy` (clone-step hold injected via `potential_of`, λ = 0.25); execute it
- [ ] T013 [US3] Record the rerun's three bars in `hq/01-RESEARCH/motivation-stack/README.md` (a "src closure" subsection under the G3 outcome) and a dated entry in `hq/01-RESEARCH/motivation-stack/JOURNEY.md` — pass or fail, same day

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T014 Add surface entries to `tests/contract/surface_inventory.py` per contracts/surface.md (CompletionItchPolicy class; the two C1 index constants)
- [ ] T015 [P] Update design docs: `hq/02-DESIGN/0005-motivation-action.md` (the event pathway + CompletionItchPolicy sections, measured provenance), `hq/02-DESIGN/0007-configuration-reference.md` (`event_head_eta` row), `hq/02-DESIGN/0008-public-api-versioning.md` (1.2.0 additive-change note)
- [ ] T016 Bump version to 1.2.0 in `pyproject.toml` (verify `pra.__version__` follows; adjust its source if pinned elsewhere)
- [ ] T017 Full quality gate green; journey episode via `/journey-log` (feature landed, committed with the work), roadmap ledger row; merge `040-event-pathway` → `main` and push

## Dependencies & Execution Order

- Phase 2 (T002, T003) blocks everything.
- US1 (T004→T005→T006, then T007/T008) blocks US2's engine-context test paths
  but T009–T011 only truly need T003 (stubbed contexts) — they may start after
  Phase 2 in parallel with US1's tail.
- US3 (T012→T013) needs US1+US2 complete.
- Polish: T014 after T009/T010; T015/T016 anytime after US2; T017 last.

## Implementation Strategy

MVP = Phase 3 (the head). Deliver in priority order; keep the gate green at
every checkpoint; the branch merges only after T017.
