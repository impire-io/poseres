# Phase 1 Data Model: PRA Validation Harness

Entities derived from the feature spec (Key Entities) and the normative data contracts
in PRA-01 §3 and the telemetry in PRA-02 §3. Types are numpy float64 arrays unless
stated. "Validation" rows capture the rules a constructor/recorder must enforce.

---

## 1. Configuration entities

### Config

The full parameter set (PRA-01 §8), a frozen dataclass. Every field has the spec
default; the harness overrides per run/mode.

| Group | Field | Type | Default | Validation |
|---|---|---|---|---|
| World | `true_dim` | int | 3 | ≥ 1 (hidden from the system; known only to the harness for T4) |
| World | `obs_dim` | int | 10 | ≥ 1; recommend ≥ 3·`true_dim` |
| World | `n_objects` | int | 4 | ≥ 1 |
| World | `n_actions` | int | 4 | ≥ 1 |
| World | `sensor_noise_std` | float | 0.04 | ≥ 0 |
| World | `action_scale` | float | 0.4 | > 0 |
| Frame | `hidden_size` | int | 12 | ≥ 1 |
| Frame | `init_weight_scale` | float | 0.3 | > 0 |
| Frame | `learning_rate` | float | 0.03 | > 0 |
| Frame | `gradient_clip` | float | 1.0 | > 0 (per-element; mandatory) |
| Frame | `ema_decay` | float | 0.9 | in [0,1) |
| Gate/birth | `fit_gate` | float | 1.0 | > 0 |
| Gate/birth | `initial_dim_min` | int | 2 | ≥ 1 |
| Gate/birth | `initial_dim_max` | int | 6 | ≥ `initial_dim_min` |
| Scorer | `scoring_mode` | enum | `predictive` | `predictive` \| `effort_only` |
| Scorer | `w_explain` | float | 0.5 | ≥ 0 |
| Scorer | `w_predict` | float | 0.5 | ≥ 0 |
| Scorer | `w_effort` | float | 0.0 | ≥ 0 |
| Scorer | `w_complexity` | float | 0.04 | ≥ 0 (parsimony; tunable) |
| Proposal | `exploit_prob` | float | 0.75 | in [0,1] |
| Proposal | `explore_dim_max_offset` | int | 4 | ≥ 1 |
| Decay | `survive_threshold_base` | float | 0.8 | > 0 |
| Decay | `survive_threshold_pop_coeff` | float | 0.04 | ≥ 0 (threshold **divides** by `1+coeff·…`) |
| Decay | `survive_threshold_pop_baseline` | int | 4 | ≥ 0 |
| Decay | `spawn_per_cycle` | int | 1 | ≥ 0 |
| Decay | `min_age_cycles` | int | 2 | ≥ 0 |
| Decay | `min_frames` | int | 1 | ≥ 1 |
| Decay | `max_frames` | int | 200 | ≥ `min_frames` |
| Schedule | `warmup_episodes` | int | 25 | ≥ 0 |
| Schedule | `n_cycles` | int | 18 | ≥ 0; the harness extends the effective run to `max(n_cycles, max(horizon_checkpoints))` so every T4 checkpoint is reached (see note below) |
| Schedule | `episodes_per_cycle` | int | 6 | ≥ 1 |
| Schedule | `steps_per_episode` | int | 40 | ≥ 1 |
| Schedule | `seeds` | list[int] | [1..8] | ≥ 1 seed |
| Harness | `horizon_checkpoints` | tuple[int] | (18, 30, 50) | each ≥ 1, strictly ascending; `max(...)` ≤ effective `n_cycles` (auto-extended, see note); T4 `best_dim`/population sampled at each |

> **Run length vs. checkpoints (resolves the `n_cycles=18` vs 18/30/50 default mismatch).**
> PRA-01 §8's `n_cycles` default is 18, but T4 (PRA-02 §4, FR-004) reads `best_dim` at
> every horizon checkpoint — the last of which is 50. The harness therefore runs each
> suite seed for `effective_n_cycles = max(n_cycles, max(horizon_checkpoints))` offline
> cycles (50 at the default config), so cycles 18, 30, and 50 are all reached and
> snapshotted, matching the v4 reference (which runs to 50). Construction forbids a
> checkpoint that exceeds the effective run length, so a checkpoint is never silently
> missed.

---

## 2. Core data contracts (PRA-01 §3)

### SensorimotorEvent
`previous_observation: float[obs_dim] | None`, `action: int | None`,
`observation: float[obs_dim]`.
Rule: `previous_observation`/`action` are null **only** on the first event of an
episode, and are the true prior step regardless of any frame's map/drop decision
(PRA-01 §3.1).

### FrameResult
`frame_id: int`, `mapped: bool`, `local_pose: float[dim] | None`,
`recon_error: float | None`, `pred_error: float | None`, `effort: float | None`.
Rule: all of `local_pose`/`recon_error` are null iff `mapped == false`;
`pred_error`/`effort` additionally null when there is no previous observation
(PRA-01 §3.2).

### GlobalPose
`map<frame_id, float[dim]>` — one entry per frame that mapped the observation; assembled
by the Engine for telemetry, never persisted (PRA-01 §3.4).

### FrameState (identity record; weights live in the FrameGroup, §3 below)
`frame_id: int`, `dim: int`, `is_candidate: bool`, `age_cycles: int`,
`recon_err_ema: float`, `pred_err_ema: float`, `effort_ema: float`.
Init rules (PRA-01 §5.3): weights ~ `Normal(0, init_weight_scale²)`, biases 0; EMAs =
1.0 for a zero-start birth, **0.9** for a candidate spawned in an offline cycle;
`age_cycles = 0`, `is_candidate = true`.

---

## 3. Batched execution entity (PRA-01 §7.2)

### FrameGroup (one per distinct `dim`)
Holds `F` frames of identical dimension `D` with weights stacked on a leading frame axis:

| Tensor | Shape | Meaning |
|---|---|---|
| `frame_ids` | int[F] | identity, ascending |
| `is_candidate` | bool[F] | candidate vs ordinary |
| `age_cycles` | int[F] | offline cycles survived |
| `recon_err_ema`,`pred_err_ema`,`effort_ema` | float[F] | survival EMAs |
| encoder `W1,b1,W2,b2` | [F,H,O],[F,H],[F,D,H],[F,D] | obs→pose |
| decoder `Dc1,dc1,Dc2,dc2` | [F,H,D],[F,H],[F,O,H],[F,O] | pose→recon |
| transition `T1,tb1,T2,tb2` | [F,A,H,D],[F,A,H],[F,A,D,H],[F,A,D] | per-action pose→pred_pose |

Operations are batched over `F` (encode/decode/transition/fit/gradient-update). Births
append a row; evictions delete one. Derived quantities (PRA-01 §5.2):
`fit_quality = ‖recon−obs‖/(‖obs‖+1e-6)`;
`prediction_error = ‖decode(pred_pose)−next_obs‖/(‖next_obs‖+1e-6)` (**observation
space**); `effort = ‖pred_pose−pose‖`.

**Validation/invariants:** no per-frame branching (one kernel for the whole group);
results reassembled per `frame_id` in ascending order for deterministic Bus output.

---

## 4. Telemetry entities (PRA-02 §3)

### PerStepRecord (within online episodes)
`map_fraction = mapped / alive`; `mean_pred_error` (mean of mapped, non-null pred_error;
recorded only when ≥1 exists); `loss_flag` (true if zero frames mapped, **counted only
post-warmup**).

### PerCycleRecord (per offline cycle)
`population_size`, `dims_alive` (multiset of `dim`), `best_frame = (dim, survival_score)`
of lowest score, `removed = [(dim, survival_score)]` evicted this cycle.

### PerSeedRunSummary (the spec's "Per-seed run summary")
`seed`, `mean_map_fraction`, `pred_error_early` (mean of first 200 recorded; **≥50
required else not-available**), `pred_error_late` (mean of last 200), `best_dim` &
`best_score` at end, `final_population`, `loss_fraction` (post-warmup),
`observation_steps`, `throughput`, plus the **per-checkpoint** `{checkpoint:
{best_dim, population_size}}` snapshot (T4/T5), the **still_growing** flag (T5), and the
run's own `improvement = pred_error_early − pred_error_late`.

**T3 ablation — two runs per seed, joined by the runner.** A `PerSeedRunSummary` describes
**one** run. T3 compares two runs of the same seed: the predictive run
(`scoring_mode=predictive`) and the effort-only ablation run (`scoring_mode=effort_only`,
fresh world from `seed+9999`, equal experience — R7/T027). Each emits its own summary with
its own `improvement`; **no single summary holds both numbers**. The runner keeps the
predictive/ablation summaries as a pair keyed by seed, and the T3 evaluator PASSes when
`improvement(predictive) > improvement(effort_only)` in a majority of seeds.

**Validation:** must be deterministically serializable to a byte-identical form
(FR-010); a seed that errored carries an `error` marker and is excluded from
"complete-result" presentation (Edge Cases).

### AcrossSeedAggregate
For every field a test uses: `mean`, `std`. For `best_dim`: the **full per-seed list**
(the spread) **at each checkpoint** — never reduced to the mean (FR-003, §3.4).

---

## 5. Verdict entities (the harness output, FR-002/FR-007)

### AcceptanceTest
`id` (T1…T6, T-SCALE), `claim`, `measure`, `criterion` (exact text),
`verdict` ∈ {PASS, FAIL, INVESTIGATORY, NOT_AVAILABLE}, `measured` (the aggregate the
verdict was computed from). T-SCALE is always INVESTIGATORY (never PASS/FAIL for the
build).

### HorizonCheckpointReading (T4 only)
Per checkpoint `c`: `best_dim_list` (per-seed spread), `within_one_count`,
`exact_count`, `seeds`. T4 verdict = PASS iff `within_one_count > seeds/2` at **every**
checkpoint.

### VerdictReport
Binds each AcceptanceTest to its measured number + criterion + verdict; carries run
metadata (config, seeds, mode, wall-clock) and the determinism-check result. Rendered as
human-readable text (always) and JSON (optional). **Validation:** never omits a failing
test; never prints a mean where a spread is required (FR-003, FR-008).

---

## 6. Relationships

```
Config ──drives──> Engine.run(seed) ──produces──> PerSeedRunSummary
   │                   │
   │                   ├─ EventSource(world)        [seam]
   │                   ├─ Bus ── publishes ──> FrameGroup(s)   [batched §7.2]
   │                   ├─ Scorer(combine)           [seam]
   │                   ├─ ProposalPolicy / DecayPolicy  [seams]
   │                   └─ Telemetry(recorder) ── PerStep/PerCycle ──> PerSeedRunSummary
   │
Harness.runner ── runs all seeds ──> [PerSeedRunSummary] ──aggregate──> AcrossSeedAggregate
   │                                                                          │
   ├─ determinism mode: run one seed twice ──> byte-compare summaries        │
   └─ acceptance.evaluate(aggregate) ──> [AcceptanceTest] ──> VerdictReport <─┘
                                                                  │
                                                          report.render ──> text + JSON (only disk artifact)
```

### State transition (a frame's life)
`born (candidate, age 0)` → online episodes update EMAs (coverage-fair) and, if mapped,
learn → offline cycle ages it → at `age_cycles ≥ min_age_cycles` becomes ordinary
(eligible for eviction) → evicted when `survival_score > population-scaled threshold`
(soft) or over `max_frames` (hard), never below `min_frames`, never while young.
