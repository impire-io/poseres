# Implementation Plan: The Gymnasium Adapter

**Branch**: `007-gymnasium-adapter` | **Date**: 2026-07-13 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/007-gymnasium-adapter/spec.md`

## Summary

Build ROADMAP B2: mount any discrete-action, Box-observation Gymnasium
environment behind the existing seams, purely additively. One new module,
`src/pra/anatomy/gymnasium_body.py`, holds the whole adapter:
**`GymnasiumWorld`** — an `EventSource` wrapping a `gymnasium.Env`
(float64 flattening, action-label mapping including nonzero `start`,
deterministic per-reset seeding, immediate-respawn termination semantics
with counters) — and **`GymnasiumBody`** — a `Body` subclass that wires
the *existing, proven* `WorldSensor`/`WorldActuator` pair around it
(feature-004 R1 already established world-through-body ≡ direct world),
plus a `GymnasiumBody.factory(...)` convenience that returns an
Engine-ready `world_factory` and validates the config's sizes at mount
time. The named design question is decided and tested: on
`terminated`/`truncated`, the adapter immediately reseeds and resets —
the world "respawns" inside the fixed-length PRA episode (research R2).
Determinism comes from a child seed sequence derived from the run
generator by a **pure state read** (no draws — the engine's stream is
untouched; research R3). `gymnasium` lands as a new optional extra
(`gym`) and joins the `dev` extra so the quality gate always runs the
adapter tests — none skipped. A heavily commented `examples/cartpole.py`
(a newcomer's second stop after GETTING-STARTED) runs the reference
schedule on CartPole-v1 in ~3 s and proves its own byte-identity.

## Technical Context

**Language/Version**: Python 3.14 (worktree `.venv`)
**Dependencies**: numpy (core, unchanged); `gymnasium>=1.0` in new optional extra `gym` + in `dev` (probed against gymnasium 1.3.0)
**Storage**: none
**Testing**: pytest — unit (seed scheme, respawn mechanics on scripted envs, flattening, rng non-perturbation), contract (EventSource/Body conformance, action mapping, every rejection path incl. missing-dependency message), integration (real CartPole byte-identity, respawns > 0, body ≡ direct world)
**Project Type**: extends the `pra` package (one new anatomy module + tests + example + pyproject extras)
**Performance**: full reference schedule on CartPole measured at ~3.1 s/seed; the example (two runs of seed 1 for the determinism proof) finishes in well under a minute (SC-003); test suite additions stay in seconds via small schedules
**Constraints**:
- **Byte-frozen reference** (FR-008/SC-002): zero engine/core/config edits; the adapter is a leaf module nothing imports unless the user does; `test_baseline_unchanged` and the whole existing suite must stay green with recorded values.
- **Determinism** (FR-005/SC-001): per-reset seeds from `SeedSequence(entropy, spawn_key=(k,))` where entropy is a pure function of the run seed (state read at mount, before any draw); the adapter never draws from the engine generator — integration-tested on CartPole, unit-tested for stream non-perturbation.
- **Termination semantics** (FR-004/FR-010): immediate seeded respawn, terminal observation discarded, respawn counted outside the learning surface — scripted-env mechanics test + real-run `respawns > 0` assertion.
- **No skipped tests** (FR-006): gymnasium is in `dev`; the missing-dependency error path is tested by monkeypatching the module's import handle, never by skipping.
**Scale/Scope**: CartPole (obs 4 / actions 2) is inside the validated reference range; no scaling claim is made (spec Assumptions).

## Constitution Check

Constitution file remains the unfilled template; gating against project
rules (AGENTS.md) and the specs:

| Gate | Requirement | Status |
|---|---|---|
| Regression (FR-008/SC-002) | validated modes byte-identical; core install numpy-only | PASS — additive leaf module; extras only in pyproject; no core imports it |
| Seam isolation (FR-001) | adapter behind `EventSource`/Body; engine untouched | PASS — `GymnasiumWorld` satisfies the protocol; `GymnasiumBody` reuses `WorldSensor`/`WorldActuator` (research R1) |
| Determinism (FR-005) | same (config, seed) → byte-identical summaries; engine rng unperturbed | PASS — pure state-read entropy + spawn-keyed child seeds (research R3), probed end-to-end before planning |
| Honest semantics (FR-004/FR-010) | termination decision explicit, consequences documented, tested | PASS — immediate respawn decided in spec; R2 records consequences + rejected alternatives; mechanics + real-run tests |
| Surface hiding (FR-002) | no reward/flags/info cross the seam | PASS — `step` returns only the observation vector; counters live on the adapter object, engine never reads them |
| Optional dependency (FR-006) | core numpy-only; gate never skips | PASS — `gym` extra + `dev` extra; lazy import with named install command; monkeypatched error-path test |
| Quality gate | ruff + pytest green, none skipped | PASS — gated in tasks |

## Project Structure

### Documentation (this feature)

```text
specs/007-gymnasium-adapter/
├── spec.md, plan.md, research.md, data-model.md, quickstart.md
├── checklists/requirements.md
├── contracts/gymnasium-adapter.md   # world / body / regression / example contracts
├── journey-chapter.md               # proposed JOURNEY.md chapter (merged by maintainer)
├── docs-propagation.md              # proposed GETTING-STARTED/README edits (merged by maintainer)
└── tasks.md                         # (/speckit-tasks output)
```

`journey-chapter.md` and `docs-propagation.md` exist because this branch
runs parallel to other work: the shared narrative files (`JOURNEY.md`,
`GETTING-STARTED.md`, `README.md`, `ROADMAP.md`) are not edited here to
avoid merge conflicts; the proposed edits are staged for integration at
merge time.

### Source Code (repository root)

```text
src/pra/anatomy/
├── body.py                  # untouched (Body, WorldSensor, WorldActuator, AnatomyError)
└── gymnasium_body.py        # NEW — GymnasiumWorld (EventSource over gymnasium.Env),
                             #   GymnasiumBody (Body subclass + factory), lazy import

examples/
└── cartpole.py              # NEW — the worked example (heavily commented)

pyproject.toml               # + [project.optional-dependencies] gym; dev += gymnasium

tests/
├── unit/test_gymnasium_world.py         # seed scheme, respawn mechanics (scripted env),
│                                        #   flattening, rng non-perturbation
├── contract/test_gymnasium_contract.py  # EventSource/Body conformance, action mapping,
│                                        #   rejection paths, missing-dependency message
└── integration/test_gymnasium_cartpole.py  # real CartPole: byte-identity, seed
                                             #   sensitivity, respawns > 0, body ≡ world
```

**Structure Decision**: one new leaf module in `anatomy/` (the adapter is
an integration-surface artifact, and its Body half lives naturally beside
`body.py`), mirroring how the ladder added one world module without
touching `core/`. No changes to `core/`, `world/`, `harness/`, or
`config.py` at all.

## Complexity Tracking

No constitution-gate violations to justify. The accepted, documented
debts are named in the spec's Assumptions with their future owners:
Box-action support and reward-as-sensor (future adapter work),
engine-side episode semantics (B3), snapshot/resume of externally
stateful worlds (B5).
