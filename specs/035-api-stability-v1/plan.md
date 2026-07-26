# Implementation Plan: API Stability & v1.0

**Branch**: `035-api-stability-v1` | **Date**: 2026-07-26 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/035-api-stability-v1/spec.md`

## Summary

Freeze the public surface as v1.0: a single authoritative inventory
classifying every user-reachable element (the four seam families plus
the config/entry surface, the shipped CLI tools, and the documented
subject space) as public or internal; a versioning policy that restates
constitution I as a compatibility promise; a deprecation policy with a
visible-notice mechanism; an automated surface guard in the gate; and
the tagged, changelogged v1.0 release. Everything is additive — this
feature freezes surfaces, not behavior, and ships zero behavior change
to any existing mode.

## Technical Context

**Language/Version**: Python 3.12+ (`requires-python >= 3.12`, episode 0026)
**Primary Dependencies**: stdlib + numpy (core); packaging via setuptools; no new runtime dependencies
**Storage**: N/A (documents, tests, metadata only)
**Testing**: pytest (repo gate: `ruff format --check && ruff check && pytest -q`, zero skips)
**Target Platform**: anywhere the package installs (library + CLI)
**Project Type**: library with CLI entry points
**Performance Goals**: N/A — no runtime paths change
**Constraints**: constitution I — byte-frozen T1–T6 under the pinned baseline; every addition must be import-time-safe (no RNG, no float work, no reordering); the deprecation helper must be dead code for all existing modes
**Scale/Scope**: one inventory (~40–70 elements expected across 6 families), one new design doc, one contract-test module, version metadata, changelog, tag

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Reference-Preserving Forever — PASS (by construction).** All
  changes are docs, tests, package metadata, top-level re-exports
  (import-time only), and an unused-by-core deprecation helper. No
  existing mode's RNG stream, behavior, or serialized summaries can
  move. The full T1–T6 gate proves it as always.
- **II. Honest Measurement — PASS.** Exit criteria pre-written in the
  spec (SC-001..005); the surface guard's failure mode is demonstrated
  (a test removing a public element must fail the guard), not asserted.
- **III. Diagnose Before Fixing — N/A** (no behavioral problem in
  scope; any behavioral surprise during implementation stops the work).
- **IV. Research Gates Before Showcase Spends — PASS.** Product
  hygiene, roadmap Phase D (episode 0060); no demo, no research gate
  consumed.
- **V. Never Lose the Instrument Panel — N/A** (no worlds).
- **VI. All-Green Quality Gate — PASS.** The gate grows (surface
  guard) and stays all-green, zero skips; signed commits.

**Post-design re-check (after Phase 1)**: unchanged — PASS. The design
adds no runtime coupling: the inventory is data, the guard is a test,
the helper is opt-in.

## Project Structure

### Documentation (this feature)

```text
specs/035-api-stability-v1/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── public-surface.md  # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit-tasks — NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
src/pra/
├── __init__.py             # gains: __version__ + curated public re-exports (additive)
└── _deprecation.py         # NEW: deprecated() helper — notice text names replacement + removal horizon

tests/contract/
├── surface_inventory.py    # NEW: THE single source of truth — the declared public surface
└── test_public_surface.py  # NEW: the surface guard (import + shape checks; failure demo)

hq/02-DESIGN/
└── 0008-public-api-versioning.md  # NEW design doc: the public API, semver promise, deprecation policy

CHANGELOG.md                # NEW: v1.0.0 entry stating the promise
README.md                   # gains: a Public API & versioning section linking Doc 0008
pyproject.toml              # version 0.1.0 → 1.0.0 (at release step)
```

**Structure Decision**: single-project library layout (the existing
one). The inventory lives in `tests/contract/surface_inventory.py` as
executable data — the guard test imports it, Doc 0008 documents it,
and one test asserts doc/inventory agreement so the two cannot drift.

## Complexity Tracking

No constitution violations; table not needed.
