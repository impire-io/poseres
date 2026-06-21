# Contract: The five swappable seams (PRA-01 §7.3)

Each interface below MUST be a single, replaceable component. Swapping any one MUST NOT
require edits to the others (PRA-01 §7.3). The Engine depends only on these interfaces,
never on a concrete backend type. Each seam has exactly the in-scope default
implementation listed; the out-of-scope side is **not** built (PRA-01 §9).

Python form: each seam is an abstract base class (or `typing.Protocol`); defaults are
concrete classes injected into the Engine. Contract tests (`tests/contract/`) verify a
substitute implementation can stand in without touching collaborators.

---

## 1. Bus — delivery only (PRA-01 §4)

```python
class Bus(Protocol):
    def register(self, frame) -> int: ...          # returns frame_id
    def unregister(self, frame_id: int) -> None: ...
    def publish(self, event: SensorimotorEvent) -> list[FrameResult]: ...
    def subscribers(self) -> list[int]: ...         # deterministic order (ascending frame_id)
```

**Default:** `InMemorySyncBus`. `publish` delivers to every subscriber in ascending
`frame_id` order, exactly once, synchronously, and returns results in subscriber order.
No queue, buffering, concurrency, loss, or reordering.
**MUST NOT:** perform gating/scoring/learning/birth (delivery only).
**Contract test:** identical seed ⇒ byte-identical event/result sequence; substituting a
recording double preserves order.

> Note: with batched evaluation (PRA-01 §7.2) the in-memory Bus delegates delivery to the
> Engine's `dim`-grouped FrameGroups but MUST preserve the per-`frame_id` ordering and the
> "delivery only" contract.

---

## 2. Scorer — evaluation (PRA-01 §6.2)

```python
class Scorer(Protocol):
    def combine(self, recon_err_ema, pred_err_ema, effort_ema, dim) -> float: ...  # lower=better
```

**Default:** `WeightedSumScorer` =
`w_explain·recon + w_predict·pred + w_effort·effort + w_complexity·dim`
(defaults 0.5/0.5/0.0/0.04). Vectorized form scores a whole FrameGroup at once.
**MUST:** be the single place survival scoring is defined; swapping it changes selection
with no change to frames/bus/engine.
**Contract test:** a substitute Scorer (e.g. error-only, no parsimony) changes which
frame is "best" without any other edit.

---

## 3. ProposalPolicy — what dimension to spawn (PRA-01 §6.5)

```python
class ProposalPolicy(Protocol):
    def propose_dimension(self, best_dim: int, population_dims, rng) -> int: ...
```

**Default (biased):** with prob `exploit_prob` → `max(1, best_dim ± 1)`; else explore →
`uniform_int(1, best_dim + explore_dim_max_offset)`. All draws from the passed seeded
`rng`.
**MUST:** be pluggable — this is the component expected to change for the high-dim scale
study (the open research question). A high-dim policy MUST be substitutable here without
touching any other component.
**Contract test:** a high-dim proposal substitute is accepted by the Engine unchanged.

---

## 4. DecayPolicy — eviction/spawning pressure (PRA-01 §6.4)

```python
class DecayPolicy(Protocol):
    def threshold(self, population_size: int) -> float: ...        # population-scaled
    def evict(self, frames, scorer, threshold, *, min_frames, max_frames, min_age_cycles) -> list[int]:
        ...  # returns frame_ids to remove (soft + hard cap, young-protected)
```

**Default:** `threshold = survive_threshold_base / (1 + survive_threshold_pop_coeff ·
max(0, n − survive_threshold_pop_baseline))` — it **divides** by the population factor so
crowding tightens the bar and eviction paces spawn (the corrected direction). Soft-evict
every unprotected frame over threshold (worst first, never below `min_frames`), then hard
cap to `max_frames`. Young frames (`age_cycles < min_age_cycles`) are exempt from both.
**MUST:** keep the population bounded **and** self-limiting (T5).
**Contract test:** with a fixed population the default threshold decreases as population
grows; young frames are never evicted.

---

## 5. EventSource — input boundary (PRA-01 §9.4, PRA-02 §1)

```python
class EventSource(Protocol):
    def reset(self) -> "observation": ...          # begin a new episode; first observation
    def step(self, action: int) -> "observation": ...
```

**Default:** `SensorimotorWorld` — `n_objects` objects each with start latent
`Normal(0,1)[true_dim]` and emission matrix `Normal(0,1)[obs_dim,true_dim]`; `n_actions`
displacements `Normal(0,1)[true_dim]·action_scale`. `emit = tanh(E_k·latent) + noise`,
noise `Normal(0, sensor_noise_std²)`. Draw order: objects (start then emission, per
object index) then actions.
**MUST:** be **nonlinear** (the `tanh`) — MUST NOT be replaced by a linear map.
**MUST NOT:** expose `true_dim`, latents, emission matrices, displacements, or object
indices to the engine, frames, or acceptance-test telemetry. The only output the system
sees is the observation vector. (`true_dim` is known to the **harness** for scoring T4.)
**Contract test:** identical seed ⇒ identical observation stream; a substitute source is
accepted by the Engine unchanged; no hidden state leaks into any FrameResult/telemetry.

---

## Cross-seam invariant

All five draw randomness only from the single seeded generator passed in (PRA-01 §7.1).
No seam holds its own unseeded RNG. Tie-breaking ("lowest survival_score") is by
ascending `frame_id`.
