# Data Model: The Event Pathway (feature 040)

## Entities

### EventHead (internal, owned by FrameStore)

| Field | Type | Semantics |
|---|---|---|
| `W` | `float64[A, D, D+1]` | Per-action linear delta model over all `D` sensed channels; column `D` is the bias. Cold start: zeros ("predicts no change"). |
| `updates` | `int` | Executed transitions learned from (telemetry/state, monotone). |
| `eta` | `float` | The NLMS step, from `Config.event_head_eta` (not persisted — config-in-force travels with the snapshot). |

Operations (all RNG-free):

- `predict(obs, action) -> float64[D]` — `W[action] @ [obs, 1]`.
- `learn(prev_obs, action, obs)` — NLMS: `W[action] += eta * outer(err, x) / (x @ x)` with `x = [prev_obs, 1]`, `err = (obs - prev_obs) - W[action] @ x`.
- `resize(new_obs_dim, new_n_actions)` — preserve existing entries bit-for-bit;
  zero-init growth (rows, columns, per-action blocks); truncate shrink.

State transitions: created iff `event_head_eta > 0` at store construction or
snapshot load with the key present; never created on the off path.

### Config (existing dataclass, additive field)

| Field | Type | Default | Validation |
|---|---|---|---|
| `event_head_eta` | `float` | `0.0` | `0 ≤ η < 2` ("event_head_eta must be in [0, 2) (0 = off; NLMS stability bound)") |

### PolicyContext (existing frozen dataclass, additive defaulted field)

| Field | Type | Default | Semantics |
|---|---|---|---|
| `predict_event_delta` | `Callable[[int], np.ndarray \| None]` | module-level `_no_event_delta` → `None` | Per-action predicted observation delta at the current observation; `None` when the head is off (or the inert baseline context). |

### CompletionItchPolicy (new public class, `pra.action.policy`)

Constructor: `(params: PolicyParams, *, kappa: float, progress_index: int,
pocket_index: int, completion_threshold: float = 1/128,
potential_of: Callable[[int], float] | None = None)`.

| Attribute | Type | Semantics |
|---|---|---|
| `completions_fired` | `int` | Directed selections where the completion rule fired for the chosen action. |
| `false_completions` | `int` | Fired completions whose realized pocket delta (next observation) did not exceed the threshold. |
| `progress_pred_error_ema` | `float` | EMA (decay 0.99) of \|predicted − realized\| progress delta on chosen directed actions; starts at 0.0 with a seen-count so early values are honest. |
| `last_was_directed` | `bool` | The established telemetry attribute (same as CuriosityLookaheadPolicy). |

Selection semantics (frozen to the measured gate): one ε uniform draw; random
path draws one integer; directed path scans actions ascending, skips frames
`predict_decoded(a) is None`, values
`drive + potential + κ·(progress_after − progress_now)`, lowest index wins
ties. `progress_after = 1.0` iff `Δ̂[pocket_index] > completion_threshold`
else `clip(obs[progress_index] + Δ̂[progress_index], 0, 1)`; the whole itch
term is 0 when `predict_event_delta(a)` is `None`. Index validation: on first
selection, `max(progress_index, pocket_index) < obs.shape[0]` or `ValueError`.

### Snapshot blob (existing format, additive-optional key)

| Key | Where | Present when | Content |
|---|---|---|---|
| `event_head` | `frame_store` state dict | head on | `{"W": ndarray copy, "updates": int}` |
| `eh__W` | `.npz` arrays | head on | the weights tensor |
| `meta["event_head"]` | meta JSON | head on | `{"updates": int}` |

Absent key on load → cold start (stated refill). Feature-off encode output is
byte-identical to the pre-040 format.

### Minecraft anatomy constants (new public constants)

| Constant | Value (derived) | Semantics |
|---|---|---|
| `C1_MINING_INDEX` | offset of sensor `mining`, label `progress` in `C1_SENSORS` order (= 14) | The sensed dig-progress channel. |
| `C1_POCKET_TOTAL_INDEX` | offset of sensor `pocket`, label `total` (= 15) | The sensed pocket-total channel (one item = 1/64). |

Derived by summing widths in spec order at import time — never hard-coded
literals, so a sensor-spec change moves them automatically (and the unit test
pins today's values).

## Relationships

```text
Config.event_head_eta ──► FrameStore(_EventHead)  ──state──► snapshot (eh__*)
                                   ▲    │ predict
             engine step loop ─────┘    ▼
             (event_learn per     PolicyContext.predict_event_delta
              executed transition)      │
                                        ▼
                              CompletionItchPolicy (itch term + watch)
                                        ▲
                    caller-injected potential_of (optional; research: clone Φ)
```
