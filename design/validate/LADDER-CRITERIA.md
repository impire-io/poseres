# Ladder criteria — what "finding the structure" means, per rung

Feature 005 (ROADMAP A3). **Pre-registered 2026-07-13, before any recorded
results** — the FR-007 obligation, under the house rules: criteria are
written before the work, judged on per-seed spreads, amended openly if
they prove degenerate (the T7/T3 precedent), and a FAIL is a finding.
Rung verdicts are investigatory at the build level — `pra-validate ladder`
never fails a build.

First-results protocol (research R9): reference-scale dials, pinned random
policy, seeds 1–8, the standard schedule (`effective_n_cycles = 50`);
readings from the shipped `pra-validate ladder` instrument.

## L1 — the non-uniform world (`world="nonuniform"`)

World: reference dynamics everywhere except the half-space
`latent[0] > 0`, where transitions gain fresh `N(0, σ²I)` noise
(`σ = region_noise_std`). Dials for first results: `true_dim=3,
obs_dim=10`, σ ∈ {0.2 (mild, = 0.5·action_scale), 0.8 (strong,
= 2·action_scale)}.

**Criterion (PASS iff both, per dial):**

1. **Structure survives beside the noise.** Paired per seed against the
   same-seed degenerate twin (σ = 0, machinery-equal): `best_dim` within
   ±1 of the twin's in a strict majority of seeds, and the rung run's
   `improvement` at least half the twin's in a strict majority (the world
   is half unlearnable-when-visited; a mixture penalty is expected — what
   the criterion forbids is collapse).
2. **The instrument reads.** Occupancy under the random policy reported
   for every seed, in [0.25, 0.75] in a strict majority (sanity band
   around the analytic ≈ ½; a violation means the region definition or
   the counters are broken, not the brain).

Both readings recorded per seed regardless of verdict; occupancy is the
A4 baseline number (drive-directed runs are judged against it later).

## L2 — the compositional world (`world="compositional"`)

World: factored dynamics (action `a` moves factor group `a mod K`) under
the reference joint emission. Dials for first results:
`factor_dims=(3,3)` (`true_dim=6, obs_dim=18`) and `factor_dims=(2,2,2)`
(`true_dim=6, obs_dim=18`).

**Criterion (PASS iff both, per dial):**

1. **It still learns the world.** The churn-matched persistence clause
   (the amended T3 form, quartet machinery) holds on the compositional
   world: churn-matched predictive beats identity, paired per seed, in a
   strict majority.
2. **The shape of the discovered structure is recorded against the known
   parts.** Final-state census (snapshot instrument): stable frames' dims
   reported per seed against `factor_dims` and `Σ d_k`, plus `best_dim`
   per seed. The envelope claim judged: `best_dim` within
   `[min_k d_k − 1, Σ d_k + 1]` in a strict majority (outside it,
   selection found neither parts nor whole — that is the failure mode).

**Pre-stated uncertainty, deliberately not a clause:** whether selection
prefers per-part frames (dims ≈ d_k), a monolith (≈ Σ d_k), or a
price-optimal point between them is the research finding this rung
exists to produce (the parsimony result makes the honest prediction
uncertain). Whatever lands is recorded.

## L3 — the distractor world (`world="distractor"`)

World: reference controllable structure on `obs_dim − m` channels plus
`m = distractor_channels` appended channels carrying an autonomous
fixed-drift latent (`structured`) or fresh unit noise (`noise`). Dials
for first results: `true_dim=3, obs_dim=20, distractor_dim=3, m=10`,
both modes.

**Criterion (PASS iff, per mode):**

1. **Selection tracks the controllable world.** `best_dim` within ±1 of
   the controllable `true_dim` in a strict majority of seeds **at every
   horizon checkpoint** (the T4 horizon rule, applied to the controllable
   size — buying dimensions for the distractor is the failure this rung
   measures).

Per-seed checkpoint trajectories recorded for both modes regardless of
verdict; the noise mode doubles as the channel-noise reading folded in
from the spec's non-uniform-rung amendment.

## Result: L1 (recorded 2026-07-13; one instrument run, 103 s for the full grid)

**As written: FAIL at both dials** — and the diagnosis says a criterion
clause, not the instrument or the brain, is what broke.

| dial | best_dim within 1 of twin | improvement ≥ ½·twin | occupancy in band | verdict |
|---|---|---|---|---|
| σ=0.2 | 7/8 | 8/8 | **3/8** | FAIL |
| σ=0.8 | **4/8** | 6/8 | 5/8 | FAIL |

Occupancy per seed — σ=0.2: [0.715, 0.861, 0.997, 0.458, 0.963, 0.859,
0.671, 0.863]; σ=0.8: [0.511, 0.718, 0.857, 0.343, 0.939, 0.653, 0.501,
0.754]. best_dim (rung | twin) — σ=0.2: [3|4, 3|3, 3|3, 3|2, 2|3, 3|2,
3|1, 2|1]; σ=0.8: [2|4, 3|3, 5|3, 4|2, 2|3, 3|2, 2|1, 4|1].

**Diagnosis of the occupancy clause.** The "analytic ≈ ½" behind the
[0.25, 0.75] per-seed band assumed occupancy concentrates near the region's
volume share. It does not: each world's four fixed action displacements
carry a net `latent[0]` drift (mean of four `N(0, action_scale²)` values —
typical |drift| ≈ 0.16/step ≈ 6 latent units over a 40-step episode,
dwarfing the ~0.8 start offset), so per-world occupancy is
**drift-dominated and bimodal**, ½ only in expectation over world draws.
The instrument read correctly — occupancy varies across seeds exactly as
the mechanism predicts and *falls* as σ rises (in-region diffusion kicks
the latent out: pooled 0.80 → 0.66) — the clause tested a wrong
distributional assumption.

**Amendment (2026-07-13, the T7 precedent — original numbers above stay).**
Clause 2 becomes: *occupancy is reported per seed, is non-degenerate
(strictly inside (0, 1) in a strict majority), and is recorded as the
random-policy baseline for A4* — what the drive study actually needs
(drive-directed occupancy is compared per seed against this baseline, same
worlds, paired). Under the amended criterion, derived from the same
recorded table: **σ=0.2 PASS** (7/8, 8/8, occupancy non-degenerate 8/8),
**σ=0.8 FAIL** (best_dim within 1 of twin only 4/8 — strong region noise
genuinely perturbs the landing: spreads widen to 2–5 vs the twin's 1–4).
That residual FAIL is a brain finding, not an instrument artifact, and it
is exactly the kind of result the rung exists to produce.

## Result: L2 (recorded 2026-07-13)

**PASS at both factorizations.**

| dial | churn-matched > identity | best_dim in envelope | verdict |
|---|---|---|---|
| (3,3) | 7/8 (margins −0.019 to +0.076) | 8/8 in [2, 7] | **PASS** |
| (2,2,2) | 7/8 (margins −0.031 to +0.090) | 8/8 in [1, 7] | **PASS** |

best_dim spreads: (3,3) → [2, 4, 3, 3, 4, 4, 3, 2]; (2,2,2) →
[2, 2, 3, 2, 3, 2, 4, 3]. The census (per-seed, dims → frames/mature) is
in the run artifact; its shape is consistent across seeds: populations
concentrate at dims 2–5 with mature frames at the part sizes, and **no
seed lands the monolith** (`Σ d_k = 6` holds at most a stray frame; the
best frame sits at part scale, 2–4). The pre-stated uncertain question
answers **parts-sized, price-optimal** at these dials — selection buys a
part, not the whole — consistent with the parsimony finding
(SCORER-DIAGNOSIS): dimensions are bought only while marginal error gain
exceeds the price, and one factor group's worth of structure is what a
frame's price buys here. Whether richer emissions change that is A4-side
research on this same rung.

## Result: L3 (recorded 2026-07-13)

**Structured mode PASS; noise mode FAIL — recorded as the finding it is.**

| mode | within 1 of controllable true_dim=3 at @18/@30/@50 | verdict |
|---|---|---|
| structured | 8/8, 7/8, 8/8 | **PASS** |
| noise | 4/8, 3/8, **2/8** | **FAIL** |

Structured finals: [2, 3, 2, 2, 2, 2, 4, 2] — selection tracks the
controllable structure and never buys the distractor (no seed lands near
3 + distractor_dim). Noise finals: [1, 4, 1, 1, 1, 3, 1, 6] — with half
the observation carrying fresh unit static, the landing collapses to
dim 1 in five of eight seeds and destabilizes in the rest.

**Reading, stated plainly:** a *structured* autonomous nuisance is
handled by the validated ecology; *unstructured channel static at high
amplitude* (unit-scale vs the tanh emission's ≤1 range, on 10 of 20
channels) is not — the honest error every frame is judged on is
dominated by an irreducible floor, and selection loses its gradient.
This is the ladder's first new open problem:
**channel-noise robustness**, now named, with the failing configuration
recorded as its reproducible testbed. (Note the dial asymmetry: L3
noise-mode static is *unit*-scale by design — the sensor-noise dial
`sensor_noise_std = 0.04` is 25× smaller; a noise-amplitude dose–response
is the natural first diagnosis experiment.)

## Standing summary (first recorded results)

Six dial sets, pre-registered criteria, one instrument invocation:
**3 PASS / 3 FAIL as written** (4/2 under the openly-amended L1 clause).
Every FAIL is attributable: one criterion clause tested a wrong
distributional assumption (amended, numbers kept); strong region noise
widens the landing spread (real, dose-dependent); high-amplitude channel
static collapses it (real, named as the channel-noise robustness
problem). The ladder is doing its job: each failure names its own cause.
