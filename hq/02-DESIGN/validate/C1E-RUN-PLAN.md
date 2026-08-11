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
