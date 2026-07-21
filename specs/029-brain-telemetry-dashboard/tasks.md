# Tasks: Brain Telemetry & Introspection Dashboard

**Input**: Design documents from `/specs/029-brain-telemetry-dashboard/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md,
contracts/brain-subjects.md, quickstart.md

**Tests**: included — the repo's constitution makes the gate the definition
of done, and every acceptance scenario in the spec names a measurable check.
Test-first within each story: the contract/integration test lands with (or
before) the code it proves.

**Organization**: by user story; US1 (channels/metadata) is the foundation
the other stories' panels consume, US2/US3 are independent of each other,
US4 consumes US1's outputs only.

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Foundational (blocking — the wire words)

**Purpose**: the subject vocabulary every story publishes/consumes.

- [ ] T001 Add `brain_anatomy_subject`, `brain_frames_subject`,
      `brain_events_subject` + the three `run_subjects` keys
      (`brain_anatomy`, `brain_frames`, `brain_events`) in
      `src/pra/nats/subjects.py`; extend `__all__`.
- [ ] T002 Contract test for the new subject names, run-scoping, and
      discover-reply keys in `tests/contract/test_brain_subjects.py`
      (FakeBusTransport; mirrors the existing subjects contract tests).

**Checkpoint**: gate green; nothing publishes yet — pure vocabulary.

---

## Phase 2: User Story 1 — named channels + live log (P1) 🎯 MVP

**Goal**: anatomy metadata on the wire from every body that can describe
itself; dashboard shows named per-channel charts + scrolling decoded log.

**Independent test**: fake-transport run publishes `brain.anatomy` at
construction + on heartbeat; dash `/run/<id>/state` carries `brain_meta`
and `steps_window`; bodies without metadata degrade to generic labels.

- [ ] T003 [P] [US1] `Ros2Body.anatomy_meta()` in
      `src/pra/anatomy/ros2/body.py`: groups from live `self._sensors`
      (id/start/width in fixed composition order), actuators from
      `self._actuators` presets (`+`-joined keys, `{}` → `idle`),
      obs_dim/n_actions. Reads live lists so grown tools stay correct.
- [ ] T004 [P] [US1] Rover `anatomy_meta()` in
      `src/pra/examples/rover/world.py` from `SENSOR_PARTS` (+ the grown
      11th channel when present) and the drive's named actions.
- [ ] T005 [P] [US1] `GymnasiumWorld.anatomy_meta()` in
      `src/pra/anatomy/gymnasium_body.py`: one structural `obs` group
      (flattened Box width), actions labeled `a<n>`.
- [ ] T006 [P] [US1] Unit tests for all three in
      `tests/unit/test_anatomy_meta.py`: slice coverage/ordering
      invariants (contiguous, non-overlapping, Σwidth == obs_dim), C1's
      exact groups/labels, rover parts, gym structural form; grown-sensor
      case updates the Ros2Body groups.
- [ ] T007 [US1] Tap capture + publish in `src/pra/nats/tap.py`:
      `_TapWorld.__init__` getattr → `tap._brain_meta_attach(meta)`
      (deep copy once, buffer `brain_meta` event); `_pump` re-publishes on
      the existing view-heartbeat clock; `_drain` serializes the
      `brain_meta` item to `brain.anatomy` (data-model.md payload).
- [ ] T008 [US1] Extend `tests/contract/test_brain_subjects.py`:
      metadata announced at world construction, re-published on the
      heartbeat clock, canonical wire form, no wall-clock keys; a world
      without `anatomy_meta` publishes nothing on the subject.
- [ ] T009 [US1] Dash model in `src/pra/dash/model.py`: `RunModel` gains
      `brain_meta` (latest) + `steps_window` (deque maxlen 600 filled by
      the `tele.step` handler: step/stream/action/obs); `_apply` handles
      `["brain","anatomy"]`; `state_payload()` exposes both keys.
- [ ] T010 [US1] Dash page in `src/pra/dash/page.html`: **Brain** tab
      (third mode); channel strip charts per group + scrolling decoded
      log from `steps_window` × `brain_meta`; generic `ch<n>` labels when
      `brain_meta` is null (FR-012).
- [ ] T011 [US1] Model unit tests in `tests/unit/test_dash_brain_model.py`:
      family handling, malformed payloads → `wire_errors`, windows respect
      maxlen (FR-013 mechanism), state payload keys present/absent
      correctly.

**Checkpoint**: MVP — C1 on the fake transport shows named channels
end-to-end through the dash endpoints.

---

## Phase 3: User Story 2 — the frame table (P2)

**Goal**: complete per-frame rows on the census cadence; dash frame table.

**Independent test**: at every published census, `brain.frames.rows`
count == `tele.census.population` and best_frame matches (SC-002).

- [ ] T012 [US2] Per-frame rows in `src/pra/nats/tap.py`
      `_publish_census`: same walk emits `brain.frames` (rows with
      id/dim/age/cand/recon/pred/effort/score, plus population,
      best_frame, steps, seq); `tele.census` payload byte-unchanged.
- [ ] T013 [US2] Contract/integration test in
      `tests/integration/test_brain_telemetry_run.py`: short reference
      run on FakeBusTransport — rows==census population + same best
      frame at 100% of censuses; scores equal the engine scorer's own
      values for the same states.
- [ ] T014 [US2] Dash model+page: `frames_latest` in
      `src/pra/dash/model.py` (`["brain","frames"]` handler + payload
      key) and the frame table (id/dim/age/errors/score, best marked,
      candidate flag) in the Brain tab of `src/pra/dash/page.html`.

**Checkpoint**: frame population visible frame-by-frame, provably
consistent with the aggregate census.

---

## Phase 4: User Story 3 — births and deaths (P3)

**Goal**: spawn/evict events, exactly once, in order; dash timeline.

**Independent test**: run with known churn — every register/unregister
appears exactly once, seq-ordered, Σspawn−Σevict == final population
(SC-003); engine outputs byte-identical with and without the tap bus.

- [ ] T015 [US3] `_TapBus` in `src/pra/nats/tap.py`: delegates
      `register`/`unregister`/`publish`/`subscribers` verbatim to the
      stock `InMemorySyncBus`, mirroring `spawn`/`evict` events
      (frame_id, steps, seq) into the buffer on the engine thread;
      `bus_factory` returns it; `_drain` serializes to `brain.events`.
- [ ] T016 [US3] Extend `tests/integration/test_brain_telemetry_run.py`:
      churn run asserts exactly-once/ordering/reconciliation from
      boot-attach AND from a mid-run attach point (spawns include
      boot registration per contract §2.3); tap-vs-no-tap engine output
      byte-equivalence (the existing tap-equivalence pattern).
- [ ] T017 [US3] Dash model+page: `events` window (deque maxlen 512) in
      `src/pra/dash/model.py` + lifecycle timeline (event list with
      step marks, newest last) in `src/pra/dash/page.html`.

**Checkpoint**: population churn answerable at a glance; honesty bars
(SC-003) proven in the gate.

---

## Phase 5: User Story 4 — the anatomy, drawn (P3)

**Goal**: the graphical body schematic, generated from metadata alone.

**Independent test**: schematic renders for reference (fallback note),
rover, and Minecraft metadata with zero body-specific dashboard code;
actuator highlight follows the newest step's action.

- [ ] T018 [US4] Schematic renderer in `src/pra/dash/page.html`: SVG
      generated from `brain_meta` — sensor-group boxes (per-channel
      activity bars from `steps_window` movement), actuator nodes
      (label + id), newest-action highlight; layout is metadata-driven
      (groups left, body hub center, actuators right); null `brain_meta`
      → the existing note-style fallback.
- [ ] T019 [US4] Extend `tests/integration/test_dash_live.py`: state
      endpoint carries every input the schematic needs (brain_meta,
      steps_window with actions) for a live fake-transport run; page
      body contains the Brain-tab renderer markers.

**Checkpoint**: all four spec panels live.

---

## Phase 6: Polish & cross-cutting

- [ ] T020 [P] Docs: extend `examples/nats/README.md` (watching the brain
      family by hand: `nats sub 'pra.v1.run.*.brain.>'`) and
      `examples/minecraft/README.md` (the Brain tab in the watching
      section).
- [ ] T021 Full gate: `./.venv/bin/ruff format --check . &&
      ./.venv/bin/ruff check . && ./.venv/bin/pytest -q` — all green,
      none skipped; `test_baseline_unchanged.py` untouched is the
      constitution-I witness.
- [ ] T022 Live verification (quickstart.md): C1 stack via
      `examples/minecraft/up.sh`, Brain tab shows named channels, frame
      table, timeline, schematic against the real broker + world;
      reference-world run shows the generic fallback.

## Dependencies & execution order

- Phase 1 blocks everything (wire words).
- US1 (Phase 2) is the MVP and blocks US4 (the schematic consumes
  brain_meta + steps_window). T003/T004/T005/T006 are parallel-safe
  (different files); T007 depends on T001; T009 on T007's payload shape;
  T010 on T009; T011 on T009.
- US2 (Phase 3) and US3 (Phase 4) are independent of each other and of
  US4; both depend on Phase 1 and touch `tap.py`/`model.py`/`page.html`
  sequentially with US1's tasks (same files — do not parallelize across
  stories in those three files).
- Polish (Phase 6) last; T020 is parallel-safe.

## Implementation strategy

MVP = Phase 1 + Phase 2 (US1): named channels end-to-end. Then US2 →
US3 → US4 in order (US2/US3 could swap; both are small once the tap
patterns from US1 exist). One commit per phase, gate green at every
checkpoint, live C1 verification once at the end (T022).
