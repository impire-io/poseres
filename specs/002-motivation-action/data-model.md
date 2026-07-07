# Phase 1 Data Model: Motivation and Action Layer

Entities derived from the feature spec and Doc 05 §2–§4, extending feature 001's
data model. Types are Python/numpy as in the existing core; "Validation" rows
are constructor/recorder rules.

---

## 1. Configuration additions (Doc 07; all frozen in `Config`)

| Group | Field | Type | Default | Validation |
|---|---|---|---|---|
| Drive | `drive_weights` | mapping name → float | `{"curiosity": 1.0}` | non-empty; weights finite, ≥ 0; names must match registered drives |
| Curiosity | `w_progress` | float | 1.0 | ≥ 0 |
| Curiosity | `w_novelty` | float | 1.0 | ≥ 0 |
| Curiosity | `lp_recent_window` | int | 60 | ≥ 1 |
| Curiosity | `lp_baseline_window` | int | 600 | > `lp_recent_window` |
| Curiosity | `novelty_memory_size` | int | 200 | ≥ 1 |
| Policy | `policy_mode` | enum | `random` | `random` \| `curiosity`; `random` is the pinned validation baseline |
| Policy | `exploration_epsilon` | float | 0.1 | in [0, 1] |
| Policy | `lookahead_min_age_cycles` | int | 2 | ≥ 0 |

> **Immutability rule (FR-003).** All of the above are fields of the existing
> frozen `Config`; per-drive parameter structs are themselves frozen. No runtime
> component holds a mutable reference to any drive parameter or weight.
> **Byte-identity rule (FR-008).** `policy_mode="random"` (the default) MUST
> leave every existing mode's RNG consumption and summary bytes unchanged.

---

## 2. Motivation entities (Doc 05 §2–§3)

### DriveContext (read-only view, built by the Engine each step)
`observation: float[obs_dim]` (current), `recent_pred_errors: Sequence[float]`
(the engine's per-step mean mapped prediction error, newest last),
`observation_memory: Sequence[float[obs_dim]]` (the bounded FIFO, newest last),
`step_index: int`.
Rule: the context exposes **no mutable handles** — drives read, never write
(bookkeeping updates are performed by the owning drive itself, after valuation).

### Drive (protocol)
`id() -> str`; `value(context) -> float`.
Rules: pure function of context + fixed params (no RNG, no hidden policy
state); MUST return a finite float for every reachable context, including the
first step of a run (FR-001).

### CuriosityDrive
Params (frozen): `w_progress`, `w_novelty`, `lp_recent_window`,
`lp_baseline_window`, `novelty_memory_size`.
Bookkeeping (mutable state, Doc 05 §3.3 — part of run state, never persisted):
`pred_error_history` (bounded to `lp_baseline_window`), `observation_memory`
(bounded FIFO of `novelty_memory_size`).
Derived terms:
- `learning_progress = max(0, mean(baseline slice) − mean(recent slice))`; 0
  until ≥ `lp_recent_window` baseline samples exist.
- `novelty(obs) = min_m ‖obs − m‖ / (‖obs‖ + 1e-6)`; **1.0 when memory empty**.
- `value = w_progress·learning_progress + w_novelty·novelty`.
Validation: mastered (flat-low) and unlearnable (flat-high) histories ⇒ LP ≈ 0;
falling history ⇒ LP > 0 (SC-005).

### WeightedDriveSet
`drives: tuple[Drive, ...]`, `weights: mapping id → float` (from Config).
`value(context) = Σ weights[d.id()] · d.value(context)`.
Validation: every configured weight has a matching drive id and vice versa;
evaluation order is the fixed registration order (determinism of float
accumulation).

---

## 3. Action entities (Doc 05 §4)

### PolicyContext (read-only view, built by the Engine each step)
`observation: float[obs_dim]`, `n_actions: int`, `best_frame:
(frame_id, dim, age_cycles) | None`, `predict_decoded(action) ->
float[obs_dim] | None` (one-step best-frame prediction decoded to observation
space; None when no eligible frame), `drive_value_of(obs) -> float` (the
drive-set valued at a hypothetical observation).

### Policy (protocol)
`select_action(context, rng) -> int` in `[0, n_actions)`.
Rules: all randomness from the passed seeded generator; deterministic given
(context, rng state).

### RandomPolicy (default; the pinned baseline)
Draws exactly `rng.integers(n_actions)` — one draw, nothing else. Byte-identical
to the validated engine's inline sampling (FR-008).

### CuriosityLookaheadPolicy
Params (frozen): `exploration_epsilon`, `lookahead_min_age_cycles`.
Per step: draw `u = rng.random()`; if `u < ε` **or** no best frame **or**
`best_frame.age_cycles < lookahead_min_age_cycles` ⇒ return
`rng.integers(n_actions)`. Else: for `a` in ascending order, value
`drive_value_of(predict_decoded(a))`; return the argmax, ties to the lowest
action index (no further draws).

---

## 4. Telemetry additions (conditional — research R2)

### PerSeedRunSummary (optional agency block)
Present **iff** the run used a drive (`policy_mode="curiosity"` / agency mode):
`value_signal_mean: float`, `value_signal_final: float`,
`learning_progress_mean: float`, `novelty_mean: float`,
`directed_fraction: float` (share of steps chosen by lookahead rather than
random/ε).
Rules: absent in every existing mode ⇒ canonical serialization of baseline runs
is byte-identical to the validated build (SC-003); all values finite; recorded
from step one (SC-001).

### AgencyRun (harness pairing, mirrors 001's SuiteRun)
`config`, `seeds`, `curious: list[PerSeedRunSummary]`,
`random: list[PerSeedRunSummary]` (same seed per pair — research R7),
`failed_seeds`, `wall_clock_seconds`, `per_seed_wall`.

### T7 verdict detail
Per seed: `curious_improvement`, `random_improvement`, `margin` (curious −
random). Verdict: PASS iff `margin ≥ 0` in a strict majority of seeds
(FR-009); the per-seed margins are always reported (never a mean alone).

---

## 5. Relationships

```
Config ──(frozen params)──> CuriosityDrive ──┐
   │                                        WeightedDriveSet ── value ──┐
   │                                                                    │
   └──> Engine.run(seed) ── per step ──> DriveContext ──────────────────┤
             │                                                          ▼
             │            PolicyContext (obs, best-frame predictor, drive) 
             │                     │                                     
             ├── Policy.select_action(ctx, rng) ──> action ──> world.step
             │        (RandomPolicy = pinned baseline; byte-identical)   
             └── telemetry: value signal per step (agency mode only)     

harness/agency.run_agency ── per seed: curious run + random run (same seed)
        └──> T7 evaluator ── margins per seed ──> verdict + report (honest rules)
```

### State transitions
- Drive bookkeeping: append-only bounded FIFOs updated once per step **after**
  valuation (value at step *t* sees memory through *t−1* — the first step sees
  an empty memory, novelty 1.0).
- Policy has no state across steps (stateless given context + rng), preserving
  the frame-population lifecycle exactly as validated.
