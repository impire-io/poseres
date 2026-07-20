# Chapter 15 — T3 at scale: the criterion breaks before the capability does (2026-07-11 → 07-12)

Took up ROADMAP A2 the day it was named: T3's persistence clause — genuine
prediction must beat a *learned* "nothing changes" predictor, the suite's
strong claim — had never been measured on the scaled worlds. The instrument
came first, reference-preserving by construction: `pra-validate scale --t3`
runs the exact reference triad (predictive + effort-only + identity, same
seed offsets, same evaluator as the suite — PRA-02 §2 verbatim) under the
scaled ecology defaults, opt-in, with the validated paths byte-identical
(regression-tested). Protocol pre-registered in the trail doc before the
run: 2000 cycles, seeds 1–8, td 20/35/50 — the capped scaled reference
protocol. The run cross-validated the instrument for free: the predictive
arm reproduced the anchored reference `best_dim` spreads seed-for-seed at
all three scales.

The verdicts, as written: **FAIL at td=20 and td=35** (identity clause 2/8,
margins −0.054 ± 0.075 / −0.030 ± 0.039), PASS at td=50 by the thinnest
majority (5/8, mean margin still negative) — the scaled ecology's measured
improvement sits at the learned-persistence floor, versus +0.067 (6/8) at
reference. The effort clause never contested (8/8 everywhere). Before
concluding "no dynamics learning at scale," the one confound had to die:
T3's measure averages honest error over **every electing frame**, and the
scaled predictive ecology carries a standing juvenile conveyor
(29/68/116 protected juveniles at td 20/35/50) while the no-consolidation
ablation arms have zero churn. The one-variable discriminator — predictive
training under the identity arm's exact semantics (same `seed+18888`
worlds, no consolidation), only the training target differing — flipped the
sign: **churn-matched, prediction beats persistence 6/6** (td 20 and 35,
margins +0.013 to +0.044). The FAIL is substantially **measurement
composition, not a capability cliff** — the same instrument-vs-scale lesson
as the maturation filter and the fair judge, now surfacing in the
acceptance suite itself. Recorded without smoothing: the frame-level edge
is *thin* (~⅓ of reference, presumably budget-bound at the scaled effective
learning rate), and the cross-scale margin trend is **not** explained by
juvenile fraction alone (it predicts the wrong ordering; elect-gating is
the named candidate — open). Verdicts stand as measured; the successor is
named, not improvised: a **churn-matched scaled form of T3**, designed
openly as a criterion amendment per the T7 precedent. Trail:
`hq/02-DESIGN/validate/T3SCALE-DIAGNOSIS.md`; committed with this chapter.
