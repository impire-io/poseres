# Deficit coupling — can hunger reach wanting?

**State:** active
**Started:** 2026-08-10

## Abstract

Episode 0082 measured the gap precisely: choice is priced by novelty
and praise, never by survival — the meter decides whether the life
survives what it chose, not what it chooses. This topic builds the
missing layer named there and asks whether it closes the gap. The
design is the "body as the first teacher" shape from Doc 0010: the
label channel becomes the **felt meal** (an interoceptive signal
proportional to what the meter paid — the body sensing its own
energy, not an oracle food table), demonstrations are witnessed
hungry so every recipe's terminal carries its own taste, and the
label's weight is **gated by the current deficit** — sated, novelty
rules; starving, taste rules. The whole coupling flows through
shipped seams (the label term of `RecipePolicy`); the world's pay
table is world truth, like block hardness.

## The question

Does deficit-gated felt-value re-price the menu toward nourishment —
the exact repricing read that measured 1.04× without the coupling
(episode 0082's E2) — while sated behavior keeps rotating and the
coupled life outlives the uncoupled one under a drain that bites?

## Instrument (frozen with the bars)

- **The felt channel**: ch32 (formerly the parent's verdict) =
  `clip(pay / 0.15, 0, 1)` at every feed tick — sticks feel 1.0,
  planks/logs 0.27, cobble 0.027. The parent is out of the loop in
  this gate (one channel; coexistence with a parent teacher is
  future work, recorded). ch33 = energy, as in the value-economy
  cohort.
- **Hungry teaching**: a fresh 24-seed 34-dim cohort (wr-graduates),
  the identical 45-wood + 2×10-recipe protocol, but teaching
  segments start at energy 0.5 (no drain within a segment) so feed
  ticks are felt and the head learns feed dynamics; captures replay
  the same way, so the shipped `RecipeMemory` max-label extraction
  makes each terminal the recipe's own tastiest moment (R9's stick
  tick carries felt 1.0; cobble recipes 0.027).
- **The hungry world (free runs)**: the lean pay table of episode
  0082, drain **0.0015**/tick (3× G4's) with the G4b taper (ramp
  1,500 → full at 3,000) — calibrated so the uncoupled life
  genuinely sags and can die; the pilot may recalibrate the drain
  openly (raw numbers in JOURNEY, before any 24-seed arm) if both
  pilot arms are all-live or all-die.
- **The coupling under test** (instrument fork on the shipped
  policy, the LabelItch precedent): effective label weight
  `β_eff = κ_h · (1 − energy)`, with **κ_h = 0.1** frozen from
  episode 0081's measured dial — at deficit 0.25 the coupling sits
  in the nudge band (0.025), at deficit 0.75 it approaches the
  command cliff (0.075): mild hunger prefers, starvation insists.
  One seam carries both effects (selection and the completion read).
- **Arms** (24 seeds, H = 5,000): **W0** uncoupled control (felt
  channel present in the stream, label unused, β = 0 — episode
  0082's fail case under real hunger); **W1** the deficit-gated
  coupling (κ_h = 0.1); **W2** constant taste at the nudge dose
  (fixed β = 0.02, ungated) — isolating whether *state-dependence*
  matters beyond a constant preference for tasty endings.
- **Pilot before the arms** (seeds 1–8, W0 + W1, published): drain
  calibration (W0 must sag into deficit 0.2–0.6 with deaths
  possible), felt-labels verified in captures and teaching.
- Attribution, classification, modal rules: identical to episodes
  0080–0082.

## Pre-registered bars

- **Bar H1 — hunger re-prices:** nourishing share (R8+R9+R10) in W1
  ≥ **1.5×** W0's share — the line that measured 1.04 without the
  coupling.
- **Bar H2 — the coupling pays in survival:** W1 alive ≥ **18/24**
  AND W0 deaths exceed W1 deaths by **≥ 4** seeds.
- **Bar H3 — sated behavior stays curious:** W1 rotation
  classification ≥ **12/24** (episode 0080's rule) AND W1 chains ≥
  **18/24** — hunger nudges; it must not enslave the sated life.

Registered readings: nourishing share as a function of deficit
(binned < 0.1 / 0.1–0.3 / > 0.3) in W1 — the state-dependent dial's
direct trace; W2 vs W1 on all three bars (does gating beat constant
taste?); the head's felt-prediction learning curve; death ticks and
final energies per arm.

## Reversal condition

This topic assumes the label seam is where hunger should reach
wanting. If W1 fails H1 while the felt-labels are verified present
in the captured terminals and the deficit genuinely bites (W0
sagging as calibrated), the seam is refuted — hunger cannot reach
wanting through terminal taste alone — and the drive itself (a
deficit-modulated valuation inside `drive_value_of`) becomes the
named successor at Doc 0005's motivation seam.

## Verdict

<Empty until graduation.>
