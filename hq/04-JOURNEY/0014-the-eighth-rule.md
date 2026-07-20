# Chapter 14 — The eighth rule and the price of a dimension (2026-07-11)

Two arcs closed in one day, each finishing the other. First the rot fix:
per-tensor max-norm control (`weight_norm_cap`), designed from Chapter 13's
measured mechanism — stateless closed-form caps at `1.2·E‖W_init‖`, biases
exempt, projected at episode starts, magnitude only (the never-trained-then-
frozen premise survives intact). The dose–response was clean (∞ rots, 1.5
attenuates, 1.2 eliminates — capped frames end 9600-episode runs at their
best-ever error, and the immune dims are untouched), and the payoff was
intervention-grade: moving *only* this mechanism lifted the td=20 scaled
landing from median 6 to 10 — onto the fair-judge basin minimum — with the
budget-drift gone, and the lift across scales ordered exactly by rot
exposure (+4 / +1 / +0.5). The capped scaled reference: **medians 10 / 9 / 9
at true_dim 20/35/50, 24/24 anchored.** The honest scaled ecology now stands
on three measured legs — fair judge, conveyor correction, lifetime cap —
each refuted as sufficient alone.

Then the parsimony re-ask on the rot-free ground the cap created, and the
retirement it forced: the long-trained honest error surface **falls
monotonically to the capacity ceiling in both components and both seeds** —
the scaled world's intrinsic dimensionality leaves no signature for any
penalty shape to find (nonlinear emission: a 20-dim latent's image is not a
20-dim linear object). "Does best_dim track true_dim at scale" is closed by
measurement: it cannot, and should not. The parsimony weight is a **price**
— selection buys dimensions while the marginal error gain exceeds it — and
the capped ecology already sits exactly at that operating point (measured
marginal gain crosses the 0.0067/dim price at dims 8–12; the landing is 10).
What T-SCALE can honestly claim, and now measures at every scale and budget:
**selection lands at the price-optimal dimensionality, stably.** That is the
finding the investigatory suite existed to produce. Trails:
`hq/02-DESIGN/validate/LONGEVITY-DIAGNOSIS.md`, SCORER-DIAGNOSIS epilogue;
committed together with this chapter.

Roadmap consequence, recorded with the Chapter 10 docs bundle as it ships:
A1 (the seventh scale rule) is closed by chapters 11–14 and marked done in
`ROADMAP.md`; **T3's persistence clause at scale enters as the new top
Phase-A gate (A2)**, with the ladder and the drive blend renumbered A3/A4.
