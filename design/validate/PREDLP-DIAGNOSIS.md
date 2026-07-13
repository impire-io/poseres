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

## E1 — the grid (to be recorded)

## Outcome (to be recorded)
