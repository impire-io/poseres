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

### 1.5 The complexity ladder (feature 005, ROADMAP A3)

Beyond the reference family, three opt-in worlds each add **one known
difficulty axis** while keeping this section's instrument panel
(determinism, seeded reproducibility, ground truth known to the harness
via `Config`, never exposed through the world surface): `nonuniform`
(a half-space region of latent space with irreducibly random transitions —
the drive-research testbed), `compositional` (factored dynamics, each
action moving one factor group, under the joint emission), and
`distractor` (appended channels driven by an autonomous drift latent, or
fresh unit noise). Selection is `Config.world`; each world's degenerate
dial is **byte-identical** to the reference family (integration-tested),
so the ladder's ground floor is the validated world above. Their
acceptance criteria and recorded results — judged per rung, investigatory
at the build level, failures recorded as findings — live in
`LADDER-CRITERIA.md`; the instrument is `pra-validate ladder`.

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
*(Scaled measurement, 2026-07-12, `pra-validate scale --t3`, 2000-cycle protocol: effort clause 8/8 at every scale; identity clause **as written FAILs at `true_dim` 20 and 35** (2/8, margins −0.054 ± 0.075 / −0.030 ± 0.039) and passes at 50 by the thinnest majority (5/8). Diagnosed: measurement composition, not capability — the scaled ecology's standing juvenile conveyor sits inside the per-step elect mean; the no-consolidation ablation arms have no churn. T3 as written is not scale-portable.)*
*(**Amended scaled form** — pre-registered and measured 2026-07-12, the T7 precedent: at scale the strong clause is **churn-matched** — a fourth arm, predictive training under the identity arm's exact semantics (same `seed + 18888` world, no consolidation), must beat the identity arm paired per seed. Result: **PASS at all three scales, 24/24 paired seeds positive**, margins +0.021 ± 0.011 / +0.028 ± 0.008 / +0.026 ± 0.015 — flat across scales, ~⅓ of the reference margin (a research quantity, presumably budget-bound). As-written counts stay in the record (2/8, 2/8, 5/8). The reference T3 above is unchanged. Full trail: `T3SCALE-DIAGNOSIS.md`.)*

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

### T7 — Directed curiosity is not worse than random exploration (agency; feature 002)
**Claim:** the motivation/action layer (Doc 05: curiosity drive + one-step lookahead policy) gathers experience at least as useful for learning the world as uniformly random actions.
**Measure:** per seed, two full predictive runs with the **same seed** (identical world, equal experience): one under the curiosity policy, one under the pinned random baseline. Per-seed margin = `improvement(curious) − improvement(random)`, where each run's `improvement = pred_error_early − pred_error_late`.
**Pass:** one-sided noninferiority on the paired mean margin — **FAIL only when `mean(margin) < −1.9·SE(margin)`**. The per-seed margins and sign counts are always reported. (A per-seed sign-majority bar was measured first and discarded openly: with continuous margins it degenerates into "strictly better per seed" and fails exact statistical equivalence by coin-flip.)
**Reference measurement (2026-07-07, 8 seeds):** mean margin −0.0061 ± 0.036 vs bound −0.0239 → **PASS**; strictly better in 3/8 seeds; mean value signal 0.159, directed-action fraction 78%. Reading: in the reference world random coverage is already near-complete, so directed exploration neither helps nor hurts — the claim this test protects is "does not hurt." Whether directedness *helps* in larger worlds is an open research question for scaled configurations.
**Scope:** T7 runs via `pra-validate agency`, not in the default suite — the T1–T6 regression gate is byte-identical to the validated build under the pinned random policy.

**Scaled measurement (2026-07-08, investigatory — `true_dim=20`, `obs_dim=60`,
`hidden=40`, 200 cycles, 8 seeds): T7 criterion FAILS at scale.** Mean margin
−0.062 ± 0.068 vs bound −0.046; strictly better in 1/8 seeds; directed-action
fraction 87%. Directed curiosity is *systematically worse* than random
exploration in the larger world. Mechanism reading: with one-step lookahead the
learning-progress term is history-shaped and near-constant across candidate
actions, so the policy is effectively a **novelty maximizer**; at scale,
chasing the least-familiar predicted observation drives the agent toward
poorly-modeled regions faster than it can learn them, degrading the experience
distribution relative to a random walk. This is precisely the failure mode the
Doc 05 **[O]** tags anticipated (§3.1/§4.2 "expected to be tuned/replaced") and
the §5 counter-drive mechanism exists for. The reference-scale PASS above
stands; the claim "directedness does not hurt" is drive- and scale-dependent.

**Resolution (2026-07-08, `AGENCY-DIAGNOSIS.md`, five controlled experiments):**
the harm is the *content* of the preference, not the directedness — a
content-free state-coupled control policy is neutral (margin +0.014), while the
inverted, familiarity-seeking preference **beats random** (+0.067, better in
6/8 seeds). (Sub-hypotheses refuted along the way with data: tanh saturation,
fit-gate starvation, action-marginal skew, walk extent.) The shipped
**competence drive** (Doc 05 §5: mastery + familiarity), selected by pure
configuration (`drive_weights = {competence: 1.0}`), PASSes T7 at **both**
scales and beats random in 6/8 seeds at each: scaled margin **+0.064** (bound
−0.056), reference margin **+0.027** (bound −0.034) — directed exploration is
now a measured net positive. Honest caveat: this world is uniformly learnable;
in worlds with unlearnable regions pure familiarity-seeking risks the camping
degeneracy, and the curiosity/competence blend remains the open [O] question.

### T-SCALE — Structure growth holds at high dimensionality and scale (the research question)
**Claim (open; this is what the whole system exists to investigate):** spawn-and-select still finds the right dimensionality when `true_dim` is large and the run processes millions of observations.
**Measure:** run T4 at `true_dim ∈ {20, 35, 50}` (Section 1.3) with run schedules long enough that `observation_steps` reaches the millions, using the batched evaluation required by Document 1, Section 7.2, and (for the large `true_dim` runs) the proposal policy supplied for high dimensionality (Document 1, Section 6.5). Report `best_dim` per seed at each `true_dim`, and report `throughput` and wall-clock.
**Pass criterion is investigatory, not pass/fail for the build:** the build is *complete* when T-SCALE can be *run and measured* (the system reaches millions of observations on a single machine via batched evaluation, and emits the `best_dim` spread and throughput). Whether `best_dim` tracks `true_dim` at scale is the **research finding** the system is built to determine; a "no" is a valid and important result, not an implementation failure. The harness **MUST** make this run executable and its results legible; it **MUST NOT** treat a poor dimensionality result at high `true_dim` as a build defect.

**Scaled reference result (2026-07-07; the research finding as of the six
scale-invariance rules of Document 1 §8.8, 2000-cycle schedules, 8 seeds,
~3.85M observation steps per `true_dim`, parallel seed execution — full trail in
`SCALE-DIAGNOSIS.md`):**

| `true_dim` | `best_dim` per seed (8 seeds) | median | throughput (obs×frame evals/s) | wall |
|---|---|---|---|---|
| 20 | [8, 18, 6, 9, 8, 6, 13, 4] | 8 | 229,348 | 10 min |
| 35 | [8, 14, 10, 11, 13, 8, 16, 10] | 10.5 | 128,733 | 34 min |
| 50 | [8, 9, 10, 11, 9, 9, 12, 10] | 9.5 | 51,746 | 141 min |

(The first three entries of each spread exactly reproduce the earlier 3-seed
measurement — per-seed determinism is visible in the data. Note the spread
*shape*: wide at `true_dim = 20` (4–18: the climb is variance-dominated when
maturation windows are plentiful, 2000/29 ≈ 69) and tight at `true_dim = 50`
(8–12: uniformly stalled when windows are scarce, 2000/116 ≈ 17).)

Reading: **no collapse at any scale** (every seed finds genuine multi-dimensional
structure; before the §8.8 rules every scaled run collapsed to `best_dim ≈ 1`),
and one `true_dim = 20` seed reaches within-one of the truth — the mechanism has
no dimensional ceiling. But the *climbed fraction* falls with scale: in a fixed
2000-cycle budget the ±1-ish selection ladder covers a similar absolute number of
rungs regardless of the target (fewer, larger maturation windows at higher
`obs_dim`). Structure-finding survives scale; its convergence **rate** does not.
This quantifies the open problem the high-dimensionality proposal seam
(Document 1 §6.5, **[O]**) exists to solve: proposals that jump toward promising
dimensionalities rather than inching, so the number of rungs — not the patience
per rung — is what shrinks.

**Reinterpretation (2026-07-08, PROPOSAL-DIAGNOSIS):** the proposal-seam
investigation answered the rung-count question (an upward-only tight-band
policy climbs ~1 rung per maturation window, doubling fixed-budget medians)
— and, un-throttled, exposed what the spread above actually measures. A
population census (via the Document 6 persistence seam) shows every scaled
run carries a standing conveyor of `spawn_per_cycle × patience` protected
juveniles, plus a mature niche that at scale only dims ≲ 12 can enter (the
absolute survival bar of Document 1 §6.4 sits below the achievable
at-maturity score of every higher dim — the open seventh scale rule,
Document 1 §8.8). The table above therefore reads the **maturation filter**
(which dims can train under the bar within one protection window), not the
score surface — which the extended dimension scan proves healthy (score
minimum at dim 12–16 at `true_dim = 20`; honest prediction error minimal at
24 and worsening past it). Under the climbing policy the niche is empty and
`best_dim` ratchets with the proposals themselves (71/74/62/68 at
`true_dim = 20`, 2000 cycles). T-SCALE's investigatory status is exactly
right: these numbers are honest measurements of the selection *ecology*, and
they say the ecology — not the proposal policy — is the binding constraint
at scale.

**Scaled reference result (2026-07-11, supersedes the tables above — the
fair-judge ecology: `score_window_steps = 5`, the conveyor-corrected
threshold baseline, climbing proposals — now the `pra-validate scale`
defaults; 2000-cycle schedules, 8 seeds; full trail in
`THRESHOLD-DIAGNOSIS.md`):**

| `true_dim` | `best_dim` per seed | median | anchored (census) | population |
|---|---|---|---|---|
| 20 | [7, 6, 4, 8, 7, 6, 6, 5] | 6.0 | 8/8, tenures to 2000 | 39–46 |
| 35 | [6, 9, 9, 8, 12, 7, 8, 6] | 8.0 | 8/8, tenures 1453–1970 | 87–92 |
| 50 | [6, 9, 10, 9, 9, 8, 7, 8] | 8.5 | 8/8, tenures 1774–1992 | 136–142 |

Reading, with the honest criterion stated plainly: these medians are
*numerically lower* than the superseded table's (8 / 10.5 / 9.5) and *further*
from `true_dim` — and they are the first scaled readings that **mean**
anything: every one of 24 runs is an anchored, self-limiting ecology whose
`best_dim` is invariant to the cycle budget and to the proposal distribution
(the superseded numbers were unstable conveyor readings that tracked
whichever policy stocked the juvenile pipeline). The level (6–8.5, vs the
frozen-eval score minimum of 12–16) is bounded by the named inter-age
asymmetry — the incumbent-lifetime advantage in niche entry — which is the
recorded successor problem, ahead of the deeper scorer question (the honest
elbow itself sits at 12–16 regardless of the world's 20/35/50 true
dimensionality at these experience budgets; Doc 03 §6 parsimony vs marginal
information).

**Scaled reference result (2026-07-11, final — adds the third ecology leg,
lifetime stability `weight_norm_cap = 1.2` (PRA-01 §8.8 eighth rule; the
table above was measured pre-cap and its landing was rot-selection —
LONGEVITY-DIAGNOSIS); same protocol otherwise:**

| `true_dim` | `best_dim` per seed | median | anchored (census) | population |
|---|---|---|---|---|
| 20 | [11, 12, 7, 10, 10, 10, 9, 10] | **10.0** | 8/8, tenures 1736–1977 | 40–46 |
| 35 | [7, 11, 10, 13, 13, 6, 8, 7] | 9.0 | 8/8, tenures 1832–1970 | 87–91 |
| 50 | [10, 9, 9, 11, 7, 9, 7, 9] | 9.0 | 8/8, tenures 1769–1920 | 137–143 |

Reading: the cap's lift is ordered exactly by each scale's rot exposure
(+4 / +1 / +0.5 median vs pre-cap — the effective learning rate delays rot
onset past the run length at larger `obs_dim`), and the T-SCALE question
itself is now **closed by measurement** (SCORER-DIAGNOSIS epilogue): the
scaled world's error surfaces carry no signature of `true_dim` (rot-free
honest error falls monotonically to the capacity ceiling), so `best_dim`
cannot and should not track it. The parsimony weight is a **price**; the
honest claim — now measured at all three scales — is that selection lands at
the price-optimal dimensionality (marginal error gain ≈ effective
`w_complexity`), stably (24/24 anchored), invariant to budget and scale.
T-SCALE remains investigatory; this is the finding it existed to produce.

---

## 5. Harness behavior

The evaluation harness orchestrates runs and reports results. Requirements:

- **Multi-seed by default.** The harness **MUST** run every seed in `seeds` (Document 1, Section 8.7) and aggregate per Section 3.4. A single-seed result **MUST NOT** be reported as if it validates a behavioral claim; single-seed runs are permitted only for debugging and **MUST** be labeled as such.
- **Determinism check.** The harness **MUST** provide a mode that runs one seed twice and asserts byte-identical per-run summaries, verifying Document 1, Section 7.1.
- **Parallel seed execution.** The harness **MAY** run independent seeds (and their ablation runs) in parallel worker processes to use the machine, but parallelism **MUST NOT** change any result: each run keeps its own seeded generator and single-threaded float pipeline, and per-seed summaries are byte-identical to a sequential execution and reassembled in configured seed order (enforced by `tests/integration/test_parallel_equivalence.py`).
- **Per-test verdicts.** The harness **MUST** emit, for each of T1–T6, the measured aggregate, the pass criterion, and a PASS/FAIL. For T4 it **MUST** additionally emit the per-seed `best_dim` list and the exact/within-one counts **at each horizon checkpoint** (default 18/30/50 offline cycles), and the T4 verdict **MUST** require the within-one majority at every checkpoint (the horizon rule in Section 4, T4). For T-SCALE it **MUST** emit per-`true_dim` `best_dim` spreads, throughput, and wall-clock, and label it investigatory. The scale command's opt-in `--t3` mode **MUST** run the Section 2 triad per `true_dim` unchanged plus the churn-matched fourth arm (the amended scaled strong clause — predictive training under the identity arm's semantics on the same world), and emit one T3 verdict per scale by the amended criterion with the per-seed quartet improvements, the paired margins, and the as-written identity counts kept in the record, in the same investigatory context (the verdict is data, never a build failure).
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
