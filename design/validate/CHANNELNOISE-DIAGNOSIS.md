# Channel-noise diagnosis — where does static break structure-finding, and why?

Date: 2026-07-14. Question under test: the ladder's first new open problem
(LADDER-CRITERIA, L3 result): on the distractor world in **noise mode** —
10 of 20 observation channels carrying fresh unit-scale static —
structure-finding collapses (`best_dim` finals [1, 4, 1, 1, 1, 3, 1, 6];
dim 1 in five of eight seeds) while the same world in *structured* mode
passes cleanly. The recorded note already names the dial asymmetry: the
static is unit-scale where `sensor_noise_std` is 0.04 (25× smaller), so
the natural first experiment is a noise-amplitude dose–response; the
suspected mechanism sits in the honest error norms every frame is judged
on (`frame.py`): both `fit` and `honest_pred_err` are relative L2 norms
over **all** channels — a per-channel irreducible floor on the static
half enters both the numerator and the `‖obs‖` denominator.

## Hypotheses (pre-registered, before any run)

- **H-dose (E1).** Structure-finding survives sensor-noise-scale static
  (σ_d = 0.04 — the static half is then just more sensor noise) and
  degrades monotonically as σ_d rises toward 1.0; a breaking amplitude
  exists inside {0.04, 0.1, 0.2, 0.5, 1.0}.
- **H-compress (E2, the suspected chain).** On a static channel the best
  achievable prediction is its mean (0), leaving an irreducible
  `m·σ_d²` in the squared error numerator; the same term inflates the
  `‖obs‖²` denominator. Both effects **compress per-dim error
  differences**: the marginal error gain of buying a dimension shrinks
  while the parsimony price is fixed (`effective_w_complexity` =
  0.04 · 10/20 = **0.02 per dim** at obs_dim = 20), so once the marginal
  gain falls below the price, the smallest dim wins the score and
  selection collapses to 1. Core structure-learning itself stays intact.
- **H-corrupt (the rival).** Unit static does not merely mask the score —
  it corrupts learning: static enters the shared encoder (`W1` spans all
  20 channels) and the decoder's static-channel rows chase pure-noise
  targets, so the learned core structure itself degrades at high σ_d.
  Prediction: the core-channel-restricted error at σ_d = 1.0 is visibly
  degraded vs σ_d = 0.04 (pre-registered threshold: dim-3 core error
  > 1.5× its σ_d = 0.04 value) and/or loses its dim gradient.
- **H-gate (side channel, read for free in E1).** The achievable fit
  floor at σ_d = 1 (≈ √(m·σ_d²)/‖obs‖ ≈ 0.8) sits near the fit gate
  (1.0), so frames elect on fewer steps — election starvation as an
  amplifier. Reading: `mean_map_fraction` vs σ_d.

H-compress and H-corrupt are not mutually exclusive; E2's decomposition
measures each contribution separately.

## The dial (instrument change, reference-preserving)

E1 needs a noise-amplitude dial that does not exist: the noise branch of
`DistractorWorld._emit` draws fresh **unit** normals. Added:
`Config.distractor_noise_std: float = 1.0`, multiplied onto the noise
branch's draw. The default **is** the current behavior (multiplying by
1.0 is bit-exact in IEEE 754 and the RNG stream is unchanged), so every
recorded L3 result remains byte-reproducible — guarded by tests
(same-stream scaling + default-equivalence). Structured mode and all
other worlds never read the dial.

## E1 — dose–response (protocol pre-registered before running)

`Config(world="distractor", true_dim=3, obs_dim=20, distractor_dim=1,
distractor_channels=10, distractor_mode="noise",
distractor_noise_std=σ_d)`, pinned random policy, seeds 1–8, the standard
schedule (`effective_n_cycles = 50`, checkpoints 18/30/50), engine runs
through `make_world` — the L3 rung reading re-instrumented with the dial.
σ_d ∈ {0.04, 0.1, 0.2, 0.5, 1.0}.

Note on `distractor_dim=1` (vs the recorded rung's 3): noise mode never
*emits* the autonomous latent, but its construction draws consume RNG, so
the σ_d = 1.0 row is a fresh **replicate** of the L3 finding at a
different construction stream, not the recorded run re-executed; the
recorded configuration stays reproducible under the inert default.

Readings per σ_d: per-seed `best_dim` at @18/@30/@50 and final;
`improvement`; `mean_map_fraction`. Judged with the pre-registered L3
criterion form (|best_dim − 3| ≤ 1 in a strict majority at every
checkpoint). **Breaking amplitude** := the smallest σ_d in the grid that
fails.

## E2 — mechanism probe (protocol pre-registered before running)

One equal-experience scan-style probe (the STEP-0 instrument, `run_scan`
adapted to the distractor world; scratchpad-only code): one frame per
dim ∈ {1, 2, 3, 4, 6, 8}, no fit gate, trained 100 episodes at the live
effective learning rate, frozen, evaluated 10 episodes. At
σ_d ∈ {0.04, 1.0} plus the E1 breaking amplitude if interior; seeds 1–3.
Per dim, measured on the frozen weights:

- (a) **all-channel** honest pred/recon error — the norm the scorer sees;
- (b) **core-restricted** error — `‖(recon−obs)[:10]‖ / ‖obs[:10]‖`
  (did the frame actually learn the controllable structure?);
- (c) **static-restricted** error — the floor, measured;
- (d) the survival score at the effective parsimony price.

Discriminating arithmetic, pre-registered:

- **H-compress confirmed** iff at σ_d = 1.0 the all-channel marginal
  error gain per dim (mean over dims 1→4) is **below** the 0.02/dim
  price while at σ_d = 0.04 it is above it, AND the core-restricted
  error keeps a clear dim gradient with its dim-3 value within 1.5× of
  the σ_d = 0.04 value (learning intact — the collapse is a scoring
  artifact).
- **H-corrupt confirmed** iff the core-restricted error at σ_d = 1.0
  breaches the 1.5× threshold or loses its dim gradient (the collapse is
  a learning failure).
- **Consistency check:** the score minimum computed from (a) + (d)
  should land where E1's live landings land (dim 1 at σ_d = 1.0; ≈3 at
  0.04) — if it does not, the mechanism is not in the frozen surface and
  the ecology (gate/eviction dynamics) is re-opened.

## Result: E1 (recorded 2026-07-14; 40 runs, one instrument invocation)

| σ_d | within 1 of 3 @18/@30/@50 | finals | dim-1 finals | median improvement [range] | map_frac range | verdict |
|---|---|---|---|---|---|---|
| 0.04 | 8/8, 6/8, 8/8 | [3,4,4,3,2,3,3,3] | 0/8 | 0.485 [0.383, 0.604] | [0.63, 0.88] | PASS |
| 0.1 | 5/8, 7/8, **4/8** | [3,5,5,3,3,2,1,1] | 2/8 | 0.441 [0.227, 0.640] | [0.61, 0.87] | FAIL |
| 0.2 | 7/8, 7/8, 8/8 | [4,3,4,3,2,3,4,3] | 0/8 | 0.392 [0.334, 0.518] | [0.64, 0.92] | PASS |
| 0.5 | **4/8, 3/8**, 6/8 | [3,4,2,2,1,2,3,1] | 2/8 | 0.198 [0.082, 0.300] | [0.55, 0.83] | FAIL |
| 1.0 | 6/8, 4/8, **2/8** | [1,1,2,4,1,6,1,1] | 5/8 | 0.107 [0.020, 0.195] | [0.64, 0.82] | FAIL |

**Readings.** (1) Degradation is dose-dependent and smooth in the
continuous measures — median improvement falls monotonically
0.485 → 0.107 — but the binary majority criterion flips
**non-monotonically at the boundary**: σ_d = 0.1 FAILs (two seeds slide
to dim 1 late: 5→2→1, 3→3→1) while 0.2 PASSes clean — a two-seed
difference across the strict-majority line, i.e. verdict flicker, not a
threshold. The as-defined breaking amplitude is therefore recorded as
**0.1 (non-robust)**; the **robust break is between 0.2 and 0.5** (at
0.5 the landing is systematically depressed and improvement halves), and
collapse is unambiguous at 1.0 (5/8 dim-1 finals — replicating the L3
finding at a different construction stream). (2) **H-gate refuted:**
`mean_map_fraction` stays in [0.55, 0.92] at every dose — frames elect
and learn throughout; there is no election starvation. (3) H-dose
confirmed in its dose-dependence, amended in shape: the transition is a
widening instability band, not a sharp threshold.

## Result: E2 (recorded 2026-07-14; ran the full E1 grid — the probe is cheap and the non-monotonicity deserved the full surface)

Equal-experience frozen surfaces (100 train episodes, means over seeds
1–3; `pred_all`/`recon_all` = the scorer's all-channel norms,
`core` = restricted to the 10 controllable channels, `score` at the
0.02/dim effective price):

σ_d = 0.04:

| dim | pred_all | recon_all | pred_core | recon_core | score |
|---|---|---|---|---|---|
| 1 | 1.034 | 1.010 | 1.024 | 0.999 | 1.042 |
| 2 | 0.842 | 0.824 | 0.836 | 0.818 | 0.873 |
| 3 | 0.557 | 0.526 | 0.549 | 0.517 | 0.602 |
| 4 | 0.502 | 0.457 | 0.494 | 0.447 | 0.559 |
| 6 | 0.363 | 0.279 | 0.356 | 0.269 | **0.441** |
| 8 | 0.384 | 0.256 | 0.378 | 0.243 | 0.480 |

σ_d = 1.0:

| dim | pred_all | recon_all | pred_core | recon_core | score |
|---|---|---|---|---|---|
| 1 | 1.042 | 1.030 | 1.020 | 0.995 | 1.056 |
| 2 | 0.999 | 0.959 | 0.901 | 0.841 | 1.019 |
| 3 | 0.989 | 0.934 | 0.886 | 0.851 | 1.022 |
| 4 | 0.958 | 0.875 | 0.821 | 0.777 | 0.996 |
| 6 | 0.943 | 0.797 | 0.763 | 0.722 | 0.990 |
| 8 | 0.935 | 0.710 | 0.768 | 0.730 | **0.983** |

(0.1 and 0.2 are byte-close to 0.04 on the core columns — core dim-3
error 0.551/0.551 vs 0.549 — and keep the score min at dim 6; 0.5 sits
between: core intact at ratio 1.02, all-channel span compressed, score
min still 6 with a flattening basin. Full tables in the run artifact.)

**Verdicts on the pre-registered fork:**

1. **H-corrupt: confirmed at σ_d = 1.0, refuted at ≤ 0.5.** Core dim-3
   error at 1.0 is 0.886 vs 0.549 at 0.04 — ratio **1.61**, over the
   pre-registered 1.5× threshold — and the core gradient flattens
   (1→6 span 0.667 at 0.04 vs 0.257 at 1.0): unit static in the shared
   encoder and noise-target decoder rows measurably corrupt core
   learning itself. At 0.5 the ratio is 1.02 — learning is intact there.
2. **H-compress: the compression is real but, as pre-registered, its
   arithmetic clause FAILS at the asymptote.** The weighted (½·recon +
   ½·pred) all-channel marginal gain over dims 1→3 compresses 6.5×
   (0.240/dim at 0.04 → 0.037/dim at 1.0) — but it stays *above* the
   0.02/dim price, and the frozen score minimum sits at **6–8 at every
   amplitude, never at 1**.
3. **The consistency check fires:** the frozen asymptotic surface cannot
   produce the live dim-1 landing. The mechanism is not in the converged
   surface — it is in the **transient**: at 1.0, corrupted learning
   roughly doubles every dim's error floor and slows convergence, and
   the live ecology judges frames young (effective patience at
   obs_dim = 20 is 6 cycles = 36 exposure episodes) under eviction
   churn — what selection sees is the young-age surface, not this one.
4. **Side finding — noise autoencoding.** At σ_d ≥ 0.5 the
   static-restricted *recon* error falls with dim (1.02 → 0.68 across
   1→8 at σ_d = 1.0): extra pose dimensions get spent passing static
   through the bottleneck, so the asymptotic min at 8 partly *buys the
   distractor* — the exact failure L3 was built to measure, visible on
   the recon side only at high amplitude.

## E2b — the transient surface at judging age (protocol pre-registered before running)

The same probe at the ages the live ecology actually judges:
`train_episodes ∈ {12, 24, 48}` (12 = `min_age_cycles`·`episodes_per_cycle`,
the age at which a frame first becomes evictable), frozen 10-episode
eval, dims {1, 2, 3, 4, 6, 8}, σ_d ∈ {0.04, 0.5, 1.0}, seeds 1–3.

**H-transient (pre-registered):** at 12 episodes the σ_d = 1.0 weighted
score surface is price-dominated — minimum at dim 1 — while the 0.04
surface already shows the elbow (min ≥ 3); 0.5 sits between (shallow
min at 2–3). With age the 1.0 minimum migrates right, explaining the two
live escape seeds (finals 4 and 6). If instead the 12-episode surface at
1.0 still has its minimum at 6–8, the remaining suspect is eviction
churn itself and the diagnosis proceeds to churn instrumentation.

**Corroborating live reading (protocol + prediction stated before
running):** rerun the E1 endpoint arms (σ_d ∈ {0.04, 1.0}, seeds 1–8 —
deterministic replays) capturing `best_score`, `mean_population`,
`final_population`. The error floor puts every EMA near 1, so a mature
frame's score is ≈ 0.5·recon + 0.5·pred + 0.02·dim ≳ 0.97 + 0.02·dim —
**above the 0.8 base survival threshold at any population size**.
Prediction: at σ_d = 1.0 the winner's `best_score` sits ≈ 1.0 (no frame
can ever clear the bar → the population is pure youth-protected
conveyor, permanently re-judged at the age where dim 1 wins), while at
0.04 `best_score` sits well below 0.8 and populations carry mature
frames.

## E3 — remedy (conditional; stance pre-registered)

Only if E2 confirms a mechanism **and** a principled, reference-preserving
fix exists (opt-in, or an effective form that is exactly the current
behavior at the reference configuration; mechanism-level, never
tuned-until-green). Candidate directions to evaluate against what E2
shows: per-channel error normalization by an estimated noise floor;
excluding never-learnable channels from the survival norm (a learned
channel-weighting design step — likely deserves deferral to a named
feature); scaling the parsimony price with the measured per-dim error
span. If no principled fix fits the arc, stop after E2 and record the
mechanism plus named remedy directions — an honest open problem with a
measured mechanism is a complete deliverable.

## Result: E2b (recorded 2026-07-14)

Weighted all-channel score surface (½·recon + ½·pred + 0.02·dim), score
minimum and basin depth (score(1) − score(min)) by σ_d × age:

| σ_d | age 12 | age 24 | age 48 |
|---|---|---|---|
| 0.04 | min **4**, depth 0.119 | min **4**, depth 0.093 | min **6**, depth 0.136 |
| 0.5 | min **4**, depth 0.097 | min **3**, depth 0.032 | min **4**, depth 0.080 |
| 1.0 | min **1**, depth 0.000 | min **1**, depth 0.000 | min 8, full span **0.015** |

**H-transient: confirmed at σ_d = 1.0.** At the ages the live ecology
judges (the protection window at obs_dim = 20 is
`effective_min_age_cycles` = 6 cycles = 36 episodes of exposure ≈ 27
equal-experience episodes at the measured map fractions — bracketed by
the 24- and 48-episode reads), the score minimum **is dim 1**; by 48
episodes the surface is not dim-1-dominated but *gradient-free* (full
span 0.015 ≈ ¾ of one dim's price — selection noise). At 0.04 the elbow
is healthy at every age. At 0.5 the pre-registered shape ("shallow min
at 2–3") is amended by the data: the minimum stays at 3–4 but the
mid-age depth collapses to 0.032 — the landing becomes seed-noise
dominated, which is exactly E1's instability band (finals [3,4,2,2,1,2,3,1]).

**Corroborating live reading (protocol above), σ_d ∈ {0.04, 1.0}, seeds
1–8:**

| σ_d | best_score per seed | mean_pop | final_pop |
|---|---|---|---|
| 0.04 | 0.13, 0.35, 0.40, 0.12, 0.14, 0.21, 0.20, 0.17 | 17–28 | 16–32 |
| 1.0 | 0.73, 0.82, 0.74, 0.79, 0.72, 0.83, 0.79, 0.76 | 10–20 | 9–16 |

At σ_d = 1.0 the *best* frame's score (0.72–0.83) sits **above** the
pop-scaled survival bar (0.8/(1 + 0.04·(pop − 4)) ≈ 0.49–0.65 across the
measured populations) — soft eviction removes every unprotected frame over the
bar, so **no frame ever survives its first unprotected judgment**: the
population is a pure youth conveyor (plus no-map births), permanently
re-judged at the ages where dim 1 wins. At 0.04 winners sit at 0.12–0.40,
far under the bar, and populations carry mature anchors. One prediction
correction, recorded honestly: the winner's score was predicted ≈ 1.0
and measured 0.72–0.83 — the all-step EMAs are tracking-flattered below
the frozen floor (the known THRESHOLD-DIAGNOSIS effect); the structural
claim (nothing matures) is what the population numbers test, and it
holds.

**The remedy-informing computation (from the same E2b data):** score the
surfaces on the core channels only — a *perfect* floor-normalization
proxy (as if an oracle excluded every static channel from the survival
norm). At σ_d = 0.5 this restores a healthy elbow (min 3–4, depth up to
0.134). At σ_d = 1.0 it does **not**: judging-age depth 0.022 (min 3 at
age 12, back to min 1 at age 24) — because H-corrupt's leg is upstream
of the score: static entering the shared encoder has already flattened
the core error itself at young ages. **Score-side channel weighting
alone is provably insufficient at unit amplitude; the encoder input
path needs the same treatment.**

## Outcome

1. **The mechanism, fully measured — a three-leg compound, not a single
   cause.** (i) *Floor compression* (E2): irreducible per-channel floors
   enter both the numerator and denominator of the all-channel honest
   error norms, compressing the per-dim error span 6.5× at unit
   amplitude (weighted 1→3 gain 0.240 → 0.037/dim) — real, but at the
   asymptote still above the 0.02/dim parsimony price, so not sufficient
   alone. (ii) *Learning corruption* (E2, the pre-registered 1.5×
   threshold): at σ_d = 1.0 static in the shared encoder and noise-target
   decoder rows nearly double the core error asymptote (dim-3: 0.886 vs
   0.549, ratio 1.61) and halve the core gradient; at ≤ 0.5 learning is
   intact (ratio 1.02). (iii) *The transient is what gets judged* (E2b +
   corroboration): the floor holds every frame's score (winners
   0.72–0.83) above the absolute survival bar (≈ 0.49–0.65 pop-scaled),
   so nothing matures — the ecology is a permanent conveyor judged at
   ages where compression + corruption leave the surface
   price-dominated, and the smallest dim wins.
   Collapse is the ecology faithfully following a score that has lost
   its gradient.
2. **Dose–response: an instability band, not a threshold.** Sensor-scale
   static (σ_d = 0.04, = `sensor_noise_std`) is harmless — PASS with
   healthy landings. Verdict flicker begins at σ_d = 0.1 (two late dim-1
   slides; 0.2 passes clean — a two-seed majority-boundary effect);
   the robust break is between 0.2 and 0.5 (median improvement halves,
   landings depress); collapse is unambiguous at 1.0 (5/8 dim-1 finals,
   replicating the recorded L3 finding at a different construction
   stream). The binary strict-majority criterion is noisy inside the
   band — the continuous measures (median improvement 0.485 → 0.107,
   monotone) are the trustworthy dose axis.
3. **Refuted along the way:** H-gate (election starvation — map
   fractions stay 0.55–0.92 at every dose); H-compress's asymptotic
   arithmetic (the frozen score minimum never reaches dim 1 — the
   compression story is true only jointly with the transient); the
   "breaking amplitude" as a sharp point (it is a band).
4. **E3: no remedy shipped — deferral, for a measured reason.** The one
   mechanism-level fix is an in-system per-channel noise-floor estimator
   feeding **both** the survival norm and the encoder input path —
   *learned channel weighting*, hereby named as the successor feature.
   The cheap half (score-side normalization only) was tested against the
   E2b data and fails exactly where the problem lives (unit amplitude);
   a survival bar with a notion of achievable error (relative rather
   than absolute) is the other named leg, and it interacts with the
   seventh scale rule (THRESHOLD-DIAGNOSIS) — neither is a small opt-in
   dial this arc could validate honestly. Per the pre-registered stance,
   the arc stops at the measured mechanism.
5. **What ships:** the `distractor_noise_std` dial (inert at 1.0,
   test-guarded byte-identity — the recorded L3 rung stays reproducible)
   as the permanent dose–response instrument, and this trail.
