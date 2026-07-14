# Research: The ROS2 Adapter

Phase 0 of `plan.md`. Every decision below is stated as
decision / rationale / alternatives, and each traces to a functional
requirement of `spec.md` or a working rule of `AGENTS.md`. Unlike 007
(where the external dependency was pip-installable and probed before
planning), the real ROS2 stack cannot run on this machine at all —
which is itself the load-bearing fact: every decision below is shaped
so that the adapter's entire contract is provable without ROS2
(FR-008), and the one thing that genuinely needs the real stack (the
container example, R8) carries its own named probe for implementation
time.

## R1 — Adapter shape: per-topic tools around a transport seam, not a monolithic world

**Decision.** A subpackage `src/pra/anatomy/ros2/` with four modules:

1. `specs.py` — plain-data declaration: `SensorSpec(id, topic, width,
   msg_type, extract)` and `ActuatorSpec(id, topic, msg_type, presets)`,
   where `extract` is an attribute path into a message object (e.g.
   `"ranges"`, `"pose.pose.position"`) whose resolved value flattens to
   float64, and each preset is a dict of attribute-path → value (e.g.
   `{"linear.x": 0.2}`). Pure functions `extract_vector(msg, spec)` and
   `build_fields(preset)` operate on duck-typed objects — no ROS2 import.
2. `body.py` — `TopicSensor` (Doc 02 `Sensor`: latest-message cache,
   staleness/overwrite counters, loud width check on every delivery),
   `CommandActuator` (Doc 02 `Actuator`: `apply(i)` publishes preset
   `i` via the transport, counts publishes), and `Ros2Body(Body)`
   overriding exactly two methods: `reset()` (boot-or-reset through the
   transport + the startup gate) and `step()` (route → publish →
   `transport.tick()` → compose). `Ros2Body.factory(...)` returns an
   Engine-ready `world_factory` that validates config sizes and the
   episode-mode/reset-capability pairing at mount time.
3. `transport.py` — the `Transport` protocol (`start`, `subscribe`,
   `publish`, `tick`, `can_reset`/`reset_world`, `close`) and
   `RclpyTransport` behind a lazy import (R7), with free-running and
   stepped-simulation tick implementations (R2).
4. `fake.py` — `FakeTransport`, in-package: scripted publishers keyed by
   tick index, an event journal (publish/tick/deliver order), a
   boot-once switch, and an optional reset mechanism — the instrument
   every contract test and the quickstart run on.

**Rationale.** Feature 007 wrapped *one object* (a `gymnasium.Env`) that
already was a world, so a monolithic `EventSource` was the natural
shape. A robot is not one object — it is N independent message streams
— and PRA already has the right abstraction for exactly that: the Doc
02 body, whose sensors and actuators are first-class tools. Making each
topic a real body tool buys the C2 showcase moment for free (mid-run
`register_sensor` = snapping a new topic onto a running robot, applied
at slow-loop boundaries by the existing engine mechanism) and keeps
width enforcement, routing, and composition on the proven `Body` path.
The tick cannot live in an actuator's `apply` (a body may carry other
registered actuators; the invariant "every step advances exactly one
tick" must hold regardless of which actuator the action routes to), so
`Ros2Body.step()` owns it — the smallest override that keeps the
invariant, and `Body.step`'s route/compose plumbing is reused inside it.

**Alternatives considered.** (a) A monolithic `Ros2World(EventSource)`
wrapped by `WorldSensor`/`WorldActuator` (the 007 shape) — rejected:
it flattens N topics into one opaque sensor, so per-topic staleness,
per-topic registration, and the grow-a-sensor demo all disappear;
Doc 02 exists precisely to avoid this. (b) Tick inside
`CommandActuator.apply` — rejected: breaks the one-tick-per-step
invariant if any other actuator is registered (and hides the feature's
central semantics inside a tool). (c) rclpy types in the declaration
API — rejected: anatomy declarations must be importable and testable on
machines without ROS2 (FR-008, SC-006); plain data + attribute paths
keep declaration = configuration.

## R2 — The tick discipline: publish → advance exactly one tick → sample (the named design question)

**Decision.** One engine step against the adapter is: (1) route the
action and **publish** the chosen preset; (2) **advance one control
tick** — stepped transport: issue the simulator's step command (a
configured number of sim steps per control tick) and deliver messages
until the step completes; free-running transport: deliver messages
until one wall-clock tick period (default 100 ms, i.e. 10 Hz) elapses;
(3) **sample** — compose the observation from every sensor's cache.
`Ros2Body.reset()` follows the same tick mechanics for its startup gate
(R3). The ordering is asserted against the fake transport's event
journal, not assumed. In free-running mode a tick whose delivery work
overruns the period increments an `overruns` counter — readable outside
the learning surface, the honesty meter for real-time claims.

**Consequences for learning (documented, not hidden).** The brain's
transition model sees the world at control-tick resolution: whatever
the sensors published last within the tick stands for "the outcome of
the action." Faster-publishing sensors are effectively subsampled
(latest wins, overwrites counted); slower ones repeat under the
staleness policy (R3). The action→outcome pairing is honest but
*coarse* — the same world at a different tick rate is a different
learning problem, which is exactly why the rate is a declared, visible
parameter of the mounted anatomy rather than a hidden constant.

**Alternatives considered.** (a) Event-driven stepping (a step
completes when the "primary" sensor's next message arrives) — rejected:
it makes episode timing a function of one topic's publisher, privileges
a sensor the anatomy layer has no business privileging, and couples the
learning cadence to network jitter in free-running mode. (b) Block
until *every* sensor has a fresh message — rejected: a robot with a
1 Hz sensor would drag the whole loop to 1 Hz, and a silent publisher
would hang the run instead of failing loudly (R3 owns that). (c)
Publish after the tick (sample-then-act) — rejected: the observation
returned for a step could then never reflect that step's action, which
inverts PRA's act-then-observe contract and would corrupt
action-conditioned prediction everywhere.

## R3 — The staleness policy: hold-last-value, visible counters, a startup gate, a loud bound

**Decision.** Per sensor: every delivered message overwrites the cache
and increments a delivery sequence number (deliveries beyond the first
within one tick increment `overwritten`). At sample time, a sensor
whose sequence number has not advanced since the previous sample
contributes its cached value unchanged and increments `staleness_total`
and `staleness_streak`; a fresh message resets the streak. A streak
crossing the configured bound (`stale_limit_ticks`, default 50 ticks)
raises `AnatomyError` naming the topic and the streak. Before the first
observation of a boot (and of every episodic reset), the **startup
gate** runs: tick (without publishing) up to `startup_timeout_ticks`
(default 100) until every sensor has at least one message; expiry names
the still-silent topics. A `TopicSensor` read before any message raises
`AnatomyError` — same contract as `WorldSensor`, and the gate exists so
the engine never encounters it.

**Consequences for learning.** Hold-last-value means a slow sensor's
channels are step-functions of the true signal — predictable *between*
updates (the brain can exploit that honestly) with irreducible surprise
*at* updates, a milder cousin of 007's respawn boundary. The counters
make the effective data rate per sensor measurable after any run, so a
user can tell "my brain plateaued" from "my sensor was silent."

**Alternatives considered.** (a) Zero-fill silent ticks — rejected
outright: it invents values the world never sent, manufacturing
phantom transitions between the real value and zero (spec FR-005 bans
it by name). (b) NaN-fill — rejected: NaN would propagate through the
frame cores and poison the learning surface; the frames have no
missing-data semantics, and inventing one is core work, not adapter
work. (c) Append a per-sensor freshness channel to the observation —
deferred, not rejected: it changes the declared anatomy (width + 1 per
sensor) and belongs to the user's experiment space once channel-noise
robustness work (the named A3 successor) says how such channels are
weighted; v1 keeps freshness in telemetry, outside the learning
surface. (d) Fail on any stale tick — rejected: real sensor rates
legitimately differ from the control rate; staleness is a normal
operating regime, not an error, until the bound says otherwise.

## R4 — Determinism: the adapter has no randomness; scripted streams reproduce byte-identically

**Decision.** The adapter contains no random draw anywhere — sensors
cache, actuators publish presets, the tick advances the world. The
factory receives the engine's generator per the `world_factory(cfg,
rng)` signature and does not touch it (asserted: bit-generator state
identical before/after mount and across a full fake-transport run,
the 007 test pattern). Byte-identity: two engine runs over the same
`FakeTransport` script with the same config and seed produce
byte-identical serialized summaries — the integration test for FR-010.
There is no per-reset seed scheme at all: unlike Gymnasium, ROS2 worlds
own their stochasticity, and the transport's `reset_world` mechanism
carries no seed in v1 (a simulator's own reset determinism is its
promise, not ours — Doc 06 §5b language, reused).

**Rationale.** Simpler than 007 by construction: where 007 had to
*derive* entropy without drawing, this adapter's only honest claim is
conditional determinism (spec Overview), so the right amount of adapter
randomness is zero. Anything more would manufacture a reproducibility
claim the transport cannot back.

**Alternatives considered.** Seeding stepped simulators through a
declared seed service — plausible future work for simulators that
support it; v1 does not pretend a universal mechanism exists (Gazebo
world reset does not re-seed physics randomness in general).

## R5 — Payload mapping: attribute-path extraction and preset building, duck-typed and rclpy-free

**Decision.** `SensorSpec.extract` is a dotted attribute path resolved
against the delivered message object; the resolved value is flattened
C-order to float64 (`ravel`), with sub-object flattening for the common
geometry compounds (a `Vector3`/`Point` contributes x, y, z; a
`Quaternion` contributes x, y, z, w — a small, documented table in
`specs.py`, applied recursively). The result must match the declared
width or the delivery fails naming the topic and both shapes (FR-002).
`ActuatorSpec.presets` is an ordered list of `{attribute-path: value}`
dicts; the real transport constructs the typed message (fields not
named keep the type's defaults — for `Twist`, zeros) and publishes it;
the fake transport records the preset dict verbatim in its journal.
Message *types* are named as strings (`"sensor_msgs/msg/LaserScan"`,
`"geometry_msgs/msg/Twist"`); only `RclpyTransport` ever resolves them
to classes (lazy, R7). v1's supported payloads are exactly: anything
whose extracted value flattens to the declared fixed width — range
arrays, poses, odometry compounds, plain float arrays. Variable-length
and non-numeric payloads fail loudly at first delivery.

**Rationale.** Attribute paths + the compound table cover the spec's
named sensor family (rangefinder, heading, odometry, scalar readings)
with one mechanism, no per-type adapter classes, and full testability
via `types.SimpleNamespace` fakes. Field-default presets mean an
anatomy declaration reads as data (`{"linear.x": 0.22}`) and carries no
ROS2 import.

**Amendment (integration-run finding).** Non-finite values (NaN/±inf)
are a loud delivery error, added after the Gazebo worked example's first
end-to-end run: real lidars emit +inf for no-hit beams, −inf below the
minimum range, and NaN for invalid returns, and passing them through
silently NaN-poisoned the entire prediction-error surface (the frames
have no missing-data semantics — the same reason R3 rejected NaN-fill).
The error names the fix: sanitize in a callable `extract`, where the
choice is declared and visible (the example clamps to the sensor's own
range bounds).

**Alternatives considered.** (a) Per-message-type converter classes —
rejected: N classes for one `getattr` chain; the compound table is the
whole irregularity. (b) User-supplied converter callables — kept
possible (a spec may carry `extract=callable`) but not the documented
default: callables can't be validated at declaration time and read as
code, not configuration. (c) Supporting images/point clouds by
flattening — rejected: a 640×480 image "works" and produces a
300k-wide observation no validated scale rule covers; vision is a
named horizon ambition, and pretending otherwise is exactly the
demo-ahead-of-capability move the roadmap forbids.

## R6 — Episode modes: continuous is native; episodic demands a declared reset mechanism

**Decision.** The transport declares `can_reset`. The factory checks
the pairing at mount time: `episode_mode="episodic"` over a transport
with `can_reset=False` raises `AnatomyError` naming the missing
capability and pointing at continuous mode (FR-006). In continuous
mode the engine boots the body exactly once (the feature-008 contract,
already in the engine); the transport additionally guards against a
second `start()` so a regression would fail loudly on the transport's
own honesty, not silently re-home a robot. In episodic mode each
`Ros2Body.reset()` calls `transport.reset_world()` (which raises
loudly on failure/timeout) and re-runs the startup gate. The worked
example runs **continuous** mode — the honest robotics story and B3's
showcase moment; episodic-with-reset is exercised by the fake
transport's optional reset mechanism in the contract suite.

**Rationale.** Both engine modes exist and are validated; the
adapter's job is only to declare, per world, which it honestly
supports — and to fail at mount, not at episode two, when the pairing
is wrong. This is C2's "written answer to physical reset": continuous
mode for hardware; a homing routine is an owner-supplied
`reset_world` if they insist on episodic.

**Alternatives considered.** Auto-falling-back to continuous when
reset is missing — rejected: episode mode changes learning cadence
semantics (008); silently switching it is a config lie. Emulating
reset by replaying a homing preset sequence — rejected for v1:
open-loop homing has no completion criterion the adapter can verify;
it belongs to the user's `reset_world` implementation if they have one.

## R7 — The dependency: no pip extra exists to give; the gate runs ROS2-free by design

**Decision.** rclpy is distributed with ROS2 distributions (apt/ros
repositories, sourced environments), not from PyPI — there is no
honest `pip install "poseres[ros2]"` to offer, so **no new pyproject
extra** is added (the first optional integration where the 007 pattern
cannot apply, stated in the docs). `transport.py` imports rclpy lazily
through one internal helper; using `RclpyTransport` without a sourced
ROS2 environment raises an ImportError explaining that rclpy ships
with a ROS2 distribution, naming the docs URL and the containerized
example as the two ways to get one. The error path is tested by
monkeypatching the import handle (007 pattern). Everything else in the
subpackage imports without ROS2 by construction (R1), so the quality
gate runs the entire contract on any machine, none skipped. The
rclpy-only glue inside `RclpyTransport` (node/executor setup, QoS,
typed-message resolution, the step-service client) is exercised by the
container example — outside the gate, and the plan says so openly
(the inverse of 007, where the real dependency sat in `dev`).

**Alternatives considered.** (a) Adding `rclpy` to a pyproject extra
anyway — rejected: `pip install poseres[ros2]` would fail on every
machine without a ROS build-farm index configured; shipping a broken
install command is worse than shipping none. (b) Vendoring a minimal
DDS client — absurd scope. (c) `pytest.importorskip` for real-stack
tests — banned by the repo's no-skip rule; the container is where the
real stack is proven.

## R8 — The worked example: minimal diff-drive SDF + ros_gz bridge, stepped, continuous, one command

**Decision.** `examples/ros2/` is a self-contained Docker build: a
pinned ROS2 LTS base image, Gazebo (the matching `ros_gz` pairing), a
**minimal in-repo SDF world** — one differential-drive robot with a
5-beam planar lidar and odometry, driving on `cmd_vel` — bridged by
`ros_gz_bridge`, and `run.py` declaring the anatomy (lidar 5 + heading
1 = obs 6; presets forward/left/right/stop = 4 actions) and running
the engine in **continuous mode, stepped simulation** (the sim starts
paused; the transport's step client advances it per control tick).
One documented command (`docker build` + `docker run`, wrapped in the
README) prints the per-seed summary and the adapter telemetry (ticks,
per-sensor staleness, overwrites, publishes). No TurtleBot3 stack.

**The named probe (resolved at implementation, not assumed).** Two
facts must be probed in-container before the example is pinned, and
the Dockerfile itself is the record: (1) **distro pairing** — the
newest ROS2 LTS whose base image carries a Python the repo supports;
the repo requires Python ≥3.13 while Ubuntu 24.04-based distros ship
3.12, so either a newer distro qualifies, or the fallback runs: build
the container, run the full quality-gate suite on the container's
Python, and only if fully green relax `requires-python` accordingly
(a measured packaging decision recorded in the closing commit — never
an untested override flag). (2) **step mechanics** — the world-control
step interface bridged into ROS2 (service name and sim-steps-per-tick
constant); probed live, then fixed in `entrypoint.sh`.

**Rationale.** A minimal SDF world keeps every moving part in-repo and
pinned (the TurtleBot3 stack is large, versioned, and opinionated —
wrong trade for an example whose job is proving the adapter contract);
stepped mode keeps the instrument panel (roadmap principle 2);
continuous mode is what B3 was built for and what real hardware needs
— the example teaches the deployment pattern, not a lab shortcut.

**Alternatives considered.** TurtleBot3 (heavier, less pinnable);
free-running example (loses replayability and teaches the wrong
default); docker-compose multi-container (one container is enough —
sim, bridge, and PRA share it; compose adds surface for zero
capability); wiring the example into CI (a multi-GB image build in
the quality gate for a repo whose gate is seconds — the README's
manual proof is the honest scope, like 007's "run it yourself").

## R9 — Persistence: Doc 06 §5b class 4, verbatim — no capture, loud where the engine is already loud

**Decision.** The adapter implements no `state_dict`/`load_state_dict`
and does not declare `snapshot_needs_state`. Consequences, all
inherited from shipped engine behavior and asserted by test: episodic
snapshots capture the engine side only (resume re-boots the world via
the factory; exactness is conditional on the world's own reset
determinism — stated); continuous-mode runs with snapshotting enabled
hit the engine's existing loud `RuntimeError` (features 008/010: world
capture required) at run start — the honest answer for a world whose
state is a physical room. The docs say what persistence *means* for a
robot deployment: the brain's snapshot is the artifact; the world
re-attaches at boot (the single-boot contract).

**Alternatives considered.** (a) Declaring `snapshot_needs_state` with
a best-effort state — rejected: the marker's contract (feature 010) is
*exact* resume, and no honest world state exists to record; declaring
it would convert a documented non-guarantee into a silent divergence.
(b) An opt-in user hook for capture-supporting simulators — plausible
future work (a stepped sim with a save/load service could honestly
join §5b class 2); out of v1 scope, named here so it isn't lost.
