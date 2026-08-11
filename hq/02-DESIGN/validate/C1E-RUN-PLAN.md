# C1E — the real life at 5×, pre-registered (2026-08-11, before launch)

The ladder's top rung ("yes, go with the ladder"; the road resumed:
"go for B2′ → c1e"): the measured stay/want/finish composition living
in the **real vanilla world** — full game rules, real physics, real
drops — at the calibrated multiplier **M\* = 5** (fast-real-bridge
B2′: primitives 20/20 at 5×, posture 5.19, the fixed geometry of
episode 0078). c1c asked whether crafting emerges unaided at 1× (no);
c1d asked whether the taught composition endures in the lab (yes,
75,359 chains); **c1e asks whether the taught composition lives in
reality at speed.**

## The life

- **World**: a fresh isolated vanilla 1.21.11 flat world (never
  c1c's, never the calibration litter), `/tick rate 100`, RCON. The
  harness stewards a **teaching grove** near spawn: oak columns
  rebuilt on the c1d regrowth rule (a dug column regrows after 2,000
  game ticks, by scheduled rcon setblock) — the world's renewal, one
  rule, recorded in every row.
- **Brain**: fresh seed 1, 33-dim (the C1 property body + the energy
  channel), `event_head_eta = 0.5` — taught **in the real world at
  1×** by the P0 protocol (45 wood-chain segments at the grove
  through the fixed bridge), then released.
- **Policy** (all shipped, zero ground truth): frames' drive +
  brain-side hold (Doc 0009, goal = the taught work position from
  the demonstrations) + `CompletionItchPolicy` (κ = 0.25, λ = 0.25).
- **The meter**: harness-side energy channel, G4's flat pay (+0.1
  per gain-tick), drain 0.0005 with the G4b taper (weaned by game
  tick 3,000-equivalent of its life) — the c1d childhood, in
  reality.
- **Pace**: `tick_ms = 50` (the B2′ posture law), ~20 brain-steps/s,
  ~5.2 game ticks per step.

## Execution

Segmented resume-chain exactly as c1d (snapshot to disk per segment,
crash-resumable; status rows to `c1e-status.jsonl`; the wrapper
guards double-launch). **Target 2,000,000 steps** (~28 wall-hours at
the measured pace) — ~10× c1c's *elected* life density at a tenth of
its wall time. Real-world honesty rows: bridge disconnects/rejoins,
server TPS spot-checks, grove-stewardship actions — all logged.

## Pre-registered readings (the c1d set, in reality)

- **R1 — endurance of election**: full chains per 200k-step decile.
- **R2 — hold drift**: dwell near the grove per decile.
- **R3 — head stability**: prediction-error EMA per segment.
- **R4 — the life**: survival, energy trajectory, the weaning window.
- **R5 — the miser watch**: roaming and work mix per decile.
- **R6 — reality's tax (new)**: dig-completion rate in the wild vs
  B2′'s 20/20; bridge/server incidents; any world event the lab
  never had (mobs, weather, drops lost).

## Stop rules (frozen)

1. **Death** — energy zero: stop, full report.
2. **Goal** — ≥ 2,000 full chains **and** ≥ 1,000,000 steps:
   graduation; stop, full report.
3. **Futility** — zero chains across 500,000 consecutive steps after
   childhood: stop, full report.
4. **Manual** — `c1e-STOP` file or the owner's word; graceful at the
   next segment boundary, resumable.
5. Otherwise: run to 2,000,000.

## Dashboard & watch

The c1d pattern: per-segment rows feed the tablet dashboard
(private artifact, updated at decile boundaries and on request); a
monitor watches MILESTONE / STOPPED / death / error lines and pushes
on anything actionable.

## Attempt 1 — death by rule 1, and amendment 1 (2026-08-11)

**The run**: teaching passed 45/45 (every stick craft asserted). The
life died at **life-tick 4250** — the exact zero-income death point
(the taper's cumulative drain reaches 1.0 at precisely 4250):
**not one pocket gain in the entire childhood** [measured]. Segment
row: 10,011 steps, 2 chains (both post-death), 38 logs / 48 sticks
at segment end, dwell 0.24, 14.8 steps/s, 1,163 instant dig aborts
in the bridge log.

**The post-mortem probe** (three arms against the still-live world,
raw rows in `c1e-attempt1/c1e-probe.json`) [measured]:

- Pinned pure dig hold: dug in **60 steps (3.11 s wall)**, 0 aborts.
- Wild posture (offset stand + yaw error): dug in 61 steps, 0
  aborts — **no posture penalty, no target-flap**.
- The tape's own shape (14 digs + 8 idles, repeated): dug only after
  3 cycles ≈ 60 dig-steps total.

**Diagnosis**: a dig's duration is set by the *client* at wall-clock
1× — ~3.0 s regardless of the world's `/tick rate`. The tape taught
a **14-step dig run**: 3.5 s at teaching pace (250 ms — enough), but
**0.7 s at life pace (50 ms) — under a quarter of what a dig needs**.
The taught skill was unexpressable at the pace it was released into;
the childhood earned nothing and the meter ran out. The 38 post-death
logs are the completion itch *extending* runs to ~60 held steps once
it locked onto the sensed mining-progress channel — the composition
can do the work; the tape's temporal shape couldn't. This is R6 —
reality's tax — delivered in segment 1.

**Amendment 1 — one temporal fabric** (before attempt 2, fresh world
and fresh brain): teaching moves into the life's own fabric (5×
world, 50 ms steps, same as release); the dig run becomes **70
consecutive held digs** (measured 60 + margin; the bridge releases a
hold on any non-dig command, idles included); the craft tail keeps
attempt 1's wall spacing (one op per 250 ms) as four idles after
each op. Meter, wean, stop rules, target, and readings all
unchanged.

**Second finding, same post-mortem — the drop flies away at 5×**
[measured]: the 106-step tape still failed teaching (0 stick crafts,
3/3 attempts). A watched dig showed the break completing but the
drop **far-scattering past pickup range** — resting up to 2.5 blocks
away — then despawning (60 s wall at 5×). Grid: at `/tick rate 20`
pickup while standing is **4/4**; at `/tick rate 100` it is **2/4**,
with lost drops resting at z 10.2–10.6, x 8.0–9.9. At 1× the drop
pops to the breaker's feet; at 5× it outruns the pickup box about
half the time — more of reality's tax.

**Amendment 1b — the tape teaches collection**: after the dig run,
the lesson walks into the drop zone and back (9 forward + 9 back,
~1.9 blocks — the probes' collect-walk); tape 22 → **124 steps**
(70 digs, 18 collect-walk, 35 spaced craft ops, 1 idle), piloted
green end-to-end (log by step 69, planks by 102, 4 sticks by 122).
Because a drop can still rest outside the collect lane (~1 in 3 of
the far-scatters), a lesson that fails its stick-craft assertion is
**repeated, up to 3 attempts** — the parent demonstrating again; a
failed attempt leaves no trace in the taught state. Teaching fails
hard if any lesson needs more than 3.

Runner mechanics, same change-set: the engine's episode length
follows the tape (the inherited config carried the old tape's 22 and
silently truncated every 124-step lesson to its first 22 digs —
caught before any brain was taught); life segments are 81 cycles
(10,044 steps), keeping the registered ~10k-step segment size.
