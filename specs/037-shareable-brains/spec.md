# Feature Specification: Shareable Brains

**Feature Branch**: `037-shareable-brains`
**Created**: 2026-07-27
**Status**: Draft
**Input**: User description: "Shareable brains (roadmap Phase D): snapshots as portable artifacts ('here's my rover brain after 100k steps — load it'). Exit criterion from the roadmap: a snapshot published by one person loads and runs for another, verified. The snapshot wire format and FORMAT_VERSION are untouched (constitution I) — the portable artifact WRAPS the existing blob, never reimplements it."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Person A publishes a brain; person B loads and runs it (Priority: P1)

Person A has run a brain with snapshotting enabled and wants to hand
the result to someone else as one file: "here's my rover brain after
100k steps — load it." Person B receives that single file, loads it
into their own snapshot store, and resumes the run — getting exactly
the continuation person A would have gotten.

**Why this priority**: This is the roadmap's exit criterion verbatim.
Everything else in this feature exists to make this handoff safe and
boring.

**Independent Test**: Run a small engine with a file store in one
directory ("person A"), export the newest snapshot to a portable
file, import it in a separate directory ("person B"), resume through
the existing resume path, and assert the resumed run's serialized
summary is byte-identical to an uninterrupted run (the repo's
established resume-exactness pattern).

**Acceptance Scenarios**:

1. **Given** a store with at least one committed snapshot, **When**
   person A exports it, **Then** exactly one portable file exists
   containing the snapshot blob byte-untouched plus a manifest
   stating what it is.
2. **Given** the portable file, **When** person B imports it into an
   empty directory, **Then** that directory is a valid snapshot store
   holding the same snapshot under the same id, and resuming from it
   is byte-identical to the uninterrupted run.
3. **Given** the export and the import, **When** either side checks
   the blob, **Then** it is the exact bytes the original store held —
   the wrapper adds a container, never a re-encoding.

---

### User Story 2 - A recipient can trust what they load (Priority: P2)

Portable files travel over networks and sit on disks. Person B must
be able to (a) see what a file claims to be without loading the brain
at all, and (b) be refused loudly when the file is damaged, tampered
with, or from a format this library does not understand — never a
silent misload.

**Why this priority**: Sharing is only useful if loading a stranger's
file is safe. A corrupted brain that loads quietly would burn the
first person it happens to.

**Independent Test**: Flip one byte of the enclosed blob and verify
import refuses with an integrity error naming the mismatch; rewrite
the container's format version to an unknown value and verify both
import and inspect refuse; verify inspect returns the manifest
without ever reading the brain (it still works on a file whose blob
is corrupt).

**Acceptance Scenarios**:

1. **Given** a portable file whose blob bytes were altered after
   export, **When** person B imports it, **Then** the import fails
   with a loud integrity error and writes nothing into their store.
2. **Given** a portable file with an unknown container format
   version, **When** anyone imports or inspects it, **Then** they get
   a loud version error, not a guess.
3. **Given** a portable file whose enclosed snapshot format version
   is one this library does not support, **When** person B imports
   it, **Then** the import refuses loudly (inspect still shows the
   manifest — that is the point of inspect).
4. **Given** any portable file, **When** person B inspects it,
   **Then** they see the manifest (provenance, dimensions, step /
   cycle / population, versions, checksum) and the brain is never
   deserialized.

---

### User Story 3 - The handoff works from the command line (Priority: P3)

Neither person should need to write Python to share a brain. A
console command exports, inspects, and imports portable files, and
its help text documents the whole flow.

**Why this priority**: The roadmap's sentence is spoken between
people, not processes. The CLI is the shape the handoff actually
takes; it is P3 only because it is a thin shell over stories 1 and 2.

**Independent Test**: Drive the person-A/person-B flow of story 1
entirely through the CLI subcommands and verify the same
byte-identical resume; verify inspect prints the manifest; verify a
tampered file makes import exit nonzero with the error on stderr.

**Acceptance Scenarios**:

1. **Given** a store directory, **When** person A runs the export
   subcommand, **Then** the newest snapshot (or a named one) becomes
   one portable file and the command reports what it published.
2. **Given** a portable file, **When** person B runs the import
   subcommand with a target directory, **Then** the directory is
   usable by the existing file snapshot store for resume.
3. **Given** a portable file, **When** anyone runs the inspect
   subcommand, **Then** the manifest prints as JSON and nothing else
   is read.
4. **Given** `--help` on the command or any subcommand, **Then** the
   usage of the whole flow is documented.

---

### Edge Cases

- Export from a store with no committed snapshot: a clear error, not
  an empty artifact.
- Export of a named snapshot id that does not exist: a clear error.
- A portable file that is not a zip archive at all, or is missing a
  member: a loud integrity error on import.
- Importing into a directory that does not exist yet: the store
  creates it (existing store behavior); importing the same file twice
  overwrites the same snapshot id with identical bytes (idempotent).
- The manifest and the blob disagree (hash mismatch): refusal — the
  blob never gets a chance to be decoded.
- Resume-side guards are unchanged and still apply after import: seed
  mismatch and body incompatibility are refused by the existing
  resume path, not re-implemented here.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The project MUST provide an export operation producing a
  single portable file from either a raw snapshot blob or a store +
  snapshot id (defaulting to the newest snapshot), containing the
  blob byte-untouched plus a manifest.
- **FR-002**: The manifest MUST state: a sha256 checksum of the blob,
  the enclosed snapshot's format version, the exporting library
  version, the brain's body dimensions (obs_dim, n_actions), the run
  position (step, cycle, population), an optional free-text
  provenance note, and a created-at timestamp injected by the caller
  (the library never reads the clock).
- **FR-003**: The portable container format MUST be boring and
  documented: a zip archive with exactly two members, `manifest.json`
  and `snapshot.bin`, carrying its own container format version in
  the manifest.
- **FR-004**: The import operation MUST verify the checksum and both
  format versions before returning the blob, refusing loudly on hash
  mismatch, unknown container version, or unsupported snapshot format
  version — and MUST NOT write anything on refusal.
- **FR-005**: An inspect operation MUST return the manifest without
  ever deserializing the brain (it reads only the manifest member).
- **FR-006**: A console command MUST expose export / inspect / import;
  import MUST write into a directory usable by the existing file
  snapshot store for resume, reconstructing the store metadata from
  the manifest.
- **FR-007**: The feature MUST be strictly additive on the existing
  persistence surface: the snapshot wire format and FORMAT_VERSION
  are untouched, existing modules are unmodified, and the existing
  encode/decode is wrapped, never reimplemented (constitution I).
- **FR-008**: All new public names (module functions, errors,
  constants, the CLI) MUST be added to the surface inventory and Doc
  0008 per the v1 public-surface duty (feature 035); the surface
  guard must pass.

### Key Entities

- **Portable brain artifact**: one zip file; members `manifest.json`
  (UTF-8 JSON, sorted keys) and `snapshot.bin` (the untouched blob).
- **Manifest**: container format version, blob sha256, snapshot
  format version, pra version, obs_dim, n_actions, step, cycle,
  population, note, created_at.
- **Errors**: an integrity error (hash mismatch, damaged container)
  and a version error (unknown container or unsupported snapshot
  format), both loud.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001** (the roadmap exit): a snapshot published by one person
  loads and runs for another — verified by a test in which person B's
  resumed run serializes byte-identical to the uninterrupted run,
  with export and import performed through the shipped CLI.
- **SC-002**: a portable file with one flipped blob byte is refused on
  import with an integrity error, and the target store receives
  nothing.
- **SC-003**: inspect returns a manifest that matches the store
  metadata (step, cycle, population, format version) and the config
  dimensions, and does so without deserializing the brain (verified
  on a file whose blob member is corrupt).
- **SC-004**: the full gate is green with the new surface entries
  guarded: format check, lint, all tests, zero skips — including the
  byte-frozen baseline (constitution I evidence that nothing moved).

## Assumptions

- **Trust model**: the checksum is an integrity check against damage
  and accidental corruption, not a cryptographic signature against a
  motivated forger. Signing artifacts is out of scope and would be a
  separate feature; the manifest's honesty about this lives in the
  documentation.
- **Seed and config travel inside the blob**: the resume path already
  requires the resuming caller to supply the same seed and a
  compatible body, and refuses otherwise (feature 003). The portable
  layer adds no second enforcement; the manifest carries dimensions
  for human triage only.
- **Newest-first default**: "the brain after 100k steps" is the
  newest snapshot; export defaults to it, with an explicit id as the
  override.
- **No version bump here**: the coordinator cuts v1.1.0 across all
  Phase D landings; this feature adds surface but does not touch the
  package version.
