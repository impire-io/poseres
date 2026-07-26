# Implementation Plan: Shareable Brains

**Branch**: `037-shareable-brains` | **Date**: 2026-07-27 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/037-shareable-brains/spec.md`

## Summary

Wrap the existing snapshot blob in a boring, documented portable
container: a zip with `manifest.json` (sha256 of the blob, snapshot
format version, pra version, body dimensions, run position, provenance
note, caller-injected created-at) and `snapshot.bin` (the blob,
byte-untouched). A new module `pra.persistence.portable` provides
`export_brain` / `import_brain` / `inspect_brain`; a new console
command `pra-brain` drives the person-to-person flow. Import verifies
checksum and format versions before anything else and writes into a
directory the existing `FileSnapshotStore` serves for resume. The exit
criterion lands as an integration test: person B's resumed run is
byte-identical to the uninterrupted run. Everything is additive — the
snapshot wire format, FORMAT_VERSION, and every existing module are
untouched.

## Technical Context

**Language/Version**: Python 3.12+ (`requires-python >= 3.12`)
**Primary Dependencies**: stdlib only for the new code (zipfile, hashlib, json, argparse) + the existing pra persistence modules; no new runtime dependencies
**Storage**: one zip file per exported brain; the existing `FileSnapshotStore` directory on import
**Testing**: pytest (repo gate: `ruff format --check && ruff check && pytest -q`, zero skips)
**Target Platform**: anywhere the package installs (library + CLI)
**Project Type**: library with CLI entry points
**Performance Goals**: N/A — export/import are I/O-bound one-shot operations
**Constraints**: constitution I — no existing mode's RNG stream, behavior, or serialized summary may move; the blob is wrapped byte-for-byte, never re-encoded; the container bytes are a pure function of (blob, manifest) so republishing the same brain is reproducible
**Scale/Scope**: one new module (~150 lines), one CLI module, one pyproject scripts line, one integration test file, 7 surface-inventory entries + the matching Doc 0008 rows

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Reference-Preserving Forever — PASS (by construction).** No
  existing module is modified. The portable layer wraps
  `pra.persistence.snapshot.encode`/`decode` and `FileSnapshotStore`;
  the blob inside the artifact is the store's bytes verbatim, checked
  by sha256. FORMAT_VERSION is read, never redefined. No RNG, no
  float work, no import-order change for existing modes; the full
  T1–T6 gate proves it as always.
- **II. Honest Measurement — PASS.** Exit criteria pre-written
  (SC-001..004); the refusal paths are demonstrated by tests (flipped
  byte, unknown versions), not asserted; the checksum's trust model
  (integrity, not signature) is stated openly in spec and docs.
- **III. Diagnose Before Fixing — N/A** (no behavioral problem in
  scope; any behavioral surprise during implementation stops the work).
- **IV. Research Gates Before Showcase Spends — PASS.** Roadmap
  Phase D product hygiene; no research gate consumed. The shareable
  artifact showcases a measured capability (byte-exact resume,
  episode 0041; transfer value of shared brains, feature 028).
- **V. Never Lose the Instrument Panel — N/A** (no worlds).
- **VI. All-Green Quality Gate — PASS.** The gate grows (the
  shareable-brains integration tests + 7 guarded surface entries) and
  stays all-green, zero skips; signed commits.

**Post-design re-check (after Phase 1)**: unchanged — PASS. The design
adds no runtime coupling: the portable module imports persistence, the
CLI imports the portable module, nothing imports either.

## Project Structure

### Documentation (this feature)

```text
specs/037-shareable-brains/
├── plan.md              # This file
├── spec.md              # Feature specification
├── quickstart.md        # The user-facing flow (usage doc lives here + in --help)
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
src/pra/persistence/
├── portable.py         # NEW: the portable container — export_brain / import_brain /
│                       #      inspect_brain, PORTABLE_FORMAT_VERSION, the two errors
└── brain_cli.py        # NEW: ``pra-brain`` — export / inspect / import subcommands

tests/integration/
└── test_shareable_brains.py  # NEW: exit criterion (CLI person-A/person-B, byte-identical
                              #      resume), tamper refusal, version refusal, manifest-only inspect

tests/contract/
└── surface_inventory.py      # gains 7 entries (portable module + pra-brain)

hq/02-DESIGN/
└── 0008-public-api-versioning.md  # gains the matching table rows (surface duty)

pyproject.toml          # gains: pra-brain = "pra.persistence.brain_cli:main"
```

**Structure Decision**: the portable layer lives inside
`pra.persistence` next to the modules it wraps — it is the persistence
surface's outward face, not a new component. The CLI is its own module
so the library part stays importable without argparse in the way. Usage
documentation goes in this spec's quickstart.md and the CLI `--help`
(docs/ pages belong to the sibling docs-site feature; creating them
here would conflict).

## Design decisions

- **Container**: zip, ZIP_STORED (the blob is already a compressed
  npz), exactly two members. Member timestamps are pinned to the zip
  epoch so the artifact's bytes are a pure function of
  (blob, manifest) — same brain + same manifest = same file.
- **Manifest facts come from the blob** via the existing `decode`
  (wrap, don't reimplement): step = obs_steps, cycle = cycles_done,
  population = the last population_by_cycle entry (the engine appends
  it at the same C4 safe point that writes the snapshot, so it equals
  the store metadata's population), dims from the frame store (so a
  mid-run resize is reported honestly). A successful decode also
  proves the snapshot format version is the supported one — export
  cannot publish a blob this library couldn't load.
- **created_at is caller-injected** (required keyword): the library
  never reads the clock; the CLI injects UTC now. Keeps the library
  deterministic and the artifact reproducible.
- **Two loud errors**, mirroring the snapshot module's pair:
  `PortableIntegrityError` (hash mismatch, damaged/missing members)
  and `PortableVersionError` (unknown container version, unsupported
  snapshot format version). Inspect refuses only on unknown
  *container* version — inspecting a brain from a newer library is
  exactly what inspect is for.
- **Import returns (blob, manifest) and writes nothing**; the CLI's
  import subcommand reconstructs store metadata from the manifest
  (timestamp = import wall time; step/cycle/population/format_version
  from the manifest) and writes through `FileSnapshotStore.write`, so
  the snapshot id (`snap-<step>-<cycle>`) matches person A's store.

## Complexity Tracking

No constitution violations; table not needed.
