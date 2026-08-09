# 10 — Recipes and the praise label (graduated research, episode 0077)

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

## Named successor

Recombination — composing recipe fragments into never-demonstrated
paths (true means-ends) — is its own research topic when licensed.
