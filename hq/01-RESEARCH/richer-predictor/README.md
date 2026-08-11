# Richer predictor — can context terms refuse the ruinous trade?

**State:** active
**Started:** 2026-08-11

## Abstract

Episode 0090 licensed this build by numbers: the linear event head
leans toward bargains (median rate 7 vs average 8) but cannot refuse
ruin (25.2% worth-destroying trades vs the 10% bar). The mechanism
diagnosis: the trade's outcome is *zero everywhere except at the
trader, where it falls with the rate* — an interaction (place ×
price) that a linear-in-observation model can only average over,
diluted by the mass of no-op trade attempts. The minimal generic
extension is the **quadratic event head**: the identical per-action
NLMS rule (one dial, zero-init, no RNG) over features
`[obs, 1, obs_i·obs_j for i ≤ j]` — no channel privileged, context
entering as multiplication, exactly the class episode 0090 refuted
linearity on. Instrument-grade (the G3 precedent: the prototype head
lived in the harness before feature 040 shipped it); a shipped form
is a later owner call with its own closure.

## The question

Does the quadratic head — taught by deterministic replay of the same
48 lessons the cohort witnessed, then learning online — flip the
completion's sign at ruinous rates (refusal ≤ 10%) while preserving
the bargain lean and the reactive-world pacing, on the unchanged
moving-senses instrument?

## Instrument (frozen with the bars)

- **The quadratic head** (harness-side): per-action NLMS, η = 0.5,
  over F = 16 + 1 + 136 = 153 features (observation, bias, all
  pairwise products); predicts the full observation delta;
  zero-initialized; updates on every witnessed transition (the
  feature-040 invariant).
- **Mounting**: a policy subclass substitutes the quadratic head's
  predictions for `predict_event_delta` in the context it hands the
  unchanged shipped arithmetic — the seam Doc 0005 names, nothing
  else touched. Pre-training: deterministic replay of the cohort's
  own 48 teaching segments (tapes, handed ingredients, phase
  offsets, the book's evolution — all reconstructable); the replayed
  book MUST equal the saved book (instrument assertion), proving the
  replay is the witnessed experience.
- **World, cohort, arms**: episode 0090's instrument unchanged —
  the mv-graduates cohort and books, the drifting rate (r ∈ [2, 14],
  break-even 10, sensed on channel 13) and the reactive rate
  (+2 markup, τ = 500). **R1** quad head on the drifting world;
  **R2** quad head on the reactive world; **anchor rows**: episode
  0090's N1/N2 arms — same seeds, same worlds, same shipped
  arithmetic, linear head — cited directly, not rerun.
- **Pilot** (seeds 1–8, R1, published before the arms): replay-book
  assertion green; the head's trade-outcome predictions logged
  against realized (the direct evidence prediction is or isn't the
  bottleneck).

## Pre-registered bars

- **RP1 — refusal:** R1 ruinous trades (r > 10) ≤ **10%** of all
  trades (anchor 25.2%).
- **RP2 — the lean preserved:** R1 median rate paid ≤ **7** (the
  linear anchor's own median — richer must not be worse).
- **RP3 — no collateral:** R1 seeds with ≥ 1 gem ≥ **18/24**
  (anchor 24/24) AND R2 seeds with ≥ 3 gems ≥ **12/24** (anchor
  21/24).

Registered readings: the trades-vs-rate histogram shift against
0090's; predicted-vs-realized trade outcomes (the head's actual
sharpness at the sign flip); pacing intervals in R2.

## Reversal condition

If RP1 fails while the head's trade-outcome predictions are
verified sharp (predicted sign matches realized at ≥ 90% of trade
opportunities logged in the pilot readings), then prediction was
not the bottleneck — the failure moves up a layer to value
arbitration (the completion rule's use of the prediction, Doc
0005), and that becomes the licensed successor with these numbers.

## Verdict

<Empty until graduation.>
