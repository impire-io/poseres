# Feature Specification: Learned Channel Weighting (The L3-Noise Remedy)

**Feature Branch**: `016-channel-weighting`
**Created**: 2026-07-18
**Status**: Draft
**Input**: User description: "Learned channel weighting — the L3-noise remedy
(research arc 016). An in-system, learning-free per-channel whiteness
estimator (lag-1 autocorrelation of the observation stream, global on
FrameStore) producing weights w ∈ [channel_weight_floor, 1] per channel,
recomputed at episode starts, applied simultaneously to (1) the survival-score
error norms, (2) the encoder input, and (3) the backprop reconstruction error
— so channels carrying irreducible static are down-weighted in both judging
and learning. Opt-in via channel_weight_floor (0.0 = off = byte-identical
pinned validated behavior; recommended 0.2 by the transport argument: weighted
σ_d=1.0 ≡ unweighted σ_d=0.2, a measured PASS). Estimator state is snapshot
state. Success: L3 ladder noise mode flips FAIL→PASS at σ_d=1.0 with no harm
anywhere else; feature OFF is byte-identical everywhere. The science is
pre-registered in design/validate/CHANNELWEIGHT-DIAGNOSIS.md; the experiment
gates become ordered tasks with stop conditions. Successor named in
CHANNELNOISE-DIAGNOSIS.md Outcome §4 (ch. 25); ROADMAP names this C2's de
facto research gate."

## Overview

Chapter 25 closed with a measured mechanism and an unshipped remedy. When half
the observation carries pure static (the L3 ladder rung in noise mode), the
brain's structure-finding collapses — not because the ecology malfunctions,
but because it faithfully follows a survival score that has lost its gradient.
The diagnosis measured a three-leg compound: irreducible per-channel noise
floors compress the score's dimensional gradient; static entering the shared
encoder corrupts core learning itself; and the floor holds every frame's score
above the survival bar, so nothing ever matures. It also measured the shape
the fix must take: score-side channel exclusion alone — even with *oracle*
knowledge of which channels are static — rescues moderate doses but **not**
unit amplitude. The learning path needs the same treatment.

This feature is that named remedy: **learned channel weighting**. The brain
maintains, from its own observation stream and nothing else, a per-channel
estimate of temporal structure (static is white; real channels carry the
world's dynamics), turns it into per-channel weights, and applies those
weights consistently in the two places the diagnosis implicated — how frames
are *judged* (the survival-score error norms) and how frames *learn* (the
encoder input and the reconstruction error that drives weight updates). A
channel that carries only noise stops drowning the signal; a channel that
carries structure keeps its full voice. The weights never reach zero: a
floor keeps every channel minimally audible, so a channel that becomes
meaningful later (a new sensor, a world change) can be re-admitted.

The design has a measured spine, not a tuned one — the **transport argument**:
with static channels weighted at the floor 0.2, every computation the brain
performs at unit static amplitude becomes operation-for-operation equivalent
to the same computation at amplitude 0.2 — an operating point the chapter-25
dose–response already measured as a clean PASS. The remedy transports the
system into a regime already known to work, rather than being tuned until it
looks green.

The science stays honest the house way. The full experimental protocol —
including an oracle gate that must pass **before** any estimator code is
written, and pre-registered failure exits that stop the arc rather than bend
the criteria — lives in `design/validate/CHANNELWEIGHT-DIAGNOSIS.md`,
committed before any experiment runs. The recorded L3 FAIL stays in the
record untouched; if the rescue succeeds, the flip is recorded as a dated
addendum, and if it only partially succeeds, the residual is recorded as a
measured ceiling — the criterion is not amended either way.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Structure-finding survives unlearnable static (Priority: P1)

A researcher runs a brain in a world where a large fraction of the
observation channels carry irreducible noise (the L3 ladder rung, noise mode,
unit amplitude — today's recorded FAIL). With learned channel weighting
enabled, the brain identifies the noise channels from its own experience,
down-weights them in judging and learning, and lands its dimensional estimate
at the true controllable structure — frames mature instead of being endlessly
churned.

**Why this priority**: This is the feature's reason to exist — the first open
problem the complexity ladder produced, and the named research gate for the
C2 robot showcase. Everything else in this spec is protection around this
outcome.

**Independent Test**: Run the ladder's L3 rung in noise mode at unit
amplitude with the feature enabled, across the full pre-registered seed
protocol; compare against the recorded FAIL (best_dim collapse to 1 in a
majority of seeds).

**Acceptance Scenarios**:

1. **Given** the L3 noise rung at σ_d = 1.0 with `channel_weight_floor = 0.2`,
   **When** the standard schedule runs across the confirmatory seed set,
   **Then** the recorded L3 criterion (|best_dim − 3| ≤ 1, strict majority at
   every checkpoint 18/30/50) is met — in its unchanged form.
2. **Given** the same runs, **When** the final populations are examined,
   **Then** a strict majority of seeds carry at least one mature frame past
   its protection window (the youth conveyor is broken).
3. **Given** the dose–response grid {0.04, 0.1, 0.2, 0.5, 1.0}, **When** the
   feature is ON, **Then** the continuous dose measure (median improvement)
   is restored toward the low-dose anchor and the doses that PASS today
   still PASS.

---

### User Story 2 - Existing users see nothing change (Priority: P1)

A user running any existing configuration — the reference suite, the ladder,
the rover, the adapters, scaled runs — upgrades to a build containing this
feature and observes byte-for-byte identical behavior, because the feature is
off by default and its off-path adds no computation, no randomness, and no
serialized fields.

**Why this priority**: The validated behavior is byte-frozen by house rule;
a remedy that perturbs the reference record is not shippable at any benefit.

**Independent Test**: The pinned seed-1 baseline test, the determinism check,
and the full existing suite run against a build with the feature present but
disabled; snapshot blobs written with the feature off are bit-identical to
the pre-feature format.

**Acceptance Scenarios**:

1. **Given** the default configuration, **When** the reference suite and
   determinism checks run, **Then** every pinned value reproduces exactly.
2. **Given** a configuration that sets the feature's parameters to their
   inert defaults explicitly, **When** a run completes, **Then** its
   serialized summary is byte-equal to the same run without the parameters
   mentioned at all.
3. **Given** a snapshot written with the feature off, **When** its bytes are
   compared to the pre-feature snapshot format, **Then** they are identical.

---

### User Story 3 - The feature travels with the brain (Priority: P2)

A researcher running a long-lived brain with channel weighting enabled
snapshots it mid-run and resumes it elsewhere; the estimator's accumulated
knowledge of which channels are noise travels with the brain, and the resumed
run continues exactly as the uninterrupted one would have. The feature
composes with the other operating modes — continuous operation, multi-stream
experience, growing anatomy.

**Why this priority**: Snapshot completeness is a standing guarantee (Doc 06);
a feature whose state silently resets on resume would violate it and corrupt
long-run science.

**Independent Test**: Snapshot/resume equivalence with the feature on
(resumed run byte-identical to uninterrupted); smoke runs under continuous
mode, multi-stream, and a mid-run anatomy resize.

**Acceptance Scenarios**:

1. **Given** a run with weighting enabled snapshotted mid-run, **When** it is
   resumed, **Then** the continuation is byte-identical to the uninterrupted
   run.
2. **Given** a pre-feature snapshot blob, **When** it is loaded by the new
   build, **Then** it resumes byte-identically under its recorded
   configuration (feature off), and loading it with the feature newly enabled
   starts the estimator fresh — stated openly, not silently.
3. **Given** a mid-run anatomy change that adds observation channels,
   **When** the estimator encounters the new channels, **Then** they enter at
   full weight until enough evidence accumulates to judge them.

---

### Edge Cases

- **Every channel is structured** (reference world, structured distractors):
  the estimator must leave all weights at or near full — measured as a
  no-suppression bar in the protocol, and any core channel down-weighted at
  judging ages is a ship-blocker (exit X2).
- **Early life, before the estimator has evidence**: all channels carry full
  weight until a derived readiness threshold is met — the brain behaves
  exactly as today until it has grounds to differ.
- **A channel changes character mid-run** (noise becomes signal): the floor
  keeps it audible and the statistics keep updating, so it can recover full
  weight; permanent exclusion is unreachable by construction.
- **All channels white** (pathological world): all weights sit at the floor;
  the weighted norms remain well-defined (floor > 0) and the run proceeds.
- **Continuous mode**: weights recompute at virtual episode boundaries — the
  same boundary the existing episode-keyed mechanisms already honor.
- **Multi-stream**: all streams feed one brain and one estimator; the merged
  stream is what the statistics see.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST estimate, per observation channel, a measure of
  temporal structure derived exclusively from the brain's own observation
  stream — never from world configuration, world internals, or any oracle.
- **FR-002**: The system MUST derive per-channel weights from that estimate,
  bounded below by a configured floor strictly greater than zero when the
  feature is enabled, and bounded above by full weight.
- **FR-003**: The system MUST apply the same weights consistently to (a) the
  survival-score error norms — numerator and denominator alike — and (b) the
  learning path: the encoder's view of the observation and the
  reconstruction error that drives weight updates. Judging and learning must
  never disagree about what a channel is worth.
- **FR-004**: Weights MUST be recomputed only at episode boundaries (real or
  virtual), never mid-episode, so that every within-episode judgment happens
  in one consistent norm.
- **FR-005**: The feature MUST be opt-in. At its default (disabled) setting
  the system's RNG stream, behavior, serialized summaries, and snapshot bytes
  MUST be identical to the pre-feature build — with zero additional
  floating-point work on the disabled path.
- **FR-006**: The feature MUST consume no randomness when enabled: two runs
  differing only in the feature toggle see identical world event streams, so
  every enabled-vs-disabled comparison is exactly paired per seed.
- **FR-007**: The estimator's accumulated state MUST be captured in
  snapshots when the feature is enabled and restored on resume such that a
  resumed run is byte-identical to an uninterrupted one; snapshots written
  with the feature disabled MUST remain bit-identical to the pre-feature
  format; pre-feature snapshots MUST load and resume unchanged.
- **FR-008**: The recorded telemetry definitions (prediction-error
  early/late, improvement) MUST keep their current unweighted meaning, so
  dose curves remain comparable with the chapter-25 record; the per-frame
  survival quantities the ecology actually judges are the weighted ones, and
  run summaries MUST carry feature fields only when the feature is enabled.
- **FR-009**: When observation channels are added mid-run, the estimator
  MUST extend to cover them, admitting new channels at full weight until its
  readiness threshold is met; when the anatomy shrinks, it MUST truncate
  accordingly.
- **FR-010**: The research protocol in
  `design/validate/CHANNELWEIGHT-DIAGNOSIS.md` is normative for this feature:
  its experiment gates run in the pre-registered order with their stop
  conditions (the oracle gate before any estimator implementation), its
  numeric bars decide PASS/FAIL, and its failure exits — including stopping
  the arc and recording an honest FAIL — are binding. The recorded L3 FAIL
  and its criterion text are never amended; a successful rescue is recorded
  as a dated addendum alongside the original record.

### Key Entities

- **Channel statistics**: per-channel running mean, variance, lag-1
  covariance, and sample count — the estimator's whole memory, sized by the
  observation width, owned by the brain's frame store, serialized with it.
- **Weight vector**: the per-channel weights in [floor, 1] derived from the
  statistics at episode boundaries; the single object both the judge and the
  learner consult.
- **Trail document** (`design/validate/CHANNELWEIGHT-DIAGNOSIS.md`): the
  pre-registered protocol, its recorded results, and the arc's outcome — the
  scientific record this feature is accountable to.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The L3 noise rung at unit static amplitude meets the recorded
  L3 criterion in its unchanged form — |best_dim − 3| ≤ 1 in a strict
  majority of seeds at every checkpoint (18/30/50) — at confirmatory power
  (24 seeds), with the feature enabled at its recommended setting.
- **SC-002**: The maturation collapse is broken: a strict majority of
  confirmatory seeds end with at least one frame surviving past its
  protection window (the recorded state is zero, in every seed).
- **SC-003**: Every currently-passing verdict stays passing with the feature
  ON: low-dose noise mode, structured mode, the L1 and L2 rungs, and the
  reference world — with per-seed paired degradation in the continuous
  measures within the pre-registered tolerance (≤ 0.05 median-improvement
  drop, strict majority of paired seeds).
- **SC-004**: With the feature disabled, the entire existing validation
  record reproduces byte-for-byte: the pinned seed-1 values, determinism,
  ladder streams, and snapshot bytes.
- **SC-005**: The estimator identifies the static channels — full rank
  separation of static from core channels by the first checkpoint in the
  pre-registered majority of seeds at every dose at or above the instability
  band — while never suppressing a core channel below the no-suppression bar
  on worlds with no static.
- **SC-006**: Whatever the outcome, the trail document records it at
  pre-registered power with spreads: a PASS as a dated addendum beside the
  untouched original FAIL; a partial rescue as a measured dose ceiling with
  the criterion left unamended; a stopped arc as a complete deliverable with
  its exit named.

## Assumptions

- **Whiteness separates static from structure in the current world family.**
  Core channels carry the world's latent dynamics (temporally correlated);
  the L3 noise channels are fresh draws each step (white). The pre-registered
  P1 probe verifies this separation empirically before the design is frozen;
  worlds with temporally-correlated-but-unpredictable channels are out of
  scope and named as the known limit of this estimator (the pre-registered
  hybrid is the named successor if such a world enters the ladder).
- **The transport argument holds as measured**: weighting static at 0.2
  reproduces the σ_d = 0.2 operating point, which the chapter-25 dose grid
  measured as PASS. The oracle gate (E1a) tests exactly this prediction
  before any estimator code exists; if it fails, the arc stops or re-scopes
  per the pre-registered exits rather than proceeding on hope.
- **The second named leg — a survival bar with a notion of achievable error —
  stays deferred.** Its pre-registered trigger (score gradient restored but
  frames still dying above the absolute bar) is evaluated from this arc's
  own measurements; if it fires, that leg gets its own pre-registration as a
  successor, explicitly re-verifying the seventh scale rule interaction. It
  is not bolted into this feature.
- **Scale behavior is a note, not a rule**: the estimator's convergence is
  per-step and independent of observation width, and the protection window
  grows at scale, so weights converge before judgments at any scale; no new
  effective-form rule is introduced. Measured validation happens at the
  ladder's recorded scale.
- **Feature numbering follows the branch** (`016-channel-weighting`), per
  house convention.
