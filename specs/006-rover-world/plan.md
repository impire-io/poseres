# Implementation Plan: The Watchable Rover World

**Branch**: `006-rover-world` | **Date**: 2026-07-13 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-rover-world/spec.md`

## Summary

Build ROADMAP B1: a deterministic 2D rover world (`RoverWorld`: bounded
arena, seeded circular obstacles, a rover with pose and four movement
actions) mounted through the **Doc 02 anatomy layer** as a body of named
parts — a 5-ray rangefinder, a compass, a position beacon, and a bumper
composed in fixed order into the validated reference widths (obs_dim 10,
n_actions 4, where every scale-rule factor is exactly 1) — running on the
**unchanged engine** via the existing `world_factory` seam. A built-in live
viewer (stdlib `http.server` + one self-contained HTML/canvas page, zero
new dependencies) shows the rover, its trail, and honest learning
telemetry (best-frame prediction-error EMA, population size, best_dim)
served from a `RoverTelemetry` tap that **observes without perturbing**:
the run path only appends plain value copies (world-side recording, the
L1 occupancy-counter precedent); the store reference is captured through a
pass-through `bus_factory` that returns the standard bus; every derived
float computation happens in the serving thread. A new console command
`pra-rover` wires run + viewer + pacing together. Byte-identity is tested
three ways: re-run reproducibility, viewer-on ≡ viewer-off, and pacing ≡
no pacing.

## Technical Context

**Language/Version**: Python 3.14 (repo `.venv`)  **Dependencies**: numpy only (viewer: stdlib `http.server`/`threading`/`json` + vanilla HTML/JS/canvas)
**Storage**: none (the only optional disk artifact is the CLI's `--json` summary)
**Testing**: pytest — unit (geometry, collision, spawn sampling, sensor widths, mount validation), contract (EventSource conformance, ground-truth hiding, tap purity), integration (byte-reproducibility, viewer-on ≡ viewer-off under live HTTP polling, endpoint shapes, CLI, pacing byte-identity) — no browser anywhere
**Project Type**: extends the `pra` package with a new `pra.examples.rover` subpackage + one console script; zero edits to core/engine/config/harness
**Performance**: the run path adds one deque append per step and nothing else; the viewer polls ≤ ~5 Hz against read-only public store accessors; default pacing 50 steps/s puts the full reference-schedule demo run at ≈ 4.3 minutes
**Constraints**:
- **Byte-frozen reference** (FR-010): purely additive — no existing module is edited except `pyproject.toml` (new script entry + package-data, both inert); the full suite and recorded reference values stay byte-identical.
- **Non-perturbation** (FR-007): no RNG and no float work on the run path; tap writers copy plain values; the bus factory returns the untouched `InMemorySyncBus`; serving-thread reads use public read-only accessors with torn-read fallback instead of run-path locks.
- **Determinism** (FR-004): one shared seeded generator, fixed draw order (construction: obstacles then spawn poses; per reset: one spawn-index draw + one emission-noise draw; per step: one emission-noise draw), bounded rejection sampling that fails deterministically.
- **Ground-truth hiding** (FR-005): the engine sees only the `Body`; pose/map/layout live behind the world's harness-only `layout()` accessor and tap recordings.
- **Honest telemetry** (SC-006): the viewer displays only existing quantities — `FrameState` EMAs scored by the real `WeightedSumScorer`, population size, best_dim, step/episode counters.
**Scale/Scope**: single-seed demo at the validated reference scale; multi-seed claims stay with `pra-validate`; drive-directed rover watching is A4's work.

## Constitution Check

Constitution file remains the unfilled template; gating against project
rules (AGENTS.md) and the specs:

| Gate | Requirement | Status |
|---|---|---|
| Regression (FR-010/SC-004) | validated modes byte-identical; no engine/core/config edits | PASS — new subpackage only; `pyproject.toml` additions inert; baseline test still gates |
| Seam isolation (FR-003) | rover behind the existing seams; engine untouched | PASS — `make_rover_body` via `world_factory`; tap via pass-through `bus_factory`; Body is the Doc 02 layer unmodified |
| Non-perturbation (FR-007/SC-003) | viewer on ≡ viewer off in bytes | PASS — run-path copies only; integration test polls live HTTP during a run and byte-compares |
| Ground truth hiding (FR-005) | nothing on the system surface reveals pose/map | PASS — harness-only `layout()`; contract-tested |
| Determinism (FR-004/SC-002) | byte-identical re-runs; deterministic failures | PASS — fixed draw order; bounded spawn sampling; integration-tested |
| Honest measurement (SC-006) | no invented metrics; single seed labeled | PASS — existing quantities only; CLI prints the single-seed caveat |
| Zero dependencies (SC-005/FR-006) | stdlib-only viewer | PASS — `http.server` + one HTML file shipped as package data |
| Quality gate | ruff + pytest green, none skipped, no browser needed | PASS — gated in tasks; endpoints tested over HTTP directly |

## Project Structure

### Documentation (this feature)

```text
specs/006-rover-world/
├── plan.md, research.md, data-model.md, quickstart.md
├── checklists/requirements.md
├── contracts/rover.md        # world / anatomy / tap / HTTP / CLI / regression contracts
├── tasks.md                  # (/speckit-tasks output)
├── journey-chapter.md        # proposed JOURNEY.md chapter (merge-time integration)
└── docs-propagation.md       # proposed GETTING-STARTED/README edits (merge-time integration)
```

### Source Code (repository root)

```text
src/pra/examples/
├── __init__.py
└── rover/
    ├── __init__.py           # public surface: make_rover_body, RoverWorld,
    │                         #   RoverTelemetry, start_viewer
    ├── world.py              # geometry helpers, RoverWorld (physics + senses +
    │                         #   layout()), RoverSensor, RoverDrive, make_rover_body
    ├── viewer.py             # RoverTelemetry (tap) + start_viewer (stdlib HTTP)
    ├── viewer.html           # the single self-contained page (package data)
    └── cli.py                # `pra-rover` console entry point

pyproject.toml                # + [project.scripts] pra-rover; + package-data *.html

tests/
├── unit/test_rover_world.py         # ray/collision/spawn math, widths, draw
│                                    #   order, mount validation, world determinism
├── contract/test_rover_contract.py  # EventSource conformance; ground-truth
│                                    #   hiding; tap coherence before/without a run
└── integration/test_rover.py        # byte-reproducibility; viewer-on ≡ viewer-off
                                     #   under live polling; endpoint shapes; CLI;
                                     #   pacing byte-identity; port-in-use error
```

**Structure Decision**: a self-contained `pra.examples.rover` subpackage —
ROADMAP B1 names `examples/` as the home of the getting-started
experience, and keeping world + viewer + CLI together makes the demo
copy-able as a template for user-built worlds. Nothing in `pra.world`,
`pra.core`, or `pra.harness` changes; the rover deliberately does NOT
extend `Config.world`/`make_world` (that enum is the validation-world
family with byte-identity obligations the rover does not carry — see
research R9).

## Complexity Tracking

No constitution-gate violations to justify. Two accepted debts, named in
the spec (Assumptions): rover-run snapshot/resume byte-identity is neither
claimed nor tested here, and the rover anatomy is fixed at reference
widths (configurable anatomy is future work).
