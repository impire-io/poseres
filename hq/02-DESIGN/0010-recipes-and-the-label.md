# 10 — Recipes and the praise label (graduated research, episodes 0077, 0080–0091)

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

## The deficit→value coupling (shipped as feature 042; episodes 0083–0084)

The "body as the first teacher" shape was built and measured on
shipped seams, no oracle: label channel = the felt meal
(`clip(pay/0.15, 0, 1)`), hungry demonstrations give each recipe its
own taste through the unchanged extraction, and the coupling is
`β_eff = κ_h·(1 − energy)` at the label seam (κ_h = 0.1, sized from
the episode-0081 dial).

- **The dial works** [measured]: food share monotone in deficit
  (0.431 sated → 0.741 starving) while the uncoupled brain's crisis
  diet equals its baseline (hunger alone changes nothing); survival
  20/24 vs 16/24 (+4 lives); sated rotation and chains intact.
- **Timing beats volume** [measured]: an ungated constant taste
  (β 0.02) reaches a higher *average* food share yet dies as often
  as no coupling at all. State-dependence is the load-bearing part.
- **Shipped as feature 042 (v1.4.0) [V]** — promoted by the
  coupling-promotion topic on its timing-primary bars (the
  aggregate-share bar of episode 0083 remains failed and mis-targeted
  on record): `CompletionItchPolicy(deficit_index=…, deficit_kappa=…)`,
  keyword-only, off by default bit-exact, closure row-for-row against
  both archived instrument arms (Bar P1). Measured operating point of
  record: κ_d = 0.1 against a [0, 1] meter.

## Generality (measured; topic second-body, episode 0084)

The whole stack of this document is **embodiment-general as
measured** [V]: the identical shipped classes mounted on a second,
structurally disjoint body (absolute moves, no facing, 7 actions, 16
channels, different indices/scales, no bridge — the engine's world
surface directly) reproduce election 24/24, taught order 24/24, and
the emergency appetite at ceiling (hungry-bin share 0.996 vs 0.780;
deaths 0/24 coupled vs 16/24 uncoupled vs 24/24 drive-alone). All
body knowledge enters through constructor indices and teaching
tapes; porting cost is one small anatomy plus tapes. Callers MUST
use the general vocabulary (acquisition channel, felt channel,
meter) — the C1 names (pocket, praise, hunger) are one body's
dressing.

## Recombination (measured; topic recombination, episode 0086)

One-seam composition is **emergent from the shipped stack** [V]: two
fragments demonstrated separately (travel-and-collect; a
handed-ingredient refine at a distinct station), the whole never
shown, compose 24/24 at scale (median 387 first-leg acquisitions,
hundreds of composed products per life; floor 1/24) with no planner
— rotation moves the bot, the pocket carries state across the seam,
and the terminal's attraction plus the itch finish the second leg
when the precondition is met. **Depth bound extended (episode
0087)** [V]: the ladder holds through **four legs** — decay 24/24 →
22 → 21 → 20 across a four-material process chain, roughly one seed
per rung, no cliff; the splice/imagination layer stays unlicensed
until a real embodiment finds the boundary (scarce inputs, longer
legs, deeper chains).

**Conversion visibility (episode 0088)** [V]: the 0086 blindness
closed as a *wiring choice*. `pocket_index` is **which sense defines
wealth**, not "which channel counts items": count-keyed, the trade
lesson cannot even be extracted and 0/24 ever hold a gem;
worth-keyed (the anatomy publishes Σ count·price as a sensed
channel — the felt-meal precedent), the identical classes trade
24/24 and compose the count-losing journey. Zero source changes.
Callers MUST choose the wealth sense deliberately (Doc 0011's dial
note).

**Learned worth (episode 0089)** [V]: the worth sense need not be
published — a body-side price book (per-item EMA of felt pay,
α = 0.25, born all-zero, carried across lessons as body state)
converges to the metabolic truth on taught meals alone and carries
the full trade economy (24/24, trade-led 24/24, no decree anywhere).
Demonstrations bootstrap the palate as they bootstrap the head. The
EMA assumes stationary pay; markets with drifting prices are the
named successor's territory.

**Moving senses (episode 0090)** [measured, split]: senses that
change outside the brain's control are **livable** (24/24 trade
under a drifting rate) and **paceable** (21/24 sustain trading when
every trade worsens the price — the world learning the brain back,
handled), and the worth machinery leans toward bargains with no
timing machinery (median rate 7 vs time-average 8) — but it **does
not refuse ruin** (25.2% of trades at worth-destroying rates vs the
10% bar). Sensing motion is not timing it: the senses-first rule's
first measured boundary.

**The richer predictor, first attempt (episode 0091)** [measured,
FAIL with a precise diagnosis]: the quadratic head (same NLMS, 153
pairwise-product features, replay-pretrained on the witnessed
lessons) does **not** fix refusal in aggregate (27.8% ruinous vs the
10% bar) — but six seeds achieve *perfect* refusal and four invert,
identical worlds and features: the representation provably carries
the interaction; **per-seed online convergence is the bottleneck**
(sharpness 0.874 < 0.90 — arbitration not implicated). The 0090
license stands unexpended.

## Named successors

**The richer predictor, next regime** — the 0090 license with 0091's
constraint: candidates are consolidation (the Doc 0004 offline loop
replaying witnessed trades), feature normalization + lower head η,
or targeted low-order context terms; its gate keeps 0091's bars and
sharpness instrument. The boundary hunt (depth 5+, scarce inputs)
when an embodiment demands it. A drive-side deficit coupling remains
the named alternative if the label seam is ever refuted.
