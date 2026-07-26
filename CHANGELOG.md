# Changelog

All notable changes to this project are documented here. The format
follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); the
versioning promise is defined in
[Doc 0008](hq/02-DESIGN/0008-public-api-versioning.md) and enforced by
the surface guard (`tests/contract/test_public_surface.py`).

## [1.1.0] — 2026-07-27

Phase D lands in parallel: the frozen surface grows additively.

### Added

- **Shareable brains** (feature 037): `pra-brain` export / inspect /
  import — a snapshot as a portable, sha256-verified, deterministic
  artifact wrapping the untouched blob; cross-person load verified by
  test (resume byte-identical). Public surface +7 elements and a fifth
  CLI (Doc 0008 updated in the same change).
- **Docs site** (feature 036): Pages workflow building from `docs/` +
  `hq/02-DESIGN` at deploy time, worlds gallery with recorded FAILs
  stated, rot-guard test in the gate. Deploy awaits the owner's Pages
  enablement.
- **Contribution surface** (feature 038): CONTRIBUTING.md against the
  frozen seams, issue/PR templates, labels + four API-verified
  good-first-issue drafts (issue creation is the owner's act).

### Notes

- Behavior of existing modes unchanged (constitution I); the reference
  suite reproduces its byte-frozen values.
- Stale tracked `src/pra.egg-info/` metadata untracked (was shadowing
  the installed version in `pip list`).

## [1.0.0] — 2026-07-26

The public surface freezes.

### Added

- **The compatibility promise**: every element listed in Doc 0008 —
  the world/body seam, anatomy, drives, persistence, the run surface,
  the CLI tools, and the `pra.v1.>` subject space — is stable for all
  of v1.x. Patch = fixes; minor = additive/opt-in only; removals at a
  major only, after a deprecation with at least one minor of grace.
  Behavior of existing modes is byte-frozen within v1.x (constitution
  I): the validated reference suite reproduces its recorded values on
  every release.
- The surface guard: the public API is declared in
  `tests/contract/surface_inventory.py` and enforced by the gate,
  including a demonstrated failure mode for removed symbols and
  renamed parameters.
- `pra.__version__` (single-sourced from the package metadata) and
  lazy top-level re-exports `pra.Config`, `pra.Engine`.
- The deprecation mechanism: uniform notices naming the replacement
  and the earliest removal release.

### Notes

- Everything not listed in Doc 0008 is internal by default:
  importable, unpromised, free to move.
- No behavior changed in this release. The validated behavior remains
  byte-frozen under the pinned baseline (T1–T6 reference values
  reproduce exactly).
