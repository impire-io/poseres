# Implementation Plan: Motivation and Action Layer

**Branch**: `002-motivation-action` | **Date**: 2026-07-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-motivation-action/spec.md`

## Summary

Turn the passive world-model into an agent, exactly as design Doc 05 specifies:
a **motivation layer** (fixed innate drives producing a scalar value signal each
online step; default and only shipped drive is curiosity = learning-progress +
novelty with automatic cold-start handover) and an **action layer** (a swappable
Policy seam; shipped default is one-step curiosity lookahead over the frames'
transition models, uniformly random at cold start / below a maturity bar / with
exploration probability). Drive identities, parameters, and weights are
read-only to the running system (Doc 05 §6, mandatory).

The load-bearing engineering constraint is **FR-008**: the validated T1–T6
suite keeps running under a pinned random-action baseline with per-seed
summaries **byte-identical** to the validated build. The Engine's inline action
draw becomes a `Policy` seam whose default (`RandomPolicy`) consumes exactly the
same single RNG draw per step as today's inline code; drives are pure functions
that consume **no** RNG; and drive/policy telemetry appears in the canonical
summary **only when the agency mode is active** (absent fields ⇒ the baseline
summary's bytes are untouched). The new behavioral claim gets its own honest
verdict — **T7: curious ≥ random on equal experience in a strict majority of
seeds** — via a new `pra-validate agency` command, leaving the T1–T6 gate
untouched and cheap.

## Technical Context

**Language/Version**: Python 3.14 (repo `.venv`; PEP 668 blocks system interpreter)
**Primary Dependencies**: numpy ≥ 2.4 (sole runtime dep, unchanged). Dev: pytest, ruff.
**Storage**: None (in-memory; only report summaries are ever written — FR-010/FR-011 of 001 carry over)
**Testing**: pytest — unit (drive terms, lookahead, maturity gate), contract (Drive/Policy seams, random-policy byte-equivalence), integration (agency determinism, T7 reference PASS, immutability, multi-drive, suite byte-identity)
**Target Platform**: Single machine, CPU only, macOS/Linux
**Project Type**: Single Python project (library `pra` + `pra-validate` CLI) — extends feature 001's package
**Performance Goals**: The one-step lookahead adds ~(n_actions × predict+decode) on **one** frame per step (~9 small mat-vecs at defaults) — negligible next to the population-wide batched update; the agency comparison (2 runs/seed × 8 seeds) must stay in single-digit minutes sequential, ~1 minute with parallel seeds
**Constraints**:
- **Byte-identity of existing modes** (FR-008, SC-003): pinned random baseline reproduces the validated build's summaries bit-for-bit; enforced by an integration test against the recorded reference values and by the canonical-serialization rule (agency fields absent unless agency mode).
- **Full determinism from seed** (FR-007): drives consume no RNG (pure functions of context); the curiosity policy consumes RNG in a fixed order (one uniform for the ε-gate; one integer draw only when exploring or below maturity); ties break by lowest action index.
- **Drive immutability** (FR-003): drive parameters live in frozen dataclasses; no runtime writer exists; enforced by test.
- **Honest reporting**: T7 reported with the per-seed spread, never a mean alone; failures shown with the numbers that explain them.
- **Component isolation** (PRA-01 §7.3 spirit): Drive and Policy are seams — substitutable without touching Engine/Bus/Scorer/world.
**Scale/Scope**: Reference config (`true_dim=3`, 8 seeds) is the validation target for T7; the drive/policy parameters are validated at the reference scale first (no new scale rules introduced; revisit under the §8.8 pattern only if agency is later run at scale)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The project constitution (`.specify/memory/constitution.md`) remains the
unfilled template — no ratified gates. As with feature 001, the plan is gated
against the binding requirements of the project's own specs and the user's
global instructions:

| Gate (source) | Requirement | Status |
|---|---|---|
| Regression gate (FR-008, SC-003) | T1–T6 byte-identical under pinned random baseline | PASS — RandomPolicy consumes the identical RNG draw; telemetry fields conditional (research R1/R2) |
| Determinism (FR-007, PRA-01 §7.1) | Single seeded generator, fixed draw order, byte-identical re-runs | PASS — drives pure, policy draw order fixed (research R3) |
| Drive immutability (FR-003, Doc 05 §6) | No runtime process can modify drive params/weights | PASS — frozen dataclasses, no writer, tested (research R4) |
| Seam isolation (Doc 05 §2.1/§4.1) | Drive and Policy swappable without touching other components | PASS — protocol interfaces + Engine injection (contracts/seams.md) |
| Honest reporting (PRA-02 §5) | T7 spread surfaced; no smoothing | PASS — same verdict machinery as T1–T6 |
| Out-of-scope discipline (Doc 05) | No multi-step planning, no tool invention, no drive evolution | PASS — one-step default only; seams left open |
| Quality gate (user CLAUDE.md) | ruff format+check clean, pytest green none skipped | PASS — same toolchain, gate in tasks |

## Project Structure

### Documentation (this feature)

```text
specs/002-motivation-action/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── seams.md             # Drive + Policy seam contracts
│   ├── cli.md               # `pra-validate agency` command contract
│   └── config.md            # New Doc 07 parameters + defaults
└── tasks.md             # Phase 2 output (/speckit-tasks — NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
src/pra/
├── config.py                # + drive/policy parameters (frozen; validation)
├── motivation/
│   ├── __init__.py
│   ├── context.py           # DriveContext: read-only view the drives evaluate
│   └── drive.py             # Drive protocol; CuriosityDrive; WeightedDriveSet
├── action/
│   ├── __init__.py
│   └── policy.py            # Policy protocol; RandomPolicy; CuriosityLookaheadPolicy
├── core/
│   └── engine.py            # action draw → Policy seam; per-step drive evaluation
│                            #   + value-signal telemetry (agency mode only)
├── telemetry/
│   └── recorder.py          # optional agency fields in PerSeedRunSummary
└── harness/
    ├── agency.py            # curious-vs-random paired runs (T7 measurement)
    ├── acceptance.py        # + T7 evaluator (curious ≥ random, strict majority)
    ├── report.py            # + T7 rendering (per-seed spread)
    └── cli.py               # + `agency` command (--seeds/--workers/--json)

tests/
├── contract/
│   ├── test_drive_contract.py       # purity, immutability, substitute drive
│   └── test_policy_contract.py      # seam substitution; RandomPolicy byte-equivalence
├── integration/
│   ├── test_agency_determinism.py   # curious mode byte-identical re-runs
│   ├── test_agency_t7.py            # T7 reference PASS + honest FAIL path
│   ├── test_baseline_unchanged.py   # pinned baseline == validated build values
│   └── test_multi_drive.py          # weighted-sum combination by config only
└── unit/
    ├── test_curiosity_drive.py      # LP flat-low/flat-high/falling; novelty incl. empty memory
    └── test_lookahead_policy.py     # argmax, tie-break, ε-gate, maturity gate, cold start
```

**Structure Decision**: `motivation/` and `action/` become sibling subpackages of
`core/`, mirroring Doc 01's component map (sensorimotor core, structural
learning, motivation, action are distinct components). The Engine grows one seam
(`policy`) and one optional collaborator (`drives`); the harness gains one
runner module and one CLI command. Feature 001's packages are extended, never
restructured.

## Complexity Tracking

> No constitution violations to justify. One deliberate scope note: the T7
> comparison ships as its own CLI command (`agency`) rather than growing the
> default suite, so the T1–T6 regression gate stays exactly as validated (same
> runtime, same bytes) — the cheaper alternative (folding T7 into `suite`) was
> rejected because it would change the gate's cost and output for a claim that
> belongs to this feature, not to the core.
