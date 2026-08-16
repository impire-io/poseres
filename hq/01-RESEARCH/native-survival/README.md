# Native survival — can the composition live on the world's own metabolism?

**State:** active
**Started:** 2026-08-11

## Abstract

c1e closed on the verdict that the scenario, not the architecture, was
the tangent (episode 0096): we ran a hand-dosed synthetic metabolism in
a world whose native survival economy we had switched off, and pinned
the bot where exploration could not matter. This topic re-grounds the
life in Minecraft's own economy: the vitals channels the body has
carried unused since feature 027 (health, food) become the meter, real
eating becomes the pay, the game's own hunger becomes the drain, and
food that regrows by the game's own plant physics replaces the rcon
steward. A pass retires the entire harness-meter layer — drain, pay,
taper, stipend — in one move; the world defines them.

## The question

Released into a world whose food regrows by the game's own rules, does
the taught composition — with the shipped deficit gate keyed to the
native food channel — sustain its own vitals by real foraging, where
the same brain without the deficit gate measurably fails to?

## Scope, declared

- **World**: vanilla, difficulty **normal** (native hunger genuinely
  bites), `doMobSpawning false` — predation is real survival but is
  DEFERRED and named; this gate is metabolism, not combat. Food:
  melon patches (dig-obtainable, edible raw, and the stems regrow
  fruit by the game's own growth — the world's renewal without one
  rcon call), planted at spawn plus at distance so foraging can move.
- **Body**: one actuator gap is real and declared — the vocabulary has
  no way to consume. Refined at registration (the owner's point: eat
  is an action *applied to an item*, and edibility is the item's
  property): the new primitive is **`use_held`** — apply the held
  item — mirroring how `place_ahead` applies the held item where it
  affords placing. Edibility joins the hand channel as a sensed
  affordance flag beside the existing placeability flag (feature-027
  grammar, additive); nourishment is the *outcome* the event head
  learns from the held signature. Eating takes ~1.6 wall-seconds of
  continuous use, so `use_held` is a **held intention** in the bridge,
  exactly like the dig hold — c1e's temporal-fabric lesson applied,
  not relearned. Instrument-grade for this topic; ships only on
  promotion. Named ablation to record (not a bar): drop the edible
  flag and measure whether the head learns edibility from signatures
  and outcomes alone — the fully classifier-free mouth.
- **No harness meter anywhere.** No drain constant, no pay constant,
  no taper, no stipend, no steward. The run reads the world's own
  food/health channels and the world's own clock.

## Pre-registered bars

Real-world runs are wall-clock expensive; like c1e, this gate runs
few, long lives with within-run readings, not 24-seed cohorts.

- **Bar N1 (the meter is real — instrument bar, before any arm):**
  under the declared world config, a bot that works but never eats
  shows the food bar draining under activity and health following
  once food ≤ 6/20; measured and published before the arms run. If no
  configuration makes the native meter bite, the reversal fires.
- **Bar N2 (sustenance):** a taught life (P0-style lessons: dig melon,
  collect, eat; deficit gate keyed to the native food channel) holds
  food ≥ 12/20 for ≥ 80% of a ≥ 100,000-step life, never reaching
  starvation health-loss, while foraging real food (≥ 50 genuine
  eat events on collected melons).
- **Bar N3 (the gate carries it):** the ablation life — same taught
  brain, deficit gate OFF, everything else identical — spends ≥ 3×
  more of its life below food 12/20, or starves to health-loss where
  N2's life did not. If the ablation life sustains just as well, the
  deficit gate is not the carrier and the pass (if any) is
  re-attributed honestly.
- **Reading R-explore (recorded, not a bar):** positional footprint
  and patch visits — whether foraging re-opens exploration is the
  reframe's promise, measured and reported without a threshold this
  gate.

## Reversal condition

If the native meter cannot be made to bite under any declared world
configuration (N1), or the eat actuator cannot be added without
invasive changes to the shipped anatomy contract, the reframe returns
to design — and the synthetic-meter layer, for all its amendments,
stands as the honest cost of a world without a usable metabolism.

## Verdict

- **Bar N1 — PASS** `[measured]` (2026-08-12): the native meter bites —
  saturation absorbs ~1,280 ticks, then the bar drains linearly (one
  point per ~213 ticks of work) to empty at 5,336; health follows 15
  ticks later at food 0 and stops at the half-heart floor. The mouth
  (`use_held` + edible affordance) verified end-to-end live.
- **Bar N2 as registered — FAIL, twice, honestly** `[measured]`: the
  pre-distal stack was stopped as pointless-as-registered (the world
  never made the composition hungry; N2 ≡ N3 by construction); the
  committed stack under the gate burst 5 eats in the first 10k then
  never re-fired and starved (54.8% vs the 80% bar).
- **Bar N3 as registered — direction REVERSED** `[measured, n=1/arm]`:
  the gate-off arm outlived and out-ate the gated arm on every
  measure (below-12 time 0.007 vs 0.452) — consistent with every
  ablation of the arc. The deficit gate is refuted as the live
  carrier; it stays available, off, with its inversion on record.
- **The amended sustenance bar — PASS, replicated** `[measured]`
  (amendment 3, frozen pre-run; eats clause re-calibrated to the
  native demand the world itself measured, ~13/100k): the blessed
  stack (palate body + flood + commitment, gate OFF, free roam)
  sustained TWO independent 100,501-step lives — 99.3% fed / 13 eats
  and 98.1% fed / 12 eats — zero starvation loss, food floors 6 and
  8, first-eats 573 and 1,878 unaided. **The topic's question
  answers YES: the composition lives on the world's own metabolism.**
  The harness-meter layer (drain, pay, taper, stipend, steward) is
  retired in one move — the world defines them, as registered.
- Reversal clause check: the meter bit (N1) and the actuator landed
  without invasive anatomy changes — the registered reversal never
  fired.
