# Implementation Plan: Brain Seeding

**Branch**: `028-brain-seeding` | **Date**: 2026-07-20 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/028-brain-seeding/spec.md`

## Summary

Measure the roadmap's compounding-intelligence claim at 24-seed power: does a
snapshotted brain, used as a *seed*, reach competence on a new rover map in less
experience than a blank brain (transfer) and than an equally-experienced brain
from an unrelated world (transfer, not maturity) — and does that head start
survive a body-growing hop (compounding)? The approach adds the *minimum*
machinery to run the experiment on existing seams — a harness-owned rover layout
seed, an opt-in permuted-rover world for the maturity control, and a
`pra-validate seeding` orchestration that reuses the existing snapshot/resume,
`resize`, and paired-margin primitives — and freezes the science in a
pre-registration (`design/validate/SEEDING-DIAGNOSIS.md`) whose θ/budgets are
pilot-calibrated then frozen before the confirmatory run. Every existing mode
stays byte-frozen; a FAIL is a recorded finding that triggers the roadmap's
reversal condition.

## Technical Context

**Language/Version**: Python 3.12 (`requires-python >= 3.12`)
**Primary Dependencies**: numpy >= 2.4 (runtime); pytest >= 8, ruff >= 0.6, gymnasium >= 1.0 (dev). No new dependencies.
**Storage**: In-memory brain state serialized to bytes via the existing snapshot codec (`pra.persistence`); the harness writes only its human-readable/JSON report and the trail doc. No database.
**Testing**: pytest (`tests/unit`, `tests/integration`, `tests/contract`); byte-identity guarded by `tests/integration/test_baseline_unchanged.py`.
**Target Platform**: CPython 3.12 on a single machine (library + CLI).
**Project Type**: Single project — research library (`src/pra/`) with a CLI harness (`pra-validate`) and example worlds (`src/pra/examples/rover/`).
**Performance Goals**: The confirmatory run is 24 seeds × (pre-train A + pre-train scramble + three arms on B + three arms on C) — bounded by the rover's existing throughput; must complete in a session, not a datacenter. No new hot-loop code (the engine loop is untouched).
**Constraints**: Reference behavior byte-frozen (the constitution); determinism per seed exact; new worlds opt-in with degenerate dials byte-identical to today's rover; no randomness consumed at hop/shift boundaries beyond documented resize draws.
**Scale/Scope**: obs_dim 10 → 11 (one added sensor), n_actions 4; two new opt-in world dials; one new harness subcommand and module; ~a handful of new test files.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

> The speckit `.specify/memory/constitution.md` is an unpopulated template. This
> project's governing principles are `ROADMAP.md` "Operating principles" and
> `AGENTS.md` "Non-negotiable working rules"; the gate is evaluated against them.

| Principle (ROADMAP / AGENTS) | This feature | Status |
|---|---|---|
| **Research gates before showcase spends** (ROADMAP 1) | This *is* a research measurement, not a showcase; it gates a vision-language claim. | PASS |
| **Never lose the instrument panel** (ROADMAP 2) | Testbed keeps ground truth, determinism, steppable time (bounded rover); layout/permutation are harness-visible. | PASS |
| **Reference-preserving forever / byte-frozen** (ROADMAP 3, AGENTS) | New worlds opt-in; degenerate dials byte-identical to today's rover; T1–T6 baseline untouched; new capability leaves existing RNG/behavior/summaries intact. | PASS (guarded by tests, FR-007) |
| **Honest criteria, stated before the work** (ROADMAP 4, AGENTS) | Bars B1/B2/C1, censoring, and the reversal condition pre-registered in `SEEDING-DIAGNOSIS.md`; θ/budgets pilot-then-freeze; no post-hoc tuning. | PASS |
| **Diagnose/record trail** (AGENTS) | `design/validate/SEEDING-DIAGNOSIS.md` carries hypotheses → instrument → frozen values → results; JOURNEY ch. 44. | PASS |
| **Quality gate before done** (AGENTS) | `ruff format --check . && ruff check . && pytest -q`, none skipped, before commit. | PASS (enforced at task 5) |
| **Spec Kit flow on a numbered branch** (AGENTS) | `028-brain-seeding`, `specs/028-brain-seeding/`, specify → plan → tasks → implement. | PASS |

**No violations.** Complexity Tracking is empty.

## Project Structure

### Documentation (this feature)

```text
specs/028-brain-seeding/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (CLI + config surface)
│   └── seeding-cli.md
├── checklists/
│   └── requirements.md  # from /speckit-specify
└── tasks.md             # /speckit-tasks output (not created here)

design/validate/SEEDING-DIAGNOSIS.md   # the normative pre-registration (FR-005)
```

### Source Code (repository root)

```text
src/pra/
├── examples/rover/
│   ├── world.py         # RoverWorld: add harness-owned layout seed (FR-001);
│   │                    #   add construction-time permutation of actions/sensors (FR-002)
│   ├── cli.py           # rover factory wiring (layout seed / permute flags)
│   └── __init__.py
├── config.py            # new opt-in dials: rover layout seed, permute flag/spec
├── harness/
│   ├── seeding.py       # NEW: the seeding experiment orchestration + margins/report (FR-003, FR-004, FR-006)
│   ├── cli.py           # register `pra-validate seeding` subcommand
│   └── acceptance.py    # reused paired-margin form (_margins_vs / ±1.9·SE); referenced, not modified where avoidable
└── core/
    └── engine.py        # unchanged run/resume/resize seams (used, not modified)

tests/
├── unit/
│   ├── test_rover_layout_seed.py     # degenerate byte-identity; independent layouts (FR-001)
│   ├── test_permuted_rover.py        # identity-permutation byte-identity; learnable; unrelated (FR-002)
│   └── test_seeding_metric.py        # time-to-threshold + censoring + margins (FR-004, FR-006)
├── integration/
│   ├── test_seeding_chain.py         # snapshot/resume across scramble + resize byte-identical (FR-007, US3)
│   └── test_baseline_unchanged.py    # EXISTING guard — must stay green (byte-frozen)
└── contract/
    └── test_seeding_cli.py           # CLI contract: args, JSON shape, verdict fields
```

**Structure Decision**: Single project. The feature is additive across three
existing homes — the rover example world (`examples/rover/world.py`), the config
surface (`config.py`), and the harness (`harness/`) — plus one new harness module
(`seeding.py`). No engine/core edits: the experiment is orchestration over the
unchanged `Engine.run(resume_from=…)`, `FrameStore.resize`, and snapshot codec.

## Complexity Tracking

> No Constitution Check violations — this section intentionally empty.
