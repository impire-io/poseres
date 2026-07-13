---
description: "Task list for the watchable rover world"
---

# Tasks: The Watchable Rover World

**Input**: Design documents from `/specs/006-rover-world/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅
**Tests**: INCLUDED (repo rule: all green, none skipped, no browser required).

## Phase 1: Setup

- [x] T001 Create the `pra.examples` / `pra.examples.rover` subpackage
      skeleton (`src/pra/examples/__init__.py`,
      `src/pra/examples/rover/__init__.py`) and the additive
      `pyproject.toml` entries: `[project.scripts] pra-rover` +
      `[tool.setuptools.package-data]` for `viewer.html` (plan structure
      decision; FR-010 — nothing else in pyproject changes)

## Phase 2: US1 — a rover world behind the existing seams (P1) 🎯 MVP

- [x] T002 [US1] Geometry core in `src/pra/examples/rover/world.py`:
      module constants (data-model table), pure helpers — ray/wall and
      ray/circle distance, collision test, spawn rejection sampling with
      the bounded attempt budget raising a constraint-naming error
      (research R4, FR-011)
- [x] T003 [US1] `RoverWorld` in `src/pra/examples/rover/world.py`:
      construction draws (obstacles then spawns, fixed order), `reset()`
      (spawn-index draw + emission), `apply(action)` (physics → emission
      → tap record → optional `step_delay` sleep), emission = clean
      10-vector + `sensor_noise_std` noise sliced into per-part caches,
      harness-only `layout()` (data-model §RoverWorld; FR-001/004/005/009)
- [x] T004 [US1] Anatomy in `src/pra/examples/rover/world.py`:
      `RoverSensor` (cached-part reads, raise before first emission),
      `RoverDrive`, `make_rover_body(config, rng, *, telemetry,
      step_delay)` composing the fixed part order onto `Body`, rejecting
      width mismatches with a naming message (research R2; FR-002/003/011)
- [x] T005 [P] [US1] Unit `tests/unit/test_rover_world.py`: ray distances
      against hand-computed cases (walls, circles, cap), collision/bump
      math, spawn-budget error, construction determinism (same seed →
      same layout/senses sequence), channel order and widths, blocked
      move sets bump and holds pose, turn never bumps, mount-time width
      rejection
- [x] T006 [P] [US1] Contract `tests/contract/test_rover_contract.py`:
      `make_rover_body` result satisfies `EventSource`; observation is a
      float64 10-vector; nothing on the body's system surface exposes
      pose/map/layout; `layout()` exists on the world only (FR-003/005)
- [x] T007 [US1] Integration (`tests/integration/test_rover.py`, first
      block): full engine run on the rover body at small budgets produces
      a standard summary; re-run byte-identity (SC-002); `step_delay > 0`
      byte-identity (FR-009)

**Checkpoint**: the rover world is a usable library world — US1 alone is
shippable value.

## Phase 3: US2 — the live viewer that costs nothing (P2)

- [x] T008 [US2] `RoverTelemetry` in `src/pra/examples/rover/viewer.py`:
      run-path recorders (plain copies, no locks), pass-through
      `bus_factory`, `finish`, and `snapshot()` — serving-thread-only
      derivation (trail copy with retry-fallback; learning block via
      `frame_states()` + `WeightedSumScorer` on copies with
      torn-read fallback) (research R5/R6; FR-007, SC-006)
- [x] T009 [US2] `start_viewer(tap, port)` in the same module:
      `ThreadingHTTPServer` (daemon threads, silent logs) on 127.0.0.1
      serving `/` (package-data page), `/layout`, `/state`, 404 else;
      ephemeral port support; clean `shutdown()`/`server_close()`
      (research R7; FR-006/011)
- [x] T010 [US2] `src/pra/examples/rover/viewer.html`: single
      self-contained page (inline CSS/JS, canvas arena + trail + rover,
      prediction-error trend chart from polled values, population/best_dim
      readouts and per-dim bars, step/episode counters, done banner, the
      R10 honesty note) — no external resources (FR-006, SC-006)
- [x] T011 [P] [US2] Contract additions in
      `tests/contract/test_rover_contract.py`: `snapshot()` coherent
      before any run (null pose, empty trail, zero counters, no learning
      block), after `finish` (done + final), and never mutates inputs
- [x] T012 [US2] Integration (second block): live-polling byte-identity —
      run with viewer serving and a hammering HTTP poller thread vs the
      same run bare, summaries byte-identical (SC-003); endpoint shapes
      (`/`, `/layout`, `/state` per data-model wire formats); 404 route;
      busy-port error naming the port; no lingering-socket warnings under
      the warnings-as-errors gate

**Checkpoint**: watchable runs exist via the library wiring (quickstart
§“your own wiring”).

## Phase 4: US3 — one command, five minutes (P3)

- [x] T013 [US3] `src/pra/examples/rover/cli.py`: argument surface per
      data-model CLI table; config build (JSON overrides); URL printed
      before the run + duration estimate; TTY-gated non-fatal browser
      open; engine run with tap wiring; honest summary print with the
      single-seed caveat; `--json` canonical artifact; hold-until-Ctrl+C
      vs `--exit-when-done`; exit 2 on unusable port (research R9;
      FR-008/009/011)
- [x] T014 [US3] Integration (third block): `main([...])` with tiny
      config, `--fps 0 --port 0 --no-open --exit-when-done --json` —
      returns 0, prints URL before summary, writes the canonical JSON,
      never opens a browser (capsys-verified output; FR-008/012);
      `--json` artifact byte-equal across two invocations (SC-002)

## Phase 5: Polish & gate

- [x] T015 [P] Author `specs/006-rover-world/journey-chapter.md`
      (proposed JOURNEY.md chapter, template-conformant) and
      `specs/006-rover-world/docs-propagation.md` (proposed
      GETTING-STARTED/README edits) — merge-time integration files; do
      NOT touch JOURNEY.md/README.md/GETTING-STARTED.md/ROADMAP.md
      directly (worktree constraint)
- [x] T016 Run the real thing once end-to-end (default budgets, `--fps 0`,
      ephemeral port, `--exit-when-done`) and record the observed
      readings (pred-error early→late, best_dim, population, wall-clock)
      in journey-chapter.md — the demo's honest numbers, single-seed
      labeled
- [x] T017 Quality gate: `./.venv/bin/ruff format --check . &&
      ./.venv/bin/ruff check . && ./.venv/bin/pytest -q` — all green,
      none skipped; existing 193 tests untouched and byte-frozen baseline
      intact (FR-010, SC-004)

## Dependencies

T001 → US1: T002 → T003 → T004 → (T005 ∥ T006) → T007 →
US2: T008 → T009 → T010 → (T011) → T012 →
US3: T013 → T014 → Polish: (T015 ∥ T016) → T017.

US2 depends on US1's world (the tap records from it); US3 composes both.
Within phases, [P]-marked test tasks can proceed in parallel with each
other once their subject exists.

## Implementation strategy

US1 first and complete — it is the MVP and everything downstream records
from it. The viewer lands as pure observation on top (its binding test is
the byte-identity proof, written with the viewer, not after). The CLI is
last because it is composition only. The gate runs once at the end but
`pytest` runs continuously during implementation.
