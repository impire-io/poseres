# 03 — Sensorimotor Core: Reference Frames, SIMD, Scoring

This document specifies the reference frames (the only learning components), how they are evaluated in SIMD batches, how their outputs are scored, and how the global pose is assembled. This is the validated core of the system.

---

## 1. Overview

A reference frame is a learnable, dimensioned coordinate space. It does two jobs:
- **Place**: turn an observation into a coordinate (local pose), via an encoder.
- **Predict**: given a pose and an action, predict the next pose, via a per-action transition model.

A frame holds **many concepts at once** (it is a space, not a slot for one object). The population of frames is the system's world-model. **[V]**

Every frame runs the **identical kernel**; frames differ only in their dimensionality `dim` and their learned weights. There **MUST NOT** be per-frame branching in the kernel. **[V]**

---

## 2. Data contracts

### 2.1 Frame result (returned per processed event)
```
FrameResult:
  frame_id     : int
  mapped       : bool
  local_pose   : float[dim] | null          # null iff mapped == false
  recon_error  : float | null               # this event's reconstruction error; null iff dropped
  pred_error   : float | null               # this event's prediction error; null iff dropped or no previous obs
  effort       : float | null               # this event's predicted-displacement magnitude; null iff dropped or no previous obs
```

### 2.2 Frame state (persists across events)
```
FrameState:
  frame_id      : int
  dim           : int
  is_candidate  : bool
  age_cycles    : int            # slow-loop cycles survived
  recon_err_ema : float          # EMA of reconstruction error
  pred_err_ema  : float          # EMA of prediction error
  effort_ema    : float          # EMA of effort
  weights       : (encoder, decoder, transition)   # Section 3
```

### 2.3 Global pose
```
GlobalPose: map<frame_id, float[dim]>   # one entry per frame that mapped the observation
```
Assembled by the engine after each event from all `FrameResult`s with `mapped == true`. It is the system's interpretation of the observation. It is consumed by the motivation and action layers (Doc 05) and **MUST** be available at each step.

---

## 3. Frame structure and math — **[V]**

Let `H` = `hidden_size` (Doc 07), `O` = current `obs_dim`, `D` = this frame's `dim`. All nonlinearities are elementwise `tanh`.

**Encoder** (observation → pose):
```
h    = tanh(W1 · obs + b1)         # W1: [H, O], b1: [H]
pose = W2 · h + b2                 # W2: [D, H], b2: [D]
```

**Decoder** (pose → reconstruction; used for the gate and the explanatory measurement):
```
hd    = tanh(Dc1 · pose + dc1)     # Dc1: [H, D], dc1: [H]
recon = Dc2 · hd + dc2             # Dc2: [O, H], dc2: [O]
```

**Transition** (pose + action → predicted next pose; independent network per action `a`):
```
th        = tanh(T1[a] · pose + tb1[a])   # T1: [n_actions, H, D], tb1: [n_actions, H]
pred_pose = T2[a] · th + tb2[a]           # T2: [n_actions, D, H], tb2: [n_actions, D]
```

### 3.1 Derived measurements
```
fit_quality(obs) = ||recon - obs|| / (||obs|| + 1e-6)                       # lower = better fit
prediction_error = ||pred_pose - encode(next_obs)|| / (||encode(next_obs)|| + 1e-6)
effort           = ||pred_pose - pose||
```
where `pose` and `pred_pose` are computed from the event's `previous_observation`, and `encode(next_obs)` is the encoder applied to the event's `observation`.

### 3.2 Initialization
On birth with a given `dim`:
- weight matrices drawn from `Normal(0, init_weight_scale²)`; biases zero;
- `recon_err_ema = pred_err_ema = effort_ema = 1.0` (a candidate spawned in the slow loop initializes these to `0.9`, Doc 04 §4);
- `age_cycles = 0`, `is_candidate = true`.

---

## 4. Processing one event — `process(event) -> FrameResult` — **[V]**

Given `event = (prev_obs, action, obs)`:

1. Compute `fit = fit_quality(obs)`.
2. **Gate.** If `fit >= fit_gate` (Doc 07): **drop**. Return `mapped=false`, all measurements null. Frame state unchanged.
3. **Map.** Otherwise:
   a. `pose = encode(obs)`.
   b. **Learn placement** (Section 5.1).
   c. `recon_err_ema ← ema_decay·recon_err_ema + (1−ema_decay)·fit`.
   d. If `prev_obs` and `action` are non-null:
      - compute `prediction_error` and `effort` (3.1) with current weights;
      - **learn transition** (Section 5.2);
      - update `pred_err_ema` and `effort_ema` with the same EMA rule.
   e. Return `mapped=true`, `local_pose=pose`, `recon_error=fit`, `pred_error` and `effort` (or null if no previous obs).

**MUST:** the gate decision uses reconstruction error only.

---

## 5. Learning — **[V]**

Standard single-hidden-layer gradient descent, learning rate `learning_rate`, **every gradient element clipped to `[−gradient_clip, +gradient_clip]` before the update**. The clip is mandatory; it prevents divergence.

### 5.1 Placement
Minimize `||recon − obs||²` by backpropagation through the decoder and then the encoder. Both decoder and encoder weights are updated.

### 5.2 Transition (two modes)
Updates **transition weights only**; the encoder is treated as fixed during this update (no gradient flows into the encoder from the transition loss).
- **Predictive mode (default):** minimize `||pred_pose − encode(next_obs)||²`.
- **Effort-only mode (diagnostic; see Doc 04 validation note):** minimize `||pred_pose||²`.

The mode is set once per run by configuration (`scoring_mode`, Doc 07) and applies to all frames. In both modes, the returned `pred_error` is always the *true* predictive error from 3.1.

---

## 6. The Scorer — **[V]**

The Scorer is the single place a frame's survival score is defined. It is a separate, replaceable component (cross-cutting requirement C2).

```
Scorer:
  combine(recon_err_ema, pred_err_ema, effort_ema) -> survival_score      # lower = better
```

**Default implementation** — weighted sum:
```
survival_score = w_explain·recon_err_ema + w_predict·pred_err_ema + w_effort·effort_ema
```
Default weights (Doc 07): `w_explain = 0.5`, `w_predict = 0.5`, `w_effort = 0.0`.

**MUST:** swapping the Scorer changes selection behavior with no change to frames, bus, or engine. The frame produces the three raw EMAs; it **MUST NOT** compute the survival score itself. The validated configuration uses the explanatory and predictive terms; the effort term is wired and available but defaults to weight 0.

---

## 7. The SIMD / vectorization requirement — **[V]**

This requirement is mandatory; it is what makes the system run many frames at scale on one machine.

- **Homogeneous kernel.** Every frame runs the kernel in Sections 3–5 with no per-frame conditional logic. All variation between frames is data: `dim` and weight values.
- **Batched evaluation by dimensionality group.** Frames of the same `dim` share weight-tensor shapes and **MUST** be evaluated together as a single batched operation: stack the per-frame weight tensors along a leading "frame" axis and compute encode, decode, transition, fit, and the learning updates for the whole group as batched array operations. Frames of different `dim` form separate groups, evaluated separately, and their results merged.
- **Prohibited.** Evaluating frames one at a time in an interpreted loop does **not** satisfy this requirement.
- **Frame I/O resize (for tool registration, Doc 02 §5).** When `obs_dim` changes, the encoder input width `O` and decoder output width `O` of every frame **MUST** be resized: existing weight columns/rows are preserved and new ones initialized from `Normal(0, init_weight_scale²)`. When `n_actions` changes, the transition tensors gain or remove per-action slices accordingly (new slices initialized from `Normal(0, init_weight_scale²)`; removed actions' slices discarded). This resize occurs during the slow loop only.

---

## 8. What the frame does NOT do
- It does not compute its survival score (the Scorer does).
- It does not decide its own birth, eviction, or `dim` (structural learning does, Doc 04).
- It does not select actions or compute value (the action and motivation layers do, Doc 05). It only *provides* poses and transition predictions that those layers use.

---

## 9. Definition of done (this document)
1. The frame kernel (Sections 3–5) exists exactly, with mandatory gradient clipping.
2. `process` implements gate → map/drop → place → predict, updating the three EMAs, returning a `FrameResult`.
3. The Scorer is a separate replaceable component with the default weighted-sum implementation and validated default weights.
4. The SIMD requirement holds: frames share one kernel and are evaluated in `dim`-grouped batches; one-at-a-time evaluation is absent.
5. Frame I/O resize works for `obs_dim`/`n_actions` changes during the slow loop.
6. The global pose is assembled each step and exposed to the motivation/action layers.
