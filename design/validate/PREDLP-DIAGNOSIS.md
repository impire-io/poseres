# Predicted-LP diagnosis — a per-candidate learnability signal

Date: 2026-07-14. Question under test: the Doc 05 [O] design gap that the
blend diagnosis (BLEND-DIAGNOSIS, JOURNEY ch. 18) made precise — the
curiosity/competence pair steers the lookahead with **one shared novelty
statistic**, so no drive blend exists; a genuine blend needs a
per-candidate term that estimates *learnability*, not familiarity. This
arc designs, ships (opt-in), and measures that term.

## The design: realized local progress (the "frontier" drive)

The engine already keeps, in curiosity mode, a bounded observation memory
and a per-step prediction-error history. Pair them: remember **what the
error was at the moment each remembered observation was visited**. Then,
for a lookahead candidate observation ô:

    frontier(ô) = max(0, mean err@visit of the OLDER half
                         − mean err@visit of the NEWER half)
                  over the k nearest remembered neighbors of ô

— *has prediction error near ô been falling within the memory horizon?*
This is realized learning progress, localized:

- **unlearnable region** (the noisy-TV): error near ô is flat-high →
  signal ≈ 0 → not sought (the anti-noise-trap property, now
  per-candidate);
- **mastered region**: flat-low → ≈ 0 → not camped on;
- **learning frontier**: falling → positive → sought.

Independence: the term is a function of the error trace, not of novelty —
so weighted blends with competence (familiarity) and curiosity (novelty)
have a real surface for the first time. Pure floats, no RNG, no new
policy machinery: it rides the existing one-step lookahead.

Shipping shape (reference-preserving): a third registered drive
(`"frontier"`), active only in curiosity mode like the others; one new
bookkeeping deque (err-at-visit, lockstep with the observation memory)
that exists only in curiosity mode; `DriveContext` gains the paired
sequence with an inert default; agency snapshot state extends additively
(old curiosity blobs resume with a NaN-filled deque — the signal degrades
to 0 until the memory refills, stated). `frontier_neighbors: int = 20`
(k), requiring ≥ 2k finite-error memory entries before the signal is
nonzero. The pinned random baseline is untouched by construction.

## Hypotheses (pre-registered)

- **H-seek**: frontier-directed runs beat random on L1 worlds (it spends
  experience where error is reducible).
- **H-blend**: frontier+competence (0.5/0.5) is the first *real* blend;
  the open question is whether it beats pure competence — plausibly yes
  at mild noise (σ=0.2, where competence's edge was inside seed noise —
  BLEND E1) by exploring learnable ground competence camps away from;
  plausibly no at σ=0.8 where avoidance is most of the value. No
  directional registration; the grid decides.
- **H-occupancy**: frontier's region occupancy sits between competence's
  avoidance and curiosity's attraction (it neither stares — flat error —
  nor systematically avoids; the region boundary is partly learnable).

## Protocol (pre-registered; the 009 power lesson applied)

Arms: random | competence | frontier | frontier+competence 0.5/0.5.
L1 worlds σ ∈ {0.2, 0.8}; horizons n_cycles ∈ {18, 30, 50}; **seeds
1–24** (margins vs random are cross-realization ≈ unpaired — 8 seeds are
underpowered; the feature-009 lesson, applied up front). Measures:
improvement margin vs same-seed random, occupancy, best_dim.

**Bars:**
1. (A4-exit form) an arm beats random in a strict majority of the 24
   seeds at every horizon, at both dials.
2. (blend question) frontier+competence vs competence: T7 noninferiority
   at both dials, and superiority read honestly from the spreads.
3. (mechanism) mean occupancy ordering: competence < frontier < curiosity
   — read from this grid plus BLEND E1's recorded curiosity occupancies.

## E1 — the grid (recorded 2026-07-14; 576 runs)

Margins vs same-seed random (cross-realization ≈ unpaired; 24 seeds by
design); occ Δ = mean occupancy minus random's.

| arm | σ | >rand @18/@30/@50 | mean margin @18/@30/@50 | noninf | occ Δ @18/@30/@50 |
|---|---|---|---|---|---|
| competence | 0.2 | **14, 17, 15**/24 | +0.030, +0.043, +0.027 | PASS ×3 | −0.047, −0.054, −0.056 |
| competence | 0.8 | **18, 15, 18**/24 | +0.070, +0.053, +0.041 | PASS ×3 | −0.024, −0.041, −0.048 |
| frontier | 0.2 | 13, 12, 12/24 | +0.020, +0.015, +0.016 | PASS ×3 | −0.009, −0.021, −0.020 |
| frontier | 0.8 | 18, 15, 11/24 | +0.046, +0.032, +0.019 | PASS ×3 | +0.018, +0.005, +0.002 |
| blend | 0.2 | **13, 15, 16**/24 | +0.024, +0.025, +0.032 | PASS ×3 | −0.048, −0.054, −0.053 |
| blend | 0.8 | **19, 14, 14**/24 | +0.062, +0.051, +0.029 | PASS ×3 | −0.012, −0.030, −0.035 |

Blend vs competence: means −0.018 to +0.005 across the six cells,
noninferiority PASS in 5/6 (FAIL at σ=0.2 @30, mean −0.018).

## Outcome

1. **The ROADMAP A4 exit criterion is met — by competence, and by the
   blend.** Both beat random in a strict majority of 24 seeds at every
   horizon, at both dials. Chapter 18's verdict ("met by no
   configuration") was recorded at 8 seeds; at proper unpaired power
   (the feature-009 lesson, applied here by pre-registration) the mild-
   noise margins are real (+0.027..+0.043, SE ≈ 0.013). A4's measured
   answer: **directed competence beats random exploration on non-uniform
   worlds, full stop** — the earlier equivocation was statistical power,
   not capability.
2. **H-seek: partially confirmed.** Frontier's margins are positive and
   noninferior everywhere, but strict-majority only in 3/6 cells — a
   real, safe signal that is *weaker than competence on this world*,
   where avoiding the unlearnable half is simply the optimal policy and
   frontier deliberately doesn't avoid (it values the learnable side of
   the boundary honestly).
3. **H-blend: the blend exists and matches competence; it does not beat
   it here.** The mechanical claim stands — frontier is the first
   per-candidate term independent of novelty, so the weight simplex
   finally has a surface (unit tests pin the independence) — but on L1
   the blend's measured value over pure competence is ≈ 0 (5/6
   noninferior, one cell below). Recorded without spin. The worlds where
   frontier should earn its keep are those where camping *costs*
   something: mastered-then-changing worlds and multi-region learnable
   worlds (the L2 rung, drive-directed — future research, now properly
   instrumented).
4. **H-occupancy: confirmed.** Ordering as registered: competence
   (−0.02..−0.06) < frontier (−0.02..+0.02) < curiosity (+0.01..+0.02,
   BLEND E1) — the frontier neither camps nor stares.
5. **Doc 05's [O] gap is closed**: predicted-LP valuation exists as the
   frontier drive (realized local progress — a *measured* learnability
   proxy rather than a predicted one; the fully predictive variant would
   need a per-candidate error model and remains future work, now with a
   baseline to beat).
