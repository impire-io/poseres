# recipe-choice — investigation journey

Topic opened 2026-08-10 (owner's call after the c1d read: "i think we
have to go for this. it is quite crucial"). Appends as it happens.

## 2026-08-10 — instrument gate: the ten tapes capture clean

`recipe_choice.py tapes` (session scratchpad): all ten demonstration
tapes yield their registered gains on fresh-world replay — the three
trees, the three wall columns, the pillar, planks, the sticks chain,
and the build-then-harvest place-loop. The position-gated judge fired
exactly once across all ten captures, on R5 (wall-center) — so
exactly one recipe carries the label, and the **shipped**
`RecipeMemory` extraction behaved as designed: R5's recipe truncates
at the applause (8 steps), every unlabeled recipe ends at its last
gain. R3's route mines a wall-north cobble on its way through the
wall (recorded: its capture legitimately contains two products).

Instrument notes, recorded before any run:

- **Episode length 26** (the measured protocol used 22): the longest
  tapes (R3, R10 at 22–23 actions) don't fit a 22-step teaching
  segment. The whole cohort — teaching and free runs alike — uses 26,
  and all three arms compare within this cohort only; no
  cross-cohort number is quoted against the 22-step gates.
- **Attribution alignment** is ±1 step (policy trace index vs view
  stream index).
- **Modal** = strict unique argmax; a tie means no modal seed —
  conservative against Bar C2.

Cohort (mc-graduates, 24 seeds) building: 45 wood segments + 2
interleaved passes over the ten tapes, judge silent except R5.

## 2026-08-10 — cohort built; pilot published before the arms

All 24 seeds built green — 65 teaching segments each, every
per-segment check passed (expected gains present; the judge fired
exactly once per R5 segment and never elsewhere).

**Pilot (seeds 1–8, arm A: menu of ten, β = 0), raw:** completions
per seed 117 / 139 / 147 / 157 / 174 / 187 / 247 / 274 — dense, so
H = 5,000 classifies without amendment. **Classification: rotation
8/8** (every seed spread completions over 5–7 recipes; entropy
2.08–2.46 bits; monoculture 0, thrash 0). Median per-step switch
rate 0.0496 — the argmax is sticky in practice: ~95% of consecutive
steps keep the same selection. Chains still complete under the menu
(7/8 seeds). Attribution health: 0 unattributed gain events across
all eight seeds; out-of-context (parrot watch) 7–91 steps of 5,018.

The mechanism showed itself in the registered value trace: at step 1
the unfamiliar cobble endings carry the highest drive values
(0.13–0.15 vs 0.06 for the taught tree), and as recipes get
practiced the terminal values compress toward equality (all ~0.10 by
mid-run) — the drive devalues the familiar and the argmax moves on.
Novelty decay is what rotates the menu `[measured, pilot scale]`.

One pilot observation to watch in the arms: R2 (tree B) is nearly
unchosen (0–4 completions per seed) while its twin R1 dominates —
proximity may shadow it. A reading, not a bar.

Arms next: A (menu β 0), B (menu β 0.5), C (single-recipe control),
24 seeds each, bars as registered.
