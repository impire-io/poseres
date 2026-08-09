# Fast real bridge — at what multiplier does the real game stay honest?

**State:** active
**Started:** 2026-08-09

## Abstract

Rung 2 of the owner's ladder ("start building rung 2"): c1e needs the
*full* Minecraft world — all rules, terrain, multiplayer observation — at
accelerated time. Vanilla ≥ 1.20.3 ships `/tick rate` (1–10,000 TPS)
natively, and our compose stack already pins vanilla 1.21.11, so no fork
is needed; the pacing seam is ours. The bridge sleeps `tick_ms` wall-clock
per brain-step and `tick_ms` is already a parameter: at server multiplier
M, `tick_ms = 250/M` restores the exact c1c posture of ~5 game ticks per
brain-step. What must be *measured* before c1e may register: whether the
server sustains M with a bot attached, whether the bot's primitives (dig,
craft) stay intact at speed, and whether the posture actually holds. One
known distortion is registered, not hidden: the bot's physics are
wall-clock, so relative to world dynamics (mobs, crops, daylight) the bot
slows by 1/M as M rises — world-relative fidelity is part of what the
bars bound.

## The question

What is the largest multiplier M\* ∈ {2, 5, 10} at which the real vanilla
world, our bridge, and the bot's primitives all hold — licensing c1e at
M\*?

## Pre-registered bars

Protocol: local fresh flat world (vanilla 1.21.11, RCON, isolated volume,
never c1c's data), the bridge patched only to report `bot.time.age`
(server game-tick clock) in every view; a controlled micro-arena built by
server console (oak column beside the bot, rebuilt per rep); per M ∈
{1 (reference), 2, 5, 10}: `/tick rate 20·M`, `tick_ms = 250/M`, five
reps of dig-the-log + craft-planks, ≥ 3 wall-minutes of stepping.

- **B1 — the server sustains it:** measured game-TPS (age progression ÷
  wall time) ≥ 90% of nominal 20·M, with the bot attached and working.
- **B2 — primitives intact:** 5/5 oak-log digs complete into inventory
  AND 5/5 log→planks crafts succeed, at every passing M.
- **B3 — the posture holds:** mean game-ticks per brain-step within
  5 ± 1 at every passing M.

**M\*** = the largest M passing all three; c1e registers at M\* (its own
run plan). All bars measured per M independently — a FAIL at 10 with a
PASS at 5 is a result, not a retry.

## Reversal condition

If even M = 2 fails B2/B3 with B1 green (server fine, bot broken), the
wall-clock-physics distortion is worse than the pacing story assumes —
the fork question (roadmap C3, one-page spec first) reopens as the
honest road to fast fidelity, per the ladder conversation.

## Verdict (partial — B1/B3 decided, B2 re-registration required)

**[measured, 2026-08-09 night, two full gate runs + instrumented probes]**

- **B1 — the server sustains it: PASS at every M.** Measured 19.9 / 40.0 /
  100.0 / 199.9-200.1 TPS against nominals 20/40/100/200, bot attached and
  working; per-tick averages ~1.6 ms against a 10 ms budget at M = 5 — the
  ceiling was not reached at 10×.
- **B3 — the posture holds: PASS at every M.** 5.02–5.29 game ticks per
  brain-step across all speeds; the tick_ms = 250/M pacing law is real.
- **B2 — primitives: the REFERENCE fails its own bar.** Digs completed
  3/5, 4/5, 2/5, 4/5 (pose-stable run) across M ∈ {1, 2, 5, 10} — **no
  speed trend; M = 1 itself misses 5/5**. Every completed dig also
  crafted (5/5 conversion): the craft pipeline is solid; the flake is
  dig completion. Bridge logs attribute it: mineflayer digs aborting
  mid-break ("Digging aborted" after 26–800 ms) — a 1×-native bridge
  behavior c1c lived with unmeasured (its 449 digs never needed
  per-attempt reliability). The bar as registered conflated
  bridge-native flakiness with speed effects and is **unmeasurable as
  written**; raw numbers recorded here per the amendment protocol.
- Instrument findings recorded on the way (all landed as fixes):
  the bridge died on a vanished client's EPIPE (fixed, committed);
  `rcon-cli` swallows negative coordinates as flags (`--` required);
  MC rotation 0 = mineflayer yaw π (the two conventions differ 180°);
  a collect-walk displaces the bot permanently at high M (wall-clock
  physics — the registered distortion, first measured in practice:
  17 brain-steps to cross a block at 10× vs 4 at 1×).

**What stands `[measured]`:** the time machine itself is real — vanilla
1.21.11 runs 10× with exact throughput and intact pacing. **What blocks
c1e** `[judgment]`: not speed — dig reliability at any speed. Successor
bars (a re-registration, not a quiet retry): B2′ as a *relative* bar
(success rate at M within noise of the 1× reference, n ≥ 20 reps per
arm) once the bridge's dig robustness question (its own small fix-and-
gate: why mineflayer aborts mid-break, likely look/movement validation)
is answered. Both are named work, neither started.
