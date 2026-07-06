# PRA Validation System — Validation & Acceptance Specification

**Document 2 of 2.** This document defines the synthetic world that feeds the system, the telemetry the system records, and the acceptance tests that determine whether an implementation is correct. It depends on "PRA Validation System — System Specification" (Document 1) for all component definitions and data contracts.

This is a functional specification. **MUST** is mandatory; **MUST NOT** is prohibited; **MAY** is permitted. Defaults given here are the shipped values unless configuration overrides them.

A run is correct only if it passes the acceptance tests in Section 4. Passing Document 1's structural checklist (its Section 11, items 1–6) is necessary but not sufficient; this document supplies the behavioral bar.

---

## 1. The synthetic world

The world is the `EventSource` (Document 1, Section 9.4) used for all validation. It is a sensorimotor world: actions lawfully move a hidden latent state, and observations are a fixed function of that state. The agent never sees the latent state, its dimensionality, the emission functions, or the object set. The world's job is to *have* a true latent dimensionality so the system's discovered dimensionality can be compared against ground truth.

### 1.1 Construction

Built once per run from the run's seed (Document 1, Section 7.1). Parameters from Document 1, Section 8.1.

- **Objects.** Create `n_objects` objects. Each object `k` has:
  - a start latent vector `start_k ∈ float[true_dim]`, drawn `Normal(0, 1)` per element;
  - an emission matrix `E_k ∈ float[obs_dim, true_dim]`, drawn `Normal(0, 1)` per element.
- **Actions.** Create `n_actions` fixed latent displacements `Δ_0 … Δ_{n_actions-1}`, each `∈ float[true_dim]`, drawn `Normal(0, 1)` per element and scaled by `action_scale`.

All draws come from the run's single seeded generator, in this order: objects (start then emission, per object in index order), then actions.

### 1.2 Dynamics

State: a current object index and a current latent vector.

- `reset()`:
  - choose a current object index uniformly at random in `[0, n_objects)` (via the seeded generator);
  - set the current latent vector to that object's `start_k`;
  - return `emit()`.
- `step(action)`:
  - set latent ← latent + `Δ_action`;
  - return `emit()`.
- `emit()` (internal):
  - `clean = tanh(E_k · latent / sqrt(true_dim / 3))` where `k` is the current object and `tanh` is applied elementwise;
  - `observation = clean + noise`, where each element of `noise` is drawn `Normal(0, sensor_noise_std²)`;
  - return `observation ∈ float[obs_dim]`.

**Requirements:**
- The emission is **nonlinear** (the `tanh`). This is mandatory: it ensures a purely linear frame cannot fully model the world, so the dimensionality result is not confounded by a linearity ceiling. An implementation **MUST NOT** replace the emission with a linear map.
- The emission pre-activation is **normalized by `sqrt(true_dim / 3)`** (exactly 1 at the reference `true_dim = 3`, so the validated reference world is unchanged). Without it the pre-activation variance grows linearly with `true_dim` and the tanh saturates into a near-binary sign channel (65% of components saturated at `true_dim = 20` vs 18% at the reference), destroying the recoverable latent geometry — a scaled run would test a categorically different world, not the same world at scale. Evidence: `SCALE-DIAGNOSIS.md` §1.
- The world **MUST NOT** expose `true_dim`, latent vectors, emission matrices, displacements, or object indices to the engine, the frames, or the telemetry used by the acceptance tests. The only output the agent may see is the observation vector. (`true_dim` is known to the *test harness* for scoring T4, but is not an input to the system under test.)

### 1.3 Scaled configurations (the research question)

In addition to the default (`true_dim = 3`, `obs_dim = 10`), the harness **MUST** be able to run scaled configurations to answer Document 1, Section 1.3:
- `true_dim ∈ {20, 35, 50}`, with `obs_dim` set to at least `3 × true_dim` (e.g. 60, 105, 150).
- Total observation throughput per run reaching the **millions** (see Section 3.3).
These scaled runs use the same world definition; only the dimensions and run length change.

Scaled runs additionally **MUST** hold the validated training regime constant across
scale: `hidden_size ≳ 2 × true_dim` (a frame cannot resolve dimensionality past its
own hidden width), and the scale-invariant parameter rules of Document 1, Section 8
(effective learning rate, fan-in init, effective parsimony — all exactly the raw
constants at the reference scale). Without these the scaled result measures
optimizer divergence, not the architecture (`SCALE-DIAGNOSIS.md` §§2–5).

### 1.4 The dimensional signal is shallow (how to read T4)

At the default configuration the world has a **real but shallow** dimensional elbow at `true_dim`. A dimension scan (train fixed-`dim` frames and measure honest, observation-space reconstruction and prediction error) shows error dropping steeply up to `true_dim` and then flattening — but *not* sharply: a flexible higher-`dim` frame keeps nibbling the error down via overfit, and a low-`dim` frame that maps only the easy observations looks deceptively good on that subset. Two consequences the harness and the reader **MUST** respect:

- **Score honestly and fairly.** `best_dim` is meaningful only when prediction is scored in observation space and the survival EMAs are coverage-fair (Document 1, Sections 5.2 and 5.4). Pose-space prediction or mapped-subset-only scoring removes the elbow and the test becomes noise.
- **Judge within-one, across horizons** (T4). Exact recovery of `true_dim` on every seed is not expected from this world; the shallow elbow is a property of the *validation world*, not a defect of the agent. Sharpening it (e.g. lowering `sensor_noise_std`, or adding an explicit bottleneck) is an optional future change to this document, not a fix the agent owes.

---

## 2. The ablation worlds and agents (T3)

Test T3 requires two additional, independent runs per seed, each configured
identically to the predictive run except for `scoring_mode`:

1. **Effort-only** (`scoring_mode = effort_only`, fresh world from `seed + 9999`):
   transitions learn to minimize predicted-move magnitude — the weak claim
   ("training on effort alone does not learn the world").
2. **Identity / learned persistence** (`scoring_mode = identity`, fresh world from
   `seed + 18888`): transitions learn to predict that the pose **stays where it
   is** — through the decoder this is the learned "nothing changes" predictor.
   This is the strong claim: in this world persistence is a deceptively good
   predictor (the analytic identity baseline at the reference is 0.165 vs the
   validated system's 0.157), so beating it is what demonstrates *genuine*
   dynamics learning rather than reconstruction quality alone.

Requirements for both ablation runs:
- Each **MUST** use a **fresh world** built from a different but deterministic seed so the runs are independent yet reproducible.
- Each **MUST** receive the **same total experience** as the predictive run it is compared against (same `warmup_episodes`, and `n_cycles × episodes_per_cycle` online episodes total).
- In every ablation the recorded `pred_error` is the **true** predictive error. The ablation measures honestly; it simply does not learn from the measurement.

---

## 3. Telemetry

The system **MUST** record the following. All of it is held in memory during a run and summarized at the end; none of it is frame *state* persistence (Document 1, Section 1.2).

### 3.1 Per-step (within online episodes)
- `map_fraction` = (number of frames that mapped this observation) / (number of frames alive this step).
- `mean_pred_error` = mean of the `pred_error` values across frames that mapped this step and had a non-null `pred_error`. (May be empty in the earliest steps; record only when at least one such value exists.)
- `loss_flag` = true if zero frames mapped this observation. **Loss is counted only after the run is "warmed"** (Document 1, Section 6.6); births during warmup are expected and are not counted as loss for T6.

### 3.2 Per-offline-cycle
- `population_size` = number of frames alive after the cycle.
- `dims_alive` = the multiset of `dim` values across the population.
- `best_frame` = the `(dim, survival_score)` of the frame with the lowest survival score after the cycle.
- `removed` = list of `(dim, survival_score)` for frames evicted this cycle.

### 3.3 Per-run summary
- `mean_map_fraction` = mean of per-step `map_fraction` over the run.
- `pred_error_early` = mean of `mean_pred_error` over the first 200 recorded per-step values (require at least 50 recorded values to report; otherwise mark as not-available).
- `pred_error_late` = mean of `mean_pred_error` over the last 200 recorded per-step values.
- `best_dim` = the `dim` of the frame with the lowest survival score at the end of the run.
- `best_score` = that frame's survival score.
- `final_population` = number of frames alive at the end of the run.
- `loss_fraction` = (count of post-warmup steps with `loss_flag`) / (count of post-warmup steps).
- `observation_steps` = total number of observation steps processed in the run.
- `throughput` = `observation_steps × mean_population` ÷ wall-clock seconds, i.e. observation×frame evaluations per second. (Reported so the scale goal is measurable; see T-SCALE.)

### 3.4 Across-seed aggregation
For each summary field that the acceptance tests use, the harness **MUST** report mean and standard deviation across all seeds, and **MUST** report the per-seed values for `best_dim` (the spread, not just the mean, is what T4 is judged on).

---

## 4. Acceptance tests

Each test below has an exact pass criterion evaluated across all configured seeds (default 8). The harness **MUST** run all seeds, compute the per-run summaries, aggregate, and emit a PASS/FAIL for each test. "Majority of seeds" means strictly more than half.

The reference behavior these criteria encode is the validated behavior of the architecture's reference run (the simulation that informed this specification). An implementation that diverges from these criteria is incorrect, regardless of whether it "seems" to work.

### T1 — Sparsity by pull
**Claim:** frames drop observations; they do not all map everything.
**Measure:** `mean_map_fraction` aggregated across seeds.
**Pass:** mean `mean_map_fraction` < 0.99.
*(Reference behavior sits well below 1.0 — frames are genuinely selective. A value at or near 1.0 means the fit gate is not gating and the implementation is wrong.)*

### T2 — Prediction error falls
**Claim:** the predictive anchor actually teaches; prediction error decreases as the system learns.
**Measure:** per seed, compare `pred_error_late` to `pred_error_early`.
**Pass:** `pred_error_late < pred_error_early` in a majority of seeds. The harness also reports the aggregate early and late means.

### T3 — Neither effort-only nor learned persistence learns the world (ablation)
**Claim:** the improvement comes from genuinely predicting the world's dynamics — not from training on effort alone (weak clause), and not from reconstruction quality plus assuming nothing changes (strong clause).
**Measure:** define `improvement = pred_error_early − pred_error_late`. Compute it for the predictive run and for each ablation run (Section 2), per seed.
**Pass:** `improvement(predictive) > improvement(effort_only)` **AND** `improvement(predictive) > improvement(identity)`, each in a majority of seeds. The harness reports both margins; the identity margin is the binding (reported) one.
*(Reference measurement, 2026-07-06: predictive beat effort-only 8/8 with margin 0.465 ± 0.070 and beat learned-persistence 6/8 with margins +0.03 to +0.18 — the persistence clause is the tight one, as intended.)*

### T4 — Structure grows to the right dimensionality (the load-bearing test)
**Claim:** starting from zero frames, spawn-and-select grows the population so that its best frame's dimensionality matches the true latent dimensionality.
**Measure:** per seed, `best_dim`; compare to `true_dim`. Report the full per-seed list of `best_dim` (the spread), the count of exact matches (`best_dim == true_dim`), and the count within one (`|best_dim − true_dim| ≤ 1`) — **at each of several horizon checkpoints**, not only at the end of the run (see the horizon rule below).
**Pass:** `|best_dim − true_dim| ≤ 1` holds in a majority of seeds **at every horizon checkpoint**.
**Mandatory reading rule (spread):** the test is judged on the **spread across seeds**, not the mean. A mean near `true_dim` produced by a wide, uncentered spread (e.g. half the seeds far below and one far above) is a **FAIL of the underlying claim** even if the arithmetic mean lands near `true_dim`. The harness **MUST** surface the per-seed list so this is visible and **MUST NOT** report only the mean.
**Mandatory reading rule (horizon):** `best_dim` is a *trajectory*, not a fixed point. The harness **MUST** record `best_dim` at multiple offline-cycle checkpoints (default: at 18, 30, and 50 cycles) and require the within-one-majority criterion to hold at **every** checkpoint. A run that satisfies the criterion at one horizon but drifts away from it at a later horizon is a **FAIL**: the early agreement was a transient, not a discovered structure. (This rule exists because the exploratory prototype passed at 18 cycles and failed at 30 — see the project handoff. Reading `best_dim` at a single end-of-run snapshot is prohibited.)
**Note (exact vs within-one):** `best_dim == true_dim` exactly is **not** required, and is not expected on every seed. The synthetic world's dimensional elbow is shallow (Section 1.4): honest error keeps decreasing slowly past `true_dim` via overfit, so individual seeds may sit one off. Within-one across horizons is the bar.

### T5 — Decay is default; population stays bounded
**Claim:** frames that do not earn their keep are removed, and the population does not grow without bound.
**Measure:** `final_population` aggregated across seeds; also inspect per-cycle `population_size` for monotonic runaway.
**Pass:** mean `final_population` < `max_frames`, **and** no seed's population is still strictly increasing over the final third of its offline cycles (i.e. eviction is keeping pace, not merely capped). The harness reports `final_population` mean/std and a per-seed "still-growing" flag.
*(Note: this is the test the eviction policy in Document 1, Section 6.4, exists to satisfy. The decay parameters in Document 1, Section 8.6, are the parameters most likely to require tuning to pass this test. Tuning those parameters to pass T5 is expected and in scope; changing the eviction *mechanism* is not.)*

### T6 — No systematic observation loss
**Claim:** once warmed up, the system maps observations rather than discarding them.
**Measure:** `loss_fraction` (post-warmup) aggregated across seeds.
**Pass:** mean `loss_fraction` < 0.15.
*(Reference behavior is far below this — well under 1% — because the zero-start birth rule creates a frame whenever an observation finds no home. A high loss fraction means the birth rule or the gate is misimplemented.)*

### T-SCALE — Structure growth holds at high dimensionality and scale (the research question)
**Claim (open; this is what the whole system exists to investigate):** spawn-and-select still finds the right dimensionality when `true_dim` is large and the run processes millions of observations.
**Measure:** run T4 at `true_dim ∈ {20, 35, 50}` (Section 1.3) with run schedules long enough that `observation_steps` reaches the millions, using the batched evaluation required by Document 1, Section 7.2, and (for the large `true_dim` runs) the proposal policy supplied for high dimensionality (Document 1, Section 6.5). Report `best_dim` per seed at each `true_dim`, and report `throughput` and wall-clock.
**Pass criterion is investigatory, not pass/fail for the build:** the build is *complete* when T-SCALE can be *run and measured* (the system reaches millions of observations on a single machine via batched evaluation, and emits the `best_dim` spread and throughput). Whether `best_dim` tracks `true_dim` at scale is the **research finding** the system is built to determine; a "no" is a valid and important result, not an implementation failure. The harness **MUST** make this run executable and its results legible; it **MUST NOT** treat a poor dimensionality result at high `true_dim` as a build defect.

---

## 5. Harness behavior

The evaluation harness orchestrates runs and reports results. Requirements:

- **Multi-seed by default.** The harness **MUST** run every seed in `seeds` (Document 1, Section 8.7) and aggregate per Section 3.4. A single-seed result **MUST NOT** be reported as if it validates a behavioral claim; single-seed runs are permitted only for debugging and **MUST** be labeled as such.
- **Determinism check.** The harness **MUST** provide a mode that runs one seed twice and asserts byte-identical per-run summaries, verifying Document 1, Section 7.1.
- **Per-test verdicts.** The harness **MUST** emit, for each of T1–T6, the measured aggregate, the pass criterion, and a PASS/FAIL. For T4 it **MUST** additionally emit the per-seed `best_dim` list and the exact/within-one counts **at each horizon checkpoint** (default 18/30/50 offline cycles), and the T4 verdict **MUST** require the within-one majority at every checkpoint (the horizon rule in Section 4, T4). For T-SCALE it **MUST** emit per-`true_dim` `best_dim` spreads, throughput, and wall-clock, and label it investigatory.
- **Honest summaries only.** The harness **MUST NOT** smooth, cherry-pick, or report only favorable seeds. If a test fails, it reports FAIL with the numbers that show why.
- **Result output.** The harness writes a human-readable summary (and **MAY** write a machine-readable summary, e.g. JSON) of the aggregated results. This output is a summary artifact, not frame-state persistence, and is the only thing the system writes to disk.

---

## 6. Definition of done (validation)

Validation is complete when:
1. The world (Section 1) is implemented exactly, including the nonlinear emission and the hidden-state requirement, and supports the scaled configurations (Section 1.3).
2. The ablation run (Section 2) is implemented with the independent-seed and equal-experience requirements.
3. All telemetry in Section 3 is recorded and summarized, including the across-seed spread for `best_dim`.
4. The harness (Section 5) runs all seeds, performs the determinism check, and emits per-test verdicts with the required detail.
5. Tests **T1, T2, T3, T6 PASS**, and **T4 PASS** at the default `true_dim = 3`.
6. Test **T5 PASS** at the default configuration (tuning the Document 1, Section 8.6, parameters to achieve this is in scope).
7. **T-SCALE is runnable and measured** at `true_dim ∈ {20, 35, 50}` reaching millions of observation steps on a single machine via batched evaluation, with `best_dim` spreads and throughput reported. The *value* of the dimensionality result at scale is a research finding, not a pass/fail gate for the build.

When items 1–7 hold, the system has done its job: the architecture's behavioral claims are confirmed at the default scale, and the open question of whether structure growth survives high dimensionality is measurable and measured — with every result attributable to a single component, because nothing in this system is distributed, persisted, or brokered.
