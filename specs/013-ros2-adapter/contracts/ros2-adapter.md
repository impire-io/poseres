# Contracts: The ROS2 Adapter

The testable promises of feature 013, grouped by seam. Every line here
maps to at least one test in the feature's suites (unit:
`tests/unit/test_ros2_specs.py`; contract:
`tests/contract/test_ros2_contract.py`; integration:
`tests/integration/test_ros2_fake_run.py`). "Loud" always means a
raised `AnatomyError` (or the engine's own error, where noted) whose
message names the offending thing.

## C1 — Declaration contract (`specs.py`)

- C1.1 `SensorSpec`/`ActuatorSpec` validate at construction: non-empty
  id/topic/msg_type; width ≥ 1; ≥ 1 preset; numeric preset values;
  well-formed dotted paths.
- C1.2 `extract_vector(msg, spec)` resolves the dotted path against any
  duck-typed object, flattens C-order to float64, expands the geometry
  compounds (Vector3/Point → x,y,z; Quaternion → x,y,z,w) recursively,
  and fails loudly when the result is not the declared width or not
  numeric.
- C1.3 Declaration never imports ROS2 — the module imports cleanly on a
  machine with no ROS2 anywhere.

## C2 — Body contract (`body.py` over any transport)

- C2.1 `Ros2Body` satisfies the `EventSource` surface (`reset`, `step`,
  `obs_dim`, `n_actions`) and composes through the unmodified Doc 02
  `Body` (fixed order, width enforcement, routing, duplicate-id
  rejection, tool registration applied at slow-loop boundaries).
- C2.2 Observations are float64 vectors of the declared total width;
  local action *i* publishes exactly preset *i* of the routed actuator,
  once.
- C2.3 **Tick ordering** (the named decision): within one `step`, the
  journal shows publish strictly before the tick advance, and sampling
  reads caches only after it. Exactly one tick per step regardless of
  which actuator the action routed to.
- C2.4 **Staleness policy**: silent tick → cache held, staleness
  counters advance; fresh delivery → streak resets; > 1 delivery in a
  tick → latest wins, `overwritten` counts; streak > `stale_limit_ticks`
  → loud, naming topic and streak. No zero/NaN filling anywhere.
- C2.5 **Startup gate**: first observation composes only after every
  sensor has ≥ 1 message; gate ticks are bounded by
  `startup_timeout_ticks`; expiry is loud and names each still-silent
  topic. A `TopicSensor` read before any delivery is loud (the
  `WorldSensor` contract).
- C2.6 Width violation at delivery is loud, naming topic, declared and
  received widths — never truncation or padding.
- C2.7 Telemetry (`ticks`, `overruns`, per-sensor and per-actuator
  counters) is readable after a run and is never part of an
  observation.

## C3 — Mount contract (`Ros2Body.factory`)

- C3.1 Config mismatch (`obs_dim`/`n_actions` vs declared anatomy) is
  loud at mount, naming both numbers.
- C3.2 `episode_mode="episodic"` over `can_reset=False` is loud at
  mount, naming the missing capability and pointing at continuous mode.
- C3.3 The factory conforms to `world_factory(cfg, rng)` and never
  draws from or perturbs `rng` (bit-generator state identical before
  and after mount and across a full run).

## C4 — Episode-mode contract

- C4.1 Continuous: a boot-once transport (second `start()` raises) runs
  a full multi-episode schedule to a normal summary — the world booted
  exactly once, no reset traffic in the journal.
- C4.2 Episodic (resettable transport): each episode begins with
  `reset_world()` + a fresh startup gate; a scripted reset failure or
  timeout is loud, naming the mechanism.

## C5 — Determinism & regression contract

- C5.1 Two engine runs over the same fake-transport script, same config
  and seed: byte-identical serialized summaries. (Different scripts:
  different summaries — the world actually reaches the brain.)
- C5.2 The full pre-existing suite passes byte-identically
  (`test_baseline_unchanged` guards seed 1); no engine/core/config
  edits exist on the branch (adapter + tests + example + docs only).
- C5.3 Core install stays numpy-only; no new pyproject dependency or
  extra (R7 — none can honestly exist).
- C5.4 Snapshots: a continuous-mode run with snapshotting enabled fails
  at run start with the engine's existing capture-required error (the
  Doc 06 §5b class-4 behavior, asserted through the adapter); the
  adapter declares no `snapshot_needs_state` and no capture protocol.

## C6 — Dependency contract (`transport.py`)

- C6.1 Importing the subpackage and declaring anatomy requires no ROS2.
- C6.2 Constructing/starting `RclpyTransport` without rclpy raises an
  ImportError that explains rclpy ships with a ROS2 distribution (not
  from the package index) and points at the containerized example —
  tested by monkeypatching the import helper, never by skipping.

## C7 — Worked-example contract (`examples/ros2/`, manual — outside the gate)

- C7.1 One documented command on a Docker-equipped machine: container
  builds (pinned ROS2 LTS + Gazebo + bridge), sim starts paused,
  stepped continuous run completes, per-seed summary + telemetry print.
- C7.2 The example declares its anatomy with public API only (specs +
  factory) — no adapter edits (SC-006).
- C7.3 The Dockerfile records R8's resolved probes: the distro/Python
  pairing (with the quality-gate suite run in-container if
  `requires-python` was relaxed) and the step-service mechanics.
