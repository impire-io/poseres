# Contract: Sensor / Actuator / Body / ToolRegistry (Doc 02 §3–§5)

## 1. Sensor

```python
class Sensor(Protocol):
    def id(self) -> str: ...
    def width(self) -> int: ...          # fixed for the sensor's lifetime
    def read(self) -> np.ndarray: ...    # exactly width() floats, every call
```
**MUST**: return exactly `width()` values on every read (wrong width →
`AnatomyError` naming the sensor). Timeout/default behavior is the sensor
implementer's duty in this in-process build (Doc 07 declares the fields).

## 2. Actuator

```python
class Actuator(Protocol):
    def id(self) -> str: ...
    def action_count(self) -> int: ...
    def apply(self, local_action_index: int) -> None: ...
```
**MUST NOT** return meaning/success — the only feedback path is subsequent
observations (Doc 02 §4.2; structural: `apply` returns None).

## 3. Body — the fixed-order composition, mounted as an EventSource

```python
Body(environment, sensors=[...], actuators=[...])   # declared order is semantic
  .reset() -> obs        # begin episode on the environment, compose first obs
  .step(a: int) -> obs   # route a -> (actuator, local), then compose all reads
  .obs_dim / .n_actions  # derived: sum of widths / disjoint-union size
```
**MUST**: concatenate sensor reads in declared order; route the global index
deterministically by fixed-order offsets; satisfy the existing `EventSource`
protocol so it mounts through the Engine's `world_factory`. A world mounted as
a single sensor/actuator pair MUST produce byte-identical runs to the direct
connection (SC-001).
**Contract test**: substitute sensors/actuators are accepted unchanged; the
Body passes `isinstance(_, EventSource)`.

## 4. ToolRegistry (on the Body)

```python
body.register_sensor(sensor) -> str      # queued; duplicate id rejected
body.register_actuator(actuator) -> str  # queued
body.deregister(tool_id)                 # queued; last sensor/actuator rejected
body.list_tools() -> [(id, kind)]
body.apply_pending_tools() -> (obs_dim, n_actions) | None   # slow loop only
```
**MUST**: defer all changes to `apply_pending_tools()` (called by the Engine at
the top of an offline cycle — C4); return the new dims when anything changed,
None otherwise.

## 5. Frame I/O resize (FrameStore)

```python
store.resize(new_obs_dim, new_n_actions, rng)   # Doc 03 §7
```
**MUST**: preserve existing weight entries bit-for-bit; grow trailing
observation columns/rows and trailing action slices with fresh draws at the
§8.8 effective scale (biases zero); discard trailing slices on shrink; draw in
the documented fixed order (groups ascending by dim; `W1, Dc2, T1, T2`);
update the store's current dims and effective learning rate.

## Inertness invariant

Without a body (plain world), the Engine's anatomy hook is one `getattr` per
offline cycle: no RNG, no float work, no behavior change (FR-008). The Bus is
untouched (Doc 02 §6 was built and validated in feature 001).
