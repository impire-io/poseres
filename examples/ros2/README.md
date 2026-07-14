# PRA on a Gazebo rover, over ROS2

The worked example for the ROS2 adapter (feature 013): a minimal
differential-drive robot with a 5-beam lidar and odometry, simulated in
Gazebo, bridged to ROS2, and driven by the unchanged PRA engine in
**stepped simulation** and **continuous mode** — the world moves only when
the brain acts, and it boots exactly once.

## Run it

On any machine with Docker (Linux recommended — the image is Linux):

```bash
examples/ros2/run-example.sh
```

That builds the image (pinned ROS 2 Jazzy + Gazebo Harmonic via `ros_gz`;
the first build downloads a few GB) and runs the example. You will see the
engine's per-seed summary (prediction error early → late, surviving frames)
followed by the adapter's telemetry: control ticks, per-sensor deliveries /
staleness / overwrites, and published commands.

## What this proves (and what it doesn't)

- **Proves**: the adapter contract — topic sensors composed into
  observations, discrete actions landing as `Twist` presets, the
  publish → step-the-sim → sample tick discipline, the startup gate, and
  single-boot continuous operation — working against a real ROS2 stack.
  It is the integration proof for the contract the test suite pins against
  the in-repo fake transport (`tests/contract/test_ros2_contract.py`).
- **Does not prove**: any learning claim. The schedule is a few hundred
  steps under the pinned random policy; the run prints honest numbers, not
  a demo of mastery. Byte-reproducibility is also not claimed here: the
  adapter is deterministic (proven on scripted transports), while a Gazebo
  run replays only as far as the simulator's own determinism (Doc 06 §5b).

## Point it at your robot

The anatomy in `run.py` is declaration, not code: topics, widths, message
types, extraction paths, presets. Swap them for your robot's topics, choose
`RclpyTransport(mode="free_running", tick_period=...)` for a live system
(real time runs at 1×, and the `overruns` counter tells you when the loop
missed its deadline), and keep `episode_mode="continuous"` — a robot has no
reset. Details: `specs/013-ros2-adapter/quickstart.md`.

## Files

- `Dockerfile` — pinned ROS 2 Jazzy; records the Python-version probe
  (the repo's full gate passed on the container's CPython 3.12 before
  `requires-python` was relaxed).
- `world.sdf` — the arena, the rover, the lidar, the diff-drive plugin.
- `entrypoint.sh` — paused sim → `ros_gz` bridge (topics + the
  world-control step service) → `run.py`.
- `run.py` — the anatomy declaration and the engine run; heavily
  commented, the newcomer path after `examples/cartpole.py`.
