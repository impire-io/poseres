# Implementation Plan: Continuous Operation

**Branch**: `008-continuous-operation` | **Date**: 2026-07-13 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/008-continuous-operation/spec.md`

## Summary

Build ROADMAP B3: an opt-in `Config.episode_mode="continuous"` in which
the engine boots the world exactly once and segments the unbroken stream
into **virtual episodes** — the episode loop changes in exactly one place
(`obs = world.reset()` becomes `obs = pending`, with the trailing
observation of each span carried forward), and every episode-keyed
mechanism (chain break, fair-judge window, lifetime-cap projection,
warmup, consolidation cadence) lands at virtual boundaries with zero
changes to the store, scorer, drives, or bodies (research R2/R3). The
design surfaced one real problem and answers it: continuous
snapshot/resume cannot ride the world-from-seed rule, so an **optional
world-state capture protocol** (`state_dict`/`load_state_dict`, the
`apply_pending_tools` duck-typing precedent) ships with in-repo
implementations, an additive optional `world_state` snapshot field
(format version unchanged, episodic blobs bit-identical), and a loud
failure for non-capturing worlds (research R4/R5, spec amended openly).
Single-boot is an engine-enforced, guard-world-tested contract — the
answer C2 was promised (R6). Ships with the investigatory
episodic-vs-continuous reading (R9), pre-registered expectation included.

## Technical Context

**Language/Version**: Python 3.14 (repo `.venv`)  **Dependencies**: numpy only
**Storage**: none beyond the existing opt-in snapshot store (one additive optional blob field)
**Testing**: pytest — unit (config validation, capture protocol round-trips, SingleBootWorld), integration (byte-frozen baseline, mode-default equivalence, single-boot full run, continuous determinism + worker invariance, boundary placements, resume byte-identity, composition with drives/body/ladder)
**Project Type**: extends the `pra` package — engine episode-loop branch, config field, snapshot field, world capture methods; no new modules except test instruments
**Performance**: identical step cost; continuous mode does strictly less world work (no per-episode reset draws — note: this changes the RNG stream vs episodic, which is expected and documented; determinism is per-mode)
**Constraints**:
- **Byte-identity** (FR-002): the episodic code path is untouched; `episode_mode="episodic"` short-circuits to today's exact behavior; frozen-baseline tests + a default-equivalence test guard it.
- **Single boot** (FR-001/FR-007): engine-owned; proven against `SingleBootWorld` for a full schedule.
- **Stream integrity** (FR-004): trailing-observation carry; observation accounting tested against the world's production count.
- **Snapshot compatibility** (FR-005): `world_state` optional both directions; episodic blobs bit-identical; capture failure is loud.
- **Honest measurement** (FR-008): the reading is investigatory, recorded with spreads in `reading.md`, judged by nothing.
**Scale/Scope**: reference-scale validation and reading; scaled continuous runs are future research (the scale rules are mode-agnostic).

## Constitution Check

Constitution file remains the unfilled template; gating against project
rules (AGENTS.md) and the specs:

| Gate | Requirement | Status |
|---|---|---|
| Regression (FR-002/SC-002) | validated modes byte-identical; default inert | PASS — untouched episodic path; default `"episodic"`; baseline tests gate |
| Design-first (FR-006/SC-004) | the four questions answered in writing before code | PASS — research R2–R7 committed in this phase, before implementation |
| Single-boot (FR-001) | engine-enforced, guard-tested | PASS — R6/R8; test against a world that raises on second reset |
| Snapshot honesty (FR-005) | additive format, loud failure, exact resume where claimed | PASS — R5; spec SC-003 amended openly when design refuted seed-derivability |
| Seam isolation | no store/scorer/drive/body edits | PASS — chain-break keying means the cap and judge carry over for free (R2 table) |
| Honest measurement (FR-008) | investigatory reading, spreads, pre-registered guess | PASS — R9; recorded whichever way it lands |
| Quality gate | ruff + pytest green, none skipped | PASS — gated in tasks |

## Project Structure

### Documentation (this feature)

```text
specs/008-continuous-operation/
├── plan.md, research.md, data-model.md, quickstart.md
├── checklists/requirements.md
├── contracts/continuous.md
├── reading.md                # the investigatory episodic-vs-continuous reading
└── tasks.md
```

### Source Code (repository root)

```text
src/pra/
├── config.py                 # + episode_mode (default "episodic") + validation
├── core/engine.py            # episode-loop branch: boot-once + pending carry;
│                             #   resume path restores world_state + pending
├── world/event_source.py     # + SensorimotorWorld.state_dict/load_state_dict
│                             #   (additive methods; behavior untouched)
├── world/ladder.py           # + capture methods on the three rung worlds
├── anatomy/body.py           # + capture delegation to the mounted environment
└── persistence/snapshot.py   # + optional SystemState.world_state (encode/decode
                              #   tolerate absence; episodic blobs bit-identical)

tests/
├── unit/test_continuous.py           # config validation; capture round-trips;
│                                     #   SingleBootWorld behavior
└── integration/test_continuous.py    # default-mode equivalence; single-boot full
                                      #   run; determinism + worker invariance;
                                      #   boundary placements (SC-004); resume
                                      #   byte-identity; loud capture failure;
                                      #   composition (drives/body/ladder)
```

**Structure Decision**: no new runtime modules — the feature is a mode of
the engine plus additive protocol methods, mirroring how persistence
(003) threaded through existing seams. `SingleBootWorld` lives with the
tests (an instrument, not a user artifact — research R8).

## Complexity Tracking

No constitution-gate violations. The one accepted semantic debt is named
in the spec (Assumptions): the transition chain breaks at virtual
boundaries (a carry-across variant is a possible future dial), and the
RNG stream of a continuous run necessarily differs from its episodic
sibling on the same seed (no per-episode reset draws) — determinism is
per-mode, never cross-mode.
