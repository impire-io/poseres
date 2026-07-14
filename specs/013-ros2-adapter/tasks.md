---
description: "Task list for the ROS2 adapter"
---

# Tasks: The ROS2 Adapter

**Input**: Design documents from `/specs/013-ros2-adapter/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅
**Tests**: INCLUDED (repo rule: all green, none skipped — the entire gate
runs on the fake transport, no ROS2 anywhere).

## Phase 1: Setup

- [x] T001 Subpackage skeleton + declaration layer: `src/pra/anatomy/ros2/`
      (`__init__.py` public surface), `specs.py` — `SensorSpec` /
      `ActuatorSpec` validation, `extract_vector` (dotted paths, geometry
      compounds, C-order float64, loud width/type failures),
      `build_fields`; unit tests in `tests/unit/test_ros2_specs.py`
      with duck-typed message objects (contracts C1; research R5)

## Phase 2: Foundational

- [x] T002 Transport seam: `Transport` protocol in
      `src/pra/anatomy/ros2/transport.py` and `FakeTransport` in
      `src/pra/anatomy/ros2/fake.py` — tick-indexed script, ordered
      event journal, `boot_once` guard, optional reset mechanism
      (scripted failure supported); unit tests for journal/guard/reset
      mechanics in `tests/unit/test_ros2_specs.py` (research R1/R6;
      the instrument every later contract test reads)

## Phase 3: US1 — mount a ROS2 world and run the engine on it (P1) 🎯 MVP

- [x] T003 [US1] `src/pra/anatomy/ros2/body.py`: `TopicSensor` (cache,
      loud width check at delivery, read-before-first raises),
      `CommandActuator` (publish preset *i*, `published` counter),
      `Ros2Body(Body)` — `reset()` boot path, `step()` =
      route → publish → one `transport.tick()` → compose,
      `telemetry()`; `Ros2Body.factory(sensors, actuators, transport=)`
      with mount-time size validation (contracts C2.1/C2.2/C2.6, C3.1)
- [x] T004 [P] [US1] Contract tests in
      `tests/contract/test_ros2_contract.py`: EventSource/Body
      conformance over `FakeTransport`, float64 widths, preset routing
      (exactly one publish per step), delivery width violation loud,
      config-mismatch rejection naming both numbers
- [x] T005 [P] [US1] Integration tests in
      `tests/integration/test_ros2_fake_run.py`: full engine run on a
      scripted stream to a normal summary; byte-identity on re-run;
      different scripts → different summaries; engine-rng
      non-perturbation across mount and full run (contracts C5.1, C3.3)

## Phase 4: US2 — the tick-and-staleness semantics, explicit and tested (P2)

- [x] T006 [US2] Staleness policy + startup gate in
      `src/pra/anatomy/ros2/body.py`: delivery sequence vs sampled
      sequence, `staleness_total`/`staleness_streak`/`overwritten`
      counters, streak bound (`stale_limit_ticks`) loud with topic and
      streak, gate ticks without publishing bounded by
      `startup_timeout_ticks` naming silent topics on expiry
      (data-model; research R3)
- [x] T007 [US2] Tick/staleness contract tests in
      `tests/contract/test_ros2_contract.py`: journal shows
      publish-before-tick, sample-after; exactly one tick per step even
      with an extra registered actuator; latest-wins + `overwritten`;
      hold-last-value on silent ticks; gate satisfied/expired paths;
      streak-bound failure; telemetry readable and outside the
      observation (contracts C2.3–C2.5, C2.7)

## Phase 5: US3 — continuous operation for worlds that boot once (P3)

- [x] T008 [US3] Episode-mode wiring + tests: factory rejects
      `episodic` × `can_reset=False` naming the capability and pointing
      at continuous (in `body.py`); episodic `reset()` calls
      `reset_world()` + fresh gate, loud on scripted reset failure;
      integration — continuous full multi-episode schedule over a
      `boot_once` transport (booted exactly once, no reset traffic in
      the journal, normal summary), and continuous + snapshotting hits
      the engine's existing capture-required `RuntimeError` (contracts
      C3.2, C4, C5.4; research R6/R9)

## Phase 6: US4 — the real stack: RclpyTransport + the Gazebo example (P4)

- [x] T009 [US4] `RclpyTransport` in `src/pra/anatomy/ros2/transport.py`:
      one lazy import helper (the monkeypatch point), free-running mode
      (monotonic tick period, `overruns`), stepped mode (step-service
      client, sim-steps-per-tick), typed-message build/extract wiring
      over the R5 helpers; contract test for the missing-rclpy
      ImportError message (distro explanation + pointer to the example)
      via monkeypatched import handle (contracts C6)
- [x] T010 [US4] `examples/ros2/`: `Dockerfile` (pinned ROS2 LTS —
      resolve R8 probe 1: distro/Python pairing, with the in-container
      quality-gate run recorded if `requires-python` is relaxed),
      `world.sdf` (minimal diff-drive robot: 5-beam lidar + odometry +
      cmd_vel), `entrypoint.sh` (sim paused + `ros_gz` bridge — resolve
      R8 probe 2: step-service mechanics), `run.py` (anatomy via public
      API only, continuous stepped run, summary + telemetry print),
      `run-example.sh` + `README.md` (the one documented command)
      (contracts C7)

## Phase 7: Polish

- [x] T011 [P] Propagate: GETTING-STARTED pointer to the ROS2
      quickstart; README worlds/examples mention; ROADMAP C2 updated
      (generalized by the ROS2 adapter — hardware gate story);
      JOURNEY.md chapter + "Where things stand" refresh; memory update
- [x] T012 Quality gate (`./.venv/bin/ruff format --check . &&
      ./.venv/bin/ruff check . && ./.venv/bin/pytest -q`, none
      skipped; `test_baseline_unchanged` byte-identical) → merge to
      `main` → push

## Dependencies

T001 → T002 → T003 → (T004 ∥ T005) → T006 → T007 → T008 → T009 →
T010 → T011 → T012. MVP = T001–T005 (US1: a mounted, running,
byte-reproducible adapter over the fake transport). US4's container
tasks (T010) are the only work that cannot be verified in this repo's
gate; its verification is the documented manual run (contract C7),
and everything it depends on (T001–T009) is gate-verified first.
