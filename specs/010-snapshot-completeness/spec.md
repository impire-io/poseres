# Feature Specification: Snapshot Completeness

**Feature Branch**: `010-snapshot-completeness`
**Created**: 2026-07-13
**Status**: Draft
**Input**: User description: "Snapshot completeness (ROADMAP B5): snapshots of anatomy-resized runs (the deferred Doc 06 format-version follow-up), and a stated persistence story for external worlds that cannot be re-derived from a seed; plus the multi-stream capture debt named by feature 009. Exit: resize → snapshot → resume is byte-identical; external-world snapshot semantics documented, including what is not guaranteed."

## Overview

Snapshots are the project's continuity story — and three features have
each left one honest hole in it, on purpose, with a name on it. This
feature pays all three debts: **grown bodies** (a run that registered new
sensors mid-run cannot be snapshot today — the frame population's resized
tensors don't match the boot configuration), **worlds with their own
memory** (a Gymnasium environment's reset counter is not derivable from
the seed, so a resumed run would silently diverge — currently documented,
not fixed), and **multi-stream runs** (K stream generators and K world
positions, rejected since feature 009). The exit is the roadmap's: resize
→ snapshot → resume byte-identical, and a written statement of exactly
what snapshots guarantee for every class of world — including what they
do not.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A grown body survives its snapshot (Priority: P1)

A researcher runs a body that registers a new sensor mid-run (the
feature-004 growth path), snapshots after the growth, and later resumes
with a factory that builds the grown anatomy. The resumed run continues
byte-identically with the uninterrupted one.

**Why this priority**: The roadmap exit names it, and it is the oldest
deferred debt (feature 003).

**Independent Test**: register → resize → snapshot → resume → compare
summaries byte for byte; also: resuming with the *wrong* anatomy fails
loudly naming the dimension mismatch.

**Acceptance Scenarios**:

1. **Given** a run whose body grew mid-run, **When** it snapshots after
   the growth and resumes from that snapshot with the grown anatomy,
   **Then** the resumed summary is byte-identical to the uninterrupted
   run.
2. **Given** the same snapshot, **When** resumed with anatomy that does
   not match the recorded grown dimensions, **Then** the resume fails
   with a message naming the mismatch.
3. **Given** a run that never resized, **When** it snapshots, **Then**
   the blob is bit-identical to the pre-feature format.

---

### User Story 2 - Worlds with their own memory snapshot honestly (Priority: P1)

A researcher snapshots a run on a world whose state is not derivable from
the seed (the Gymnasium adapter's episode counter). Worlds that can state
their memory do so and resume exactly; worlds that cannot make the
snapshot fail loudly; and the persistence guarantees per world class are
written down in the design docs — including what is *not* guaranteed
(external environment internals, hardware).

**Why this priority**: The roadmap exit's documentation clause, plus a
real fix where one is cheap (the adapter's counter is one integer).

**Independent Test**: episodic Gymnasium run → snapshot → resume →
byte-identical summary; a world declaring it needs state but not
providing it → loud failure; the Doc 06 guarantees section exists.

**Acceptance Scenarios**:

1. **Given** an episodic Gymnasium run, **When** snapshot and resumed,
   **Then** the summary is byte-identical to the uninterrupted run
   (within the adapter's stated determinism assumptions).
2. **Given** any world that declares its state non-derivable without
   providing capture, **When** a snapshot is attempted, **Then** it fails
   loudly at capture time.

---

### User Story 3 - Multi-stream runs snapshot and resume (Priority: P2)

A researcher snapshots a K-stream run (episodic or continuous) and
resumes it; all stream positions — generators, world states where
required, carried observations, and the merge position — restore exactly,
and the resumed run is byte-identical.

**Why this priority**: The feature-009 debt; needed before any
long-running multi-stream deployment, but nothing downstream is gated on
it this week.

**Independent Test**: K=3 run in each mode → snapshot mid-run → resume →
byte-identical summaries; K=1 blobs remain bit-identical to the
pre-feature format.

**Acceptance Scenarios**:

1. **Given** a K-stream run in either mode, **When** snapshot and
   resumed, **Then** the summary is byte-identical to the uninterrupted
   run.
2. **Given** K=1, **When** snapshots are taken, **Then** blobs are
   bit-identical to the pre-feature format.

---

### Edge Cases

- Old snapshots (every prior format) must keep decoding and resuming
  exactly as before — every addition is optional-with-absent-default.
- Snapshots taken before a mid-run resize and resumed into the original
  anatomy must keep working (the growth happened after the safe point).
- Combined cases compose: resized + continuous (world capture and grown
  dims together), multi-stream + needs-state worlds.
- The loud-failure paths never write a partial artifact.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Snapshots MUST record the frame population's **current**
  dimensions when they differ from the boot configuration, and resume
  MUST rebuild the population at the recorded dimensions and verify the
  booted world/body presents them, failing loudly on mismatch.
- **FR-002**: Unresized, single-stream, seed-derivable-world snapshots
  MUST remain bit-identical to the pre-feature blob format; all format
  additions are optional keys written only when their condition holds.
- **FR-003**: A world MAY declare its state non-derivable from the seed
  (a capture-required marker); for such worlds the engine MUST capture
  world state in **both** episode modes (via the feature-008 protocol)
  and MUST fail loudly at capture time if the world declares the marker
  without providing capture.
- **FR-004**: The Gymnasium adapter MUST implement capture (its reset
  counter) so episodic Gymnasium runs snapshot/resume byte-identically,
  with its determinism assumptions stated; what remains non-guaranteed
  (mid-episode external state, non-deterministic environments, hardware)
  MUST be documented.
- **FR-005**: Multi-stream runs MUST snapshot and resume exactly: per-
  stream generator states, per-stream world state where required
  (continuous mode or capture-required worlds), per-stream carried
  observations, and the merge position; the feature-009 configuration
  rejection is lifted.
- **FR-006**: Doc 06 MUST gain a "what snapshots guarantee" section
  covering every world class — seed-derivable, capture-supporting,
  capture-required, and non-capturable — including explicitly what is
  not guaranteed.

### Key Entities

- **Current dimensions record**: the grown population's obs/action widths,
  recorded when ≠ boot config.
- **Capture-required marker**: a world's declaration that its state is
  not derivable from the seed.
- **Stream record**: per-stream generator state (+ world state/carried
  observation where applicable) and the merge position.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: resize → snapshot → resume is byte-identical (the roadmap
  exit), and wrong-anatomy resume fails loudly.
- **SC-002**: episodic Gymnasium snapshot/resume is byte-identical;
  capture-required-without-capture fails loudly.
- **SC-003**: K-stream snapshot/resume is byte-identical in both modes.
- **SC-004**: every pre-feature blob class decodes and resumes unchanged;
  unresized/K=1/derivable blobs are bit-identical.
- **SC-005**: the Doc 06 guarantees section exists, enumerating the four
  world classes and the non-guarantees.
- **SC-006**: the full existing suite stays green and byte-frozen.

## Assumptions

- Resumed runs supply the grown anatomy via their factory (tools are
  code; the snapshot records dimensions and part identities for
  verification, not executable sensors) — the same principle as world
  reconstruction: code comes from the caller, state from the blob.
- The Gymnasium capture guarantee is conditional on the environment's
  own `reset(seed)` determinism — stated, not assumed silently.
- Format version stays 1: everything is additive-optional in both
  directions (the 003/008 precedent).
