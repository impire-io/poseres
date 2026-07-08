# Feature Specification: Anatomy and Body

**Feature Branch**: `004-anatomy-body`
**Created**: 2026-07-08
**Status**: Draft
**Input**: User description: "Anatomy & body (design Doc 02): Sensor/Actuator interfaces, fixed-order observation composition, disjoint-union action space, ToolRegistry with slow-loop registration and Doc 03 §7 frame I/O resize; Bus already built."

## User Scenarios & Testing *(mandatory)*

Today the system's only body is the monolithic synthetic world. Doc 02 says the
anatomy must be **configurable** — the same system runs on different bodies by
changing configuration only, sees observations as vectors and actions as
indices, and can grow new sensors/actuators at runtime (tools) without losing
what it has learned. This feature builds that body layer. The Bus (Doc 02 §6)
was built and validated in feature 001 and is untouched.

### User Story 1 - A body composed of declared parts (Priority: P1)

A researcher declares sensors and actuators in a fixed order; the system reads
all sensors each step into one concatenated observation and routes each global
action index to exactly one actuator — with the existing synthetic world
mounted as just another sensor/actuator pair, behaving byte-identically to the
direct connection.

**Why this priority**: This is the anatomy contract itself (Doc 02 §3.3/§4.2);
everything else composes on it. Byte-identity with the direct world proves the
layer adds semantics without perturbing the validated behavior.

**Independent Test**: Run a seed with the world mounted through a body and
byte-compare the summary against the direct-world run; unit-check composition
order and action routing.

**Acceptance Scenarios**:

1. **Given** sensors declared in a fixed order, **When** the body composes an
   observation, **Then** it is the concatenation of their outputs in exactly
   that order, with total width = sum of widths.
2. **Given** actuators declared in a fixed order, **When** a global action index
   is applied, **Then** it maps deterministically to exactly one
   (actuator, local index) pair, and the disjoint-union size is the sum of
   action counts.
3. **Given** the synthetic world mounted as a single-sensor/single-actuator
   body, **When** a full run executes, **Then** the summary is byte-identical
   to the direct-world run.
4. **Given** a sensor that returns the wrong width, **When** the body composes,
   **Then** it fails with a clear error naming the sensor (never a silently
   corrupted observation).

---

### User Story 2 - The body grows without forgetting (Priority: P1)

A researcher registers a new sensor (or actuator) at a consolidation boundary;
the observation/action space grows; every existing frame is adapted by the
Doc 03 §7 rule — learned weights preserved, new slices freshly initialized —
and the run continues without loss, restart, or nondeterminism.

**Why this priority**: Runtime anatomy extension is the point of the tool
mechanism and the riskiest part (it touches every frame's tensors). "Preserved,
not reset" is what makes it *growth* rather than a fresh boot.

**Independent Test**: Register a tool mid-run at a slow-loop boundary; assert
frame tensor shapes changed, pre-existing weight slices are bit-equal to their
pre-registration values, the run completes, and a re-run of the same seed is
byte-identical.

**Acceptance Scenarios**:

1. **Given** a pending sensor registration, **When** the slow loop applies it,
   **Then** `obs_dim` grows by the sensor's width, every frame's
   encoder-input/decoder-output tensors gain freshly-initialized slices, and
   all previously-learned weight entries are preserved exactly.
2. **Given** a pending actuator registration, **When** the slow loop applies
   it, **Then** `n_actions` grows, every frame's transition tensors gain
   freshly-initialized per-action slices, and existing action slices are
   preserved exactly; deregistering removes the corresponding slices.
3. **Given** any tool registration, **When** it is requested mid-episode,
   **Then** it takes effect only at the next slow-loop boundary (never
   mid-step).
4. **Given** the same seed and the same registration schedule, **When** the run
   is repeated, **Then** the summary is byte-identical (resize draws come from
   the run's single generator in a fixed order).

---

### User Story 3 - The validated behavior is untouched (Priority: P1)

With no body configured (the default), every existing mode behaves and
serializes byte-identically to the validated build.

**Why this priority**: The permanent regression rule of this repository.

**Independent Test**: The pinned reference-seed values reproduce exactly; the
slow-loop tool hook is inert for the plain synthetic world.

**Acceptance Scenarios**:

1. **Given** the default configuration, **When** any existing mode runs,
   **Then** behavior and summary bytes are identical to the validated build.

---

### Edge Cases

- **Action feedback**: actuators return nothing; the only feedback path from an
  action is subsequent observations (structural, Doc 02 §4.2).
- **First event after a (re)start** carries null previous-observation/action —
  already the episode semantics; the body preserves it.
- **Deregistering a sensor** shrinks the observation; the affected frame slices
  are discarded (Doc 03 §7 "removed ... discarded"). Deregistering below one
  sensor or one actuator is rejected (a body must sense and act).
- **Duplicate tool ids** are rejected at registration.
- **Snapshot of an anatomy-resized run**: out of scope for this feature — the
  snapshot blob records the boot configuration, and restoring a resized
  population is a Doc 06 format-version follow-up. Registering tools and
  snapshotting in the same run is documented as unsupported (a clear
  limitation, not a silent corruption: restore's body-compatibility check
  rejects the stale dims).
- **Timeouts** (Doc 02 §3.2/§4.2): in this in-process build, sensors/actuators
  are synchronous calls; the timeout rule is the sensor implementer's duty and
  the config fields remain declared (Doc 07) — enforcement belongs to a future
  hardware body.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Sensor and Actuator MUST be swappable interfaces: a sensor
  declares an id and a fixed width and returns exactly that many values per
  read; an actuator declares an id and a discrete action count and applies a
  local action index, returning nothing.
- **FR-002**: The body MUST compose observations by concatenating all active
  sensors' reads in the fixed declared order (`obs_dim` = sum of widths), and
  MUST expose the global action space as the fixed-order disjoint union of
  actuators (`n_actions` = sum of counts) with deterministic global→local
  routing.
- **FR-003**: A wrong-width sensor read MUST fail loudly, naming the sensor.
- **FR-004**: The body MUST be mountable wherever the synthetic world is used
  today (the same environment seam), and a world mounted through a body MUST
  produce byte-identical runs to the direct connection.
- **FR-005**: A ToolRegistry MUST support register/deregister/list of sensors
  and actuators at runtime; registrations requested mid-episode MUST take
  effect only at the next slow-loop boundary; duplicate ids MUST be rejected;
  removing the last sensor or actuator MUST be rejected.
- **FR-006**: Applying an anatomy change MUST resize every frame by the
  Doc 03 §7 rule: existing weight entries preserved exactly; new
  encoder-input/decoder-output slices (observation growth) and new per-action
  transition slices (action growth) initialized from the frame-initialization
  distribution at the effective scale; removed slices discarded. Resize draws
  MUST come from the run's single seeded generator in a fixed documented order.
- **FR-007**: After a resize the run MUST continue without restart: newborn
  frames use the new dimensions, action selection uses the new action count,
  and the scale-dependent effective parameters (PRA-01 §8.8) MUST track the
  new observation width.
- **FR-008**: With no body/tools configured, every existing mode MUST remain
  byte-identical to the validated build; the slow-loop anatomy hook MUST be
  inert (no RNG, no float work) for plain worlds.
- **FR-009**: The Bus MUST remain delivery-only and untouched; the system
  continues to depend only on the Bus interface (Doc 02 §6.4/§6.5).

### Key Entities

- **Sensor / Actuator**: the declared parts of a body (id, width/action-count,
  read/apply).
- **Body**: the fixed-order composition — observation concatenation, action
  routing, current `obs_dim`/`n_actions`; mounts an episodic environment (the
  synthetic world) plus any additional parts; hosts the ToolRegistry.
- **ToolRegistry**: runtime extension surface; pending changes applied at the
  slow loop.
- **Frame I/O resize**: the preservation-plus-fresh-slices adaptation of every
  frame group's tensors.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A world-through-body run is byte-identical to the direct-world
  run for the same seed.
- **SC-002**: After a mid-run sensor and actuator registration, all
  pre-existing weight entries equal their pre-registration values bit-for-bit,
  shapes reflect the new dims, and the run completes with a byte-identical
  re-run.
- **SC-003**: The reference seed reproduces the validated build's values with
  the anatomy layer present and unused.
- **SC-004**: Composition order, widths, routing, wrong-width rejection,
  duplicate-id rejection, and last-part protection are all unit-verified.
- **SC-005**: A registration requested mid-episode is measurably deferred to
  the next slow-loop boundary.

## Assumptions

- The synthetic world remains the only *environment*; anatomy composition is
  demonstrated with synthetic extra sensors/actuators (e.g. a constant or
  derived sensor) — a hardware body is out of scope, as is the [O] mechanism by
  which the system invents its own tools (interface only, Doc 02 §5.2).
- Continuous action spaces remain [O]/out of scope (Doc 02 §2.2).
- Snapshot/restore of anatomy-resized runs is a documented Doc 06 follow-up
  (see Edge Cases); the restore compatibility check makes the limitation loud.
- New resize slices use the effective (fan-in-matched) initialization scale of
  PRA-01 §8.8 at the *new* widths — the reference-preserving reading of
  Doc 03 §7's "Normal(0, init_weight_scale²)".
