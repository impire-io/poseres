# Recipe choice — with a ten-item menu, does the brain rotate, fixate, or thrash — and can praise steer it?

**State:** active
**Started:** 2026-08-10

## Abstract

Everything measured about recipes so far used a menu of one (plus one
newcomer in the reach gate). The shipped `RecipePolicy` (feature 041,
Doc 0010) re-runs its selection **every step**: argmax over stored
recipes of `drive_value_of(terminal) + β·terminal[label]`. With one
recipe that argmax is decorative; with ten it is the whole game — and
its two faces have never been separated: the drive's novelty decay
predicts *rotation* (practice recipe A until its ending bores you,
switch to B — variety for free), while per-step re-selection predicts
*thrash* (abandon a half-done chain mid-walk whenever another ending
edges ahead, finish nothing). The owner's call ("we have to go for
this — it is quite crucial"): choice is the door to the economy
(recipes competing on yield under the meter) and to recombination
(the named means-ends successor), and neither can be registered on a
mechanism whose menu behavior is unmeasured.

## The question

When `RecipeMemory` holds ten distinct taught recipes, what does the
shipped per-step argmax selection *do* — rotate, fixate, or thrash —
and does the parent's praise (β·terminal[label]) steer which recipe
wins?

## Instrument (frozen with the bars)

- **World**: the deterministic lab world (FakeBridge), unchanged src.
  Ten demonstration tapes, each a fresh-world replay (the measured
  capture protocol): R1–R3 log digs at the three trees ((−1,0),
  (−2,3), (5,−1)); R4–R6 cobble digs at wall north/center/south
  ((3,−2), (3,0), (3,2)); R7 cobble at the pillar (−4,0); R8
  log → planks; R9 log → planks → sticks (the classic chain, the P0
  tape); R10 a two-product tour (wall cobble, then tree log).
  *Instrument gate before any run:* every tape must yield its
  registered gain on replay; a station that cannot be dug cleanly is
  replaced by an unused wall column ((3,−1) or (3,1)), recorded
  openly.
- **Cohort**: a fresh 24-seed 33-dim cohort (verdict channel,
  `event_head_eta = 0.5` during teaching, the E3.1/G5 protocol): 45
  wood segments (P0 chain teaching, judge silent), then two passes
  over each of the ten tapes, interleaved. **The judge is
  position-gated** (a parent who applauds at a *place*): it fires
  only on cobble gains at wall-center (3,0) — so exactly one
  recipe's captured terminal carries the label. Praised recipe := R5.
- **Policy**: the **shipped** `RecipePolicy` (v1.3.0) with the
  measured constants (κ = 0.25, λ_r = 0.25, positions (0,1)×64,
  label channel 32); a harness subclass logs the selected recipe id
  per step (instrument-side only).
- **Attribution rule**: a pocket-gain event at tick *t* is credited
  to the recipe selected at *t*. Raw gains are also published
  unattributed.
- **Arms** (24 seeds each, H = 5,000 free steps, the measured
  horizon): **A** menu of ten at β = 0 (choice by drive alone);
  **B** menu of ten at β = 0.5 (the measured operating point);
  **C** single-recipe control (memory holds only R9, β = 0).
- **Pilot before the arms** (seeds 1–8, arm A only, published in
  JOURNEY.md): tapes all yield; selection actually varies; the
  attribution is sane; completions dense enough at H = 5,000 to
  classify choice — if not, H is amended openly with the pilot's raw
  numbers before any 24-seed arm runs.

## Pre-registered bars

- **Bar C1 — work survives a menu:** ≥ 18/24 seeds in arm A realize
  ≥ 1 attributed recipe completion within H. (The recipe-reach chain
  bar held under a menu of ten.)
- **Bar C2 — praise steers the menu:** in arm B the praised recipe
  (R5) is the modal attributed completion for ≥ 14/24 seeds, **and**
  that count is at least twice arm A's R5-modal count. (Chance modal
  under a ten-item menu ≈ 2–3/24.)
- **Bar C3 — dither does not destroy output:** the median attributed
  completions per seed in arm A is ≥ half of arm C's median. (The
  menu may split the work; it must not shred it.)

Registered readings (evidence, not bars): per-seed choice
distribution (shares, modal recipe, entropy); classification counts —
rotation (≥ 3 recipes each ≥ 10% of the seed's completions),
monoculture (top recipe ≥ 80%), neither; per-step switch rate of the
argmax; `out_of_context`; and the drive-value trace of the chosen
terminal (does novelty decay actually drive the rotation?).

## Reversal condition

This topic assumes per-step argmax re-selection is a workable
selection mechanism. If **Bar C3 fails and the median per-step switch
rate exceeds 10%**, that premise is refuted as measured thrash:
commitment/hysteresis (a stickiness term on the active recipe)
becomes the named successor, and the shipped `RecipePolicy` selection
seam is the amendment site.

## Verdict

<Empty until graduation.>
