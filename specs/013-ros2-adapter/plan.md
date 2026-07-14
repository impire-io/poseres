# Implementation Plan: The ROS2 Adapter

**Branch**: `013-ros2-adapter` | **Date**: 2026-07-14 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/013-ros2-adapter/spec.md`

## Summary

Build the ROS2 body adapter (ROADMAP C2 generalized): mount a declared set
of topic sensors and command actuators as a PRA body, purely additively.
One new subpackage, `src/pra/anatomy/ros2/`, holds the whole adapter in
three transport-separated layers:

1. **`specs.py`** — plain-data anatomy declaration (`SensorSpec`: topic,
   width, message type, field extraction path; `ActuatorSpec`: topic,
   message type, ordered presets as field-value dicts) plus the pure
   helpers that turn duck-typed message objects into float64 vectors and
   preset dicts into field assignments. No ROS2 import anywhere; testable
   with plain objects.
2. **`body.py`** — `TopicSensor` (latest-message cache, staleness and
   overwrite counters, loud width enforcement), `CommandActuator`
   (publish preset *i*, count publishes), and `Ros2Body(Body)` — the tick
   discipline lives here: `step()` routes and publishes, then calls
   `transport.tick()` exactly once, then composes; `reset()` boots (or
   resets) the world through the transport and runs the startup gate
   (bounded ticks until every sensor has a first message). The factory
   validates config sizes and rejects episodic mode over a transport
   without a reset mechanism — at mount time, loudly.
3. **`transport.py` + `fake.py`** — the `Transport` protocol (start,
   subscribe, publish, tick, reset capability, close) with two
   implementations: `FakeTransport` (in-package, numpy-only — scripted
   publishers keyed by tick index; the whole contract suite and the
   quickstart run on it on any machine) and `Rclpy​Transport` (lazy
   rclpy import with a distro-aware error message; free-running mode
   spins one wall-clock period per tick, stepped mode drives a
   simulator's world-control step service).

The named design questions are decided and tested: **time** is a fixed
control-loop tick with publish-before-tick, sample-after ordering
asserted by test (research R2); **staleness** is hold-last-value with
per-sensor counters outside the learning surface, a startup gate before
the first observation, and a loud bound (research R3). The adapter draws
no randomness at all — the engine's stream is untouched by construction,
and identical scripted message streams reproduce byte-identically
(research R4). rclpy ships with a ROS distribution, not from the package
index, so there is **no pip extra**: the quality gate runs entirely on
the fake transport (none skipped), and the real-stack proof is
`examples/ros2/` — a Gazebo differential-drive robot (minimal in-repo
SDF world + `ros_gz` bridge, stepped simulation, continuous episode
mode) launched by one documented command in a pinned-LTS Docker
container (research R8). Persistence follows Doc 06 §5b class 4 exactly
as written: no world-state capture; continuous-mode snapshots hit the
engine's existing loud error, episodic resume is conditional on the
world's reset determinism, both documented and tested (research R9).

## Technical Context

**Language/Version**: Python 3.14 (repo `.venv`); the example container
runs the pinned ROS2 LTS distro's Python — compatibility is R8's probe.
**Dependencies**: numpy (core, unchanged). No new pip dependency and no
new extra: rclpy is not installable from PyPI (research R7); `dev` extra
unchanged. The example pins its ROS2 distro + Gazebo in the Dockerfile.
**Storage**: none (snapshot behavior inherited; no world capture, R9)
**Testing**: pytest — unit (spec validation, field extraction/message
building with duck-typed objects, preset construction), contract (Body
conformance over the fake transport, tick ordering, staleness policy,
startup gate, episode-mode gates, every rejection path incl. the
missing-rclpy message), integration (full engine runs on the fake
transport: byte-identity, continuous single-boot on a boot-once
transport, snapshot loud-error path, engine-rng non-perturbation)
**Project Type**: extends the `pra` package (one new anatomy subpackage
+ tests + containerized example)
**Performance Goals**: fake-transport engine runs complete in seconds
(small schedules, in-memory transport); free-running mode is honestly
1× wall-clock (10 Hz default tick — a deployment mode, not a lab);
stepped simulation runs as fast as the simulator steps
**Constraints**:
- **Byte-frozen reference** (FR-009/SC-001): zero engine/core/config
  edits; `Ros2Body` subclasses `Body` without touching `body.py`; no new
  `Config` fields (tick rate, timeouts, and anatomy live in specs and
  transport construction) — `test_baseline_unchanged` and the entire
  existing suite stay green with recorded values.
- **Adapter determinism** (FR-010/SC-003): the adapter contains no RNG
  use at all; the factory receives the engine generator per the
  `world_factory` signature and never reads or draws from it
  (state-identity asserted by test); byte-identity proven end-to-end on
  scripted streams.
- **Tick discipline** (FR-004): publish strictly before tick, sample
  strictly after — asserted via a transport that journals event order.
- **Staleness policy** (FR-005): hold-last-value + counters + startup
  gate + loud bound; no invented values (a sensor read before its first
  message is an `AnatomyError`, same as `WorldSensor`).
- **No skipped tests** (FR-007/SC-002): everything in the gate runs on
  the fake transport; the rclpy error path is tested by monkeypatching
  the import handle; rclpy-only glue is exercised by the container
  example (stated openly as outside the gate, the inverse of 007's
  in-gate CartPole).
**Scale/Scope**: the example anatomy (5-beam lidar + compass-like
heading, 4 presets) sits inside the validated reference range (obs ≈ 6
vs reference 10; 4 actions = reference 4); no scaling claim is made.

## Constitution Check

Constitution file remains the unfilled template; gating against project
rules (AGENTS.md) and the specs:

| Gate | Requirement | Status |
|---|---|---|
| Regression (FR-009/SC-001) | validated modes byte-identical; core install numpy-only | PASS — additive leaf subpackage; no core/config edits; nothing imports it unless the user does |
| Seam isolation (FR-001) | adapter behind the Body seam; engine untouched | PASS — `Ros2Body(Body)` overrides only `reset`/`step` on its own instances; sensors/actuators are ordinary Doc 02 tools (mid-run `register_sensor` works for free) |
| Determinism (FR-010) | engine rng unperturbed; adapter deterministic on scripted streams | PASS — the adapter has no randomness by construction; state-identity + byte-identity tests |
| Honest semantics (FR-004/FR-005/FR-012) | tick + staleness decisions explicit, consequences documented, rejected alternatives recorded | PASS — decided in spec, recorded in research R2/R3, asserted by ordering/staleness tests |
| Surface hiding (FR-002/FR-003) | only float64 vectors cross the seam; telemetry outside the learning surface | PASS — caches compose to observations; ticks/staleness/overruns/publish counts live on the body object, engine never reads them |
| Optional dependency (FR-007) | quality gate green with no ROS2 present, none skipped | PASS — fake transport in-package; lazy rclpy import; monkeypatched error-path test; no pip extra (impossible to express — documented, R7) |
| Episode modes (FR-006) | continuous single-boot honored; episodic requires reset, rejected loudly otherwise | PASS — mount-time gate in the factory + boot-once guard on the transport; feature-008 contract untouched |
| Persistence honesty (R9) | Doc 06 §5b class 4; nothing written that silently diverges | PASS — no capture protocol, no `snapshot_needs_state`; continuous+snapshot hits the engine's existing loud error (tested) |
| Quality gate | ruff + pytest green, none skipped | PASS — gated in tasks |

## Project Structure

### Documentation (this feature)

```text
specs/013-ros2-adapter/
├── spec.md, plan.md, research.md, data-model.md, quickstart.md
├── checklists/requirements.md
├── contracts/ros2-adapter.md    # transport / body / regression / example contracts
└── tasks.md                     # (/speckit-tasks output)
```

No staged `journey-chapter.md`/`docs-propagation.md` here: this branch
runs alone (the 007 pattern existed to dodge parallel-branch conflicts),
so `JOURNEY.md`, `ROADMAP.md`, and `GETTING-STARTED.md` are edited
directly in the closing commit, per AGENTS.md.

### Source Code (repository root)

```text
src/pra/anatomy/
├── body.py                # untouched (Body, AnatomyError — the seam)
├── gymnasium_body.py      # untouched (the 007 sibling)
└── ros2/                  # NEW — the adapter subpackage
    ├── __init__.py        #   public surface re-exports
    ├── specs.py           #   SensorSpec / ActuatorSpec / extraction & message-building helpers (no ROS2 anywhere)
    ├── body.py            #   TopicSensor, CommandActuator, Ros2Body(Body) + factory (transport-agnostic)
    ├── transport.py       #   Transport protocol; RclpyTransport (lazy import, free-running + stepped)
    └── fake.py            #   FakeTransport — scripted publishers, event journal (numpy-only, shipped)

examples/ros2/             # NEW — the containerized worked example
├── README.md              #   the one documented command + what you will see
├── Dockerfile             #   pinned ROS2 LTS + Gazebo + poseres
├── world.sdf              #   minimal diff-drive robot: lidar + cmd_vel (no TurtleBot3 stack)
├── run.py                 #   anatomy declaration + engine run + telemetry print
└── entrypoint.sh          #   bring up sim (paused) + bridge + run

tests/
├── unit/test_ros2_specs.py          # spec validation, extraction, preset building (duck-typed)
├── contract/test_ros2_contract.py   # conformance, tick ordering, staleness, gate,
│                                    #   episode modes, rejections, missing-rclpy message
└── integration/test_ros2_fake_run.py  # full engine runs on FakeTransport: byte-identity,
                                        #   single-boot, snapshot loud error, rng non-perturbation
```

**Structure Decision**: a subpackage rather than 007's single module
because the adapter has three genuinely separable layers (pure
declaration, transport-agnostic body logic, transports) and the
fake/real transport split is the feature's testability spine (FR-008).
The fake transport ships in-package — it is how the quickstart runs on
machines that cannot install ROS2 (including the maintainer's), and how
tests import it without path hacks. No changes to `core/`, `world/`,
`harness/`, or `config.py` at all.

## Complexity Tracking

No constitution-gate violations to justify. The accepted, documented
debts are named in the spec's Assumptions with owners: continuous
(Box-like) command values and non-vector payloads (images, point
clouds) are future adapter work; reward-as-sensor stays out (Doc 05);
world-state capture for live worlds is impossible by Doc 06 §5b class 4
and stays a documented non-guarantee; the container's Python-version
compatibility is R8's named probe with a recorded fallback.
