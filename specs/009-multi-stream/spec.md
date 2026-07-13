# Feature Specification: Multi-Stream Experience

**Feature Branch**: `009-multi-stream`
**Created**: 2026-07-13
**Status**: Draft
**Input**: User description: "Multi-stream experience (ROADMAP B4): parallel world instances feeding one brain — the bus seam's moment, and the only honest answer to 'learning is too slow'. This changes the learning regime (EMAs, drive context, consolidation cadence assume one stream), so it is research and engineering: design doc first, measured against single-stream baselines. Exit: K-stream run demonstrably matches or beats the single-stream baseline per unit of experience, spread reported; determinism story stated (per-stream seeds, merged deterministically)."

## Overview

Today one brain learns from one world, one step at a time. Every
deployment that wants faster learning has exactly one honest lever in a
steppable world: **more experience per unit of wall time from parallel
copies of the world** — N game instances, N simulation copies, one brain
learning from all of them. That is what this feature builds: K world
instances of the *same* world, explored differently, feeding one shared
frame population through a deterministic merge.

This is research as much as engineering, and the research question is
stated up front: the validated learning dynamics assume one temporally
coherent stream — prediction chains, scoring windows, drive bookkeeping,
and the consolidation cadence all ride on it. Interleaving K streams
changes the statistics of what the brain sees between consolidations.
Whether merged experience learns *as well as* focused experience per
observation is precisely the exit measurement, taken against
single-stream baselines at equal total experience, with spreads,
whichever way it lands.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - K explorers, one brain, one deterministic summary (Priority: P1)

A researcher sets a stream count K in the configuration and runs the
engine. K instances of the same world (same hidden structure) are
explored by K independent action streams; every observation feeds the
single shared brain through a fixed, documented merge order. The run
produces the same per-seed summary any run produces — deterministically:
same configuration and seed, byte-identical summary, regardless of
worker parallelism.

**Why this priority**: This is the capability. Everything else (the
measurement, the composition) needs K streams running deterministically
first.

**Independent Test**: Run K=4 on the reference world across seeds;
re-run any seed and compare summaries byte for byte; verify the world
instances share structure and the streams' experiences differ.

**Acceptance Scenarios**:

1. **Given** `n_streams=4`, **When** the engine runs, **Then** four world
   instances with identical hidden structure are each explored by their
   own action stream, all feeding one frame population, and the summary
   is complete.
2. **Given** the same configuration and seed, **When** the run repeats,
   **Then** summaries are byte-identical.
3. **Given** `n_streams=1` (the default), **When** any existing mode
   runs, **Then** behavior and summaries are byte-identical to the
   validated build.

---

### User Story 2 - The learning regime is explicit and mechanism-safe (Priority: P1)

A researcher reading the design can point at every stream-coupled
mechanism — the per-stream transition chain, the per-stream scoring
window, the shared drive bookkeeping, birth and consolidation draws, and
the consolidation cadence — and see where it acts under K streams and
why. The consolidation cadence is stated in **total experience** (the
lesson feature 008 made explicit: the slow loop is a cadence in
experience), so a K-stream run consolidates at the same experience
milestones as a single-stream run of equal length.

**Why this priority**: The exit measurement is only meaningful if the
K-stream regime differs from the baseline in exactly one way — merged
experience — and not accidentally in cadence, chains, or windows.

**Independent Test**: Mechanism-placement tests: transition chains never
cross streams; scoring windows restart per stream-episode; consolidation
fires at the same total-experience positions for K=1 and K=4.

**Acceptance Scenarios**:

1. **Given** a K-stream run, **When** transitions are formed, **Then**
   each uses the previous observation and action of its *own* stream —
   never a neighbor's.
2. **Given** K=1 and K=4 runs with the same schedule, **When**
   consolidation positions are compared in total observation count,
   **Then** they are identical.

---

### User Story 3 - The exit measurement: merged vs focused experience (Priority: P1)

A researcher runs the pre-registered comparison: K-stream runs against
single-stream baselines at **equal total experience**, same world
structure per seed, standard seeds, spreads reported. The recorded
verdict against the roadmap's bar — K-stream matches or beats the
baseline per unit of experience — is the feature's research deliverable,
recorded whichever way it lands.

**Why this priority**: The roadmap exit is this measurement; the
capability without the measurement would be exactly the kind of
demo-before-science the project refuses.

**Independent Test**: The comparison table exists in the feature's
reading document with per-seed values, spreads, and a judged verdict
against the pre-registered bar.

**Acceptance Scenarios**:

1. **Given** the comparison protocol, **When** it runs across the
   standard seeds, **Then** per-seed improvement and structure readings
   for K ∈ {2, 4} vs K=1 at equal total experience are recorded with
   spreads and judged against the pre-registered bar.

---

### Edge Cases

- K=1 must be byte-identical to the validated single-stream build — not
  merely equivalent (the default path is untouched).
- Stream counts that don't divide the schedule (rounds and cycles) must
  behave deterministically under a stated rule, not implicitly.
- Continuous mode (feature 008) composes: K streams, each booted exactly
  once, each carrying its own trailing observation. Episodic and
  continuous multi-stream must both be deterministic.
- Snapshots of multi-stream runs must either work exactly (all stream
  worlds captured, in continuous mode via the capture protocol) or fail
  loudly — never a silently unresumable artifact.
- Drive-directed policies compose: the shared brain's bookkeeping sees
  merged experience; each stream's policy acts on its own observations.
  No claim is made about directed-policy performance under K streams —
  that is future research on this feature's instrument.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a configurable stream count K
  (default 1 — byte-identical to the validated build) running K world
  instances **of the same hidden structure per run seed**, each explored
  by an independent, deterministically-seeded action stream.
- **FR-002**: All streams MUST feed the single shared frame population
  through a **fixed, documented, deterministic merge order**; worker
  parallelism MUST NOT change any result.
- **FR-003**: Stream-coupled mechanisms MUST be stream-local: transition
  chains and scoring windows never cross streams; each stream's episodes
  begin and end on its own boundaries (in continuous mode, each stream
  boots once and carries its own trailing observation).
- **FR-004**: Brain-coupled mechanisms MUST be shared and
  merge-order-deterministic: one frame population, one brain generator
  for births/proposals/initialization, shared drive bookkeeping.
- **FR-005**: The consolidation cadence MUST be stated and implemented in
  **total experience**, mode-invariant: K-stream and single-stream runs
  of equal total observation count consolidate at the same experience
  positions.
- **FR-006**: The design MUST be written before implementation, stating:
  the stream/brain ownership split of every randomness source (per-stream
  seeds derived from the run seed; the determinism story the roadmap
  names), the merge discipline, what "same world, K explorers" means for
  world construction, and how the mode composes with episodic/continuous
  operation, drives, bodies, and snapshots.
- **FR-007**: The exit measurement MUST be pre-registered (bar stated
  before data) and recorded with per-seed spreads: K ∈ {2, 4} vs K=1 at
  equal total experience on the reference world, standard seeds —
  whichever way it lands.
- **FR-008**: Invalid configurations (K < 1; K-stream with schedules that
  cannot fit one round) MUST be rejected at configuration time with a
  message naming the constraint.
- **FR-009**: Multi-stream snapshots MUST capture all stream worlds'
  positions exactly (continuous mode: via the feature-008 capture
  protocol per stream) or fail loudly at capture time.

### Key Entities

- **Stream**: one world instance plus its independent exploration
  (action/noise randomness and episode boundaries), identified by a
  stream index; structure shared with all streams of the run.
- **Merge order**: the fixed interleaving discipline by which stream
  experiences reach the shared brain.
- **Brain generator**: the run's shared randomness source for
  births/proposals/initialization, consumed in merge order.
- **Exit reading**: the pre-registered equal-experience comparison
  (K ∈ {1, 2, 4}) with spreads and a judged verdict.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: K=4 runs on the reference world complete across the
  standard 8 seeds and reproduce byte-identically on re-run, worker
  count notwithstanding.
- **SC-002**: The full existing validation suite passes byte-identically
  after the feature ships; K=1 summaries are byte-identical to the
  pre-feature build.
- **SC-003**: Mechanism-placement tests prove: no cross-stream
  transitions; per-stream windows; total-experience consolidation
  positions identical across K.
- **SC-004**: The exit reading exists with per-seed spreads for
  K ∈ {1, 2, 4} at equal total experience, judged against the
  pre-registered bar (match-or-beat per unit of experience).
- **SC-005**: Multi-stream composes with continuous mode (K single-boot
  streams) and with snapshots (exact resume or loud failure), each
  covered by a test.

## Assumptions

- "Parallel" means **experience parallelism with a deterministic merge**,
  not thread parallelism inside one run: the brain is one computation and
  the merge order is part of the semantics. Wall-clock speedups come from
  the world side (real deployments step worlds concurrently and the merge
  consumes them in order); making the in-process reference implementation
  multi-threaded is an optimization outside this feature's scope.
- Streams explore **the same world structure** (one construction per run
  seed, shared across instances) because that is the deployment story (N
  copies of one game, one robot fleet in one room type) and the only form
  under which "structure discovered" keeps a single ground truth. One
  brain across *different* worlds is multi-task learning — a different
  research question, out of scope.
- The default interleaving is round-robin at episode granularity per
  round (each stream completes one episode per round, in stream order) —
  the coarsest merge that keeps all within-episode mechanics untouched;
  finer-grained merges are future dials if research demands them.
- The exit bar reuses the project's noninferiority discipline (the T7
  precedent): per-seed paired margins vs the equal-experience baseline,
  judged by the one-sided noninferiority rule rather than a strict-win
  sign count — "matches or beats" is the roadmap's own wording.
- The pinned random policy produces the exit reading (the validation
  baseline); drive-directed multi-stream behavior is future research.
