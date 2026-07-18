---
description: "Task list for the web dashboard (one face for any brain)"
---

# Tasks: The Web Dashboard (One Face for Any Brain)

**Input**: Design documents from `/specs/015-web-dashboard/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅
**Tests**: INCLUDED (repo rule: all green, none skipped — fake transport +
urllib carry everything; no NATS, no server, no browser in the gate).

## Phase 1: Setup

- [x] T001 Skeleton + scheme + packaging: `src/pra/dash/` (`__init__.py`
      public surface), `view_static_subject` / `view_live_subject` added
      to `src/pra/nats/subjects.py` (additive; `run_subjects()` gains the
      two view entries), `pyproject.toml` gains the `pra-dash` script and
      `pra.dash` package-data for `page.html`; subject-scheme unit-test
      additions in `tests/unit/test_nats_subjects.py` (data-model §1)

## Phase 2: Foundational

- [x] T002 The consumer model: `src/pra/dash/model.py` —
      `DashboardModel(transport)` (subscribe `pra.v1.>`, discovery sweep
      at start + slow interval, thread-safe payload handlers, malformed →
      `wire_errors`) and `RunModel` (state, monotonic liveness, latest +
      bounded census history, `seq_gaps`, counters, snapshot notices,
      anatomy, world view, completed summary); unit tests in
      `tests/unit/test_dash_model.py` — two-run separation, late-appearing
      run, liveness aging, gaps counted not repaired, malformed frames
      skipped and counted, completion terminal (contracts §2; research R3)

## Phase 3: US1 — one dashboard for any live brain (P1) 🎯 MVP

- [x] T003 [US1] Server + page (simple mode): `src/pra/dash/server.py` —
      `start_dashboard(model, port)` on 127.0.0.1 with `/`, `/runs`,
      `/run/<id>/state`, `/run/<id>/ctrl` (verbatim forwarding, 5 s / 60 s
      snapshot timeouts, 404 for unknown runs); `src/pra/dash/page.html` —
      self-contained page: run list, simple mode (state, liveness, plain
      census, completed summary); endpoint contract tests via urllib in
      `tests/contract/test_dash_contract.py` (contracts §3.1–§3.4;
      research R1/R4)
- [x] T004 [P] [US1] Observer proof, generic: integration tests in
      `tests/integration/test_dash_live.py` — seeded engine run (tap over
      the shared fake transport) with a live `DashboardModel` and the HTTP
      server hammered by a polling thread, byte-identical to the bare run
      (reference world; multi-stream continuous); attach-poll-detach
      mid-run changes nothing (contracts §4.1–§4.2)

## Phase 4: US2 — the world shows itself (P2)

- [x] T005 [US2] The view channel on the tap:
      `NatsTap.world_view(kind)` in `src/pra/nats/tap.py` — adapter with
      exactly `attach_layout`/`record_reset`/`record_step`, static part on
      first drain + 5 s heartbeat, live part per record in the existing
      seq family; contract tests in
      `tests/contract/test_dash_contract.py` — journal shape, heartbeat,
      rover mounts via `make_rover_body(..., telemetry=adapter)` with zero
      rover edits, byte-identity on/off/bare + rng non-perturbation
      (contracts §1; research R2)
- [x] T006 [US2] View rendering surface: `/run/<id>/state` carries
      `view {kind, static, live}`; `page.html` renders the rover SVG
      (arena, obstacles, pose, client-capped trail) and the
      present-but-unrenderable fallback naming unknown kinds; endpoint
      tests with scripted view payloads incl. unknown kind (contracts
      §3.3; spec US2 scenarios 2–4)

## Phase 5: US3 — the instrument panel with the controls wired (P3)

- [x] T007 [US3] Advanced mode data + control forwarding complete:
      census history / best_dim trajectory / per-dim histogram /
      counters / snapshot notices all served in `/state` and rendered in
      the page's advanced tab; `/run/<id>/ctrl` contract tests for every
      path — inspect, pause (position surfaced), resume, snapshot success,
      every B6 error reply verbatim, transport timeout → `{ok:false}`,
      unknown run 404 (contracts §2.3, §3.2; research R4)
- [x] T008 [P] [US3] Integration: control round-trip through the
      dashboard's own ctrl endpoint during a live run (pause → mirrored
      steps freeze → resume → snapshot id on a configured run), the
      paused-and-resumed run byte-identical to never-paused; advanced-mode
      data completeness for a scaled config over the fake transport
      (contracts §4.3, §5.4)

## Phase 6: US4 — the worked example (P4)

- [x] T009 [US4] `src/pra/dash/cli.py` (`pra-dash`: lazy real transport,
      `--url`/`--port`, prints the URL) + `examples/nats/brain_rover.py`
      (paced rover, tap + view channel + store) +
      `examples/nats/dashboard_demo.py` (find-or-start `-js` server, rover
      brain + dashboard, headless proofs decide the exit code, URL printed)
      + README dashboard section; run the demo against the real stack and
      record the measurement (contracts §6; research R6/R7)

## Phase 7: Polish

- [x] T010 Docs + close-out: GETTING-STARTED §7 gains the dashboard
      (`pra-dash`) and the world-view wiring; ROADMAP B7 marked done with
      exit evidence; JOURNEY.md chapter 29 + "Where things stand" refresh;
      full quality gate green, zero skips, byte-frozen values untouched
      (contracts §5)

## Dependencies

Phase 1 → 2 → 3 (MVP). Phase 4: T005 needs only Phase 1 (tap side);
T006 needs T003 + T005. Phase 5 needs Phase 3 (T007) and Phase 4 for the
rover-flavored round-trip (T008 uses the reference world, so strictly
T003). Phase 6 composes everything. Phase 7 closes.

## Parallel opportunities

T004 alongside T005 (different files, different halves of the fence);
T008 alongside T006. T009 is sequential (composes all).

## Implementation strategy

MVP is Phase 3: any tap-attached run visible in a browser page served
from scripted-traffic-tested endpoints, with the observer proof already
standing. Each later phase is a complete increment (world view, panel +
controls, real-stack example); the gate must be green at the end of every
phase.
