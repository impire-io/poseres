# Episode 0078 — The mirrored map: sixteen days of mining the wrong block (2026-08-09, midnight)

Rung 2's "flaky hands" (episode 0077's open blocker) fell to a delegated
instrumented diagnosis, and the root cause rewrites how a chapter of the
record must be read. `aheadColumn()` — the bridge's definition of "the
block in front of you", feeding the blocks channel, `dig_ahead`, and
`place_ahead` — had been wrong since feature 027 `[measured]`:
mineflayer's yaw is π − notchian yaw (its own physics walks along
(−sin, −cos)) but the bridge computed +cos, mirroring z and naming the
block *behind* a z-facing body; `Math.round` shifted it another half
block onto a diagonal neighbour whose identity flips whenever a
coordinate fraction crosses .5. Every "Digging aborted" in the
calibration was the bridge releasing its own dig when a 12 cm coast
renamed "ahead" 53 ms into a 3,000 ms break; the server never refused
one. The missing pickups were drops stranded off the walking axis.

**Why nobody noticed for sixteen days:** mineflayer's 5.1-block dig
reach silently honoured the mis-named column — **c1c's 449 completed
digs were the body quietly mining its diagonal-rear neighbour.** The
c1c record stands as measured, but its sensed world was mirrored; c1e
registers on the fixed geometry. The lab world is unaffected — its
locomotion and `_ahead` share one formula, so every gate and the
running c1d stand `[measured]`.

**The fix (f972181, probed clean):** floor(−sin, −cos) plus the held
dig intention outliving momentary re-aims. Break and collect counted
separately against server ground truth: stable 20/20 + 20/20 (was
20/20 + 14/20), drift 10/10 + 10/10 (was 5/10 + 3/10), tick rate 100
10/10 + 10/10 — zero aborts anywhere post-fix `[measured]`. What
remains of rung 2 is a formality: the B2′ relative-bar grid on the
fixed geometry with the diagnosis's four probe corrections (wall-time
dig holds, per-rep drop cleanup among them); the 5× probe already runs
clean.

What it teaches, again: the instrument is part of the claim. Twice
today a "brain" question (blurry itch, flaky hands) resolved into an
instrument truth (banker's rounding, a mirrored map) — the
pre-registered reference arm is what caught both.

Reversal condition: none — records a completed diagnosis and fix; the
fast-real-bridge topic's M\* question remains open until B2′ runs.

Trail: fix f972181; topic `hq/01-RESEARCH/fast-real-bridge/`
(diagnosis recorded 0c020a3); diagnosis artifacts
`scratchpad/bridgefix/` (fix.diff, probes, legacy repro — session
scratchpad, arc convention); episodes [0077](0077-the-recipe-ships.md),
[0043](0043-the-brain-moves-into-minecraft.md) (feature 027, where the
formula was born).
