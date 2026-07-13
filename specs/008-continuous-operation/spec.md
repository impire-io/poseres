# Feature Specification: Continuous Operation

**Feature Branch**: `008-continuous-operation`
**Created**: 2026-07-13
**Status**: Draft
**Input**: User description: "Continuous operation (ROADMAP B3): run the engine on worlds that cannot restart — no reset() after boot — the prerequisite for MMOs, hardware, and anything persistent. The engine gains an opt-in continuous mode in which the world is reset exactly once at run start and never again; the experience stream is segmented into virtual episodes, and every episode-keyed mechanism keeps its meaning at virtual boundaries. The design must be written first."

## Overview

Everything the system has validated so far assumes a world that can be
restarted: every episode begins with the world jumping to a fresh state.
Most worlds worth deploying into cannot do that — a persistent online
game does not rewind because an agent's episode ended, and a physical
robot cannot teleport home forty times a minute. Continuous operation is
the bridge: an opt-in mode in which the world is prepared **once** at the
start of a run (boot — for hardware, a homing routine; for a persistent
service, a login) and then experiences one unbroken stream of time.

The engine's learning rhythm, however, is built on episodes: young-frame
protection windows, the fair-judge scoring window, the weight-norm
lifetime cap, and the transition chain are all keyed to episode
boundaries — and all of it is validated, byte-frozen behavior. The design
principle of this feature is therefore **virtual episodes**: the unbroken
stream is segmented into fixed-length spans that carry every
episode-keyed mechanism exactly as real episodes do, so that the *only*
behavioral difference between the validated mode and continuous mode is
the absence of the world's state jump. One new property, everything else
held fixed — the same discipline as the complexity ladder.

This is a design-first feature (it touches engine semantics — the first
feature since the anatomy layer to do so): the written design must answer
what consolidation boundaries mean without resets, what the
reproducibility story becomes, and what "reset once" means for hardware —
the answer the hardware showcase (ROADMAP C2) was promised.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A world that cannot restart runs to a faithful summary (Priority: P1)

A researcher or maker has a world with no restart capability — once
booted, it only moves forward. They select continuous mode in the
configuration and run the unchanged engine on it. The run boots the world
exactly once, learns from the unbroken stream through the normal fast and
slow loops, and ends with the same per-seed summary any other run
produces — deterministically: the same configuration and seed give the
same summary, byte for byte, every time.

**Why this priority**: This is the feature — the prerequisite for every
persistent deployment (ROADMAP C1, C2). Without it, nothing that cannot
`reset()` can be learned from at all.

**Independent Test**: Run continuous mode on a reset-less world across
seeds; assert the world's boot happened exactly once per run, the summary
is complete, and re-running any seed reproduces its summary byte for
byte.

**Acceptance Scenarios**:

1. **Given** a world that raises an error if restarted after boot,
   **When** the engine runs it in continuous mode for the standard
   schedule, **Then** the run completes to a full per-seed summary and
   the world was booted exactly once.
2. **Given** the same configuration and seed, **When** the run is
   repeated, **Then** the two summaries are byte-identical.
3. **Given** continuous mode is *not* selected, **When** any existing
   mode runs, **Then** its behavior and serialized summaries are
   byte-identical to the validated build (the frozen reference).

---

### User Story 2 - Every learning mechanism keeps its meaning (Priority: P1)

A researcher reading the design or the telemetry of a continuous run can
point at each episode-keyed mechanism — the young-frame protection
window, the fair-judge scoring window, the lifetime weight cap, the
transition chain, warmup — and see exactly where it acts in the unbroken
stream and why that placement preserves the mechanism's validated
meaning. The stream is segmented into virtual episodes of the same length
as real ones; boundaries carry the same mechanics; no observation is
skipped and none is processed twice.

**Why this priority**: The mode is only trustworthy if the validated
learning dynamics carry over interpretably — otherwise every downstream
result on continuous worlds would need its own re-validation from
scratch.

**Independent Test**: On the same seeded world, compare a continuous run
against an episodic run mechanism by mechanism: boundary-triggered
actions (chain break, window restart, cap projection) occur at the same
stream positions; the continuous run consumes every observation the
world produced exactly once.

**Acceptance Scenarios**:

1. **Given** a continuous run, **When** its stream positions are
   examined, **Then** boundary-keyed mechanisms fire at the virtual
   boundaries — the same positions where episodic mode would have reset —
   and nowhere else.
2. **Given** a virtual boundary, **When** the next span begins, **Then**
   its first observation is the one the world produced last (no gap, no
   double-processing, no synthetic observations).
3. **Given** a snapshot taken at a consolidation boundary of a continuous
   run, **When** the run is resumed from it, **Then** the resumed run's
   summary is byte-identical to the uninterrupted run (the existing
   persistence guarantee, now in continuous mode).

---

### User Story 3 - The episodic-vs-continuous reading is recorded (Priority: P2)

A researcher runs the same seeded, resettable world both ways — episodic
(the validated baseline) and continuous (the world simply never jumps
back) — across the standard seeds, and records what changes: prediction
improvement, discovered structure size, population. The reading is
investigatory: it is recorded whichever way it lands, as the first
honest data on what the absence of resets does to learning.

**Why this priority**: The mode ships with its first measurement, per
house rules — but the mode's correctness (US1/US2) does not depend on
this reading's outcome.

**Independent Test**: Run the paired comparison across 8 seeds; the
per-seed readings and spreads are recorded in the feature's trail
document, pass or fail nothing.

**Acceptance Scenarios**:

1. **Given** the reference world run both ways at the standard schedule
   across the standard seeds, **When** the comparison completes, **Then**
   per-seed improvement, structure size, and population are recorded
   side by side with spreads, labeled investigatory.

---

### Edge Cases

- A world whose boot itself is expensive or stateful (hardware homing, a
  service login) must be booted exactly once per run — never lazily
  re-booted, never skipped. The single-boot guarantee is a tested
  contract, not a convention.
- Resuming a continuous run from a snapshot must not re-boot the world a
  second time *logically*: the resumed process necessarily reconstructs
  a world instance, and for seed-derivable worlds this is exact; for
  worlds whose state cannot be re-derived (external services, hardware)
  the limitation is ROADMAP B5's, stated here and unresolved here.
- Schedules whose step counts don't align (a stream shorter than one
  virtual episode; warmup longer than the run) must behave sensibly and
  deterministically — the same segmentation rules at every scale of
  schedule.
- Continuous mode with drives (directed policies), bodies (anatomy
  layer), ladder worlds, and snapshots must compose without special
  cases — the mode changes *when boundaries happen*, not what any other
  subsystem does.
- Selecting continuous mode together with a world that expects per-episode
  resets is legitimate (any resettable world can run continuously — it
  just never jumps back); the reverse — episodic mode on a world that
  cannot reset — fails today and keeps failing, with the world's own
  error surfacing clearly.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide an opt-in continuous mode, selected
  in configuration, in which the world is prepared exactly once per run
  and never restarted afterward; the single-preparation guarantee MUST be
  enforced by the engine (not left to world implementations) and be
  observable in tests.
- **FR-002**: With continuous mode not selected, every existing mode's
  behavior and serialized summaries MUST remain byte-identical to the
  validated build.
- **FR-003**: In continuous mode the experience stream MUST be segmented
  into virtual episodes of the configured episode length, and every
  episode-keyed mechanism — transition-chain break, scoring-window
  restart, lifetime-cap projection, warmup accounting, per-episode
  telemetry — MUST act at virtual boundaries exactly as it acts at real
  episode boundaries in episodic mode.
- **FR-004**: Across a virtual boundary, the stream MUST be gap-free and
  duplication-free: the last observation produced before the boundary is
  the first observation of the next span; no observation is synthesized,
  skipped, or processed twice.
- **FR-005**: Continuous runs MUST be deterministic per configuration and
  seed — byte-identical summaries on re-run, unaffected by worker
  parallelism — and MUST support the existing snapshot/resume guarantee
  (resume from any consolidation-boundary snapshot reproduces the
  uninterrupted run byte for byte) for worlds whose state is derivable
  from the seeded stream.
- **FR-006**: The design MUST be written before implementation and MUST
  answer, explicitly: what consolidation boundaries mean without resets;
  what the reproducibility story is; what single-boot means for hardware
  and persistent services (the ROADMAP C2 promise); and how the mode
  composes with drives, bodies, ladder worlds, and persistence.
- **FR-007**: The feature MUST ship with a reset-less validation world
  (a world that permits exactly one boot and fails loudly on any second
  attempt) used by the engine's own tests to prove the single-boot
  contract.
- **FR-008**: The feature MUST record the investigatory
  episodic-vs-continuous reading (same world, same seeds, both modes;
  per-seed improvement, structure size, population, with spreads) in its
  trail documentation — whichever way it lands.
- **FR-009**: Invalid combinations (continuous mode with a schedule of
  zero virtual episodes; contradictory episode dials) MUST be rejected at
  configuration time with a message naming the violated constraint.

### Key Entities

- **Continuous mode**: the configuration-selected run mode; identical to
  episodic mode except the world's state never jumps back.
- **Virtual episode**: a fixed-length span of the unbroken stream carrying
  every boundary-keyed mechanism of a real episode; the unit warmup and
  scoring windows count in continuous mode.
- **Boot**: the world's single preparation at run start (a reset, a
  homing routine, a login); in continuous mode it happens exactly once.
- **Reset-less validation world**: the in-repo world that enforces and
  proves the single-boot contract (boots once, fails loudly on any second
  attempt).
- **Episodic-vs-continuous reading**: the recorded investigatory
  comparison of the two modes on the same seeded world.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reset-less world runs in continuous mode across the
  standard 8 seeds to complete summaries, with the world booted exactly
  once per run, and re-running any seed reproduces its summary byte for
  byte.
- **SC-002**: The full existing validation suite passes with its recorded
  reference values byte-identical after the feature ships (zero
  behavioral drift in every validated mode).
- **SC-003**: A continuous run resumed from a mid-run snapshot produces a
  summary byte-identical to the uninterrupted run, on a seed-derivable
  world.
- **SC-004**: The written design (committed before implementation)
  answers the four named questions of FR-006, and each episode-keyed
  mechanism's continuous-mode placement is documented and covered by a
  test that would fail if its boundary moved.
- **SC-005**: The episodic-vs-continuous reading exists in the trail
  documentation with per-seed spreads for the standard seeds, labeled
  investigatory.
- **SC-006**: A user can switch a working episodic configuration to
  continuous mode by changing one configuration selection, with no world
  or code changes, when their world supports being run unbroken.

## Assumptions

- Time is simulated and steppable throughout: "continuous" means *no
  state jumps*, not *real time*. Wall-clock/real-time worlds remain out
  of scope (they arrive with the hardware showcase, gated on this
  feature).
- Virtual episodes reuse the configured episode length rather than
  introducing a new dial: the segmentation exists to preserve validated
  mechanism meanings, and those meanings were validated at that length.
  A separate virtual-length dial is future work if a deployment demands
  it.
- The transition chain breaks at virtual boundaries (rather than carrying
  across) because every validated boundary mechanism keys off that break;
  carrying it across would silently change the meaning of the scoring
  window, the cap, and protection windows all at once. The cost — one
  untrained transition per virtual episode — is small and stated; a
  carry-across variant is a possible future dial, not part of this
  feature.
- Multi-stream experience (several worlds, one brain) is ROADMAP B4;
  snapshot semantics for worlds whose state cannot be re-derived from the
  seed is ROADMAP B5. Both are named neighbors, not scope.
- The investigatory reading uses the pinned random policy (the validation
  baseline), consistent with how every first reading in this project is
  produced.
