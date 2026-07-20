# Inter-age diagnosis — does the ecology land where its judge points?

Date: 2026-07-11. Question under test: THRESHOLD-DIAGNOSIS closed with the
scaled ecology working (24/24 anchored, medians 6–8.5 at true_dim 20/35/50)
but landing **below the frozen-eval elbow (12–16)**, with a slow downward
drift over budget, and named "fair inter-age comparison" as the successor:
niche entry order favors fast-training dims, and incumbents defend tenure
with a lifetime-training advantage no one-window candidate can match. Before
any remedy: is that story actually what sets the landing level?

## Hypotheses

- **H-A (inter-age bias):** the fair judge's own score surface at *equal
  experience* bottoms at 12–16 like the frozen scan; the live 6–8.5 landing
  is entry-order + tenure bias. Remedy family: dim-scaled maturation windows
  or a patience dose (give slower-training dims the time their asymptote
  needs).
- **H-B (already faithful):** the fair-judge surface itself bottoms at ~6–10
  (a K=5 window admits some within-window adaptation; at-maturity experience
  is one patience window). Selection already lands at its judge's minimum;
  the residual is not an ecology defect but the **scorer question** (Doc 03
  §6 parsimony vs marginal information — the deeper frontier E1 of
  THRESHOLD-DIAGNOSIS exposed).

## E1 — the fair-judge surface at equal experience (the discriminator)

Replicate the live judge exactly (EMA decay 0.9 over pre-learning recon +
post-learning honest pred, advancing only on the first 5 steps of each
episode, read at episode ends, plus effective parsimony), one frame per dim,
equal experience, td=20, seeds 1–3. Read the surface at **at-maturity
experience** (174 episodes = one patience window — what niche entry sees) and
at **long experience** (600 episodes — where anchors equilibrate), plus each
dim's episodes-to-asymptote.

| dim | score @174ep (maturity) | @600ep (long) | eps to within 5% of final |
|---|---|---|---|
| 4 | 0.650 | 0.501 | 336 |
| 6 | 0.562 | 0.443 | 326 |
| 8 | 0.549 | 0.434 | 333 |
| 10 | **0.526** | **0.419** | 333 |
| 12 | 0.528 | 0.421 | 358 |
| 16 | 0.538 | 0.432 | 337 |
| 20 | 0.550 | 0.451 | 325 |
| 24 | 0.590 | 0.478 | 327 |

## Both hypotheses die; the problem dissolves

1. **H-A's mechanism is refuted outright:** episodes-to-asymptote is *flat*
   in dim (~330 everywhere). There is no differential-training-speed rigging
   of niche entry, and dim-scaled maturation windows would remedy a mechanism
   that does not exist.
2. **H-B's level is wrong too:** the fair judge's own minimum is 10–12 (a
   residual ~2–4 dims of K-window flattery vs the frozen scan's 12–16), not
   the live 6–8.5.
3. **The real finding: the basin is flat.** Across dims 6–16 the asymptotic
   fair-judge score spans **0.024** — the same order as seed noise and as two
   or three parsimony increments (0.0067/dim). Selection has no gradient to
   climb; the live landing is the low edge of a flat basin, reached first
   from the birth dims and mildly preferred by parsimony plus residual
   flattery.
4. **"Tenure" was misread.** The E4′ trajectories churn freely through the
   basin (seed 1: 11→10→12→10→6→13→13→7 across checkpoints; 10–17 mature
   frames per run) — no frozen anchors, no unbeatable incumbents. The
   ecology-level anchoring (the mature niche always populated) coexists with
   free within-basin movement of "best"; the slow downward drift is a random
   walk with a mild low-dim pull, not compounding incumbent advantage.

## Outcome

The named successor problem "fair inter-age comparison" is **dissolved by
measurement**: no inter-age mechanism sets the landing level, and no
inter-age remedy is warranted. What sets the level is the **score surface
itself** — a basin too flat to resolve the honest optimum, shaped by the
parsimony term against a marginal-information signal that has gone flat
(exactly the Doc 03 §6 [D] question flagged since SCALE-DIAGNOSIS layer 4,
now with the measurement that makes it concrete). The frontier, restated
precisely: **make the basin informative** — candidates are a re-shaped
parsimony (`w_complexity·log(dim)`, or elbow-relative selection), a sharper
judge (frozen shared-window evaluation at consolidation, removing the last
~2–4 dims of window flattery), or accepting the basin and reporting
`best_dim` with basin-width error bars. Any of these changes the score
definition — a design-level [D] investigation with reference revalidation,
deliberately not begun here.

One-experiment arc; the instruments (fair-judge equal-experience surface,
trajectory churn reading) took an afternoon of compute. Negative results are
results.
