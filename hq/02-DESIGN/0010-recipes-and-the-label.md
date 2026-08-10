# 10 — Recipes and the praise label (graduated research, episodes 0077, 0080–0082)

**Status:** SHIPPED as feature 041 (v1.3.0); this document records the
functional design the measurements license.

## What was measured

Reach is taught: recipe memory (remembered demonstration sequences,
applauded endings marked by the label) + chained subgoal holds over the
event head's predicted positions carried 24/24 seeds to a goal the label
alone reached 0/24 times, with own chains held at bar and 20/24 provably
recipe-led (topic recipe-reach; episode 0076). The label itself is safe:
read only inside fired completions, no hangover at any dose (E3.1).

## The shipped design (Doc 0005 §4.5; surface in Doc 0008)

- `CompletionItchPolicy(label_index=…, label_beta=…)` — a fired
  completion counts `1 + β·clip(Δ̂[label], 0, 1)`; off by default,
  bit-exact when off.
- `RecipeMemory(pocket_index, label_index=None).add_demonstration(seq)`
  — terminal = max-label observation (label set) else last pocket gain;
  no gain → no recipe.
- `RecipePolicy(params, memory, kappa, progress_index, pocket_index,
  lambda_r, position_indices, position_scale, …)` — per directed step:
  select the most-valued ending (drive + β·label), point the
  nearest-step-plus-one subgoal, hold it via head-predicted positions;
  the itch works each station. Counters: `advance_events`,
  `out_of_context` (the parrot watch).
- Measured operating points of record: κ 0.25, λ_r 0.25, β 0.5. Recipes
  are caller-kept state in v1 (reconstructible from demonstrations).

## The twins, measured and bounded

The obsessive (applauded work eclipsing owned goals): real, bounded at
β = 0.5 (chains exactly at bar), dose-sensitive above. The parrot
(steps out of context): ~2% of steps at the measured point. Both ship
as counters, not hopes.

## Menu behavior (measured; topic recipe-choice, episode 0080)

With ten distinct recipes in memory the per-step selection argmax is
validated as shipped [V]:

- **Rotation by boredom** — with the label off, the drive's novelty
  decay turns the menu: 24/24 seeds spread completions over 5–7
  recipes, ~5% per-step switch rate, no thrash, no fixation; output
  matches or exceeds a single-recipe specialist in raw completions
  (the specialist still wins on its own product's depth).
- **Praise has a measured dial** (episode 0081) [V] — the dose
  curve is traced: **β = 0.02 nudges** (praised recipe modal 24/24
  at ~half the work, monoculture 0/24, chains 24/24 — nothing lost),
  **β = 0.5 commands** (share 1.00 ×24, obsessive twin at its known
  strength: chains 18/24, dwell ~63%). The cliff between preference
  and command sits at β ≈ 0.05–0.1, where the additive label crosses
  the drive's terminal-value band (0.06–0.15). A caller choosing β
  is choosing between a preference and an order; the cliff moves if
  a future drive's value scale moves.
- The `out_of_context` and `advance_events` counters are the
  designed watch here too; attribution of gains to the selected
  recipe is harness-side, not policy state.

## The economy limit (measured; topic value-economy, episode 0082)

Survival pressure alone does **not** re-price the menu [V]: under a
lean meter whose payments differ 40×, the choice distribution is
statistically unchanged from the flat control (nourishing share
0.382 vs 0.366; the registered no-repricing prediction confirmed at
24 seeds). Two structural facts for any caller:

- **Choice is priced by novelty and praise, never by survival.** The
  meter decides whether the life survives what it chose — not what
  it chooses.
- **Praise commands the hands, not the mouth**: the selection
  pointer obeys the label while the completion itch feeds the
  metabolism from whatever the pocket holds (a praise-commanded junk
  diet stayed alive 24/24 on side-chains). Diet cannot be forced
  through selection.

## Named successors

Recombination — composing recipe fragments into never-demonstrated
paths (true means-ends) — is its own research topic when licensed.
The **deficit→value coupling** — hunger reaching wanting — is the
economy's named missing layer **[O]**, motivated by episode 0082's
numbers; candidate shapes: the meter's deficit modulating the
drive's terminal valuation, or the deficit driving the label channel
("hunger praises food").
