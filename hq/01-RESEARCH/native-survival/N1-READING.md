# Bar N1 — the meter is real (measured 2026-08-12)

**Verdict: MET.** Under the declared world config, a bot that works but
never eats empties its own food bar under activity, health follows once
the bar is empty, and starvation stops at the normal-difficulty floor.
The native meter bites; the arms may run.

## The declared world, as built

Vanilla 1.21.11 (the bridge's pin), superflat like C1, difficulty
**normal**, mob spawning off, melon patches at spawn plus at distance
(probe/provision.py — water-hydrated farmland, four age-7 stems per
patch, eight pre-grown melons). No harness meter anywhere: no drain,
pay, taper, stipend, or steward; after provisioning, nothing outside
the game touched the world during the reading. Two version facts,
recorded: 1.21.11 renamed the gamerules to snake_case (`spawn_mobs` is
this version's `doMobSpawning`), and `spawnRadius` left the rule set —
the default spawn scatter is accepted (pose is spawn-anchor-relative).

## The probe

`probe/n1_probe.py`: a scripted patrol (jump-forward sides, quarter
turns; digs whatever solid stands ahead), no brain, no meter, `use_held`
never issued. 6,036 ticks at the 250 ms posture (~25 min), 4,516 jump
commands, 0 digs (the patrol never lined up a melon), pocket 0
throughout. Rows in `probe/n1-rows.jsonl` (local, gitignored); the
published summary is `probe/n1-summary.json`.

## The measured curve

- **Saturation buffer**: the visible bar first moves at tick 1,280 —
  the hidden 5-point saturation absorbs the first ~20 exhaustion, the
  game's own rule.
- **Drain under activity**: from there, perfectly linear — one food
  point every ~213 ticks (~53 s of continuous jump work); the bar
  empties at tick 5,336 (19 points over 4,056 ticks).
- **Health follows**: first health loss at tick 5,351 — 15 ticks after
  the bar emptied, **at food 0**. The registration approximated this as
  "once food ≤ 6/20"; the game's real rule is starvation damage at 0
  (≤ 6 only disables sprint, which this body cannot do). The bar is
  judged on its intent — the meter bites — with the exact mechanism
  recorded here.
- **The floor**: health reaches 1/20 (half a heart) at tick 5,636 and
  holds there unchanged through a further 400-tick reading. Normal
  difficulty starves you to the brink and no further — a starving life
  is crippled, not erased, which is what makes N2's "never reaching
  starvation health-loss" a real bar and N3's ablation survivable
  enough to measure.

## Supplementary: the live mouth (instrument check, not a bar)

`probe/mouth_check.py`, run after the reading (bot tp'd to a melon —
world admin between readings, never during one): a real melon broke in
8 dig ticks and dropped **6 slices** (the game's own 3–7 roll); the
held slice read `edible = 1` on the live hand channel beside
`placeable = 0`; one `use_held` intention held for 7 ticks (~1.75 s)
consumed exactly one slice and the world paid **food 0 → 2** — the
starved N1 body ate by its own actuator. The whole instrument N2's
teaching relies on is proven on the real server.

## Arithmetic the arms inherit

One slice pays 2 food points ≈ 427 ticks of the probe's work intensity
(~1.8 min); a full bar plus saturation is ~5,500 such ticks (~23 min).
Real activity mixes drain slower (walking is exhaustion-free in this
version), so these are worst-case-work numbers, not a prescription.
