# 0013 — The palate: worth eaten into existence, read at the distance

**Status:** design (graduated from research topic the-aim, 2026-08-15,
[episode 0100](../04-JOURNEY/0100-the-aim.md)). Instrument-grade in the
live bridge today, opt-in on every surface; ships into the default
body only on promotion (a spec-kit feature decision). Every rule below
carries its measurement. The topic's steering claim was REFUTED — this
document records what stands: the palate as body-seam substrate and
the worth channel as a sense. Aim-as-salience and aim-as-lookup are
recorded dead ends (episode 0100); do not rebuild them from here.

## What it is

The palate extends episode 0089's tongue (worth learned from felt
meals, no decree) to the live body: a name → price book held at the
body seam (the bridge), never sensed as names — the senses expose
prices keyed by appearance only.

## The rules (functional, speckit-ready)

1. **One pay, the metabolic truth.** A meal is food RISING during a
   held use. Its pay is Δfood/20 (the meter's own scale). rcon doses
   land outside held uses and pay nothing (measured: the W-guard).
2. **The EMA.** price ← price + α·(pay − price), α = 0.25 (0089's
   constant). Measured: four chained slices price the chain at
   0.1·(1−0.75⁴) = 0.068 exactly.
3. **The trace.** The meal pays every name the chain touched within
   600 game ticks: dig completions, drop pickups, the held item.
   Necessary because the world's naming separates the appearance dug
   (`melon`) from the meal eaten (`melon_slice`) — a mouth-only
   tongue can never light the glance. Cost, accepted: coincidental
   contacts get paid (superstition) and wash out over meals.
4. **Relative worth at the lookup.** Every exposed price is
   price/best-known-price — scale-free (the budget-arb rule: never a
   magic constant). A naive book reads 0 everywhere.
5. **Body state.** The book persists across bridge restarts
   (`PALATE_FILE`) and is form-independent (measured: written by one
   form's process, read correctly by the other's). The runner decides
   when a life is born naive; taught tongues are part of taught body
   state and reset with the brain.
6. **The worth channel** (`AIM=worth`): one relative price per glance
   sector plus the sensed drop's, width 9, appended LAST (obs 82/86);
   plain, ungained by hunger (measured identical hungry/sated).
   `AIM_ABLATE=1` keeps the palate learning but returns naive prices
   at the lookup — the decoupling ablation by construction.
7. **Byte-discipline.** AIM unset = zero new behavior anywhere; the
   worth form widens the handshake so mismatched stacks fail loud.

## Wire and code homes

Bridge: `examples/minecraft/bridge/bridge.js` (book, trace, meal
detection, both lookups). Contract: `specs/027-minecraft-body/
contracts/minecraft-adapter.md`, "The aim" section. Anatomy:
`c1_anatomy(aim="worth")`. Proof: A1-READING.md (11/11, git history
of `hq/01-RESEARCH/the-aim/`).

## What builds on it

The native-survival re-runs use the worth body and taught tongue as
substrate; the-last-crack's commitment mechanism (design
[0014](0014-the-last-crack.md)) is what lets the chains it prices
actually finish. Named successor (unregistered): the market —
drifting prices, the EMA's stationarity assumption under test.
