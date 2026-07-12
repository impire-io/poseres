# T3 at scale — does genuine prediction still beat learned persistence?

Date: 2026-07-11. Question under test: **T3's persistence clause has never
been measured on the scaled worlds** — the last acceptance criterion
validated only at reference scale (ROADMAP A2, named the top open research
item when the eighth rule closed T-SCALE, JOURNEY ch. 14). T3 is the
suite's ablation test: genuine predictive training must beat *both* an
effort-only ablation (the weak claim) and a learned-persistence ablation
(the strong claim — "the system predicts better than assuming nothing
changes"). PRA-02 §2 notes persistence is a *deceptively good* predictor
even at reference (analytic identity baseline 0.165 vs the validated
system's 0.157); nothing guarantees the scaled ecology clears that bar on
worlds whose emission is a random nonlinear map three times wider than the
latent.

## The criterion, applied verbatim

No new criterion is invented for scale. Per `true_dim`, the reference T3
runs unchanged (one evaluator, `evaluate_t3`, shared with the suite):
predictive improvement > effort-only improvement AND > identity
improvement, each in a strict majority of seeds; `improvement` is
`pred_error_early − pred_error_late` (first vs last 200 recorded per-step
honest errors, PRA-02 §3.3). Both ablations receive equal online experience
from fresh deterministic worlds (`seed + 9999` / `seed + 18888`) and measure
honestly while learning their ablated targets (PRA-02 §2). Investigatory
context like T-SCALE: the verdict is data, never a build pass/fail.

## Pre-registration (before the full run)

- **Protocol:** `pra-validate scale --t3 --true-dims 20,35,50`, 2000 cycles,
  seeds 1–8, checkpoints (400, 800, 1200, 1600, 2000) — the capped scaled
  reference protocol of LONGEVITY-DIAGNOSIS E2, with the shipped ecology
  defaults (fair judge `score_window_steps=5`, conveyor correction,
  `weight_norm_cap=1.2`, climbing proposals; `obs_dim=3·td`,
  `hidden=2·td`).
- **Verdict rule:** T3 PASS at a scale iff predictive beats effort-only in
  ≥5/8 seeds AND beats identity in ≥5/8 seeds at that scale. Reported
  either way, with both per-seed margin spreads.
- **Secondary reads:** the predictive arm's `best_dim` spread (should
  reproduce the 10/9/9 anchored reference — same runs, same protocol), and
  both margins per seed (the identity margin is the binding one and is the
  reported measure).
- **Reference baseline for comparison (measured 2026-07-11, this machine):**
  T3 PASS at reference — effort-only beaten 8/8, identity 6/8, identity
  margin 0.067 ± 0.065.

**Instrument.** New opt-in harness path (this feature): `run_scale_t3`
builds the identical scaled configs as `run_scale` (shared
`scaled_config`) and runs the reference triad through `run_suite` with the
climbing proposal factory; ablation arms never consolidate (PRA-02 §2
semantics preserved — equal online experience, no offline cycles), so the
proposal policy is inert there. The validated default path is untouched
(`proposal_factory=None`; a regression test asserts byte-identical
summaries), and the reference suite still passes byte-identically.

**Probe note (context, not evidence).** A single-seed, 200-cycle sizing
probe showed the shape to expect: effort-only improvement ≈ 0 at scale
(its frames train toward the zero pose; honest error does not fall), while
identity improvement lands in the same band as predictive (td=20:
0.484 vs 0.460 — identity *ahead* on that seed; td=50: 0.602 vs 0.650).
The identity clause is the contest; the full protocol decides it.

## Result (2000 cycles, seeds 1–8, shipped scaled ecology; 5.7 h wall)

| `true_dim` | effort clause | identity clause | identity margin (mean ± std) | verdict |
|---|---|---|---|---|
| 20 | 8/8 | **2/8** | **−0.054 ± 0.075** | **FAIL** |
| 35 | 8/8 | **2/8** | **−0.030 ± 0.039** | **FAIL** |
| 50 | 8/8 | 5/8 | −0.005 ± 0.036 | PASS |

Per-seed identity margins — td=20: [+0.040, +0.037, −0.045, −0.029, −0.117,
−0.023, −0.195, −0.101]; td=35: [−0.058, −0.013, −0.017, −0.103, +0.009,
+0.022, −0.064, −0.017]; td=50: [+0.060, −0.051, +0.008, +0.009, −0.063,
−0.014, +0.005, +0.005]. The td=50 PASS is the thinnest possible majority
with a *negative* mean margin — statistically the same floor as the two
FAILs. The weak clause is never the contest (effort-only improvement is ≈ 0
to negative everywhere, as designed). **Instrument cross-check:** the
predictive arm's `best_dim` per seed reproduces the capped scaled reference
(PRA-02 §4 final table) exactly, seed-for-seed, at all three scales — same
protocol, so the triad's predictive runs *are* the anchored reference runs.

Read as written, T3's strong clause fails at scale: the scaled ecology's
measured improvement sits at the learned-persistence floor (reference:
+0.067 ± 0.065, 6/8).

## The discriminator: composition, not capability

Before concluding "the scaled system does not learn dynamics," one
confound had to die (the repo rule: diagnose before concluding). T3's
measure averages honest error over **every electing frame**
(`elect_pred_errors`, PRA-02 §3.1). The scaled predictive ecology carries a
standing conveyor of `spawn_per_cycle × patience` protected juveniles
(29 / 68 / 116 at td 20/35/50 — patience is an effective rule in
`obs_dim`) inside populations of ~43 / ~89 / ~140; the ablation arms never
consolidate (PRA-02 §2), so their small populations (~12–31) have **no
churn at all**. The predictive arm's mean is polluted by perpetual
newborns; the identity arm's is not.

The one-variable discriminator: run *predictive* training under the
identity arm's exact semantics — same `seed + 18888` worlds, no
consolidation, same scaled config — so the only difference left is the
training target. td=20, seeds 1–3, 2000 cycles, vs the identity arm's
measured improvements from the full run:

| scale | seed | predictive, churn-matched | identity arm | margin |
|---|---|---|---|---|
| td=20 | 1 | +0.5422 | +0.4981 | **+0.0441** |
| td=20 | 2 | +0.5800 | +0.5650 | **+0.0150** |
| td=20 | 3 | +0.7536 | +0.7338 | **+0.0198** |
| td=35 | 1 | +0.7376 | +0.7027 | **+0.0349** |
| td=35 | 2 | +0.7293 | +0.6936 | **+0.0357** |
| td=35 | 3 | +0.7017 | +0.6884 | **+0.0133** |

Churn-matched, predictive beats learned persistence **6/6 across both FAIL
scales** (mean margin +0.026 at td=20, +0.028 at td=35) — the sign flips
from the full run's 2/8. The scaled T3 FAIL is substantially
**measurement composition, not a capability cliff**. Two honest caveats,
recorded rather than smoothed:

1. **The frame-level persistence edge at scale is thin**: +0.015 to +0.044
   (mean ≈ +0.026), roughly a third of the reference margin (+0.067) —
   consistent with PRA-02 §2's warning that persistence is deceptively
   good in this world, and presumably budget-bound (the effective learning
   rate shrinks with `obs_dim`; 2000 cycles is far from asymptote at
   `obs_dim = 60+`).
2. **The cross-scale margin trend is NOT explained by juvenile fraction
   alone.** Pollution ∝ juvenile-fraction predicts margins *worsening*
   with scale (fractions 0.67 → 0.76 → 0.83); the measured margins
   *improve* (−0.054 → −0.030 → −0.005). Something else co-varies —
   candidate: elect gating (badly-fitting juveniles at larger `obs_dim`
   elect less often, so they pollute the mean less). Open, named, not
   measured here.

## Outcome

1. **ROADMAP A2's exit criterion is met**: T3 measured at td 20/35/50
   under the reference protocol, PASS/FAIL and both margins recorded per
   scale with the full spreads — and the result is a finding, not a pass.
   **T3 as written is not scale-portable:** at scale its population-mean
   measure reads ecology composition (the juvenile conveyor), not dynamics
   learning — the same instrument-vs-scale lesson as the maturation filter
   (PROPOSAL-DIAGNOSIS) and the fair judge (THRESHOLD-DIAGNOSIS), now on
   the acceptance side.
2. **The capability claim survives the diagnosis, thinly**: churn-matched
   predictive training beats learned persistence at scale (6/6 at td=20
   and td=35, the two FAIL scales), with a margin ~⅓ of reference.
   Genuine dynamics learning above the persistence floor exists at scale;
   it is not abundant.
3. **The verdicts stand as measured** (FAIL / FAIL / PASS on the criterion
   as written) — recorded, not amended quietly. The successor question is
   named: **a churn-matched form of T3 at scale** (e.g. mature-frames-only
   improvement, or the discriminator's no-consolidation pairing as the
   scaled instrument), designed openly as a criterion amendment with this
   document as its evidence base, per the T7 precedent.
4. The instrument ships: `pra-validate scale --t3` (opt-in, investigatory,
   reference-preserving; one evaluator shared with the suite).
