# Chapter 18 — The blend dissolves: one novelty statistic, three behaviors (2026-07-13)

ROADMAP A4, taken up the day A3 unblocked it, pre-registered before the
data (BLEND-DIAGNOSIS.md): on the L1 noisy-region world, does curiosity
stare at the noise (H-stare), does competence camp away from it (H-camp),
and does any curiosity/competence blend beat both poles (H-blend — the
Doc 05 §5 open question)? 288 runs: six drive arms × two noise strengths
× three horizons × eight seeds, margins paired against the same-seed
random arm, occupancy from the feature-005 world-side counters.

The anomaly was the finding: **blend-75 reproduced pure curiosity
bit-for-bit across all 48 runs.** The mechanism sits in the drive forms
plus one policy line — the only per-candidate term either drive has is
the *same* novelty statistic ν (curiosity adds +ν; competence adds
`max(0, 1−ν)`; LP and mastery are history-shaped, candidate-constant),
so a weighted sum's candidate ordering reduces to `sign(w_cur − w_comp)`
wherever ν ≤ 1, and equal weights make every candidate tie — which the
lookahead's ascending strict-`>` scan collapses to action 0. **The blend
axis has no surface to tune**: {curiosity, competence, a degenerate tie
corner} is the whole simplex. H-blend dissolved by mechanism; blend-50's
grid-best strong-noise numbers are a degenerate-policy artifact
(mostly-fixed-action drift = maximally predictable experience — and a
warning about reading blend grids without mechanism checks).

The poles behaved as the pre-registration predicted, with one honest
refutation: curiosity IS pulled toward the region where the noise is
strong (Δoccupancy +1–2 points at σ=0.8, negative at σ=0.2 — mild noise
isn't novel enough to attract) but its margins never went meaningfully
negative — the LP term's flatness in unlearnable regions caps the
noisy-TV damage exactly as Doc 05 §3.1 designed (H-stare: attraction
confirmed, harm refuted). Competence avoids the region (−4 to −10
points) and **wins where the noise bites** (σ=0.8: margins +0.09–0.13,
signs 7/8, 5/8, 7/8, best_dim unharmed — the camping degeneracy did not
materialize). The pre-registered A4 exit (majority of seeds at every
horizon, both dials) was **met by no configuration**: at mild noise the
directed-vs-random effect sits inside seed noise at reference budgets.
Recorded as measured. What remains of A4 is the predicted-LP lookahead —
a per-candidate *learnability* signal, the only live path to a genuine
blend; interim showcase guidance is `competence` on strongly non-uniform
worlds. Trail: `hq/02-DESIGN/validate/BLEND-DIAGNOSIS.md`; committed with this
chapter.
