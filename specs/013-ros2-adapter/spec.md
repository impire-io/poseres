# Feature Specification: The ROS2 Adapter

**Feature Branch**: `013-ros2-adapter`
**Created**: 2026-07-14
**Status**: Draft
**Input**: User description: "ROS2 body adapter — mount ROS2 topic-based worlds
(simulators like Gazebo and real robot hardware) behind the existing Body seam:
topic-subscribing sensors with a declared width, a latest-message cache, and an
explicit staleness policy; topic-publishing actuators mapping discrete actions
to preset commands; a fixed control-loop tick; stepped simulation first,
free-running hardware documented as non-reproducible; continuous mode for
single-boot worlds; the ROS2 client library optional and never required by the
quality gate (fake transport layer in-repo); a Gazebo worked example in Docker."

## Overview

ROS2 is the robotics ecosystem's shared interface: simulators (Gazebo, Webots,
Isaac Sim) and real robots alike expose their senses and controls as named
message streams — *topics*. One adapter that mounts a set of topics as a PRA
body covers both halves of ROADMAP C2's ambition at once — virtual worlds and
physical hardware — through a single seam, instead of a one-off body per
device. The engine, drives, and harness run on it unchanged, exactly as they
did for the Gymnasium adapter (feature 007), whose design this feature
deliberately parallels.

The adapter must resolve one genuine impedance mismatch **explicitly**, not by
accident — and it is a different mismatch than 007's. PRA steps in lock-step:
act, then observe the consequence. A ROS2 world streams: every sensor
publishes on its own clock, commands are fire-and-forget, and nothing in the
transport ties an action to "the observation that resulted from it." Whatever
the adapter does to reimpose step semantics is a *learning-semantics decision*
— it decides which transitions the brain sees — so this spec names the
decision (a fixed control-loop tick: publish the chosen command, advance
exactly one tick, then sample every sensor's latest cached message), names its
companion decision (what a sensor reports when nothing fresh arrived — the
staleness policy), and requires tests that prove both actually happen as
documented.

The second honest reckoning is reproducibility. The project's constitution is
byte-frozen validated behavior, and every world so far reproduces
byte-for-byte. A live ROS2 transport cannot promise that: message timing
jitters, and a real robot's physics is not seedable. The adapter's claim is
therefore split in two and stated openly: the *adapter* is deterministic — the
same message stream in produces the same behavior out, provable against a
scripted transport — while the *world's* reproducibility is graded by mode:
stepped simulation (the sim advances only when told to) keeps the instrument
panel and is the v1 worked-example target; free-running operation (real time,
real hardware) is supported and documented as non-reproducible, the class Doc
06 §5b already defined for live external worlds.

Everything else follows standing law: purely additive (no engine or core
edits; the byte-frozen suite stays green), the heavy dependency optional — and
this one is heavier than usual, since the ROS2 client library ships with a ROS
distribution rather than from the package index, and does not support macOS —
so the adapter must be *fully* contract-testable against an in-repo fake
transport, with the real-stack worked example running in a Linux container.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Mount a ROS2 world and run the engine on it (Priority: P1)

A maker with a robot (simulated or physical) declares its anatomy: each sensor
names a topic and the fixed number of values it contributes (a 5-beam laser
scanner: 5; a compass: 1), each actuator names a topic and a finite set of
preset commands ("forward", "turn left", "turn right", "stop" — four actions
publishing four fixed velocity commands). They mount the composition as a PRA
body, set the two matching configuration numbers (observation size, action
count), and run the unchanged engine on it. Observations arrive at the brain
as float64 vectors of the declared total width; the brain's action indices
become published commands.

**Why this priority**: This is the adapter itself — without it nothing else in
the feature exists. It must be testable *without any ROS installation*,
because the project's quality gate runs on machines (including this one) where
ROS2 cannot be installed: the adapter's whole contract is exercised against a
scripted in-repo transport.

**Independent Test**: Can be fully tested by mounting a body over the fake
transport with scripted publishers, running the engine across a small
schedule, and asserting the composed observations, the published commands, and
the run summary — with no ROS2 present, no example file, and no documentation.

**Acceptance Scenarios**:

1. **Given** a declared anatomy of topic sensors and command actuators over a
   transport, **When** the engine runs on the mounted body, **Then** the run
   completes to a normal per-seed summary, every observation crossing the seam
   is a float64 vector of the declared total width, and every action index
   results in exactly one published command from that actuator's preset set.
2. **Given** a sensor whose incoming message carries a different number of
   values than the sensor declared, **When** the message arrives, **Then** the
   run fails loudly naming the topic, the declared width, and the received
   width — never a silent truncation or pad.
3. **Given** a configuration whose observation size or action count does not
   match the mounted anatomy, **When** the body is mounted through the
   factory, **Then** mounting fails immediately with a message naming both
   numbers — never a shape error deep inside a run.
4. **Given** the same scripted message stream, **When** the run is repeated
   with the same configuration and seed, **Then** the serialized run summaries
   are byte-identical — the adapter adds no nondeterminism of its own, and
   never draws from the engine's random stream.

---

### User Story 2 - The tick-and-staleness semantics is explicit, documented, and tested (Priority: P2)

A researcher reads, in the feature documentation, exactly what one PRA step
means against a streaming world: the chosen command is published, the world
advances exactly one control tick (a stepped simulator is told to advance; a
free-running world is given one real tick period), and then every sensor
reports the latest message it has cached. If a sensor received nothing new
this tick, the staleness policy answers — by default it holds the last value
(the world simply hasn't changed as far as that sensor reported) — and the
per-sensor staleness count is readable outside the learning surface, so the
researcher can see how live their sensors actually were. A sensor that stays
silent beyond a configurable bound fails the run loudly rather than letting
the brain learn from a frozen ghost.

**Why this priority**: This is the named design question of this feature —
the analogue of 007's termination boundary. It is P2 only because the adapter
(US1) must exist before its tick semantics can be observed; it is the part of
the feature most likely to silently mislead users if left implicit.

**Independent Test**: Can be fully tested against the fake transport with
scripted publishers at controlled rates: assert publish-tick-sample ordering,
latest-message-wins within a tick, hold-last-value on a silent tick, staleness
counters, the startup gate, and the loud failure at the staleness bound.

**Acceptance Scenarios**:

1. **Given** a mounted body, **When** one engine step executes, **Then** the
   command is published *before* the tick advances and every sensor is sampled
   *after* it — the observation can reflect the action's consequence, and the
   ordering is asserted by test, not assumed.
2. **Given** a sensor whose topic delivered no new message during a tick,
   **When** the observation is composed, **Then** the sensor contributes its
   last cached value unchanged and its staleness count increments; **Given**
   several messages arrived within one tick, **Then** the latest wins and the
   overwritten count is visible outside the learning surface.
3. **Given** a freshly mounted body, **When** the first episode begins,
   **Then** the adapter waits until every sensor has received at least one
   message (bounded by a configurable timeout whose expiry names the silent
   topics) — the brain never observes an invented placeholder.
4. **Given** a sensor silent for more than the configured staleness bound,
   **When** the bound is crossed, **Then** the run fails with an error naming
   the topic and the silence duration.
5. **Given** the feature documentation, **When** a user looks up what a step
   means, **Then** the tick discipline, the staleness policy, and their stated
   consequences for learning are written down, including the rejected
   alternatives (blocking on fresh messages; zero-filling silent sensors;
   event-driven stepping) and why each was rejected.

---

### User Story 3 - Continuous operation for worlds that boot once (Priority: P3)

A maker points PRA at a world that cannot restart — a physical robot, or a
long-lived simulation — using the continuous episode mode shipped by feature
008: the world boots exactly once, virtual episode boundaries segment the
unbroken stream, and no reset is ever demanded of it. Alternatively, against a
simulator that *does* expose a reset mechanism, episodic mode works as
everywhere else — each episode begins from a world reset. Choosing episodic
mode over a world that cannot reset fails loudly at mount time, not at the
second episode.

**Why this priority**: Continuous operation is why the roadmap sequenced B3
before any hardware work — a robot has no `reset()`. It is P3 because both
engine modes already exist and are validated; this story is the adapter
declaring, per mounted world, which modes it honestly supports.

**Independent Test**: Can be fully tested against the fake transport: a
transport that forbids a second boot runs a full multi-episode schedule in
continuous mode to a normal summary; the same transport mounted in episodic
mode is rejected at mount time with a message naming the missing capability.

**Acceptance Scenarios**:

1. **Given** a world that forbids a second boot, **When** a full schedule runs
   in continuous mode, **Then** the world is booted exactly once, virtual
   episode boundaries pass with no reset traffic on the transport, and the run
   completes to a normal summary.
2. **Given** a world mounted in episodic mode without a declared reset
   mechanism, **When** the body is mounted, **Then** mounting fails with a
   message naming the missing capability and pointing at continuous mode.
3. **Given** a simulator with a declared reset mechanism in episodic mode,
   **When** a new episode begins, **Then** the world is reset through that
   mechanism and the first observation of the episode follows the same
   startup gate as US2.

---

### User Story 4 - The Gazebo worked example: the integration proof (Priority: P4)

A maker with Docker installed runs one documented command; a Linux container
brings up a ROS2 distribution, a Gazebo-simulated differential-drive robot,
and PRA; the engine runs a short schedule against the simulated robot's laser
scanner and velocity commands in stepped-simulation mode, and prints the
honest per-seed summary plus the adapter's own telemetry (ticks, staleness
counts, published commands). The example is the proof that the contract the
fake transport encodes is the contract the real stack honors.

**Why this priority**: The worked example is the roadmap's visible half, but
it is pure composition of US1–US3 — nothing in it can work before they do —
and it is the only story that cannot run in this repository's own quality
gate (it needs Linux and a ROS2 distribution), so it is documented and
container-scripted rather than wired into the test suite.

**Independent Test**: Run the documented command on a Linux machine with
Docker; the container exits successfully having printed the run summary and
adapter telemetry.

**Acceptance Scenarios**:

1. **Given** a machine with Docker, **When** the user runs the documented
   example command, **Then** the container builds, the simulated robot comes
   up, the engine completes its schedule in stepped-simulation mode, and the
   summary plus adapter telemetry are printed.
2. **Given** an installation without the ROS2 client library, **When** the
   adapter module is used directly, **Then** the failure is a clear error
   explaining that the library ships with a ROS2 distribution (not from the
   package index) and pointing at the containerized example — never a bare
   import traceback.

---

### Edge Cases

- A message arrives whose payload cannot be read as a fixed-width numeric
  vector (wrong type, variable length, non-numeric): rejected loudly at the
  sensor, naming the topic and the offending shape — never a silent cast.
  Message payloads outside the supported numeric-vector forms are rejected at
  mount time where declarable, at first receipt otherwise.
- Two sensors (or two actuators) declare the same topic: allowed — topics are
  streams, not exclusive resources — but duplicate *tool ids* stay rejected by
  the existing body contract.
- Multiple messages within one tick: the latest wins; the overwritten count
  is readable outside the learning surface (US2).
- The control loop misses its deadline in free-running mode (the tick took
  longer than the period — a slow drive, a network stall): the overrun is
  counted and readable outside the learning surface; the run continues. The
  count is the honesty meter for real-time claims.
- Snapshot/resume of a ROS2-mounted run: the engine side resumes exactly (the
  brain, drives, and schedule position); the world side follows Doc 06 §5b's
  live-external-world class — a free-running world's state is *not* captured
  and the resumed run is documented as diverging; a stepped simulator may
  offer better and the guarantee stays stated per world class, never implied.
- Reset in episodic mode when the simulator's reset mechanism fails or times
  out: the run fails loudly naming the mechanism — never a silent continue on
  an un-reset world.
- The transport delivers messages during startup before the body is fully
  mounted: cached normally; the startup gate (US2) only requires that every
  sensor has at least one message before the first observation composes.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide an adapter body that mounts a declared
  set of ROS2 topic sensors and command actuators behind the existing body
  seam, so the engine, drives, and validation harness run on it unchanged.
- **FR-002**: A topic sensor MUST declare its topic and fixed width at
  mount time, cache the latest received message, and contribute exactly its
  declared width of float64 values to the composed observation; a received
  payload that does not match the declared width or cannot be read as a
  numeric vector MUST fail loudly naming the topic and both shapes.
- **FR-003**: A command actuator MUST declare its topic and a finite ordered
  set of preset commands; applying local action index *i* MUST publish
  exactly the *i*-th preset command and nothing else; the actuator's action
  count is the size of its preset set. Nothing is returned — the only
  feedback path is subsequent observations, as everywhere in the body layer.
- **FR-004**: One engine step against the adapter MUST follow the tick
  discipline: publish the chosen command, advance exactly one control tick
  (instruct a stepped world to advance; allow a free-running world one tick
  period of wall-clock time), then compose the observation from every
  sensor's cache. The ordering MUST be asserted by test.
- **FR-005**: The staleness policy MUST be explicit: a sensor with no new
  message this tick contributes its last cached value and increments a
  per-sensor staleness count readable outside the learning surface; the first
  observation MUST NOT compose until every sensor has received at least one
  message (bounded by a configurable startup timeout naming silent topics on
  expiry); silence beyond a configurable staleness bound MUST fail the run
  naming the topic. No mode may invent values the world never sent.
- **FR-006**: The adapter MUST support both episode modes honestly: continuous
  mode boots the world exactly once and never demands a reset (the feature
  008 contract); episodic mode requires a declared reset mechanism and MUST
  reject mounting without one, naming the missing capability and pointing at
  continuous mode. A failed or timed-out reset fails the run loudly.
- **FR-007**: The ROS2 client library MUST be optional: the core package
  keeps its numpy-only install and the quality gate MUST pass on a machine
  with no ROS2 present, no tests skipped. Using the real transport without
  the library MUST fail with a clear error explaining that it ships with a
  ROS2 distribution (not from the package index) and pointing at the
  containerized example.
- **FR-008**: The adapter's contract logic MUST be separated from the
  transport behind a seam, with an in-repo fake transport implementing that
  seam, so that every requirement above (conformance, widths, routing, tick
  ordering, staleness, startup gate, both episode modes, every rejection
  path, adapter determinism) is exercised by the in-repo test suite against
  scripted message streams.
- **FR-009**: The feature MUST be purely additive: no engine or core edits;
  every existing test and recorded reference value stays byte-identical;
  nothing imports the adapter unless the user does.
- **FR-010**: The reproducibility claim MUST be split and stated: the adapter
  itself is deterministic — identical scripted message streams with the same
  configuration and seed produce byte-identical run summaries, proven against
  the fake transport — and it MUST never draw from or perturb the engine's
  random stream. Live-transport runs are documented non-reproducible per Doc
  06 §5b's external-world class; stepped simulation is documented as the mode
  that keeps a replayable world, and the worked example uses it.
- **FR-011**: The repository MUST ship a container-scripted worked example —
  a Gazebo-simulated differential-drive robot in stepped-simulation mode,
  launched by one documented command on a Docker-equipped machine — that runs
  the engine on the real ROS2 stack and prints the per-seed summary plus the
  adapter's telemetry (ticks, staleness counts, overruns, published
  commands).
- **FR-012**: The tick-and-staleness decision (FR-004/FR-005) MUST be
  recorded in this feature's documentation with its consequences for learning
  and the rejected alternatives (blocking on fresh messages, zero-filling
  silent sensors, event-driven stepping), and the adapter's telemetry MUST
  stay outside the learning surface everywhere.

### Key Entities

- **Topic sensor**: a declared (topic, width) pair with a latest-message
  cache and a staleness count; contributes its cached float64 values to the
  composed observation each tick.
- **Command actuator**: a declared (topic, ordered preset commands) pair;
  local action index *i* publishes the *i*-th preset; action count = preset
  count.
- **Control tick**: the unit that reimposes step semantics on a streaming
  world — publish, advance one tick (stepped instruction or one wall-clock
  period), sample caches; carries the overrun count in free-running mode.
- **Staleness policy**: hold-last-value with visible per-sensor counts, a
  startup gate before the first observation, and a loud failure bound.
- **Transport seam**: the boundary between adapter logic and message
  delivery; implemented by the real ROS2 stack in deployment and by the
  scripted fake transport in the test suite — the same contract, provably.
- **Worked example**: the containerized Gazebo run — the integration proof
  that the fake transport's contract is the real stack's contract.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The full existing validation suite passes with its recorded
  reference values byte-identical after the adapter ships, and the core
  install still requires numpy only.
- **SC-002**: The entire adapter contract — conformance, widths, action
  routing, tick ordering, staleness policy, startup gate, both episode
  modes, adapter determinism, and every rejection path — is covered by the
  in-repo suite against the fake transport, passing on a machine with no
  ROS2 installed, zero tests skipped.
- **SC-003**: Two runs over identical scripted message streams with the same
  configuration and seed produce byte-identical serialized summaries; a
  continuous-mode run over a transport that forbids a second boot completes
  a full multi-episode schedule to a normal summary.
- **SC-004**: On a Docker-equipped Linux machine, the worked example goes
  from the single documented command to a completed engine run on the
  simulated robot, printing the per-seed summary and adapter telemetry,
  without manual ROS2 setup.
- **SC-005**: The tick discipline, staleness policy, and split
  reproducibility claim are recorded in the feature's spec/research record
  with rejected alternatives before the adapter's first release, and a user
  can read what one step means without opening source code.
- **SC-006**: A maker can declare a new robot anatomy (topics, widths,
  preset commands) and mount it without editing the adapter — declaration
  is configuration, not code change, demonstrated by the example using only
  the public surface.

## Assumptions

- **Discrete actions only in v1.** A command actuator is a finite preset set;
  continuously-valued commands (true velocity control) are out of scope and
  documented, exactly as Box actions were for feature 007 — a principled
  discretization is future work, not a hidden default.
- **Fixed-width numeric payloads only in v1.** Sensors read message payloads
  that are, or contain, fixed-length numeric vectors (range arrays, poses,
  scalar readings). Images, point clouds, and variable-length payloads are
  out of scope — vision is a named horizon ambition, not an adapter detail.
- **Reproducibility is conditional on the world, and said so.** The adapter
  is deterministic; stepped simulation keeps a replayable world conditional
  on the simulator's own determinism; free-running mode reproduces nothing
  and is documented as the deployment mode, per Doc 06 §5b. This is the
  first PRA mode that can run non-reproducibly, and it ships stated, not
  discovered.
- **Real time runs at 1×.** In free-running mode the engine advances at the
  control-loop rate — wall-clock slow, exactly as ROADMAP principle 2
  predicted for real-time worlds. The multi-stream parallelism story (B4)
  applies only to steppable simulators. The example therefore runs stepped.
- **Linux container for the real stack.** The ROS2 client library targets
  Linux; macOS is unsupported by ROS2 upstream. Development machines run
  the fake-transport suite; the worked example is the container's job. The
  ROS2 distribution pinned in the container is the current LTS release.
- **Physical reset is a documented answer, not automation.** For hardware,
  the recommended mode is continuous (single boot, virtual episodes); a
  homing routine as an episodic reset mechanism is the owner's affair and
  the documentation says so — this is C2's "written answer to physical
  reset", stated rather than improvised.
- **Transport delivery settings default to the ecosystem's sensor-data
  conventions** and are declarable per topic; the spec requires only that
  whatever is declared is what the staleness telemetry measures against.
- **Snapshot guarantees follow Doc 06 §5b unchanged.** This feature adds no
  new persistence claims: engine-side exactness, world-side per-class
  honesty. The live-world class was written for exactly this adapter.
