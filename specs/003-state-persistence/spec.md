# Feature Specification: State Persistence

**Feature Branch**: `003-state-persistence`
**Created**: 2026-07-08
**Status**: Draft
**Input**: User description: "State persistence (design Doc 06): snapshot/restore of the full learned state — frame population, drive bookkeeping, counters, RNG — via an atomic, versioned SnapshotStore; restore resumes the run."

## User Scenarios & Testing *(mandatory)*

The system learns continuously; today its accumulated state dies with the
process. This feature makes the entire learned state durable: a snapshot taken
at a safe point can be restored later and the system carries on as if never
interrupted. The governing invariant is stronger than Doc 06's minimum ("a
valid continuation"): in this deterministic build, **a run resumed from a
cycle-boundary snapshot is byte-identical to the uninterrupted run** — the most
honest, testable form of "exactly the state captured."

### User Story 1 - Nothing learned is ever lost (Priority: P1)

A researcher snapshots a running agent at a consolidation boundary, kills the
process, restores from the snapshot, and continues — ending with exactly the
summary the uninterrupted run would have produced.

**Why this priority**: This is the feature's reason to exist and the strongest
proof that the snapshot captures *all* behavior-affecting state (Doc 06 §2's
"no part of learned state lives only in transient memory").

**Independent Test**: Run a seed uninterrupted; run the same seed with a
snapshot at cycle k, restore into a fresh engine, resume; byte-compare the two
final summaries.

**Acceptance Scenarios**:

1. **Given** a snapshot taken at a consolidation-cycle boundary, **When** a
   fresh engine restores it and resumes, **Then** the final run summary is
   byte-identical to the uninterrupted run's.
2. **Given** a curiosity-mode run (drive bookkeeping in play), **When**
   snapshotted and resumed, **Then** the continuation is byte-identical too —
   drive state survives.
3. **Given** any restored system, **When** it resumes, **Then** the first event
   is a fresh sensing start (no stale in-flight step is replayed).

---

### User Story 2 - Snapshots are safe artifacts (Priority: P1)

Snapshots are atomic (a reader never sees a partial write), versioned (an
unsupported format is rejected with a clear error, never silently
misinterpreted), and carry the metadata needed to pick one (timestamp, step,
cycle, population, format version).

**Why this priority**: A corrupt or misread snapshot is worse than no snapshot
— it silently poisons the continuation. Equal-P1 because US1 is meaningless
without it.

**Independent Test**: Interrupt a write and confirm no partial snapshot is
listed/readable; doctor a blob's version and confirm restore refuses with a
clear error.

**Acceptance Scenarios**:

1. **Given** a snapshot write in progress, **When** the store is listed or
   read, **Then** the incomplete snapshot is never returned.
2. **Given** a blob whose format version is unsupported, **When** restore is
   attempted, **Then** it fails with a clear error naming the version.
3. **Given** any stored snapshot, **When** its metadata is listed, **Then**
   timestamp, step counter, cycle counter, population size, and format version
   are present, newest first.

---

### User Story 3 - The validated behavior is untouched (Priority: P1)

Persistence is opt-in: with no store configured (the default), every existing
mode — the T1–T6 suite, determinism, scale, scan, agency — behaves and
serializes byte-identically to the validated build, and still writes nothing to
disk but requested reports.

**Why this priority**: The regression gate is the project's spine; feature 001's
FR-011 (only report summaries on disk) must keep holding for every validation
mode.

**Independent Test**: The pinned reference-seed values reproduce exactly; a
default-config run creates no files.

**Acceptance Scenarios**:

1. **Given** the default configuration, **When** any existing mode runs, **Then**
   behavior and summary bytes are identical to the validated build and no
   snapshot files are created.
2. **Given** snapshotting enabled at a cadence, **When** the run executes,
   **Then** snapshots appear only at consolidation-cycle boundaries (never
   mid-step — the Doc 06 C4 consistency rule).

---

### User Story 4 - Restore refuses an incompatible body (Priority: P2)

Restoring a snapshot into a system whose configuration disagrees on the
body-defining facts (observation width, action count) fails with a clear error
rather than loading an inconsistent state.

**Why this priority**: Doc 06 §5 makes this mandatory; it is cheap and prevents
the least-debuggable failure mode.

**Independent Test**: Snapshot at one `obs_dim`, attempt restore under another,
confirm the clear error.

**Acceptance Scenarios**:

1. **Given** a snapshot from a body with `obs_dim=10`, **When** restore is
   attempted with `obs_dim=60`, **Then** restore fails naming the mismatch.
2. **Given** a compatible configuration, **When** restore runs, **Then** it
   succeeds and US1 holds.

---

### Edge Cases

- **Snapshot cadence 0 (default)**: persistence fully off; no store required,
  no files written.
- **Empty population**: a snapshot taken before any frame is born restores to
  an empty-population system that continues normally (zero-start rules re-birth).
- **Restore from the newest vs a named snapshot**: the store lists newest
  first; the restorer may pick any listed id.
- **Delete**: removing a snapshot makes it unlistable and unreadable; other
  snapshots are unaffected.
- **Policy state**: shipped policies are stateless; the snapshot records the
  policy mode so a restored run uses the same policy. (A future stateful policy
  adds its state to the blob under the same rule: if it affects future
  behavior, it is in the snapshot.)
- **Tool registry**: does not exist yet in this build; the format reserves the
  field so its later addition is a version bump, not a redesign.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The complete learned state MUST be serializable into one snapshot
  blob and restorable from it: configuration in force, the full frame
  population (identity, dims, ages, candidate flags, EMAs, all weights), drive
  bookkeeping (error windows, observation memory) when present, run counters
  (step, cycle, next frame id), telemetry accumulators needed for the run's
  summary, and the random generator state.
- **FR-002**: A snapshot MUST be taken only at a consistent point: a
  consolidation-cycle boundary or a clean stop — never mid-step (C4).
- **FR-003**: Restoring a cycle-boundary snapshot and resuming MUST produce a
  byte-identical continuation of the uninterrupted run (the buildable-strength
  form of Doc 06 §1's "valid continuation"); the first event after restore is a
  fresh sensing start.
- **FR-004**: Snapshot writes MUST be atomic from the reader's perspective:
  `read`/`list` never return a partially written snapshot.
- **FR-005**: Every blob MUST carry a format version; restore MUST reject an
  unsupported version with a clear error.
- **FR-006**: The SnapshotStore seam MUST expose `write(blob, metadata) → id`,
  `read(id) → blob`, `list() → [{id, metadata}]` newest first, and
  `delete(id)`; metadata MUST include timestamp, step counter, cycle counter,
  population size, and format version. The store treats blobs as opaque.
- **FR-007**: One durable backend (local filesystem) MUST be built; the seam
  MUST accept substitutes (e.g. in-memory) without changes elsewhere. The
  event-log and pose-index seams remain defined-not-built (Doc 06 §4.2).
- **FR-008**: Restore MUST validate body compatibility (observation width,
  action count) against the booting configuration and fail clearly on mismatch.
- **FR-009**: Persistence MUST be opt-in: default configuration takes no
  snapshots, writes no files, and leaves every existing mode's behavior and
  summary bytes identical to the validated build.
- **FR-010**: When enabled, snapshotting MUST occur at the configured cadence
  (`snapshot_every_n_cycles`) during the slow loop, and the run MUST be
  resumable from any snapshot it produced.

### Key Entities

- **Snapshot blob**: the single serialized artifact holding all Section-2 state
  plus the format version.
- **Snapshot metadata**: the pick-one-without-opening-it record (timestamp,
  step, cycle, population, version).
- **SnapshotStore**: the durable seam (write/read/list/delete); filesystem
  default, substitutable.
- **Restored state**: the deserialized form an engine resumes from.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For both the pinned random baseline and curiosity mode, a run
  snapshotted at a cycle boundary and resumed in a fresh engine ends with a
  summary byte-identical to the uninterrupted run.
- **SC-002**: An interrupted write is never visible to `read`/`list`; a doctored
  format version is rejected with an error naming it.
- **SC-003**: The reference seed reproduces the validated build's values with
  persistence code present and disabled; a default-config run creates zero
  files.
- **SC-004**: A body-incompatible restore fails with an error naming the
  mismatched field.
- **SC-005**: Snapshot metadata lists newest first and carries all five required
  fields; delete removes exactly the targeted snapshot.

## Assumptions

- The synthetic validation world is the environment; world state is *not*
  system state (Doc 06 §2) and is not snapshotted. Byte-identical continuation
  is achievable regardless because consolidation boundaries fall between
  episodes: the next act after restore is a fresh episode reset, exactly as in
  the uninterrupted run.
- The random generator state is system state ("state that affects future
  behavior" — Doc 06 §2 MUST), even though Doc 06 §1 does not demand replayable
  futures; including it is what upgrades "valid continuation" to the testable
  byte-identical form.
- Blob bytes need not be identical across snapshot writes (archives may embed
  timestamps); the byte-identity requirement applies to the *continuation
  summaries*, which is what the determinism machinery already compares.
- The harness commands stay snapshot-free; persistence is exercised through the
  engine API and its own tests. No new CLI command is needed for this feature.
- Doc 06's tool registry does not exist in this build; the blob format reserves
  the field as empty.
