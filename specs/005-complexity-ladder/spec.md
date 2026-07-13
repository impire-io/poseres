# Feature Specification: The Complexity Ladder

**Feature Branch**: `005-complexity-ladder`
**Created**: 2026-07-13
**Status**: Draft
**Input**: User description: "The complexity ladder (ROADMAP A3): a family of synthetic worlds, shipped in-repo, that get harder in known ways while keeping ground truth measurable — the controlled staircase between the current uniformly-learnable SensorimotorWorld and real worlds. Three rungs, each an EventSource-conformant world with known true structure: (1) non-uniform learnability; (2) compositional latents; (3) distractor dimensions. Every rung keeps the instrument panel; the validated reference world stays byte-identical; each rung defines measurably what 'finding the structure' means; ladder results are recorded per rung including failures."

## Overview

Today the system is validated on one kind of world: a single hidden pose,
uniformly learnable — every observation channel rewards modeling equally.
Real worlds are not like that: they contain noise nothing can learn,
structure made of independent parts, and signals that move on their own no
matter what the agent does. The complexity ladder is the controlled
staircase between those two points. Each rung is a new synthetic world that
is harder than the reference world **in exactly one known way**, so that
when the brain fails, the failure names its own cause — and each rung keeps
the full instrument panel (determinism, seeded reproducibility, ground
truth known to the measurement harness) that made the existing validation
trustworthy.

The ladder is research infrastructure with a stated customer: the drive
research of ROADMAP A4 needs the non-uniform rung (a world where
curiosity's known failure mode — staring at unlearnable noise — and
competence's known risk — camping on mastered regions — become measurable
rather than hypothetical), and every future showcase inherits whatever the
ladder finds. Its exit criterion, fixed in the roadmap before this spec:
the world family ships in-repo with its own acceptance criteria, and ladder
results are recorded per rung, **including failures**.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The non-uniform world: structure next to noise (Priority: P1)

A researcher configures a world where a known fraction of the observation
carries the familiar learnable structure and the remaining channels carry
noise that nothing can ever learn. They run the existing engine on it,
unchanged, across the standard seeds, and receive an honest reading:
did the population still find the learnable structure, at what quality
relative to the all-learnable baseline, and how was the system's experience
and capacity allocated between the learnable and unlearnable parts of the
world?

**Why this priority**: This rung is the named gate for the A4 drive-blend
research (the noisy-TV / camping testbed) — it unblocks the next roadmap
item, and it is the smallest step off the validated staircase (one new
property: learnability is no longer uniform).

**Independent Test**: Can be fully tested by running the rung across seeds
with the pinned random policy and reading its per-seed report — structure
quality on the learnable part, the known noise floor on the unlearnable
part, and the allocation reading — with no other rung present.

**Acceptance Scenarios**:

1. **Given** a non-uniform world with a chosen learnable/unlearnable split,
   **When** the engine runs across the standard seeds, **Then** the harness
   reports, per seed, a structure-quality reading on the learnable portion
   that is comparable against the same-size all-learnable baseline world,
   and the result is recorded whether it passes or fails the rung's
   pre-registered criterion.
2. **Given** the same run, **When** the report is produced, **Then** it
   includes an experience/capacity-allocation reading (how much of what the
   system modeled sits on learnable vs unlearnable channels) precise enough
   for the A4 drive study to detect camping and noise-staring.
3. **Given** two runs with the same seed and configuration, **When** their
   summaries are compared byte-for-byte, **Then** they are identical.

---

### User Story 2 - The compositional world: structure made of parts (Priority: P2)

A researcher configures a world whose hidden state is not one monolithic
pose but several independent factor groups of known sizes, each moved by
its own share of the action, all emitting into one observation. They run
the engine unchanged and receive an honest reading of whether the frame
ecology discovers the parts — multiple stable frames at the factors' sizes
— or instead builds one monolithic model at the combined size, and at what
prediction quality either way.

**Why this priority**: Compositionality is the second-named rung in the
roadmap and the first question about the *shape* of discovered structure
rather than its size — but nothing downstream is gated on it the way A4 is
gated on the non-uniform rung.

**Independent Test**: Can be fully tested by running the rung across seeds
and reading its per-seed report of discovered structure sizes against the
known factor sizes, with no other rung present.

**Acceptance Scenarios**:

1. **Given** a compositional world with known factor-group sizes, **When**
   the engine runs across the standard seeds, **Then** the harness reports
   per seed the sizes of the stable discovered structures and prediction
   quality, judged against the rung's pre-registered criterion, and the
   result is recorded either way.
2. **Given** two runs with the same seed and configuration, **When** their
   summaries are compared byte-for-byte, **Then** they are identical.

---

### User Story 3 - The distractor world: signal that moves on its own (Priority: P3)

A researcher configures a world where, alongside the controllable pose,
additional channels carry a structured signal that evolves autonomously —
predictable in principle, but never influenced by the agent's actions.
They run the engine unchanged and receive an honest reading of whether the
selected structure tracks the controllable part of the world or absorbs
the distractor into itself.

**Why this priority**: The distractor rung sharpens what "the right
dimensionality" means (controllable vs merely-present structure) and is
the closest analogue to real sensor streams — but it depends on the same
machinery as the first two rungs and gates nothing downstream directly.

**Independent Test**: Can be fully tested by running the rung across seeds
and reading its per-seed report of selected structure size against the
known controllable size, with no other rung present.

**Acceptance Scenarios**:

1. **Given** a distractor world with known controllable and distractor
   sizes, **When** the engine runs across the standard seeds, **Then** the
   harness reports per seed the selected structure size and prediction
   quality on controllable vs distractor channels, judged against the
   rung's pre-registered criterion, and the result is recorded either way.
2. **Given** two runs with the same seed and configuration, **When** their
   summaries are compared byte-for-byte, **Then** they are identical.

---

### User Story 4 - The ladder as one instrument (Priority: P4)

A researcher runs the whole ladder — every configured rung across the
standard seeds — with one command, and receives one report with per-rung,
per-seed readings and verdicts against each rung's pre-registered
criterion. The recorded results (including failures) become the ladder
results the roadmap's exit criterion requires.

**Why this priority**: Convenience and the recording obligation; it
composes the first three stories but adds no new world behavior.

**Independent Test**: With at least one rung implemented, the single
command produces the combined report and a machine-readable artifact.

**Acceptance Scenarios**:

1. **Given** the implemented rungs, **When** the ladder command runs,
   **Then** one report carries every rung's per-seed spread, its criterion,
   its verdict, and wall-clock — and a failing rung is reported exactly as
   visibly as a passing one, never as a build error.

---

### Edge Cases

- A rung configured to be degenerate (zero unlearnable channels, one
  factor group, zero distractor channels) must reduce to a world
  behaviorally equivalent to the reference family, so every rung's dial
  starts from validated ground.
- Configurations that cannot be honored (more unlearnable channels than
  observation channels; factor-group sizes that exceed the hidden-state
  size; distractor sizes exceeding available channels) must be rejected at
  configuration time with a clear message, never silently adjusted.
- The scale rules key off the *total* observation size. On rungs where
  part of the observation is noise or distractor, the effective rules will
  see a bigger world than the learnable core. The rung reports must carry
  enough information (total vs learnable sizes) for this to be visible in
  analysis rather than discovered by surprise.
- A rung run with a single seed must carry the existing
  "for debugging only" labeling — no single-seed result reads as a
  validated claim.
- Ladder worlds must be usable through the existing body/anatomy layer the
  same way the reference world is (they sit behind the same seam), so
  drive research can mount them without new plumbing.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a non-uniform-learnability world in
  which a configurable portion of the observation carries the familiar
  learnable structure and the remainder carries irreducible noise, with
  the split known to the measurement harness and never exposed to the
  learning system.
- **FR-002**: The system MUST provide a compositional world whose hidden
  state consists of a configurable number of independent factor groups of
  configurable sizes, jointly emitted into one observation, with the group
  structure known to the harness and never exposed to the learning system.
- **FR-003**: The system MUST provide a distractor world in which
  configurable observation channels carry structured signal that evolves
  independently of the agent's actions alongside the controllable
  structure, with the controllable/distractor split known to the harness
  and never exposed to the learning system.
- **FR-004**: Every ladder world MUST present exactly the same surface to
  the learning system as the existing world (begin an episode, step under
  an action, expose only observation and action-space sizes), so the
  engine, body layer, and drives run on it unchanged.
- **FR-005**: Every ladder world MUST be deterministic and seeded: the
  same seed and configuration produce byte-identical run summaries, and
  parallel execution never changes any result.
- **FR-006**: The ladder MUST be opt-in: with no ladder world selected,
  every existing mode — the validated reference suite, agency, scale, and
  persistence behavior — remains byte-identical to its recorded reference.
- **FR-007**: Each rung MUST have a pre-registered acceptance criterion,
  written in the repository before that rung's results are produced,
  defining measurably what "finding the structure" means for that rung
  (in the spirit of the existing horizon and spread rules: judged on
  per-seed spreads at stated checkpoints, never on a bare mean).
- **FR-008**: The harness MUST be able to run each rung across the
  configured seeds and emit per-seed readings sufficient to judge the
  rung's criterion, including: structure-quality relative to the rung's
  stated baseline, discovered-structure sizes against the known ground
  truth, and (for the non-uniform rung) the allocation of modeling across
  learnable vs unlearnable channels.
- **FR-009**: Rung results MUST be investigatory at the build level: a
  failing rung is recorded and reported with the numbers that show why,
  and MUST NOT fail the build or be smoothed away; the reporting follows
  the honest-summary rules (spreads, per-seed lists, failures surfaced).
- **FR-010**: The ladder MUST be runnable as one command producing one
  combined human-readable report and one machine-readable artifact
  carrying every rung's configuration summary, per-seed readings,
  criterion, verdict, and wall-clock.
- **FR-011**: Invalid rung configurations MUST be rejected at
  configuration time with a message naming the violated constraint.
- **FR-012**: Each rung, set to its degenerate dial position, MUST reduce
  to behavior equivalent to the reference world family so the ladder's
  ground floor is the validated system.

### Key Entities

- **Ladder rung**: one world family member with a named difficulty axis
  (non-uniform learnability, compositional latents, distractor
  dimensions), its configuration dials, its ground-truth descriptor
  (known to the harness only), and its pre-registered criterion.
- **Rung configuration**: the dials of one rung (e.g., learnable size vs
  noise size; factor-group sizes; controllable vs distractor sizes) plus
  the shared world dials (observation size, actions, seeds).
- **Rung reading**: the per-seed measurement set the criterion is judged
  on (structure sizes, quality readings, allocation readings, checkpoint
  trajectory).
- **Ladder report**: the combined artifact — per rung: configuration
  summary, per-seed readings, criterion, verdict, wall-clock — in both
  human-readable and machine-readable form.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Each implemented rung runs across the standard 8 seeds from
  a single configuration to a complete per-seed report, and re-running any
  seed reproduces its summary byte-for-byte.
- **SC-002**: The full existing validation suite still passes with its
  recorded reference values byte-identical after the ladder ships (zero
  behavioral drift in every validated mode).
- **SC-003**: Every rung's acceptance criterion exists in the repository
  before that rung's first recorded results, and the recorded ladder
  results include at least one full per-rung, per-seed reading for every
  implemented rung — pass or fail.
- **SC-004**: The non-uniform rung's report gives the A4 drive study a
  quantitative allocation reading (learnable vs unlearnable modeling
  share) for every seed of every run, without any additional
  instrumentation work.
- **SC-005**: Nothing observable through the learning system's world
  surface distinguishes ground truth: the system-visible surface carries
  only observations and action-space size on every rung.
- **SC-006**: A newcomer following the repository documentation can run
  the whole ladder with one command and locate every rung's verdict and
  spread in the output without reading source code.

## Assumptions

- The ladder's first measured results use the pinned random policy (the
  validation baseline), matching how every existing acceptance result is
  produced; drive-directed runs on ladder worlds are A4's work, not this
  feature's.
- Rung difficulty dials follow the project's reference-preserving pattern:
  each dial has a degenerate position at which behavior is equivalent to
  the validated reference family, and rungs are exercised at moderate,
  stated dial positions for their first recorded results (reference-scale
  observation sizes, not the large-scale grid, unless the criterion says
  otherwise).
- "Unlearnable noise" means signal with no learnable relationship to
  latent state or action (fresh randomness every step) — the strongest
  honest form of the noisy-TV property; "structured distractor" means a
  signal predictable from its own hidden state but uninfluenced by
  actions.
- The existing per-seed summary and reporting machinery is the vehicle
  for rung readings; rung-specific readings extend the report rather than
  invent a parallel reporting path, and they follow the established
  honest-summary rules (per-seed spreads, no bare means, failures
  surfaced).
- The three rungs are separate worlds sharing dials, not one world with
  all three difficulties at once; combining axes is future ladder work
  and out of scope here.
- Scale-rule interaction (effective rules keying off total observation
  size on worlds whose learnable core is smaller) is reported transparently
  in this feature and studied, if needed, as its own follow-up — the
  ladder's first results do not attempt to resolve it.
