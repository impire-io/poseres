---
description: "Task list for the external bus backend (NATS at the seams)"
---

# Tasks: The External Bus Backend (NATS at the Seams)

**Input**: Design documents from `/specs/014-nats-bus-backend/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅
**Tests**: INCLUDED (repo rule: all green, none skipped — the entire gate
runs on the fake transport, no NATS library, no server).

## Phase 1: Setup

- [x] T001 Subpackage skeleton + the scheme: `src/pra/nats/`
      (`__init__.py` public surface), `subjects.py` — subject builders
      for every family in data-model §2, `run_id` validation (token
      rules, uuid4 default off the engine's stream), canonical-JSON
      payload helpers (recorder discipline: fixed key order, compact
      separators, ascii, no wall-clock); `pyproject.toml` gains the
      `nats = ["nats-py>=2.9"]` extra (the only edit outside new
      dirs); unit tests in `tests/unit/test_nats_subjects.py` — scheme
      names, id rejection paths, payload byte-determinism (contracts
      §5.2; research R4)

## Phase 2: Foundational

- [x] T002 Transport seam: `BusTransport` protocol in
      `src/pra/nats/transport.py` (publish / subscribe /
      serve_requests / request / object_put / object_get /
      object_list / object_delete / healthy / counters / close) and
      `FakeBusTransport` in `src/pra/nats/fake.py` — ordered
      subject journal, synchronous subscription dispatch, scriptable
      request/reply, in-memory object store, `set_down()`/`set_up()`
      with `publish_failures`/`reconnects` counting; unit tests for
      journal order, down-state fire-and-forget vs loud explicit ops,
      and object-store mechanics in
      `tests/unit/test_nats_subjects.py` (contracts §1; research R7 —
      the instrument every later contract test reads)

## Phase 3: US1 — watch a live brain from another process (P1) 🎯 MVP

- [x] T003 [US1] The tap in `src/pra/nats/tap.py`: `NatsTap`
      (run identity, counters, bounded mirror deque + tap-wide
      sequence), `world_factory()` returning delegating `_TapWorld`
      wrappers (per-step mirror of action/obs copies, episode/boot
      events, stream index by construction order, `__getattr__`
      passthrough for `n_actions`/`snapshot_needs_state`/
      `state_dict`/`apply_pending_tools`), `bus_factory` capture
      (stock `InMemorySyncBus` returned, `FrameStore` reference
      kept), the daemon publisher thread (50 ms drain, drop
      derivation from sequence gaps, census at 500 ms via the
      viewer's frame_states-on-copies discipline with last-good
      fallback), `start()` (status `started` with anatomy numbers)
      and `finish(summary)` (status `completed` with the canonical
      summary) (research R1–R3; data-model §3, §5, §6)
- [x] T004 [P] [US1] Contract tests in
      `tests/contract/test_nats_contract.py`: mirror fidelity (journal
      reproduces exact stream/episode/step/action sequence with obs
      values matching the world's), payload byte-determinism across
      identical runs, census derived only off-path with torn-read
      fallback, status lifecycle, counters present and outside the
      learning surface (contracts §2.3, §2.5–§2.7)
- [x] T005 [P] [US1] Integration tests in
      `tests/integration/test_nats_fake_run.py`: byte-identity
      attached vs absent (reference world; multi-stream continuous
      run), engine-rng bit-state non-perturbation, no-backpressure —
      tiny buffer + stalled publisher and transport-down-for-life both
      complete byte-identical with `events_dropped`/`publish_failures`
      counted (contracts §2.1–§2.4)

## Phase 4: US2 — snapshots through the object store (P2)

- [x] T006 [US2] `NatsSnapshotStore` in `src/pra/nats/store.py`:
      four-method `SnapshotStore` protocol over the transport's
      object-store ops — ids via existing `snapshot_id_for`, canonical
      metadata in the object description, `list()` newest-first,
      bucket default `pra-snapshots` (write creates, read/list/delete
      loud on absence), every failure a `RuntimeError` naming store /
      operation / id, bounded timeout (research R6; data-model §8)
- [x] T007 [US2] [P] Store contract + integration tests: the existing
      store-contract expectations run against a fake-backed
      `NatsSnapshotStore` (write/read/list/delete, metadata round-trip,
      newest-first) in `tests/contract/test_nats_contract.py`;
      byte-exact blob round-trip at reference and scaled-run size, and
      cross-store resume equivalence (resume from fetched blob ==
      resume from `FileSnapshotStore` copy, byte-compared summaries)
      in `tests/integration/test_nats_fake_run.py` (contracts §4)

## Phase 5: US3 — the control plane (P3)

- [x] T008 [US3] Control plane in `src/pra/nats/control.py` + the gate
      in `tap.py`: pause `threading.Event` checked at wrapped
      `step()`/`reset()` entry; `serve_requests` listener answering
      `inspect` (read-only, answers in every state), `pause`/`resume`
      (boundary-exact, idempotent, position in reply), `snapshot`
      (deferred fulfillment via `tap.wrap_store` observing the
      engine's C4 write — snapshot notices on `tele.snapshot`, pending
      requests answered with the new id; immediate error naming
      missing store/cadence; error on completion-first), discover
      replies, error replies for non-JSON / non-object / unknown cmd
      (research R2/R5; data-model §4, §7)
- [x] T009 [US3] [P] Control tests: contract —
      pause quiescence in the journal, idempotence, every enumerated
      error reply, deferred snapshot fulfillment and both error paths,
      discover reply shape (in `tests/contract/test_nats_contract.py`);
      integration — paused-then-resumed run byte-identical to
      never-paused (steppable world), snapshot-on-request id matches
      the store's write during a live run (in
      `tests/integration/test_nats_fake_run.py`) (contracts §3)

## Phase 6: US4 — the real binding and the worked example (P4)

- [x] T010 [US4] `NatsTransport` in `src/pra/nats/transport.py`: one
      lazy import helper (the monkeypatch point) raising the
      `pip install "poseres[nats]"` error; one asyncio loop on a
      daemon thread — `publish` via `call_soon_threadsafe`
      (non-blocking), `request`/object-store ops via
      `run_coroutine_threadsafe(...).result(timeout)` (loud),
      subscription/request handlers dispatched into thread-safe tap
      state, reconnect counting, idempotent `close()`; contract test
      for the missing-library error via monkeypatched import handle
      (contracts §5.1; research R7)
- [x] T011 [US4] `examples/nats/`: `brain.py` (seeded run, tap + fake
      cadence-sized `NatsSnapshotStore` via `wrap_store`, finish
      publishing the summary), `watch.py` (subscribe `tele.>`, print
      live telemetry; inspect → pause → resume → snapshot with
      cadence-sized timeout; pull the snapshot back and byte-verify),
      `demo.py` (find `nats-server` else `docker run … nats:latest
      -js` else a clear error naming both; run both processes; exit
      zero only on all three proofs), `README.md` (the one documented
      command + what you will see) (contracts §6; research R8)

## Phase 7: Polish

- [x] T012 Docs propagation + close-out: Doc 06 §5b feature-014
      paragraph (telemetry-out observer-safe; pause class-preserving
      with the free-running caveat; store-backed snapshots inherit
      their world's class; experience-in named class 4, out of scope)
      per research R9; ROADMAP B6 marked done with exit evidence;
      JOURNEY.md chapter 28 + "Where things stand" refresh; full
      quality gate (`ruff format --check`, `ruff check`, `pytest -q`)
      green with zero skips and the recorded reference values
      untouched (contracts §5.2–§5.3)

## Dependencies

- Phase 1 → Phase 2 → Phase 3 (US1, MVP).
- Phase 4 (US2): T006 needs only Phase 2; T007's resume-equivalence
  needs T003 only for the wrapper-free store path — runs after T006.
- Phase 5 (US3): needs T003 (the tap and its gate); the snapshot
  command needs T006 (a store to wrap).
- Phase 6 (US4): T010 needs the protocol (T002) frozen by the passing
  Phases 3–5 suites; T011 composes every prior surface.
- Phase 7 closes the branch.

## Parallel opportunities

- T004 and T005 (different test files) once T003 lands.
- T006 can start alongside Phase 3 (it depends only on T002).
- T009's two test files parallel once T008 lands; T010 and T011 are
  sequential (the example uses the real transport).

## Implementation strategy

MVP is Phase 3: a live brain watched from a second process over the
fake transport with byte-identity proven — the feature's core claim,
independently demonstrable. Each later phase is a complete increment
(store, control, real stack + example), and the gate must be green at
the end of every phase, not only at close-out.
