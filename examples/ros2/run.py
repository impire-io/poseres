"""PRA drives a simulated rover over ROS2 — the worked example (feature 013).

This script runs *inside* the example container (see README.md for the one
command that builds and runs it): Gazebo holds a paused diff-drive robot, the
ros_gz bridge exposes its lidar, odometry, and velocity command as ROS2
topics, and PRA mounts them as a body. The transport runs in **stepped**
mode — every engine step publishes a velocity preset, advances the simulator
exactly 100 physics steps (0.1 s of simulated time), and samples the sensor
caches — so the world only moves when the brain acts (the instrument-panel
principle; ROADMAP operating principle 2).

Three honest notes, in the spirit of the CartPole example:

1. **This proves plumbing, not science.** The schedule is small (a few
   hundred steps) and the policy is the pinned random baseline: what you
   watch is the adapter's contract working against a real ROS2 stack —
   observations composed from live topics, presets landing as Twist
   messages — plus the run summary and the adapter's own telemetry.
2. **Continuous mode, single boot.** The world is never reset; virtual
   episode boundaries segment the unbroken stream (feature 008). That is
   the deployment pattern real hardware needs.
3. **Reproducibility is the world's promise here, not the adapter's.** The
   adapter is deterministic (proven against scripted transports in the test
   suite); a Gazebo run replays only to the extent the simulator is
   deterministic (Doc 06 §5b).
"""

import math

from pra.anatomy.ros2 import ActuatorSpec, RclpyTransport, Ros2Body, SensorSpec
from pra.config import Config
from pra.core.engine import Engine

# --- the anatomy, as data ----------------------------------------------------
# The lidar reports 5 beams; beams that see nothing return +inf, beams below
# the minimum range return -inf (bumping a wall), and invalid returns are
# NaN. The adapter rejects non-finite values loudly — the learning surface
# has no missing-data semantics — so the spec sanitizes them in the callable
# escape hatch: declared, visible, and honest about what the brain sees.
LIDAR_MIN, LIDAR_MAX = 0.1, 10.0


def clamp_ranges(msg):
    # +inf (no hit) -> max range; -inf (closer than min range) -> min range;
    # NaN (invalid return) -> max range, the no-information default.
    return [LIDAR_MAX if math.isnan(r) else min(max(r, LIDAR_MIN), LIDAR_MAX) for r in msg.ranges]


sensors = [
    SensorSpec(
        id="lidar",
        topic="/scan",
        width=5,
        msg_type="sensor_msgs/msg/LaserScan",
        extract=clamp_ranges,
    ),
    SensorSpec(
        id="position",
        topic="/odom",
        width=3,
        msg_type="nav_msgs/msg/Odometry",
        extract="pose.pose.position",
    ),
    SensorSpec(
        id="orientation",
        topic="/odom",
        width=4,
        msg_type="nav_msgs/msg/Odometry",
        extract="pose.pose.orientation",
    ),
]
actuators = [
    ActuatorSpec(
        id="drive",
        topic="/cmd_vel",
        msg_type="geometry_msgs/msg/Twist",
        presets=(
            {"linear.x": 0.3},  # forward
            {"angular.z": 0.8},  # spin left
            {"angular.z": -0.8},  # spin right
            {},  # stop (all Twist defaults)
        ),
    ),
]

# --- the stepped transport (R8 probe 2, resolved: the ros_gz world-control
# service bridged as ros_gz_interfaces/srv/ControlWorld; multi_step advances
# the paused world and re-pauses it) -------------------------------------------
transport = RclpyTransport(
    mode="stepped",
    step_service="/world/pra_world/control",
    step_service_type="ros_gz_interfaces/srv/ControlWorld",
    step_fields={"world_control.multi_step": 100},  # 100 x 1 ms sim steps per tick
    service_timeout=30.0,  # first step waits for the sim to come up
    drain_period=0.05,  # let bridged messages land after each step
)

# --- a small schedule: the plumbing proof, not a science claim ------------------
config = Config(
    obs_dim=12,
    n_actions=4,
    episode_mode="continuous",  # single boot; the robot is never reset
    warmup_episodes=2,
    n_cycles=3,
    episodes_per_cycle=2,
    steps_per_episode=40,
    horizon_checkpoints=(1, 3),
)

mounted = []
inner = Ros2Body.factory(sensors, actuators, transport=transport)


def factory(cfg, rng):
    body = inner(cfg, rng)
    mounted.append(body)
    return body


print("PRA on a Gazebo rover (stepped, continuous, seed 1) ...", flush=True)
summary = Engine(config, world_factory=factory).run(seed=1)
body = mounted[0]

print()
print(f"  observation steps:   {summary.observation_steps}")
print(f"  prediction error:    {summary.pred_error_early:.4f} early")
print(f"                   ->  {summary.pred_error_late:.4f} late")
print(f"  surviving frames:    {summary.final_population}")
print()
telemetry = body.telemetry()
print(f"  control ticks:       {telemetry['ticks']}")
print(f"  overruns:            {telemetry['overruns']} (stepped mode: always 0)")
for name, counts in telemetry["sensors"].items():
    print(
        f"  sensor {name:12s} deliveries={counts['deliveries']:5d}  "
        f"stale={counts['staleness_total']:5d}  overwritten={counts['overwritten']:5d}"
    )
for name, counts in telemetry["actuators"].items():
    print(f"  actuator {name:10s} published={counts['published']}")
body.close()
print()
print("Done. The adapter contract this run exercised is the one the test")
print("suite proves against the fake transport — see")
print("specs/013-ros2-adapter/quickstart.md to point PRA at your own robot.")
