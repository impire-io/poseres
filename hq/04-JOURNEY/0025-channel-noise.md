# Chapter 25 — Channel noise: the score loses its gradient before the brain loses its structure (2026-07-14)

The ladder's first open problem (L3 noise mode: half the observation
carrying unit static; best_dim collapses to 1 in 5/8 seeds) got its
diagnosis, run in a parallel worktree alongside chapter 24's arc. A new
inert dial (`distractor_noise_std`, 1.0 = the recorded behavior,
byte-guarded) made the amplitude sweepable: harmless at sensor scale
(0.04 — PASS), verdict flicker from 0.1, robust break between 0.2 and
0.5, collapse at 1.0 — a widening instability band, not a threshold
(median improvement falls monotonically 0.485 → 0.107). The mechanism
is a measured three-leg compound: irreducible channel floors compress
the per-dim error span 6.5× (real, insufficient alone — the frozen
score minimum never reaches dim 1); unit static corrupts core learning
itself through the shared encoder (dim-3 asymptote ratio 1.61, over the
pre-registered 1.5× bar; intact at ≤ 0.5); and the floor holds every
frame's score above the absolute survival bar (winners 0.72–0.83 vs
bar ≈ 0.49–0.65), so nothing matures — a permanent conveyor judged at
ages where the transient surface is price-dominated and dim 1 wins
(judging-age basin depth 0.000 at σ=1.0 vs 0.119 at 0.04). Refuted:
election starvation (map fractions healthy throughout) and the
one-cause compression story. The remedy is named, not shipped, for a
measured reason: perfect score-side channel exclusion (computed from
the probe data) rescues σ=0.5 but not 1.0 — the encoder input path
needs the same treatment — so the fix is **learned channel weighting**
(an in-system per-channel floor estimator feeding both the survival
norm and the encoder), a real feature, not a dial. Trail:
`hq/02-DESIGN/validate/CHANNELNOISE-DIAGNOSIS.md`; the dose–response dial
ships inert with byte-identity tests.
