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

## Result: L1 (to be recorded)

*(filled by the first instrument run — verdicts, per-seed spreads,
occupancy; including failures)*

## Result: L2 (to be recorded)

*(filled by the first instrument run — verdicts, paired margins, census,
best_dim spreads; including failures)*

## Result: L3 (to be recorded)

*(filled by the first instrument run — verdicts, checkpoint trajectories
both modes; including failures)*
