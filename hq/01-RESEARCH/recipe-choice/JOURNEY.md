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

## 2026-08-10 — the arms: all three bars PASS, and praise is a cliff

72 runs (24 seeds × 3 arms), 570 s. Raw:

- **Arm A (menu, β 0):** 24/24 seeds complete (Bar C1 PASS, bar 18);
  **rotation 24/24** — monoculture 0, thrash 0; median switch rate
  0.0495; chains 23/24; median completions 170.5. Product mix across
  the arm: 2,232 cobble / 542 logs / 1,482 planks / 1,030 sticks —
  a genuinely mixed economy; dwell median 89.1% (the menu tours).
  R5 (the praised station, label ignored at β 0) was modal for
  0/24 seeds — median 5 completions.
- **Arm B (menu, β 0.5):** the praised recipe is modal **24/24**
  (Bar C2 PASS vs 0/24 in A — maximal separation), and it is not a
  nudge: **selection monoculture 24/24** — share 1.00 for every
  seed (min = median = max). Cobble 3,447 (+54% over A), logs 391
  (−28%), dwell median falls to 62.62%, chains **18/24** — the
  obsessive twin at exactly recipe-reach's measured R2 number,
  independently reproduced on a different cohort and world protocol.
  Median completions 229 (cobble digs are 3-tick).
- **Arm C (single R9):** median completions 143.5, chains 23/24,
  dwell 99.18%, sticks 1,783 — the specialist out-produces both arms
  on the chain product by ~73% over A (1,030).
- **Bar C3 PASS, inverted from the fear:** menu median 170.5 ≥
  half of 143.5 — in fact the menu *out-counts* the specialist
  outright. Caveat recorded: completions are counted, not
  value-weighted; cobble (3-tick) is cheaper than a log (12-tick),
  and arm C converts its narrower attention into 73% more sticks.

Mechanism notes `[measured]`: novelty decay rotates the menu (the
value-trace compression, pilot section); the β = 0.5 label (+0.5 on
the terminal) sits 3–8× above the drive's whole value scale
(0.06–0.15 in the traces), which is *why* steering saturates into
monoculture at the measured operating point — praise at this dose is
a command, not a preference `[mechanism-argument]`. Successor
readings named, none run: the β dose curve between 0 and 0.5 (is
there a nudge regime?); R2's shadowing by its nearby twin (0–4
completions beside R1 everywhere); a value-weighted economy (the
meter with unequal yields) as the next rung toward survival-priced
choice.
