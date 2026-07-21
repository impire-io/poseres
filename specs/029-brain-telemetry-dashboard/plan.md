# Implementation Plan: Brain Telemetry & Introspection Dashboard

**Branch**: `029-brain-telemetry-dashboard` | **Date**: 2026-07-21 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/029-brain-telemetry-dashboard/spec.md`

## Summary

Extend `pra.v1` with an additive `brain.*` subject family — anatomy/channel
metadata, per-frame census rows, frame lifecycle events — published entirely
from the existing NatsTap seams, and grow `pra-dash` with a Brain tab:
named per-channel strip charts + scrolling log, a frame table, a spawn/evict
timeline, and a metadata-driven graphical anatomy schematic. **Zero core
engine edits**: the three data sources already cross the tap's seams —
per-step observations are mirrored (they just lack names), the census
already walks `frame_states()` (it aggregates the rows away), and spawn/evict
already route through the Bus the tap constructs (`bus.register` /
`bus.unregister` in `offline_cycle`, engine.py:420-424).

## Technical Context

**Language/Version**: Python ≥3.12 (repo venv `./.venv`, currently 3.14)
**Primary Dependencies**: numpy; stdlib `http.server` (dash); optional
`nats-py` via the `[nats]` extra — the in-repo `FakeBusTransport` carries
every gate test, no live broker needed
**Storage**: none new (telemetry is fire-and-forget; logs are bounded
in-memory windows per spec Assumptions)
**Testing**: pytest (contract tests on `FakeBusTransport`, dash-endpoint
integration tests mirroring `tests/integration/test_dash_live.py`, plus the
byte-frozen suite `test_baseline_unchanged.py` which must not notice)
**Target Platform**: darwin/linux localhost (dash binds 127.0.0.1)
**Project Type**: single Python package (`src/pra`) + one self-contained
HTML page (`src/pra/dash/page.html`)
**Performance Goals**: run-path budget unchanged (the tap contract:
per step one Event check, increments, one array copy, one deque append);
dash keeps up at ≥10 steps/s with bounded memory (FR-013/SC-006)
**Constraints**: additive-only under `pra.v1`; byte-frozen reference
untouched; canonical wire form, no wall-clock, seq-ordered (FR-004..006)
**Scale/Scope**: populations ride `max_frames` (arc 026) — per-frame rows
are bounded by it (~few KB/census); step window bounded (~600 entries)

## Constitution Check

*GATE: evaluated against `hq/00-GENESIS/constitution.md` v1.0.0.*

- **I. Reference-Preserving Forever — PASS.** No `src/pra/core` edits at
  all. New publications live in `src/pra/nats` (tap, subjects) and
  `src/pra/dash`; bodies gain an inert `anatomy_meta()` data method in the
  anatomy layer. Without a tap none of it is constructed;
  `test_baseline_unchanged.py` and the full T1–T6 suite run untouched.
- **II. Honest Measurement — PASS.** Drops stay derived from seq gaps and
  rendered; per-frame rows are complete (bounded by `max_frames`, never
  silently truncated); the dash renders gaps/wire-errors as today.
- **III. Diagnose Before Fixing — N/A** (no behavioral problem; product
  surface).
- **IV. Research Gates Before Showcase Spends — PASS.** This is instrument
  panel, not showcase: it *shows* whatever the brain honestly is, which is
  the article's spirit. No new capability claims.
- **V. Never Lose the Instrument Panel — PASS** (this feature *is* the
  instrument panel; no new world).
- **VI. All-Green Quality Gate — applies**; ruff + pytest + hq lint before
  done, signed commits.

**Post-design re-check (Phase 1): PASS** — the design introduces no core
edits and no new dependencies; all additions are constructed only when a
tap exists.

## Project Structure

### Documentation (this feature)

```text
specs/029-brain-telemetry-dashboard/
├── plan.md              # This file
├── research.md          # Phase 0: seam decisions + alternatives
├── data-model.md        # Phase 1: payload entities + validation rules
├── quickstart.md        # Phase 1: run it live / run the gate
├── contracts/
│   └── brain-subjects.md  # Phase 1: the brain.* wire contract
└── tasks.md             # Phase 2 (/speckit-tasks — not this command)
```

### Source Code (repository root)

```text
src/pra/
├── nats/
│   ├── subjects.py      # + brain_anatomy/frames/events subjects; run_subjects grows 3 keys
│   ├── tap.py           # + _TapBus (lifecycle mirror), anatomy capture in world_factory,
│   │                    #   per-frame rows in _publish_census, anatomy heartbeat in _pump
│   └── control.py       # (unchanged — discover reply already serializes run_subjects)
├── anatomy/
│   ├── ros2/body.py     # + Ros2Body.anatomy_meta() from live sensors/actuators
│   ├── gymnasium_body.py # + GymnasiumWorld.anatomy_meta() (structural groups)
│   └── (minecraft rides Ros2Body — nothing to do)
├── examples/rover/world.py  # + anatomy_meta() from SENSOR_PARTS + action names
└── dash/
    ├── model.py         # + brain families in _apply; bounded step window; state_payload grows
    └── page.html        # + Brain tab: schematic SVG, strip charts, log, frame table, timeline

tests/
├── contract/            # + test_brain_subjects.py (FakeBusTransport contract)
├── integration/         # + test_brain_telemetry_run.py (short run: rows==census,
│                        #   lifecycle exactly-once + reconciliation, heartbeat)
│                        # test_dash_live.py grows brain-panel endpoint assertions
└── unit/                # + test_anatomy_meta.py (per-body metadata correctness)
```

**Structure Decision**: single-project layout, additions ride the existing
module boundaries: wire words in `nats/subjects.py`, publication in
`nats/tap.py`, body self-description in the anatomy layer, rendering in
`dash/`. The dashboard stays one self-contained page (feature 015 pattern).

## Design at a glance (details in research.md / contracts/)

1. **Metadata seam** — optional world method `anatomy_meta()`; `_TapWorld`
   construction does one `getattr`, deep-copies the dict, buffers it, and
   `_pump` re-publishes it on the existing view-heartbeat clock so late
   consumers catch it (the `view.static` pattern verbatim).
2. **Per-frame rows** — `_publish_census` already walks `frame_states()`
   and scores each frame; it now also emits `brain.frames` with the full
   row list in the same walk, same cadence, same torn-read guard. The
   existing `tele.census` payload stays byte-identical.
3. **Lifecycle events** — `bus_factory` returns a `_TapBus` wrapper
   (delegating `register`/`unregister`/`publish`/`subscribers` verbatim to
   the stock `InMemorySyncBus`) that mirrors register→`spawn` /
   unregister→`evict` into the tap buffer on the engine thread (single
   writer preserved). "Spawn" includes boot/restore registration — stated
   in the contract, and it is what makes SC-003's reconciliation exact.
4. **Dash** — `RunModel` grows bounded windows (steps, events) + latest
   metadata/rows; the page grows a Brain tab rendering all four panels
   from `/run/<id>/state` alone (pure consumer, FR-011), with the
   schematic generated from metadata (FR-010) and graceful absence
   fallbacks (FR-012).

## Complexity Tracking

No constitution violations; table not needed.
