# 07 — Configuration Reference

Every configuration parameter in the system, with type, default, valid range, the document that defines its behavior, and its status tag. An implementation **MUST** expose every parameter listed here; defaults apply when unset.

Status: **[V]** validated, **[D]** design, **[O]** open (see Doc 00 legend).

---

## 1. Anatomy (Doc 02) — supplied per body, no universal default

| Parameter | Type | Default | Range / notes | Status |
|---|---|---|---|---|
| `sensors` | ordered list of sensor declarations | — (required) | each declares `id` and `width`; fixed order defines observation layout | [D] |
| `actuators` | ordered list of actuator declarations | — (required) | each declares `id` and `action_count`; fixed order defines the action index mapping | [D] |
| `obs_dim` | int (derived) | sum of sensor widths | ≥ 1; not set directly — computed from `sensors` | [D] |
| `n_actions` | int (derived) | sum of actuator action counts | ≥ 1; not set directly — computed from `actuators` | [D] |
| `sensor_read_timeout_ms` | int | 50 | ≥ 0; on timeout a sensor returns its default | [D] |
| `actuator_apply_timeout_ms` | int | 50 | ≥ 0 | [D] |

---

## 2. Reference frames (Doc 03)

| Parameter | Type | Default | Range / notes | Status |
|---|---|---|---|---|
| `hidden_size` | int | 12 | ≥ 1 | [V] |
| `init_weight_scale` | float | 0.3 | > 0 | [V] |
| `learning_rate` | float | 0.03 | > 0 | [V] |
| `gradient_clip` | float | 1.0 | > 0; per-element clip; mandatory | [V] |
| `ema_decay` | float | 0.9 | in [0, 1); new-sample weight is `1 − ema_decay` | [V] |
| `fit_gate` | float | 1.0 | > 0; map iff `fit_quality < fit_gate` | [V] |

---

## 3. Scorer (Doc 03 §6)

| Parameter | Type | Default | Range / notes | Status |
|---|---|---|---|---|
| `scoring_mode` | enum | `predictive` | `predictive` or `effort_only` (diagnostic); applies to all frames | [V] |
| `w_explain` | float | 0.5 | ≥ 0; on coverage-fair `recon_err_ema` (Doc 03 §4) | [V] |
| `w_predict` | float | 0.5 | ≥ 0; on coverage-fair, **observation-space** `pred_err_ema` (Doc 03 §3.1) | [V] |
| `w_effort` | float | 0.0 | ≥ 0; validated default is 0 | [V] |
| `w_complexity` | float | 0.04 | ≥ 0; parsimony — penalty per latent `dim` (MDL/Occam); selects the true dimensionality; **expected to be tuned** | [D] |

---

## 4. Structural learning (Doc 04)

| Parameter | Type | Default | Range / notes | Status |
|---|---|---|---|---|
| `initial_dim_min` | int | 2 | ≥ 1 | [V] |
| `initial_dim_max` | int | 6 | ≥ `initial_dim_min` | [V] |
| `spawn_per_cycle` | int | 1 | ≥ 0 | [V] |
| `exploit_prob` | float | 0.75 | in [0, 1]; proposal policy | [D] |
| `explore_dim_max_offset` | int | 4 | ≥ 1; proposal policy | [D] |
| `min_age_cycles` | int | 2 | ≥ 0; young-frame protection | [V] |
| `survive_threshold_base` | float | 0.8 | > 0; **expected to be tuned** | [D] |
| `survive_threshold_pop_coeff` | float | 0.04 | ≥ 0; **expected to be tuned** | [D] |
| `survive_threshold_pop_baseline` | int | 4 | ≥ 0 | [D] |
| `min_frames` | int | 1 | ≥ 1 | [V] |
| `max_frames` | int | 200 | ≥ `min_frames`; hard population cap; **scale-dependent, expected to be raised** | [D] |

---

## 5. Motivation — drives (Doc 05)

| Parameter | Type | Default | Range / notes | Status |
|---|---|---|---|---|
| `drives` | ordered list of drive declarations | `[curiosity]` | each declares `id`, parameters, and `drive_weight`; base build has exactly one | [D] |
| `drive_weight[d]` | float | 1.0 (single drive) | ≥ 0; per drive; fixed at boot | [D] |
| `w_progress` | float | 1.0 | ≥ 0; curiosity learning-progress weight | [O] |
| `w_novelty` | float | 1.0 | ≥ 0; curiosity novelty weight | [O] |
| `pred_err_recent_window` | int | 50 | ≥ 1; steps in the short prediction-error window | [O] |
| `pred_err_baseline_window` | int | 500 | ≥ `pred_err_recent_window`; steps in the long window | [O] |
| `observation_memory_size` | int | 1000 | ≥ 1; size of `recent_observation_memory` for novelty | [O] |

**MUST:** all drive parameters above are read-only at runtime (Doc 05 §6).

---

## 6. Action — policy (Doc 05 §4)

| Parameter | Type | Default | Range / notes | Status |
|---|---|---|---|---|
| `policy` | enum | `curiosity_lookahead_1step` | the configured policy implementation | [O] |
| `action_candidate_sample` | int | `n_actions` | ≥ 1; number of candidate actions evaluated per step (subset if < `n_actions`) | [O] |
| `exploration_epsilon` | float | 0.1 | in [0, 1]; probability of a uniformly random action | [D] |
| `min_frame_maturity_for_lookahead` | int | 5 | ≥ 0; slow-loop cycles before lookahead is trusted; below this the policy acts randomly | [D] |

---

## 7. Lifecycle and consolidation (Docs 01, 04, 06)

| Parameter | Type | Default | Range / notes | Status |
|---|---|---|---|---|
| `boot_mode` | enum | `fresh` | `fresh` or `restore` | [D] |
| `restore_snapshot_id` | id | newest | used only when `boot_mode = restore` | [D] |
| `slow_loop_every_n_steps` | int | 240 | ≥ 1; fast-loop steps between slow-loop runs | [D] |
| `snapshot_every_n_cycles` | int | 1 | ≥ 1; slow-loop cycles between snapshots | [D] |

(Note: `slow_loop_every_n_steps = 240` with the historical validation schedule corresponds to roughly the prior "6 episodes of 40 steps per cycle"; tune to deployment.)

---

## 8. Storage (Doc 06)

| Parameter | Type | Default | Range / notes | Status |
|---|---|---|---|---|
| `snapshot_store_backend` | enum | `filesystem` | the durable snapshot backend | [D] |
| `snapshot_store_path` | path | — (required if filesystem) | durable location for snapshots | [D] |
| `snapshot_format_version` | int (fixed) | 1 | written into every snapshot; restore rejects unknown versions | [D] |
| `event_log_enabled` | bool | false | optional seam; not implemented in base build | [D] |
| `pose_index_enabled` | bool | false | optional seam; not implemented in base build | [O] |

---

## 9. Parameters that govern scale (call-outs)

The following are the parameters an operator changes to run the system at larger scale; collected here so the scale story is in one place.

- `max_frames` (§4) — raise for more capacity; the hard population bound.
- `survive_threshold_*` (§4) — tune so eviction keeps pace with `spawn_per_cycle` at the chosen `max_frames`.
- `policy` and `proposal policy` parameters (§4, §6) — the **[O]** components expected to be replaced for large `obs_dim`/`n_actions`/dimensionality.
- `hidden_size` (§2) — frame capacity; **MUST scale ≳ 2 × the expected latent dimensionality** — a frame cannot resolve structure past its own hidden width.

**Scale-invariant parameter rules [D]** (PRA-01 §8.8, evidence in
`design/validate/SCALE-DIAGNOSIS.md`): `learning_rate`, `init_weight_scale`, and
`w_complexity` are regime-dependent — their defaults were validated at
`obs_dim = 10`, `hidden_size = 12` and silently leave that regime at larger
dimensions (raw `learning_rate` *diverges* at `obs_dim = 60`). Implementations
**MUST** apply them through the effective forms of PRA-01 §8.8
(`·(10/obs_dim)^1.5`, per-tensor `·sqrt(fan_in_ref/fan_in)`, `·(10/obs_dim)`
respectively), and `min_age_cycles` through `·(obs_dim/10)^1.5` (protection must
grow with convergence time). All factors are exactly 1 at the reference scale.

The SIMD requirement (Doc 03 §7) is not a parameter — it is mandatory and is what makes raising `max_frames` and `hidden_size` feasible on one machine.

---

## 10. Definition of done (this document)
1. Every parameter named in Docs 01–06 appears here with type, default, range, source document, and status.
2. Derived quantities (`obs_dim`, `n_actions`) are marked as derived, not set directly.
3. All drive parameters are marked read-only at runtime.
4. The scale-governing parameters are collected in Section 9.
