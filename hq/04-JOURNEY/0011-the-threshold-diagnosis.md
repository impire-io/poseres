# Chapter 11 — The threshold diagnosis: the fair judge and the conveyor (2026-07-10 → 07-11)

Took up Chapter 9's successor: make the scaled selection ecology real. The
first idea — scale the survival bar with a fitted power law — died twice,
each time to a pre-registered measurement. Raising the bar alone reopened the
mature niche and handed it to tracking-flattered low dims (best_dim *fell* to
4–7): the training-stream EMA is the third form of self-graded homework, the
*when* hole that coverage-fair (which) and observation-space (where) scoring
left open. The fix is the **fair judge** (`score_window_steps`): survival
EMAs advance only on episode-start steps, scoring transfer, not tracking. The
judge alone made things worse (nothing reached the bar; the ratchet ran
faster than ever) — the two fixes only work as a pair. The paired power law
(exponent fit at obs 60, confirmed at 105) then failed its extrapolation test
at obs=150 — and the failure's arithmetic named the true mechanism: the
population-scaled threshold was counting `spawn_per_cycle × patience`
**unevictable juveniles**, a conveyor that grows as `(obs/10)^1.5` and
tightens the bar for the frames that can be evicted. Excluding it —
`effective_survive_threshold_pop_baseline`, the **seventh scale rule,
constant-free** — restored the ecology at all three scales with residual
factor exactly 1.0. The recorded re-ask (2000 cycles, shipped defaults:
fair judge + conveyor correction + climbing proposals): **24/24 runs
anchored**, populations self-limited, `best_dim` medians 6 / 8 / 8.5 at
true_dim 20/35/50 — invariant to budget and to the proposal distribution.
Honest framing: lower numbers than the superseded conveyor readings, and the
first that mean anything. Remaining gap to the frozen-eval elbow (12–16) is
the named successor: fair inter-age comparison (the incumbent-lifetime
advantage in niche entry), ahead of the scorer-level question the elbow scans
exposed (the honest optimum sits at 12–16 regardless of the world's true
dimensionality at these budgets). Trail:
`hq/02-DESIGN/validate/THRESHOLD-DIAGNOSIS.md`; committed together with this
chapter.
