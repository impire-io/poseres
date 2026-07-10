# PRA Validation System — System Specification

**Document 1 of 2.** This document defines *what is built now* and *how it functions*. Its companion, "PRA Validation System — Validation & Acceptance Specification" (Document 2), defines the synthetic world, the telemetry, and the acceptance tests that determine whether an implementation is correct and complete.

This is a functional specification. It states behavior and contracts as requirements. Where a value is given as a default, it is the value an implementer ships unless configuration overrides it. Where a requirement uses **MUST**, it is mandatory; **MUST NOT** is prohibited; **MAY** is permitted.

---

## 1. Purpose and scope

### 1.1 What this system is

The PRA Validation System is a **single-machine, deterministic, vectorized simulation** of the Pose Resolution Architecture. Its job is to let the architecture's claims be checked at meaningful scale (millions of observations, latent dimensionality in the tens) while keeping every failure attributable to exactly one component.

It is **not** the deployed "brain." It is the testbed that must pass before a deployed system is justified.

### 1.2 What this system is explicitly NOT (out of scope)

An implementer **MUST NOT** build any of the following as part of this system. They are named here so their absence is unambiguous and so the seams that will later accept them are built correctly (Section 9).

- **No message broker.** No NATS, no JetStream, no Kafka, no external queue. The bus is an abstraction (Section 4) with exactly one backend in this system: in-memory and synchronous.
- **No persistence.** No database, no durable storage, no checkpointing of frame state to disk. A run lives in memory and ends when it ends. (The evaluation harness writes result *summaries* to disk; that is not state persistence.)
- **No vector database / nearest-neighbor index.** No Chroma or equivalent. Frames hold their state in memory as plain arrays.
- **No distribution.** No multi-process, no multi-machine, no RPC. One process, one machine.
- **No real sensors or real data.** Input comes only from the synthetic world (Document 2).
- **No GPU requirement.** Vectorized CPU execution is sufficient and is the target. An implementer **MAY** use a GPU but **MUST NOT** make the system depend on one.

### 1.3 The question this system exists to answer

After this system passes its acceptance tests (Document 2), it must answer one open research question: **does spawn-and-select structural learning grow frames to the correct dimensionality when the true latent dimensionality is large (tens), under a biased proposal policy, at scale (millions of observations)?** All architectural decisions below serve keeping that question answerable with a single suspect.

---

## 2. Glossary

| Term | Meaning |
|---|---|
| **Observation** | A fixed-length real-valued vector emitted by the world. Length = `obs_dim`. |
| **Action** | An integer index in `[0, n_actions)` identifying which movement was applied. |
| **Sensorimotor event** | The unit delivered on the bus: `(previous_observation, action, observation)`. See 3.1. |
| **Frame** | A learnable coordinate space: an encoder, a decoder, and a per-action transition model. See Section 5. |
| **Local-pose** | The coordinate a single frame assigns to an observation. A real vector of length = that frame's `dim`. |
| **Global-pose** | The set of `(frame_id → local-pose)` entries from all frames that mapped a given observation. |
| **Map / drop** | A frame's decision, per observation, to assign it a pose (map) or ignore it (drop), based on a fit gate. |
| **Explanatory error** | Reconstruction error: how poorly a frame reconstructs the observation from its pose. |
| **Predictive error** | How poorly a frame's transition predicts the next pose given an action. |
| **Effort** | The magnitude of the pose displacement a transition predicts. |
| **Survival score** | The combined quantity used to select frames. Lower is better. Produced by the Scorer. |
| **Online phase** | Frame structure is fixed; frames place observations and learn weights. |
| **Offline phase** | Frame structure changes: candidates are spawned, poor frames are evicted. |
| **Candidate** | A newly spawned frame, protected from eviction until it has had enough exposure. |

---

## 3. Data contracts

All vectors are dense arrays of 64-bit floats unless stated otherwise. All randomness is drawn from a seeded generator (Section 8).

### 3.1 Sensorimotor event

The single unit of input flowing through the system.

```
SensorimotorEvent:
  previous_observation : float[obs_dim]  | null   # null only on the first event of an episode
  action               : int             | null   # null only on the first event of an episode
  observation          : float[obs_dim]                  # always present
```

**Requirement (event ordering):** `previous_observation` is **always** the observation from the immediately preceding step in the stream, and `action` is the action that was applied to produce `observation` from `previous_observation`. This is independent of any frame's map/drop decisions. A frame that dropped the previous observation still receives the true previous observation in the next event. An implementer **MUST NOT** make the event's `previous_observation` depend on which frames mapped what.

### 3.2 Frame result

What a frame returns after processing one event.

```
FrameResult:
  frame_id        : int
  mapped          : bool
  local_pose      : float[frame.dim] | null   # null iff mapped == false
  recon_error     : float | null              # this event's reconstruction error; null iff dropped
  pred_error      : float | null              # this event's prediction error; null iff dropped or no previous
  effort          : float | null              # this event's predicted-displacement magnitude; null iff dropped or no previous
```

### 3.3 Frame state (persistent across events within a run)

```
FrameState:
  frame_id        : int
  dim             : int
  is_candidate    : bool
  age_cycles      : int            # number of offline cycles survived
  recon_err_ema   : float          # exponential moving average of reconstruction error
  pred_err_ema    : float          # exponential moving average of prediction error
  effort_ema      : float          # exponential moving average of effort
  weights         : (encoder, decoder, transition)   # see Section 5
```

### 3.4 Global-pose

```
GlobalPose: map<frame_id, float[frame.dim]>   # one entry per frame that mapped the observation
```

The Global-pose is assembled by the Engine after each event from the `FrameResult`s where `mapped == true`. It is the architecture's full interpretation of that observation and **MUST** be available for telemetry. It is not persisted.

---

## 4. The Bus

### 4.1 Responsibility

The Bus delivers each sensorimotor event to every registered frame and returns the collected per-frame results. It does **not** gate, score, learn, or birth frames. It is delivery only.

### 4.2 Interface

```
Bus:
  register(frame)                         -> frame_id        # adds a frame as a subscriber
  unregister(frame_id)                                       # removes a frame
  publish(event) -> list<FrameResult>                        # delivers to all subscribers, collects results
  subscribers() -> list<frame_id>                            # current registration, in deterministic order
```

### 4.3 The single backend built now: in-memory synchronous

- `publish(event)` **MUST** iterate over registered frames in a **deterministic order** (registration order, equivalently ascending `frame_id`) and call each frame's `process(event)` exactly once.
- `publish` is **synchronous**: it returns only after every frame has processed the event, and it returns the list of `FrameResult` in subscriber order.
- There is no queue, no buffering, no concurrency, no message loss, no reordering. A given seed produces a byte-identical sequence of events and results on every run.

### 4.4 Prohibitions

- The Bus **MUST NOT** perform any frame logic (no gating, scoring, learning).
- No other backend is implemented in this system. The interface exists so an asynchronous backend can be added later (Section 9.1); building that backend now is out of scope.

---

## 5. The Frame

A frame is the only component that learns. Every frame runs the **identical** computational kernel; the only differences between frames are their `dim` and their learned weight values. There **MUST NOT** be per-frame branching in the kernel — see the homogeneity requirement (Section 7).

### 5.1 Structure

A frame holds three small networks. `H` = `hidden_size` (config). `O` = `obs_dim`. `D` = this frame's `dim`.

**Encoder** (observation → pose):
```
h    = tanh(W1 · obs + b1)         # W1: [H, O], b1: [H]
pose = W2 · h + b2                 # W2: [D, H], b2: [D]
```

**Decoder** (pose → reconstructed observation), used only for the fit gate and the explanatory error:
```
hd    = tanh(Dc1 · pose + dc1)     # Dc1: [H, D], dc1: [H]
recon = Dc2 · hd + dc2             # Dc2: [O, H], dc2: [O]
```

**Transition** (pose + action → predicted next pose), one independent network per action `a`:
```
th         = tanh(T1[a] · pose + tb1[a])   # T1: [n_actions, H, D], tb1: [n_actions, H]
pred_pose  = T2[a] · th + tb2[a]           # T2: [n_actions, D, H], tb2: [n_actions, D]
```

### 5.2 Derived quantities

```
fit_quality(obs)      = ||recon - obs|| / (||obs|| + 1e-6)            # lower = better fit
prediction_error      = ||decode(pred_pose) - next_obs|| / (||next_obs|| + 1e-6)   # OBSERVATION space
effort                = ||pred_pose - pose||                          # magnitude of predicted displacement
```

`decode` is the decoder (Section 5.1); `next_obs` is the event's `observation`; `pose` and `pred_pose` are computed from the event's `previous_observation`.

**Requirement:** `prediction_error` is measured in **observation** space — decode the predicted pose to an observation and compare it to the real next observation — **not** in the frame's own pose space (`||pred_pose − encode(next_obs)||`). A dimensionally-collapsed frame makes its own pose trivially predictable while predicting the world no better than baseline; the pose-space measure rewards that collapse and defeats T4, the observation-space measure does not. Transition *learning* (Section 5.6) still targets the next pose; only this survival *measurement* is in observation space.

### 5.3 Initialization

When a frame is born with a given `dim`:
- All weight matrices initialized from `Normal(0, init_weight_scale²)`; all bias vectors initialized to zero.
- `recon_err_ema = pred_err_ema = effort_ema = 1.0`.
- `age_cycles = 0`, `is_candidate = true`.
- A candidate spawned during an offline cycle (Section 6.4) initializes its EMAs to `0.9` instead of `1.0`. (This is a small head-start so a promising candidate is not evicted purely for being new; the young-frame protection in 6.4 is the primary mechanism.)

### 5.4 Processing one event — `process(event) -> FrameResult`

Given `event = (prev_obs, action, obs)`:

1. **Measure (every event).** Compute `fit = fit_quality(obs)`, and — if `prev_obs` and `action` are non-null — `prediction_error` and `effort` (Section 5.2) with the frame's *current* weights.
2. **Update survival EMAs (coverage-fair, every event).** Update `recon_err_ema = ema_decay · recon_err_ema + (1 - ema_decay) · fit`, and (when `prev_obs`/`action` are present) `pred_err_ema` and `effort_ema` with the same rule. These EMAs are updated whether or not the frame maps: a frame is scored on what it is *exposed to*, not only on what it elects to map.
3. **Gate (mapping + learning).** If `fit < fit_gate` (config) the frame **maps**: compute `pose = encode(obs)`; **learn placement** (Section 5.5); if `prev_obs`/`action` are present, **learn transition** (Section 5.6); the frame contributes `local_pose` to the global pose. Otherwise the frame does **not** map: no learning, no global-pose contribution (the EMAs in step 2 were still updated).
4. Return `FrameResult(mapped, local_pose=pose if mapped else null, recon_error=fit if mapped else null, pred_error=prediction_error_or_null if mapped else null, effort=effort_or_null if mapped else null)`. The per-event result is the telemetry view (measurements for mapped events, feeding T2); the coverage-fair EMAs in step 2 are the internal inputs to the Scorer.

**Requirement:** the gate decision uses reconstruction error only, and **learning happens only on mapped events** (sparsity by pull, Document 2 T1). But **survival scoring is coverage-fair** (EMAs updated every event): scoring only the cherry-picked mapped subset lets a low-dimensional frame explain little, very selectively, and still score well, which defeats dimensionality selection (T4).

### 5.5 Learning placement

Minimize squared reconstruction error `||recon - obs||²` by gradient descent through the decoder and then the encoder, with learning rate `learning_rate` and every gradient element clipped to `[-gradient_clip, +gradient_clip]` before the update. Both encoder and decoder weights are updated. (This is standard single-hidden-layer backpropagation; the clip is mandatory and is what prevents divergence.)

### 5.6 Learning transition (three modes)

The transition update minimizes a loss over the transition weights **only**. The encoder is treated as fixed during this update: poses are computed with the current encoder and **no gradient flows into the encoder from the transition loss**.

- **Predictive mode (default).** Loss = `||pred_pose - encode(next_obs)||²`. This trains the transition to predict reality.
- **Effort-only mode (ablation; see Document 2, T3 weak clause).** Loss = `||pred_pose||²`. This trains the transition to predict the smallest move, ignoring reality.
- **Identity mode (ablation; see Document 2, T3 strong clause).** Loss = `||pred_pose - pose||²`. This trains the transition to predict that the pose stays where it is — through the decoder, the learned "nothing changes" (persistence) predictor.

The mode is set once per run by configuration (`scoring_mode ∈ {predictive, effort_only, identity}`) and applies to all frames in that run. In **every** mode the returned `pred_error` is the *true* predictive error from 5.2 (the ablation runs still measure honestly; they just do not learn from that measurement).

Gradient descent uses `learning_rate` and the same `[-gradient_clip, +gradient_clip]` clip.

### 5.7 What the frame does NOT do

- The frame **MUST NOT** compute the survival score. It produces the three raw EMAs; combining them is the Scorer's job (Section 6.2). This keeps evaluation swappable.
- The frame **MUST NOT** decide its own birth, eviction, or dimensionality. The Engine and policies own structure.

---

## 6. The Engine and the learning lifecycle

The Engine owns the frame population, drives the world, publishes events, applies the Scorer and policies, and records telemetry.

### 6.1 Components the Engine holds

```
Engine holds:
  event_source     : EventSource          # the world for validation (Document 2); a seam (Section 9.4)
  bus              : Bus
  scorer           : Scorer
  proposal_policy  : ProposalPolicy
  decay_policy     : DecayPolicy
  frames           : list<Frame>           # starts EMPTY (zero-start)
  config           : Config                # Section 8
  rng              : RandomGenerator       # single seeded source
  telemetry        : Telemetry             # Document 2, Section on telemetry
```

### 6.2 The Scorer

```
Scorer:
  combine(recon_err_ema, pred_err_ema, effort_ema, dim) -> survival_score   # lower = better
```

**Default implementation:** weighted sum with a parsimony term.
```
survival_score = w_explain · recon_err_ema + w_predict · pred_err_ema + w_effort · effort_ema + w_complexity · dim
```
Default weights: `w_explain = 0.5`, `w_predict = 0.5`, `w_effort = 0.0`, `w_complexity = 0.04`.

**Requirement:** the Scorer is the single place survival scoring is defined. Swapping the Scorer implementation **MUST** change selection behavior without any change to frames, bus, or engine. The default weights above are the configuration validated by the simulation; `w_effort` defaults to 0 because the validated configuration used explanatory + predictive terms only. The effort term is wired and available but inactive by default.

**The parsimony term (`w_complexity · dim`) is required for T4.** With honest, coverage-fair errors, reconstruction and prediction error keep drifting down past the true dimensionality via overfit, so "lowest error wins" over-dimensions. The per-dimension penalty puts the winner at the start of the diminishing-returns plateau (MDL / Occam) — the true dimensionality. Its weight is expected to be tuned: too small over-dimensions, too large collapses toward `dim = 1`.

### 6.3 Online episode — `run_online_episode(steps)`

```
obs        = event_source.reset()      # start a new episode on a (randomly chosen) object
prev_obs   = null
prev_act   = null

repeat `steps` times:
    event   = SensorimotorEvent(prev_obs, prev_act, obs)
    results = bus.publish(event)                       # every frame maps or drops

    mapped  = [r for r in results if r.mapped]

    if mapped is empty:
        # zero-start / no-loss rule: birth a frame for this observation
        if frames is empty:
            dim = uniform_int(initial_dim_min, initial_dim_max)     # via rng
        else:
            best_dim = dim of the frame with lowest survival_score
            dim      = max(1, best_dim + uniform_choice({-1, 0, +1}))  # via rng
        new_frame = birth_frame(dim)        # initialize per 5.3, register on bus
        record loss event in telemetry (only counted post-warmup; see Document 2)

    assemble global_pose from `mapped`        # for telemetry
    record per-step telemetry:
        map_fraction      = count(mapped) / count(frames)
        mean_pred_error   = mean(r.pred_error for r in mapped if r.pred_error is not null)   # may be empty early

    prev_obs = obs
    prev_act = uniform_int(0, n_actions)      # via rng
    obs      = event_source.step(prev_act)
```

**Requirements:**
- Structure is fixed during an online episode except for births triggered by the no-loss rule. No eviction occurs online.
- Survival scores are computed on demand from the frames' EMAs via the Scorer wherever "lowest survival_score" is needed.

### 6.4 Offline cycle — `run_offline_cycle()`

Runs between blocks of online episodes. Performs aging, eviction, and spawning. This is where structural learning happens, and the eviction policy here is the primary guarantee that the population stays bounded.

```
cycle += 1

# 1. Age every frame; matured candidates become ordinary frames.
for f in frames:
    f.age_cycles += 1
    if f.is_candidate and f.age_cycles >= min_age_cycles:
        f.is_candidate = false

# 2. Eviction (soft threshold + hard cap), protecting young frames.
# Threshold DIVIDES by the population factor: crowding tightens the tolerated-error
# bar, so eviction pressure rises with the population and paces the spawn rate.
threshold = survive_threshold_base / (1 + survive_threshold_pop_coeff · max(0, count(frames) - survive_threshold_pop_baseline))

evictable = [ f for f in frames
              if f.age_cycles >= min_age_cycles            # young/candidate frames are protected
              and scorer.combine(f.emas, f.dim) > threshold ]   # scored worse than the (population-scaled) threshold

# Soft eviction: remove all evictable frames, but never drop below min_frames.
sort evictable by survival_score descending (worst first)
for f in evictable:
    if count(frames) <= min_frames: break
    remove f from frames; unregister from bus

# Hard cap: if still over max_frames, remove the worst eligible frames until at cap.
while count(frames) > max_frames:
    worst = the frame with highest survival_score among those with age_cycles >= min_age_cycles
    if no such frame exists: break        # everything over the cap is still protected; allow temporary overflow
    remove worst from frames; unregister from bus

# 3. Spawn candidates (rate-limited). Re-dimensioning is the spawn knob.
repeat `spawn_per_cycle` times:
    best_dim = dim of the frame with lowest survival_score (or initial range if population empty)
    new_dim  = proposal_policy.propose_dimension(best_dim, population_dims, rng)
    cand     = birth_frame(new_dim)       # initialize per 5.3 with candidate EMAs = 0.9
    cand.is_candidate = true
```

**Requirements:**
- Young-frame protection (`age_cycles < min_age_cycles`) **MUST** exempt a frame from both soft eviction and the hard cap, so a freshly spawned candidate of a new dimensionality always gets at least `min_age_cycles` offline cycles (i.e. several online episodes each) of exposure before it can be removed.
- The hard cap is the bound on memory and compute; the soft threshold is the routine pressure. Together they **MUST** keep the population bounded (Document 2, T5). The population-scaled threshold (5.3 / above) **MUST** divide by the population factor so eviction *paces* the spawn rate and the population **self-limits** below the cap — not merely grow to the cap and stop. A threshold that rises with population makes soft eviction vanish and fails T5's "self-limits, not merely capped" criterion.

### 6.5 Proposal policy

```
ProposalPolicy:
  propose_dimension(best_dim, population_dims, rng) -> new_dim
```

**Default implementation (biased proposal):**
```
if rng.uniform() < exploit_prob:                 # exploit: search near the current best
    new_dim = max(1, best_dim + rng.choice({-1, +1}))
else:                                            # explore: occasional jump
    new_dim = rng.uniform_int(1, best_dim + explore_dim_max_offset)
```
Defaults: `exploit_prob = 0.75`, `explore_dim_max_offset = 4`.

**Requirement:** the proposal policy is pluggable. It is the component expected to change when the system is run at high true dimensionality (the open research question, 1.3): a near-random proposal cannot cover a large dimensionality range fast enough, so a higher-dimensionality run will supply a different proposal policy. The interface **MUST** allow this without touching any other component.

**Measured high-dimensionality variant (PROPOSAL-DIAGNOSIS, 2026-07-08):** the climbing policy — every proposal in `(best_dim, best_dim + explore_dim_max_offset]` (exploit `+{1,2}`, else explore uniform in the band). The jump-size dose–response showed selection at scale is **waste-limited, not reach-limited**: proposals at or below the incumbent burn a maturation window, proposals far above die on their transient; the tight just-above band doubles the fixed-budget median `best_dim` (~1 rung per maturation window). It is **opt-in, not the scale default**: un-throttled climbing exposed the open threshold-scale problem (Section 8.8), under which its scaled `best_dim` ratchets with the proposals rather than tracking the world. Deploy it once the survival bar scales.

### 6.6 Full run — `run(seed)`

```
seed the rng with `seed`
build event_source, bus, scorer, policies, empty frame population from config

# Warmup: online only, lets the zero-start population grow before structure is judged.
repeat `warmup_episodes` times:
    run_online_episode(steps_per_episode)
mark telemetry "warmed" = true     # loss counting starts here (Document 2)

# Main loop: alternate online learning and offline structural change.
repeat `n_cycles` times:
    repeat `episodes_per_cycle` times:
        run_online_episode(steps_per_episode)
    run_offline_cycle()

return collected telemetry for this seed
```

---

## 7. Cross-cutting requirements

### 7.1 Determinism

A full run is **fully reproducible from its seed**. Every source of randomness — world construction, frame weight initialization, action sampling, proposal-policy choices, and any tie-breaking (e.g. selecting "the lowest survival_score" when two are equal: break ties by ascending `frame_id`) — **MUST** draw from the single seeded generator in a fixed order. Two runs with the same seed and config produce identical telemetry. This is mandatory; it is the property that keeps failures attributable to one component.

### 7.2 Homogeneous, vectorizable kernel

- Every frame runs the **identical** kernel (Section 5). There **MUST NOT** be per-frame conditional logic in encode, decode, transition, or learning. All variation between frames lives in data: their `dim` and their weight values.
- The system **MUST** support **batched evaluation across frames**. Because frames of different `dim` have different weight-tensor shapes, the required layout is: **group frames by `dim`; within each group, stack the per-frame weights along a leading frame axis and compute encode/decode/transition/fit for the whole group as batched array operations.** Groups of different `dim` are processed separately and their results merged. An implementation that evaluates frames one Python-level loop iteration at a time does **not** satisfy this requirement.
- This batched layout is what makes the scale goal (1.3, and Document 2's scaled test) achievable on one machine. It is a hard requirement, not an optimization.

### 7.3 Component isolation (the seams that must stay clean)

The following **MUST** each be a single, replaceable component with no logic leaking into others:
- **Bus** (delivery) — Section 4.
- **Scorer** (evaluation) — Section 6.2.
- **ProposalPolicy** and **DecayPolicy** (structural learning) — Sections 6.4, 6.5.
- **EventSource** (input boundary) — Section 9.4 and Document 2.

Swapping any one **MUST NOT** require edits to the others.

---

## 8. Configuration

All parameters, with types, defaults, and valid ranges. An implementation **MUST** expose every one of these as configuration; defaults are used when unset.

### 8.1 World / stream
| Parameter | Type | Default | Range / notes |
|---|---|---|---|
| `true_dim` | int | 3 | ≥ 1. Validation sweeps this up to ~50. Hidden from the agent. |
| `obs_dim` | int | 10 | ≥ 1. Recommended ≥ 3 × `true_dim`. |
| `n_objects` | int | 4 | ≥ 1 |
| `n_actions` | int | 4 | ≥ 1 |
| `sensor_noise_std` | float | 0.04 | ≥ 0 |
| `action_scale` | float | 0.4 | > 0 |

### 8.2 Frame
| Parameter | Type | Default | Range / notes |
|---|---|---|---|
| `hidden_size` | int | 12 | ≥ 1 |
| `init_weight_scale` | float | 0.3 | > 0 |
| `learning_rate` | float | 0.03 | > 0 |
| `gradient_clip` | float | 1.0 | > 0. Per-element clip. Mandatory. |
| `ema_decay` | float | 0.9 | in [0, 1); new-sample weight is `1 - ema_decay` |

### 8.3 Gating and zero-start birth
| Parameter | Type | Default | Range / notes |
|---|---|---|---|
| `fit_gate` | float | 1.0 | > 0. Map iff `fit_quality < fit_gate`. |
| `initial_dim_min` | int | 2 | ≥ 1 |
| `initial_dim_max` | int | 6 | ≥ `initial_dim_min` |

### 8.4 Scorer
| Parameter | Type | Default | Range / notes |
|---|---|---|---|
| `scoring_mode` | enum | `predictive` | `predictive`, `effort_only`, or `identity` (ablations; §5.6) |
| `w_explain` | float | 0.5 | ≥ 0; on coverage-fair `recon_err_ema` |
| `w_predict` | float | 0.5 | ≥ 0; on coverage-fair, observation-space `pred_err_ema` |
| `w_effort` | float | 0.0 | ≥ 0 (validated default is 0) |
| `w_complexity` | float | 0.04 | ≥ 0; parsimony penalty per latent `dim` (MDL/Occam); expected to be tuned |

### 8.5 Proposal policy
| Parameter | Type | Default | Range / notes |
|---|---|---|---|
| `exploit_prob` | float | 0.75 | in [0, 1] |
| `explore_dim_max_offset` | int | 4 | ≥ 1 |

### 8.6 Decay / offline (the block most likely to need tuning)
| Parameter | Type | Default | Range / notes |
|---|---|---|---|
| `survive_threshold_base` | float | 0.8 | > 0 |
| `survive_threshold_pop_coeff` | float | 0.04 | ≥ 0; threshold **divides** by `(1 + coeff·…)` so crowding tightens the bar (§6.4) |
| `survive_threshold_pop_baseline` | int | 4 | ≥ 0 |
| `spawn_per_cycle` | int | 1 | ≥ 0 |
| `min_age_cycles` | int | 2 | ≥ 0. Young-frame protection. |
| `min_frames` | int | 1 | ≥ 1 |
| `max_frames` | int | 200 | ≥ `min_frames`. Hard population cap. |

### 8.7 Run schedule
| Parameter | Type | Default | Range / notes |
|---|---|---|---|
| `warmup_episodes` | int | 25 | ≥ 0 |
| `n_cycles` | int | 18 | ≥ 0 |
| `episodes_per_cycle` | int | 6 | ≥ 1 |
| `steps_per_episode` | int | 40 | ≥ 1 |
| `seeds` | list<int> | [1,2,3,4,5,6,7,8] | ≥ 1 seed |

### 8.8 Scale-invariant parameter rules **[D]**

Every constant above was validated at the reference scale `obs_dim = 10`,
`hidden_size = 12`, `true_dim = 3`. Three of them are **regime-dependent**: used
raw at larger dimensions they silently leave their validated operating regime
(evidence and measurements: `SCALE-DIAGNOSIS.md`). Implementations **MUST** apply
the raw parameter through these effective forms. Each factor is exactly 1 at the
reference scale, so reference behavior is byte-identical.

| Rule | Effective form | Why |
|---|---|---|
| Learning rate | `learning_rate · (10 / obs_dim)^1.5` | SGD stability threshold shrinks as input norms grow; raw 0.03 diverges at `obs_dim = 60` (recon 1.14 vs 0.34 at the scaled rate). Exponent 1.5 is empirical **[D]** (the naive bound gives 1; measured at `obs_dim = 60`, the 1.5-rule dominates the 1.0-rule at every scanned dim). |
| Weight init | per-tensor `init_weight_scale · sqrt(fan_in_ref / fan_in)` for the tensors whose fan-in is `obs_dim` (encoder in) or `hidden_size` (pose/recon/transition out); pose-dim fan-ins stay raw | Unscaled init saturates the encoder at birth (`0.3·sqrt(60) ≈ 2.3` pre-activation sd) and initial output magnitude grows with `sqrt(hidden)`. |
| Parsimony | `w_complexity · (10 / obs_dim)` | The per-dim error span flattens as the world's information spreads over more observation dims; the raw linear penalty (0.68 across dims 2→20) overwhelms the achievable error gain (~0.27) and forces collapse to low dim. |
| Young-frame protection | `round(min_age_cycles · (obs_dim / 10)^1.5)` | Convergence time grows by the inverse of the learning-rate factor; judged at the raw window a scaled candidate is evicted on its transient score (~0.85) long before its asymptote (~0.44), freezing selection at low dim regardless of schedule length. Dose–response at `true_dim = 20`: patience 2/12/24/29 → mean `best_dim` 4.7/5.7/6.7/10.7, one seed reaching 18 (within-one). |

Additionally, scaled runs **MUST** set `hidden_size ≳ 2 × true_dim`: a frame
cannot resolve dimensionality past its own hidden width (at `hidden_size = 12`
the dimension scan plateaus at dim ≈ 10–16 regardless of the true value).

**Known open seventh rule (identified, not yet designed — PROPOSAL-DIAGNOSIS,
2026-07-08):** `survive_threshold_base` is scale-variant in the same family.
At the reference, mature scores (~0.37) sit far under the population-scaled
bar (~0.65); at `obs_dim = 60` the achievable juvenile score at maturity
(~0.42+) sits *above* the bar (~0.36–0.40) for every dim past ~12, so the
mature niche is marginal-to-empty and selection is governed by the maturation
filter (score at `age = patience` vs the absolute bar), not by the score
surface (Section 6.2's, measured healthy at scale). A reference-preserving
`effective_survive_threshold_base` rule is the natural candidate; until it
exists, scaled `best_dim` readings describe the juvenile conveyor's
composition under the proposal policy in force.

---

## 9. Forward seams (built now, populated later — DO NOT implement the later side)

These exist so the system that *is* built does not have to be rewritten when the deployed system is built. Build the seam (the interface and the one in-scope implementation); do not build the out-of-scope implementation.

### 9.1 Bus backend seam
The `Bus` interface (Section 4.2) is the seam. The in-memory synchronous backend is the only implementation now. A future asynchronous/distributed backend will need a different result-collection mechanism than `publish` returning a list (fire-and-forget delivery cannot synchronously return all results); designing that mechanism is out of scope. The interface **MUST** be defined such that the engine depends only on it, not on the in-memory backend's concrete type.

### 9.2 Scorer seam
The `Scorer` interface (Section 6.2) is the seam for changing the evaluation later. Nothing further to build now.

### 9.3 Frame-storage seam
Frames hold their state in memory as plain arrays now. If a future deployed frame needs fast nearest-neighbor lookup over stored poses, that is a vector-index concern that attaches behind a storage interface. Build frames so their state access goes through a small internal accessor (not scattered field reads across the codebase), so a storage backend could later be introduced. Do not build the storage backend.

### 9.4 EventSource seam
```
EventSource:
  reset() -> observation        # begin a new episode; returns the first observation
  step(action) -> observation   # apply an action; returns the resulting observation
```
The validation world (Document 2) implements this. Real sensors or a distributed simulator would implement it later. The engine **MUST** depend only on this interface, never on the concrete world.

---

## 10. Worked example (normative illustration)

A single online step with two frames already alive (`F1` dim 2, `F2` dim 4):

1. Engine builds `event = (prev_obs, action=2, obs)`.
2. `bus.publish(event)` calls `F1.process` then `F2.process` (ascending id).
3. `F1`: `fit_quality(obs) = 0.7 < 1.0` → maps. Encodes pose `[0.3, -1.1]`. Learns placement. `recon_err_ema` updated with 0.7. `prev_obs` present → computes `pred_error = 0.2`, `effort = 0.4`, learns transition (predictive mode), updates `pred_err_ema`, `effort_ema`. Returns mapped result.
4. `F2`: `fit_quality(obs) = 1.3 ≥ 1.0` → drops. State unchanged. Returns dropped result.
5. Engine: `mapped = [F1]`. Global-pose = `{F1: [0.3, -1.1]}`. `map_fraction = 1/2 = 0.5`. `mean_pred_error = 0.2`.
6. Engine samples next action, advances the world, loops.

A single offline cycle with population `[F1(dim2, age3, score0.18), F2(dim4, age3, score0.41), C(dim3, age1, candidate, score0.7)]`, `threshold` computed at, say, 0.8:

1. Age all: F1→4, F2→4, C→2 (C matures: `is_candidate=false`).
2. Eviction: threshold 0.8. Evictable = frames with `age≥min_age_cycles(2)` and score>0.8. None exceed 0.8, so none evicted. (C is now age 2 and eligible, but its score 0.7 < 0.8.)
3. Hard cap (200) not exceeded.
4. Spawn 1: best is F1 (dim 2). Proposal exploits with prob 0.75 → e.g. `new_dim = 3`. Birth candidate `C2(dim3, age0, candidate, EMAs=0.9)`, register on bus.

---

## 11. Definition of done (for this document's scope)

An implementation satisfies this specification when:
1. Every component in Sections 4–6 exists with the stated interface and behavior.
2. Every configuration parameter in Section 8 is exposed with the stated default.
3. The determinism requirement (7.1) holds: identical seed + config → identical telemetry, verified by running the same seed twice.
4. The homogeneity and batched-evaluation requirements (7.2) hold: frames share one kernel and are evaluated in `dim`-grouped batches.
5. The component-isolation requirement (7.3) holds: Bus, Scorer, ProposalPolicy, DecayPolicy, and EventSource are each swappable in isolation.
6. None of the out-of-scope items (1.2) are present.
7. The system passes the acceptance tests defined in Document 2.

Correctness against the *behavioral* claims (sparsity, prediction, ablation, structure growth, bounded population, no-loss) is defined entirely by Document 2.
