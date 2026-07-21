# 02 — Anatomy, I/O, and the Bus

This document specifies the body (sensors, actuators, tools) and the communication mechanism (the bus). It defines the data that flows and the interfaces that produce, consume, and deliver it.

> **Build status (2026-07-08, feature `004-anatomy-body`):** implemented and
> validated. Sensor/Actuator interfaces, fixed-order observation composition,
> the disjoint-union action space, and the ToolRegistry with slow-loop-deferred
> registration are built; the Body satisfies the EventSource seam, so a world
> mounted through it runs **byte-identically** to the direct connection, and
> the frame I/O resize (Doc 03 §7) preserves learned weights bit-for-bit while
> initializing new slices at the §8.8 effective scale. The Bus (§6) was built
> and validated in feature 001. Remaining [O]/deferred, as specified: tool
> self-invention (§5.2), continuous actions (§2.2), in-process timeout
> enforcement (§3.2 — a hardware-body concern), and snapshot/restore of
> anatomy-resized runs (a Doc 06 format-version follow-up; restore's
> compatibility check fails loudly on the stale dims).

---

## 1. Principles

- The anatomy is **configurable**. The same system runs on different bodies (e.g. a robot with servos and distance sensors, or a software body with abstract sensors) by changing configuration only. **[D]**
- The system is **agnostic to what a sensor measures or an actuator does**. It sees observations as vectors and emits actions as commands from a declared space. Meaning is learned, not configured. **[D]**
- Sensors and actuators are declared at boot and **MAY** be extended at runtime as tools. **[D]**

---

## 2. Data types

### 2.1 Observation
```
Observation: float[obs_dim]
```
A dense real vector. `obs_dim` is fixed for a given anatomy configuration and is the concatenation of all active sensors' outputs (Section 3.3).

### 2.2 Action
```
Action: int            # an index into the configured discrete action set, in [0, n_actions)
```
The base system uses a **discrete action space** of size `n_actions`. **[D]**
A continuous action space is a permitted extension but is **[O]** (it changes the action layer's internals, Doc 05); the base build is discrete.

### 2.3 Sensorimotor event
```
SensorimotorEvent:
  previous_observation : Observation | null   # null only on the first event after a (re)start
  action               : Action      | null   # the action that produced `observation`; null only on the first event
  observation          : Observation               # always present
```
**MUST** hold: `previous_observation` is always the immediately preceding observation in time, and `action` is the action applied to produce `observation` from it — independent of any frame's map/drop decisions (Doc 03). An implementation **MUST NOT** make `previous_observation` depend on which frames mapped what.

---

## 3. Sensors

### 3.1 Interface — **[D]**
```
Sensor:
  id()          -> sensor_id
  width()       -> int                  # number of float values this sensor contributes to an observation
  read()        -> float[width()]       # current reading; called once per fast-loop step
```

### 3.2 Requirements
- Each sensor produces a fixed-width real vector per step.
- A sensor **MUST** return a value of exactly `width()` on every `read()`. If a hardware sensor has no new value, it returns its last value or a configured default; it **MUST NOT** return a different width.
- Sensors **MUST NOT** block the fast loop indefinitely; reads have a configured timeout, on which the sensor returns its default (Doc 07).

### 3.3 Composition into an observation
At each fast-loop step, the body reads all active sensors in a **fixed declared order** and concatenates their outputs into one `Observation`. `obs_dim` = sum of all active sensors' `width()`. The order is fixed for the lifetime of a configuration (changing it changes the meaning of every observation dimension and requires a fresh boot, not a restore). **[D]**

### 3.4 Self-description (telemetry; feature 029) — **[V]**
The body exposes `anatomy_meta()`: channel groups (sensor id, slice start,
width) in composition order and one labeled entry per global action id,
read from the *live* sensor/actuator lists so tool growth stays reflected.
Actuators may offer an optional `action_labels()` hook (the ROS2/Minecraft
`CommandActuator` derives labels from preset keys, `{}` → `idle`; the rover
drive names its four actions). This is inert data — nothing calls it unless
a telemetry tap is attached, and the tap publishes it verbatim as the
`brain.anatomy` subject (specs/029-brain-telemetry-dashboard/contracts/).

---

## 4. Actuators

### 4.1 Interface — **[D]**
```
Actuator:
  id()              -> actuator_id
  action_count()    -> int                  # number of discrete actions this actuator offers
  apply(local_action_index)                  # execute the action; index in [0, action_count())
```

### 4.2 Requirements
- The system's global action space is the **disjoint union** of all active actuators' actions: `n_actions` = sum of `action_count()` across active actuators. A global `Action` index maps deterministically to exactly one `(actuator, local_action_index)` pair via the fixed declared actuator order. **[D]**
- `apply` **MUST** be idempotent with respect to being called once per selected action and **MUST NOT** block the fast loop beyond a configured timeout.
- Actuators **MUST NOT** report success/meaning back as a privileged signal. The *only* feedback the system receives about its actions is through subsequent observations (sensors). This keeps the system sensorimotor: it learns the effects of actions by observing them.

---

## 5. Tools (runtime extension of the anatomy)

### 5.1 Interface — **[D]**
A tool is a sensor, an actuator, or both, registered after boot.
```
ToolRegistry:
  register_sensor(sensor)     -> sensor_id      # adds to the active sensor set
  register_actuator(actuator) -> actuator_id    # adds to the active actuator set
  deregister(id)                                # removes a tool
  list() -> [ {id, kind} ]
```

### 5.2 Requirements
- Registering a tool changes `obs_dim` and/or `n_actions`. The system **MUST** handle a change in `obs_dim` or `n_actions` without restart, by the following rule: **existing frames are preserved; their input/transition dimensions are adapted** so they continue to operate on the changed observation/action space. The adaptation rule is specified in Doc 03 §7 (frame I/O resize) and Doc 04 §6 (action-space change). **[D]**
- Tool registration is a structural event and **MUST** occur during the slow loop (consolidation), never mid-fast-loop, so the change is applied on a consistent state.
- **Out of scope / [O]:** the mechanism by which the *system itself* invents and registers a new tool. The `ToolRegistry` interface exists so this is possible later; the base build only registers tools supplied externally (by configuration or operator).

---

## 6. The Bus

### 6.1 Responsibility — **[V]** interface, **[V]** in-memory backend
The bus delivers each sensorimotor event to every registered frame and returns the collected per-frame results. It performs **delivery only**: no gating, scoring, learning, or birth. (Frame logic is Doc 03.)

### 6.2 Interface
```
Bus:
  register(frame)            -> frame_id
  unregister(frame_id)
  publish(event)             -> list<FrameResult>     # deliver to all registered frames, collect results
  subscribers()              -> list<frame_id>        # in deterministic order
```
`FrameResult` is defined in Doc 03 §2.

### 6.3 The in-memory synchronous backend (the only backend built now)
- `publish(event)` **MUST** deliver the event to every registered frame in a **deterministic order** (ascending `frame_id`), calling each frame's `process(event)` exactly once, and **MUST** return the list of results in that order only after all frames have processed the event.
- No queue, no buffering, no concurrency, no loss, no reordering.

### 6.4 Prohibitions
- The bus **MUST NOT** perform any frame logic.
- No other backend is implemented now.

### 6.5 Distribution seam — **[D]** (interface only; do not implement)
The `Bus` interface is the seam for a future asynchronous or distributed backend (e.g. an external broker, multiple machines). The whole system depends only on the `Bus` interface, never on the in-memory backend's concrete type. A future fire-and-forget backend cannot return all results synchronously from `publish`; the alternative result-collection mechanism is **out of scope now** and will be specified when distribution is built. Building the system against the interface (not the concrete backend) is mandatory so this is possible without rework.

---

## 7. Definition of done (this document)
1. Sensor, Actuator, and Tool interfaces exist as specified; observations are composed by fixed-order concatenation; the global action space is the fixed-order disjoint union.
2. The bus delivers events to frames in deterministic order and returns collected results, with the in-memory synchronous backend.
3. Tool registration changes `obs_dim`/`n_actions` during the slow loop and triggers the frame adaptation rules in Docs 03 and 04.
4. The system depends only on the `Bus` interface (distribution seam intact).
5. The only feedback path from actions to the system is through sensors.
