# Chapter 26 — Feature 013: the ROS2 adapter — robots are message streams, so topics became tools (2026-07-14)

The question was C2's, generalized: one adapter for everything that speaks
ROS2 — Gazebo, Webots, real hardware — instead of a one-off body per
device. The shape deliberately inverts 007: a Gymnasium env is *one world
object*, so 007 wrapped it as one EventSource; a robot is *N independent
message streams*, so each topic became a first-class Doc 02 tool
(`TopicSensor`/`CommandActuator` around a `Transport` seam), which keeps
mid-run `register_sensor` — snapping a sensor onto a running robot — alive
for free. The named design decision is **time**: one engine step is
publish → advance exactly one control tick → sample every sensor's latest
cached message, with the tick owned by the body (never an actuator, so the
one-tick-per-step invariant survives any registered tool) and asserted
against a journaling fake transport, not assumed. Its companion is the
**staleness policy**: hold-last-value with per-sensor counters outside the
learning surface, a startup gate before the first observation, and a loud
bound — which promptly fired in anger *during the feature's own authoring*:
the quickstart's scripted world ran dry at 6,000 ticks because the default
schedule actually consumes 13,001 (325 episodes — `effective_n_cycles`
stretches to the last horizon checkpoint — a wrong-arithmetic trap the
guard caught exactly as designed). Determinism claims are split honestly:
the adapter carries **zero randomness** (simpler than 007's pure state
read — the only honest claim is conditional, so the right amount is none;
byte-identity proven on scripted streams), while free-running operation is
the project's first openly non-reproducible mode (Doc 06 §5b class 4, now
naming this adapter). Two firsts in the plumbing: rclpy has no honest pip
extra (it ships with ROS distributions), so the entire quality gate runs
on the in-package `FakeTransport` — and `requires-python` was relaxed to
3.12 the project's way: the full gate, byte-frozen baseline included, run
green on CPython 3.12.8 *first*, because Jazzy's rclpy binds to Ubuntu
24.04's interpreter. The worked example — a minimal diff-drive rover
(5-beam lidar, odometry, cmd_vel) in a Gazebo arena, stepped through the
bridged `ControlWorld` service, continuous single-boot — was built and run
end-to-end in its Docker container during the feature, and the first real
run earned its keep: it surfaced **non-finite lidar beams** (+inf no-hit,
−inf below-min-range, NaN invalid) silently NaN-poisoning the whole
prediction-error surface — the summary read `nan early → nan late` while
the exit code smiled. The contract was amended openly (research R5): the
adapter now rejects non-finite deliveries loudly, naming the fix (a
sanitizing callable `extract`, which is what the example's lidar clamp
does — to the sensor's own range bounds). The rerun prints finite,
honest numbers. One ROS-classic snag also recorded: ROS setup scripts
violate `set -u`. C2's platform half is landed; the physical build,
guide, and growth video remain the showcase.
Trail: `specs/013-ros2-adapter/` (spec, plan, research R1–R9, contracts,
quickstart), `examples/ros2/`.
