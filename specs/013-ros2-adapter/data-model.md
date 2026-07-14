# Data Model: The ROS2 Adapter

Phase 1 of `plan.md`. Entities, fields, validation, and state — all
transport-agnostic unless marked. Nothing here touches engine or core
state; every entity is adapter-local.

## SensorSpec (plain data, `specs.py`)

| Field | Type | Meaning | Validation (at declaration) |
|---|---|---|---|
| `id` | str | body tool id | non-empty; uniqueness enforced by `Body` |
| `topic` | str | topic to subscribe | non-empty |
| `width` | int | declared vector width | ≥ 1 (Doc 02 sensor contract) |
| `msg_type` | str | message type name, e.g. `"sensor_msgs/msg/LaserScan"` | non-empty; resolved only by `RclpyTransport` |
| `extract` | str \| callable | dotted attribute path into the message (default: whole payload), or an escape-hatch callable | path syntax checked at declaration; result width checked at every delivery |

## ActuatorSpec (plain data, `specs.py`)

| Field | Type | Meaning | Validation (at declaration) |
|---|---|---|---|
| `id` | str | body tool id | non-empty |
| `topic` | str | topic to publish | non-empty |
| `msg_type` | str | message type name, e.g. `"geometry_msgs/msg/Twist"` | non-empty; resolved only by `RclpyTransport` |
| `presets` | list[dict[str, float]] | ordered field-path → value dicts; index *i* is local action *i* | ≥ 1 preset; keys are dotted paths; values numeric |

## TopicSensor (`body.py`; implements Doc 02 `Sensor`)

State (all adapter-local, outside the learning surface except the cache):

| Field | Meaning |
|---|---|
| `cache: ndarray \| None` | latest extracted float64 vector; `None` until first delivery (read then raises `AnatomyError`, the `WorldSensor` contract) |
| `deliveries` | total messages delivered |
| `overwritten` | deliveries beyond the first within a tick (latest-wins evidence) |
| `staleness_total` | samples with no fresh message since the previous sample |
| `staleness_streak` | consecutive such samples; reset by any fresh delivery |
| `_seq / _seen_seq` | delivery sequence vs last-sampled sequence (the staleness detector) |

Transitions: `deliver(payload)` → extract → width check (loud fail
naming topic + both shapes) → cache, `_seq += 1`. `read()` (called by
`Body._compose` at sample time) → staleness accounting → streak-bound
check (loud fail naming topic + streak) → return cache.

## CommandActuator (`body.py`; implements Doc 02 `Actuator`)

| Field | Meaning |
|---|---|
| `spec` | its `ActuatorSpec` |
| `published` | count of publishes (telemetry) |

`apply(i)` → `transport.publish(topic, presets[i])`. Returns nothing
(Doc 02 §4.2). Does **not** tick (R1 — the tick is the body's).

## Ros2Body (`body.py`; subclasses `Body`, overrides `reset`/`step` only)

| Field | Meaning |
|---|---|
| `transport` | the mounted `Transport` |
| `ticks` | control ticks advanced (telemetry) |
| `startup_timeout_ticks` | gate bound (default 100) |
| `stale_limit_ticks` | per-sensor streak bound (default 50), pushed into each `TopicSensor` |

Transitions:
- `reset()`: first call → `transport.start()` + subscribe all sensors;
  later calls → `transport.reset_world()` (only reachable in episodic
  mode; the factory already rejected the bad pairing). Then the
  **startup gate**: tick without publishing until every sensor has
  ≥ 1 message, bounded by `startup_timeout_ticks` (expiry names silent
  topics). Returns the composed first observation.
- `step(a)`: route (existing `Body.route`) → `actuator.apply(local)`
  (publish) → `transport.tick()` (`ticks += 1`) → compose (sample).
- `telemetry()`: dict of ticks, overruns (from transport), per-sensor
  deliveries/overwritten/staleness, per-actuator publishes — never read
  by the engine.

Factory validation (mount time, all `AnatomyError`): config
`obs_dim`/`n_actions` vs declared anatomy (both numbers named);
`episode_mode="episodic"` with `transport.can_reset == False` (names
the missing capability, points at continuous); empty sensor or actuator
lists (existing `Body` contract).

## Transport (protocol, `transport.py`)

| Member | Contract |
|---|---|
| `start()` | boot the connection/world; **raises on a second call** (single-boot honesty, R6) |
| `subscribe(topic, deliver)` | register a delivery callback (called only inside `start`/`tick`/gate pumping) |
| `publish(topic, preset)` | send preset (real: typed message built from field paths; fake: journaled verbatim) |
| `tick()` | advance exactly one control tick, delivering messages (stepped: issue step command, wait for completion; free-running: one wall-clock period; fake: advance script index) |
| `can_reset` | bool — a declared reset mechanism exists |
| `reset_world()` | perform the reset; **loud failure/timeout**; only valid if `can_reset` |
| `overruns` | free-running deadline misses (0 for stepped/fake) |
| `close()` | release resources; idempotent |

### FakeTransport (`fake.py`, shipped)

Script: `{topic: {tick_index: [payload, ...]}}` — payloads delivered
in order during that tick. Journal: ordered event list
(`("publish", topic, preset)`, `("tick", k)`, `("deliver", topic)`) —
the instrument that proves FR-004's ordering. Flags: `boot_once`
(second `start()` raises — the 008 guard-world pattern),
`resettable` (`can_reset`; `reset_world` rewinds the script index or
raises if scripted to fail).

### RclpyTransport (`transport.py`, lazy rclpy)

Modes: `stepped` (a step-service client; sim-steps-per-tick constant)
| `free_running` (tick period seconds; monotonic deadline; `overruns`).
All rclpy symbols resolved inside `start()` via one import helper
(monkeypatch point for the missing-dependency error test).

## Telemetry record (returned by `Ros2Body.telemetry()`)

Plain dict: `{"ticks", "overruns", "sensors": {id: {"deliveries",
"overwritten", "staleness_total", "staleness_streak"}}, "actuators":
{id: {"published"}}}`. Printed by the worked example; asserted by
contract tests; never crosses the learning seam.
