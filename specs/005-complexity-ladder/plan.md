# Implementation Plan: The Complexity Ladder

**Branch**: `005-complexity-ladder` | **Date**: 2026-07-13 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-complexity-ladder/spec.md`

## Summary

Build ROADMAP A3: three opt-in synthetic worlds, each one known difficulty
axis off the validated staircase, behind the existing `EventSource` seam so
the engine, body layer, drives, and snapshots run on them unchanged —
**L1** `NonUniformWorld` (a half-space region of latent space where
transitions carry irreducible fresh noise; the A4 noisy-TV/camping
testbed, with world-side occupancy counters), **L2** `CompositionalWorld`
(factored dynamics — each action moves exactly one factor group — under
the reference joint emission), **L3** `DistractorWorld` (extra observation
channels driven by an autonomous fixed-drift latent, dial to pure noise).
Selection is a new `Config.world` field with inert defaults; a
`make_world` factory feeds the Engine's existing `world_factory`
parameter — **zero engine changes**. A `pra-validate ladder` command runs
requested rungs across seeds and reports per-rung readings and verdicts
against pre-registered criteria (`design/validate/LADDER-CRITERIA.md`,
committed before results), reusing the harness's existing measurement
patterns: paired same-seed twin runs (L1), the churn-matched T3 quartet
(L2), snapshot census (L2), horizon checkpoints (L3). Every rung at its
degenerate dial is **byte-identical** to the reference world, tested.

## Technical Context

**Language/Version**: Python 3.14 (repo `.venv`)  **Dependencies**: numpy only
**Storage**: none (L2 census uses the in-memory snapshot codec; the only disk artifact is the `--json` report)
**Testing**: pytest — unit (dials/validation, draw order, region/mask/append math), contract (EventSource conformance + ground-truth hiding per rung), integration (degenerate byte-identity per rung, determinism, ladder CLI, baseline unchanged)
**Project Type**: extends the `pra` package (`world/ladder.py` + `harness/ladder.py` + config fields + CLI subcommand)
**Performance**: rung worlds add O(1) draws per step over reference; ladder runs are reference-scale (seconds per seed) — the whole first-results grid is minutes, not hours
**Constraints**:
- **Byte-identity** (FR-006/FR-012): `world="reference"` default routes to the untouched path; each rung's degenerate dial consumes exactly the reference draw sequence (extra draws only when non-degenerate, in documented order) — integration-tested per rung.
- **Ground-truth hiding** (SC-005): ground truth and occupancy live behind a harness-only `ladder_readings()` accessor; the `EventSource` surface stays observations + sizes.
- **Determinism** (FR-005): fixed draw order per rung (documented in data-model), worker-parallelism invariant, snapshot/resume exact.
- **Honest criteria** (FR-007/FR-009): `LADDER-CRITERIA.md` pre-registered before results; verdicts investigatory at build level; spreads and failures always reported.
**Scale/Scope**: first recorded results at reference-scale dials, pinned random policy, 8 seeds (research R9); scaled-dial ladder runs are follow-up work.

## Constitution Check

Constitution file remains the unfilled template; gating against project
rules (AGENTS.md) and the specs:

| Gate | Requirement | Status |
|---|---|---|
| Regression (FR-006/SC-002) | validated modes byte-identical; defaults inert | PASS — `world="reference"` default; opt-in params on `run_suite` default `None`; baseline test still gates |
| Degenerate ground (FR-012) | each rung's dial-zero ≡ reference, in bytes | PASS — draw-order discipline (research R7) + per-rung integration test |
| Seam isolation (FR-004) | rungs behind `EventSource`; engine untouched | PASS — `make_world` via existing `world_factory`; no engine edits |
| Ground truth hiding (SC-005) | nothing on the system surface reveals dials | PASS — harness-only accessor, contract-tested |
| Honest measurement (FR-007/009) | criteria pre-registered; FAIL is data; spreads | PASS — `LADDER-CRITERIA.md` committed before results; investigatory exit code |
| Instrument reuse | no parallel measurement inventions | PASS — paired runs, T3 quartet, snapshot census, checkpoint readings all reused (research R8) |
| Quality gate | ruff + pytest green, none skipped | PASS — gated in tasks |

## Project Structure

### Documentation (this feature)

```text
specs/005-complexity-ladder/
├── plan.md, research.md, data-model.md, quickstart.md
├── checklists/requirements.md
├── contracts/ladder.md      # world / harness / CLI / regression contracts
└── tasks.md                 # (/speckit-tasks output)
```

### Source Code (repository root)

```text
src/pra/
├── config.py                # + world, region_noise_std, factor_dims,
│                            #   distractor_dim/_channels/_mode + validation
├── world/
│   ├── event_source.py      # untouched (reference world)
│   └── ladder.py            # NonUniformWorld, CompositionalWorld,
│                            #   DistractorWorld, make_world(cfg, rng)
└── harness/
    ├── runner.py            # run_suite: optional world_factory pass-through
    ├── ladder.py            # run_ladder + rung readings (paired twin, quartet,
    │                        #   census via snapshot codec, occupancy readout)
    ├── report.py            # ladder report builder + text/JSON blocks
    └── cli.py               # `pra-validate ladder` subcommand

design/validate/
└── LADDER-CRITERIA.md       # pre-registered per-rung criteria; results filled in

tests/
├── unit/test_ladder_worlds.py        # dials, validation, region/mask/append math,
│                                     #   draw order, occupancy counters
├── contract/test_ladder_contract.py  # EventSource conformance; surface hides truth
└── integration/test_ladder.py        # degenerate byte-identity per rung (vs
                                      #   SensorimotorWorld), determinism, CLI + JSON,
                                      #   run_suite world_factory default unchanged
```

**Structure Decision**: one new world module + one new harness module,
mirroring how `scale.py`/`scan.py`/`agency.py` sit beside `runner.py`;
no changes to `core/` at all.

## Complexity Tracking

No constitution-gate violations to justify. The one accepted debt is
named in the spec (Assumptions): scale-rule interaction on rungs whose
learnable core is smaller than their total observation width is reported
transparently, not resolved here.
