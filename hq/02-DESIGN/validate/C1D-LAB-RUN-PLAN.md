# C1D-LAB — the provisioned life, pre-registered (2026-08-09, before launch)

The first rung of the owner's ladder ("yes, go with the ladder. include the
meter"): the full brain-side composition living long in the deterministic
lab world at maximum speed, while the tick-synchronized real-Minecraft
bridge (rung 2, its own calibration gate) is built in parallel. c1c asked
whether crafting emerges unaided in a real game at 1×; c1d-lab asks whether
the *measured* stay/want/finish life **endures** — 10× c1c's lived
experience in a weekend of wall-clock.

## The life

- **Brain**: the G4 meter-cohort graduate, seed 1 (33-dim, event head
  trained through 45 demonstrations, `event_head_eta = 0.5`). One brain,
  one life, continuous world across the whole run (world state persists in
  every snapshot; no resets after boot).
- **Policy** (all shipped seams, zero ground truth): frames' drive +
  head-derived hold (Doc 0009 form, goal = the taught work position) +
  `CompletionItchPolicy` itch at κ = 0.25, λ = 0.25.
- **The meter, with the owner's tapered childhood** (G4b's measured dose):
  drain 0.0005/tick scaled by clip((t − 1500)/1500, 0, 1) — one childhood,
  at the start of the life only; +0.1 per pocket-gain tick; death at zero.
- **World renewal** (new rule, required for a multi-million-step life in a
  three-tree world): a dug column regrows 2,000 ticks after it was dug
  (wood and mineral alike; placed blocks untouched). One rule, applied by
  the harness world wrapper, recorded in every row.

## Execution

Segmented resume-chain: ~50,000-step segments (2,273 cycles), snapshot to
disk at every boundary (crash-resumable), per-segment rows appended to
`c1d-status.jsonl`. Engine telemetry accumulators are trimmed to a recent
window between segments (memory/snapshot hygiene at 50M-step scale; the
readings below come from the per-segment rows, not the engine summary —
recorded openly). Target **50,000,000 steps** (~10× c1c's 5.7M) at the
lab world's measured ~500–700 steps/s ≈ one weekend.

## Pre-registered readings

- **R1 — endurance of election**: full chains per 5M-step decile; the
  reading is the decile trajectory (does election persist, decay, or
  grow?).
- **R2 — hold drift** (episode 0074's reversal watch): dwell per decile;
  drift off the work position after long homeostasis reopens
  brain-side-hold as a memory question.
- **R3 — head stability at horizon**: the policy's progress-prediction
  error EMA and the head's update count per segment; NLMS wander at 50M
  steps is this run's novel exposure.
- **R4 — the life itself**: survival (death tick if any), energy
  trajectory, the weaning window's behavior.
- **R5 — the miser watch**: unique positions and work mix per decile
  under permanent stakes.

## Stop rules (frozen)

1. **Death** — energy hits zero: the life ended; stop, full report.
2. **Goal met (the owner's early-stop)** — ≥ 2,000 full chains before
   target: graduation; stop, full report.
3. **Futility** — zero chains across any consecutive 10M steps after
   childhood: stop, full report.
4. **Manual** — the stop file (`c1d-STOP`) or the owner's word to the
   session; graceful at the next segment boundary, snapshot kept,
   resumable by design.
5. Otherwise: run to 50M.

## Dashboard & watch

Per-segment rows feed a tablet-viewable status page (redeployed from the
live JSONL; private artifact); a monitor watches for milestone / death /
goal / stop lines and pushes a notification when one lands. Rung 2
(registered intent, own gate before any run): the tick-synchronized
transport + mineflayer-at-speed calibration against vanilla 1.21.11's
`/tick rate`, then c1e in the full game at the measured multiplier.
