# Tasks: Shareable Brains

**Input**: Design documents from `/specs/037-shareable-brains/`
**Prerequisites**: plan.md, spec.md, quickstart.md

**Tests**: The spec's success criteria demand enforcement tests (the
exit-criterion resume test, the tamper refusal, the version refusal,
the manifest-only inspect) — these are deliverables, not TDD ceremony,
and are tasked as such.

**Organization**: grouped by user story; US1 alone is a viable MVP
(the library round-trip with the byte-identical resume), US2 adds the
trust checks, US3 puts the flow on the command line.

## Phase 1: Setup

- [X] T001 Confirm branch `037-shareable-brains` is current and the full gate is green before any change: `./.venv/bin/ruff format --check . && ./.venv/bin/ruff check . && ./.venv/bin/pytest -q` (zero skips) — the byte-frozen baseline this feature must not move

## Phase 2: Foundational (blocking all stories)

- [X] T002 Create `src/pra/persistence/portable.py`: the container format (zip, `manifest.json` + `snapshot.bin`, epoch-pinned member times), `PORTABLE_FORMAT_VERSION`, `PortableIntegrityError`, `PortableVersionError`, and the manifest-key contract — module docstring documents the format (FR-003)

## Phase 3: User Story 1 — person A publishes, person B loads and runs (P1) 🎯 MVP

**Goal**: export/import round-trips the blob byte-untouched; a resumed
run from an imported artifact is byte-identical to the uninterrupted
run.

**Independent Test**: library-level export → import → resume equals
uninterrupted serialize (the repo's resume-exactness pattern).

- [X] T003 [US1] Implement `export_brain(path, *, blob | store [+ snapshot_id], note, created_at)` in `src/pra/persistence/portable.py`: resolve the blob (newest snapshot by default), derive manifest facts through the existing `decode` (wrap, never reimplement — FR-001/FR-002/FR-007), write the zip atomically (temp + `os.replace`), return the manifest
- [X] T004 [US1] Implement `import_brain(path) -> (blob, manifest)` (verification order: container version → snapshot format version → sha256; returns the untouched blob; writes nothing) and `inspect_brain(path) -> manifest` (reads only `manifest.json`, never the blob — FR-004/FR-005)
- [X] T005 [US1] Integration test `tests/integration/test_shareable_brains.py`: person A runs a small engine with a `FileSnapshotStore` in tmpdir A, exports the newest snapshot; person B imports into tmpdir B and resumes via the existing resume path; resumed serialize is byte-identical to the uninterrupted run (SC-001, library level); blob-vs-store export produce byte-identical artifacts (reproducibility)

**Checkpoint**: US1 alone = a shareable brain that provably runs for its recipient

## Phase 4: User Story 2 — a recipient can trust what they load (P2)

**Goal**: damage and version mismatch are refused loudly; inspect
never touches the brain.

**Independent Test**: flipped blob byte → integrity refusal; unknown
container/snapshot versions → version refusal; inspect works on a file
with a corrupt blob.

- [X] T006 [US2] Tests in `tests/integration/test_shareable_brains.py`: tampered `snapshot.bin` → `PortableIntegrityError` and nothing written (SC-002); unknown `portable_format_version` → `PortableVersionError` on import *and* inspect; unsupported `snapshot_format_version` → `PortableVersionError` on import while inspect still returns the manifest; missing member / not-a-zip → `PortableIntegrityError`
- [X] T007 [US2] Test that `inspect_brain` matches the exporting store's metadata (step, cycle, population, format version) and config dims, and still answers on a corrupt-blob file — the proof it never deserializes (SC-003)

**Checkpoint**: loading a stranger's file is refuse-or-exact, never a guess

## Phase 5: User Story 3 — the handoff works from the command line (P3)

**Goal**: `pra-brain export | inspect | import`, documented in --help;
import writes a directory the existing store resumes from.

**Independent Test**: the person-A/person-B flow of T005 driven
entirely through `pra-brain`, same byte-identical resume; tampered
import exits nonzero with the error on stderr.

- [X] T008 [US3] Create `src/pra/persistence/brain_cli.py` (`main(argv) -> int`): subcommands `export` (--store, --out, --snapshot, --note; injects UTC created-at), `inspect` (prints the manifest as JSON), `import` (file, --store; reconstructs store metadata from the manifest, writes via `FileSnapshotStore`); loud errors to stderr, exit 1 on refusal; --help documents the flow (FR-006)
- [X] T009 [US3] Add `pra-brain = "pra.persistence.brain_cli:main"` to `pyproject.toml [project.scripts]`; re-run `pip install -e ".[gym]"` so the entry point resolves for the surface guard
- [X] T010 [US3] CLI tests in `tests/integration/test_shareable_brains.py`: the exit criterion end-to-end through `brain_cli.main` (SC-001 as shipped), inspect prints valid JSON equal to the manifest, tampered import returns nonzero with stderr naming the refusal and the target store stays empty

**Checkpoint**: the roadmap sentence works as spoken — one file, two people, no Python

## Phase 6: Public-surface duty & landing (house rules: same merge)

- [X] T011 Add the 7 new public names to `tests/contract/surface_inventory.py` (portable constant, two errors, three functions with promised params, the `pra-brain` CLI) and the matching rows to `hq/02-DESIGN/0008-public-api-versioning.md` (Persistence + Operational tables; CLI count updated); the surface guard must pass bidirectionally (FR-008)
- [X] T012 Full gate green: `./.venv/bin/ruff format --check . && ./.venv/bin/ruff check . && ./.venv/bin/pytest -q` — zero skips, byte-frozen baseline untouched (SC-004)
- [ ] T013 Landing (coordinator, with the merge): roadmap Phase D item marked landed, journey episode via `/journey-log`, CHANGELOG entry under the v1.1.0 cut across all Phase D landings — deliberately not done on this branch to avoid cross-feature conflicts

## Dependencies

- T002 blocks T003/T004; T003+T004 block T005.
- US2 (T006/T007) needs T003/T004; parallel with US3.
- US3: T008 needs T003/T004; T009 with T008; T010 needs T008+T009.
- T011 needs the final shape of T003/T004/T008/T009; T012 last on the
  branch; T013 at merge time (coordinator).

## Implementation Strategy

MVP = Phases 1–3 (US1): the provably-running shared brain. US2 and US3
are small increments on top; the one review-heavy artifact is the
manifest contract (spec Key Entities), frozen before the CLI is built
on it.
