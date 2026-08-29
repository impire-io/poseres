# Changelog

All notable changes to this project are documented here. The format
follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); the
versioning promise is defined in
[Doc 0008](hq/02-DESIGN/0008-public-api-versioning.md) and enforced by
the surface guard (`tests/contract/test_public_surface.py`).

## [Unreleased]

## [2.4.0] — 2026-08-29

### Added

- **Process recipes on `RecipeMemory`** (feature 046; episode 0120,
  design 0021 rung 2): `process` (keyword-only, off by default,
  bit-exact off; requires `label_index`). A demonstration with no
  pocket gain but a strictly positive label stores as a process
  recipe — terminal = the applauded observation by the existing
  max-label rule, steps = the walked path through it, the record
  marked `process` (new defaulted field on `Recipe`). Gainless
  without applause still stores nothing; the acquisition door is
  untouched. Worth is the shipped label/deficit grammar (features
  041/042) and the policy is unchanged — pointing, holding, and
  place-keyed futility (045) treat both recipe kinds identically.
  Closes the measured absence of episode 0120: fifteen taught lap
  demonstrations, zero storable as behavior.

## [2.3.0] — 2026-08-29

### Added

- **Place-keyed futility on `RecipePolicy`** (feature 045; episode
  0120, design 0021 rung 1): `futility_k` / `futility_w`
  (keyword-only, `futility_k=0` off by default, bit-exact off — RNG
  stream included). A subgoal pointer that makes no progress for
  `futility_k` followed steps poisons the pointed place for
  `futility_w` selection steps: every recipe currently pointing
  there is ineligible together, with none eligible the policy is
  exactly its parent, and expiry is a clean peek — the re-check
  cadence emerges from the constants. Watch counters
  `fatigue_events` / `revive_events`. The measured provenance: the
  rig prototype (K=200/W=800) abolished a 4,672-step futile press
  and produced the larder arena's first brain-driven crossings; both
  per-recipe forms are recorded failure modes (boundary thrash at
  556 events, cohort fallback).

## [2.2.0] — 2026-08-16

### Changed

- **The survival body is the default anatomy** (feature 044; episode
  0104, design 0015): `c1_anatomy()` now returns the measured
  operating point that lives — the property body plus the mouth,
  distal senses, flood, and worth channel (obs 86 / 13 actions) —
  and the bridge wire defaults to match (SURVIVAL on,
  FLOOD=intrusion, AIM=worth when unset). Every explicit flag keeps
  its exact prior meaning; `survival=False` / `SURVIVAL=0` is the
  pre-044 property body (the feature-033 default-change precedent).

## [2.1.0] — 2026-08-16

### Added

- **Commitment** (feature 043; episode 0101, design 0014):
  `commit_kappa` / `explore_defers_holds` on
  `CompletionItchPolicy`/`RecipePolicy` — incumbency while sensed
  progress advances (dying with its intention at a progress
  collapse) and exploration deferring to a live hold. Defaults
  off, bit-exact with v2.0.0 (RNG stream included). Measured: the
  parked-geometry pair went 0 → 10 completed digs with a full
  forage chain first-eating at step 333; free-roam, the committed
  stack produced the record's first sustained self-feeding life.

### Changed

- **License**: MIT → [Sustainable Use License](LICENSE) (fair-code).
  Free to use, modify, and self-host for internal or non-commercial
  use; offering PRA to others as a paid product or service now requires
  an agreement (see [impire.io/license](https://impire.io/license/)).
  Versions up to and including v1.1.0 remain MIT.

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
