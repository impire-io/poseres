# Quickstart: The ROS2 Adapter

Two on-ramps, honestly ordered: the fake transport runs on *any*
machine (it is how the adapter is tested, and the fastest way to see
the tick/staleness mechanics); the real stack runs in the containerized
example (Linux + Docker).

## 1. Any machine: mount a scripted robot on the fake transport

```python
import numpy as np
from pra.config import Config
from pra.core.engine import Engine
from pra.anatomy.ros2 import (
    SensorSpec, ActuatorSpec, Ros2Body, FakeTransport,
)

# The robot's anatomy, as data. A 5-beam lidar and a heading channel
# (obs 6), and four velocity presets (actions 4).
sensors = [
    SensorSpec(id="lidar", topic="/scan", width=5,
               msg_type="sensor_msgs/msg/LaserScan", extract="ranges"),
    SensorSpec(id="heading", topic="/heading", width=1,
               msg_type="std_msgs/msg/Float64", extract="data"),
]
actuators = [
    ActuatorSpec(id="drive", topic="/cmd_vel",
                 msg_type="geometry_msgs/msg/Twist",
                 presets=[{"linear.x": 0.2},              # forward
                          {"angular.z": 0.6},             # left
                          {"angular.z": -0.6},            # right
                          {}]),                           # stop
]

# A scripted world: payloads per topic per tick. (Your tests will look
# like this too — the fake transport is the adapter's instrument.)
transport = FakeTransport(script={
    "/scan":    {k: [np.full(5, 1.0 + 0.01 * k)] for k in range(5000)},
    "/heading": {k: [np.array([0.1 * (k % 63)])] for k in range(0, 5000, 3)},
})  # heading publishes every 3rd tick -> watch its staleness counters

cfg = Config(obs_dim=6, n_actions=4, episode_mode="continuous")
engine = Engine(world_factory=Ros2Body.factory(sensors, actuators,
                                               transport=transport))
summary = engine.run(cfg, seed=1)
```

What to look at afterwards: the run summary (the same honest numbers as
every PRA world), and the adapter telemetry — `body.telemetry()` shows
ticks, per-sensor `deliveries` / `staleness_total` / `overwritten`, and
per-actuator `published`. The heading sensor's staleness counters will
be ≈ ⅔ of ticks: that is the hold-last-value policy, measured, not
hidden.

Notes:
- **Continuous mode** is the native robotics mode (single boot, virtual
  episodes — feature 008). Episodic mode needs a transport with a reset
  mechanism (`can_reset`); mounting the wrong pairing fails at mount
  time with the message telling you so.
- Same script + same config + same seed → byte-identical summaries.
  That claim is about the *adapter*; a live transport's replayability
  belongs to the world (see §3).

## 2. Real stack: the containerized Gazebo example

On a machine with Docker (Linux recommended; the image is Linux):

```bash
cd examples/ros2
./run-example.sh        # docker build + docker run, documented in README.md
```

You get: a pinned ROS2 LTS + Gazebo container, a minimal
differential-drive robot (5-beam lidar, odometry heading, cmd_vel) in a
paused world, and PRA driving it in **stepped simulation** — the
transport advances the sim one control tick at a time, so the run is
replayable to the extent the simulator is deterministic. The run prints
the per-seed summary and the full adapter telemetry.

To point the adapter at *your* robot instead: source your ROS2
environment, declare your anatomy (as in §1 — the specs are identical),
and construct the real transport:

```python
from pra.anatomy.ros2 import RclpyTransport
transport = RclpyTransport(mode="free_running", tick_period=0.1)  # 10 Hz
```

`RclpyTransport(mode="stepped", ...)` needs the simulator's step
service (see the example's entrypoint for the Gazebo wiring).

## 3. The honest fine print

- **Free-running mode is not reproducible** — message timing is real.
  This is PRA's first openly non-reproducible mode (Doc 06 §5b class
  4). The `overruns` counter tells you when the control loop missed
  its deadline.
- **Snapshots**: the brain's state snapshots exactly, always. A
  continuous-mode ROS2 run with snapshotting enabled fails loudly at
  run start (the engine requires world capture it cannot have) — for a
  robot deployment, persistence means the brain's snapshot; the world
  re-attaches at boot. Episodic sim runs resume conditional on the
  sim's own reset determinism.
- **rclpy is not pip-installable.** There is deliberately no
  `poseres[ros2]` extra — rclpy ships with a ROS2 distribution. The
  fake transport (§1) and the container (§2) are the two supported
  ways in; using `RclpyTransport` without a sourced ROS2 environment
  tells you exactly that.
- **What a step means**: publish the chosen preset → advance exactly
  one control tick → sample every sensor's latest cached message.
  Sensors slower than the tick rate repeat their last value (counted);
  faster ones are subsampled (counted). The tick rate is part of your
  experiment's meaning — declare it, don't inherit it.
