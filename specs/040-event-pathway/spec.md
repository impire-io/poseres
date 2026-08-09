# Feature Specification: The Event Pathway

**Feature Branch**: `040-event-pathway`
**Created**: 2026-08-09
**Status**: Draft
**Input**: User description: "Promote the measured motivation-stack G3 prototype (episode 0071) into the product: the event head as a second brain-side prediction pathway, the completion-itch policy that reads it, snapshot persistence, and the additive v1 surface growth — with zero behavior change when the feature is off."

## Licensing context

This build is licensed by a pre-registered research result, not by intuition:
motivation-stack G3 (episode 0071, `hq/01-RESEARCH/motivation-stack/README.md`)
measured all three frozen bars passing — the brain's own learned model of its
progress channel carried election (24/24 seeds) and chains (13/24, double the
bar) at prediction error 0.0081 against the frames' 0.0612. Episode 0071's
reversal condition binds this feature: the shipped build must reproduce Bar A
at its own gate, or the reading reopens.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The brain can learn to expect events (Priority: P1)

A researcher or hobbyist running a continuously-learning brain enables the
event pathway with one configuration value. The brain then maintains a second,
sharp prediction of how each of its possible actions will change each of its
sensed channels — learned online from its own experience, starting from
nothing, persisting across snapshot/resume like every other part of the brain.
Anyone not enabling it gets exactly the behavior they had before, to the byte.

**Why this priority**: This is the measured mechanism itself — everything else
in the feature reads from it. Without the head there is no itch signal, no G5
prerequisite, and no reproduction of the G3 result.

**Independent Test**: Run any validated configuration with the feature off and
confirm byte-identical summaries to the pre-feature build; run with the
feature on and confirm the head's prediction error on a known-regular channel
falls with experience.

**Acceptance Scenarios**:

1. **Given** the feature dial at its default (off), **When** any existing
   validated mode runs, **Then** every summary, snapshot blob, and RNG draw is
   byte-identical to the pre-feature build.
2. **Given** the feature enabled, **When** a run executes transitions,
   **Then** the head's per-action predictions improve with experience (error
   on a deterministic channel falls below the one-tick signal scale measured
   in G3).
3. **Given** the feature enabled and snapshots on, **When** a run is stopped
   and resumed from its snapshot, **Then** the resumed run behaves identically
   to the uninterrupted run (the head's learned state travels).
4. **Given** a snapshot written with the feature off (or an old blob),
   **When** it is resumed with the feature on, **Then** the head cold-starts
   and the run proceeds (stated refill, the established precedent).
5. **Given** a mid-run anatomy change (observation or action growth),
   **When** the resize applies, **Then** existing head knowledge is preserved
   and new channels/actions start at "predicts no change", with no RNG drawn.

---

### User Story 2 - The completion itch is a shipped policy (Priority: P2)

A user who wants directed behavior — the measured stay/want/finish
composition — constructs the shipped completion-itch policy with their
anatomy's progress and pocket channel indices and injects it into the engine,
exactly as they inject any policy today. The policy values actions by the
drive term plus an optional caller-supplied per-action term plus the
completion itch read from the event head. Its honesty counters (completions
predicted, completions predicted-but-not-realized, progress prediction error)
are readable after the run.

**Why this priority**: The policy is the consumer that turns the head's
expectations into the measured behavior; it is what a user actually runs to
get woodcutters that finish chains.

**Independent Test**: Unit-test the policy against a stubbed context: draw
order, tie-breaking, the completion rule, and the counters — no world needed.

**Acceptance Scenarios**:

1. **Given** the policy with the event head off, **When** it selects actions,
   **Then** it behaves exactly as the shipped curiosity lookahead (the itch
   term contributes nothing) and its random-path draw order is identical.
2. **Given** a stubbed context where one action's predicted pocket delta
   exceeds the completion threshold, **When** the policy values actions,
   **Then** that action's progress-after counts as full (1.0).
3. **Given** a stubbed context with known predicted progress deltas, **When**
   the policy values actions, **Then** the itch term equals
   kappa · (progress_after − progress_now) with progress_after clipped to
   [0, 1], and ties resolve to the lowest action index.
4. **Given** a sequence of steps where a predicted completion is not realized
   in the next observation, **When** the run proceeds, **Then** the
   false-completion counter increments and no unbounded memory grows.

---

### User Story 3 - The research gate closes on the shipped build (Priority: P3)

The maintainer reruns the G3 confirmatory protocol using the shipped event
head and shipped policy (in place of the scratchpad prototype) and records the
result in the motivation-stack topic README. Episode 0071's reversal condition
is thereby answered on the record: the mechanism, not the instrument, carried
the pass.

**Why this priority**: It is the feature's honesty obligation, but it can only
run after stories 1 and 2 exist.

**Independent Test**: The rerun script consumes only shipped components plus
the existing measured harness pieces; Bar A (≥ 18/24 seeds gain a log at
κ = 0.25) must hold, with all three bars recorded either way.

**Acceptance Scenarios**:

1. **Given** the shipped head and policy, **When** the 24-seed G3 confirmatory
   protocol reruns, **Then** Bar A reproduces (≥ 18/24) and the result —
   pass or fail — is recorded in the topic README the same day.

---

### Edge Cases

- Old snapshot blobs (pre-feature) and feature-off blobs carry no head state:
  loading them with the feature on cold-starts the head; loading a head-on
  blob with a feature-off boot config follows the snapshot's config-in-force
  (the established resume rule — the snapshot wins).
- The policy is constructed but the engine's config never enabled the head:
  the itch term is inert (no crash, no drift from the curiosity baseline).
- Channel indices out of range for the anatomy must fail loudly at
  construction, not silently misread a channel.
- A user setting the dial at or above the stability bound (η ≥ 2) must be
  refused at configuration time.
- Episode boundaries in continuous mode: the head must learn the boundary
  transition (the measured instrument did); episodic mode must never learn
  across a world reset (no invalid pairs can form).
- Multi-stream runs (n_streams > 1): one brain, K worlds — the head learns
  from the merged stream in episode order, exactly as the frames do.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide an event head: per-action predictors of
  the next-observation delta over all sensed channels, learned online by
  normalized least-mean-squares with a single step-size dial, cold-started at
  zero, consuming no randomness.
- **FR-002**: The event head MUST be off by default, and when off MUST add no
  state, no floating-point work, and no RNG consumption — every existing mode
  byte-identical to the pre-feature build.
- **FR-003**: The configuration dial MUST be validated at construction:
  0 ≤ η < 2, with 0 meaning off.
- **FR-004**: When on, the head MUST learn from every executed transition the
  policy witnesses — including across virtual episode boundaries in
  continuous mode — and MUST NOT form learning pairs across a real world
  reset in episodic mode.
- **FR-005**: Policies MUST be able to read the head's per-action predicted
  delta for the current observation through the policy context; the reading
  MUST be None whenever the head is off, and the pinned random baseline MUST
  not do any head work.
- **FR-006**: The system MUST ship a completion-itch policy valuing each
  candidate action as: drive value of the frames' predicted outcome, plus an
  optional caller-injected per-action term, plus κ times (progress-after
  minus progress-now); progress-after is 1.0 when the head predicts a pocket
  gain above a caller-set threshold, else the clipped sum of sensed progress
  and predicted progress delta. Draw order, exploration/maturity gating,
  candidate-skip, and tie-breaking MUST be identical to the shipped curiosity
  lookahead policy.
- **FR-007**: The policy MUST expose bounded honesty counters — completions
  predicted, completions predicted but not realized against the next
  observation, and an exponential moving average of progress prediction
  error — with no unbounded per-step memory.
- **FR-008**: The head's learned state MUST persist in snapshots when on
  (absent key = cold start on load); feature-off blobs MUST stay bit-identical
  to the pre-feature format.
- **FR-009**: Anatomy resize MUST preserve existing head entries bit-for-bit,
  zero-initialize growth, truncate shrink, and draw no randomness.
- **FR-010**: The Minecraft anatomy MUST export the sensed channel index
  constants (mining progress, pocket total) derived from its sensor specs, so
  policy construction never hard-codes positions.
- **FR-011**: The v1 public surface MUST grow additively only: new inventory
  entries for the new class/constants/config field, design docs 0005/0007/0008
  updated, package version bumped one minor step.
- **FR-012**: The G3 confirmatory rerun on the shipped components MUST be
  executed and its three bars recorded in the motivation-stack topic README
  before the feature is declared done (episode 0071's reversal condition).

### Key Entities

- **Event head**: the brain's second prediction pathway — per-action linear
  delta models over all sensed channels; owned by the brain's learning-state
  owner alongside the frames; state = weights + update count.
- **Completion-itch policy**: a shipped action-selection policy composing
  drive value, an optional injected per-action term, and the event-head itch;
  carries the honesty counters.
- **Policy context**: the read-only per-step view policies select from; gains
  the head's per-action prediction accessor.
- **Snapshot**: the complete behavior-affecting state; gains the head's state
  as an additive-optional entry.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: With the feature off, every existing validated mode produces
  byte-identical results to the pre-feature build (proven by test, not
  assertion).
- **SC-002**: With the feature on, a stopped-and-resumed run is identical to
  the uninterrupted run (resume equivalence at the head's presence).
- **SC-003**: The shipped build reproduces G3 Bar A: ≥ 18 of 24 seeds gain at
  least one log under the G3 confirmatory protocol at κ = 0.25, using only
  shipped components for head and policy.
- **SC-004**: The head's progress-channel prediction error under the G3
  protocol lands at the measured order (≤ half a tick, the Bar-P line), not
  the frames' order.
- **SC-005**: The full quality gate (format, lint, all tests including the
  structural lint and the public-surface guard) is green, and the surface
  diff is additive-only.

## Assumptions

- The feature ships the mechanism and its seams; it does not change any
  default behavior, drive, or policy selection — enabling remains an explicit
  owner/user act (config dial + injected policy).
- Channel indices and κ are anatomy-specific runtime knowledge and belong to
  policy construction, not global configuration; the G3-measured operating
  point (η = 0.5, κ = 0.25, threshold = half an item) is documented as the
  recommended starting point, not hard-coded.
- The per-action potential term (the "hold") remains caller-injected: the
  measured clone-step potential is research instrumentation, not part of the
  brain, and ships nowhere.
- The engine summary schema is not extended in this feature (the policy's
  counters are read from the policy object, the existing telemetry pattern);
  a summary field can be a later additive change if wanted.
- Multi-stream learning uses the same merged-stream semantics as the frames;
  no per-stream heads.
