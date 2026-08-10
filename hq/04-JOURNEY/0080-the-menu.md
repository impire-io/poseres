# Episode 0080 — The menu: boredom rotates it, praise commands it (2026-08-10)

The owner's question after the c1d read: "what if you have 10
different chains and you can pick one over the other?" — and his
call: "we have to go for this. it is quite crucial." Everything
measured about recipes had used a menu of one; the shipped
`RecipePolicy` re-runs its selection argmax every step, and that
mechanism's two faces had never been separated: novelty decay
predicts *rotation*, per-step re-selection predicts *thrash*. The
recipe-choice topic froze three bars before any run, an instrument
gate proved ten distinct teachable recipes in the unchanged lab
world (three trees, three wall columns, the pillar, planks, the
sticks chain, a build-then-harvest place-loop), a fresh 24-seed
cohort was taught all ten with a position-gated judge applauding
exactly one (wall-center cobble), and the pilot was published before
the arms.

All three bars passed at 24-seed power [measured]:

- **Rotation, not thrash.** With the label off, 24/24 seeds spread
  completions over 5–7 recipes (monoculture 0, thrash 0); the
  argmax switched on only ~5% of steps; chains still landed 23/24.
  The registered value trace caught the mechanism directly: novel
  endings start 2–3× more valuable than the familiar tree, and
  practice compresses everything toward equality — the drive gets
  bored, so the menu turns. The topic's reversal condition (thrash)
  closed unfired.
- **Praise steers — as a command, not a nudge.** At the measured
  β\* = 0.5 the praised recipe became the modal completion for
  24/24 seeds (0/24 with the label off) with selection share 1.00
  everywhere: total monoculture. The label's +0.5 sits 3–8× above
  the drive's entire value scale (0.06–0.15) — that is *why* it
  saturates [mechanism-argument]. The obsessive twin arrived at
  exactly recipe-reach's measured strength: chains 18/24, dwell
  62.6% — the same 18/24 on a different cohort and world protocol,
  an independent reproduction.
- **Choice is not a tax.** The menu arm out-counted the
  single-recipe specialist outright (median 170.5 vs 143.5
  completions) — the feared dither cost never materialized. Honest
  caveat: counts, not value — the specialist converts narrow
  attention into 73% more of the chain product.

Nothing was refuted; one prediction was sharpened: steering at the
shipped operating dose is binary in effect. What it opens (named,
none run): the β dose curve between 0 and 0.5 (is there a nudge
regime?), the shadowed-twin reading (tree B nearly unchosen beside
tree A), and the value-weighted economy — the meter with unequal
yields, where recipe choice becomes survival-priced. That last is
the owner's "survival of the fittest" instinct given a registrable
shape, and the natural rung between this gate and recombination.

Instrument honesty: 26-step episodes (the longest tapes outgrow the
measured 22-step protocol; all arms compare within-cohort only),
attribution ±1 step with 0 unattributed gains across all 96 runs,
modal = strict unique argmax.

Reversal condition: none — records a completed measurement. The
menu's behavior beyond ten recipes, under the meter, or at
intermediate β is unmeasured evidence space; a future arm showing
per-step re-selection thrashing (switch rate > 10% with output
below half the specialist's) reopens the selection mechanism.

Trail: Doc 0010 (menu behavior section added);
`hq/01-RESEARCH/recipe-choice/` (folder retired at graduation, full
trail in git history); runner `recipe_choice.py` + row files in the
session scratchpad; commits 145c7c8 (registration), 4cadff3
(instrument gate), 91cb818 (pilot), c7e2435 (verdict).
