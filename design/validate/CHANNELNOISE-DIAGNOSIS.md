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
