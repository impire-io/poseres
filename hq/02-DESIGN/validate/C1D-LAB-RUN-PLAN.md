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
2. **Goal met (the owner's early-stop)** — ≥ 2,000 full chains **and ≥
   25M steps**: graduation; stop, full report. *(Amended openly
   2026-08-09 before the rule fired, raw numbers recorded: segment 1
   measured 131 chains per 50k steps under regrowth — the bare count
   would have fired at ~1.5% of target with zero endurance readings,
   the run's registered purpose. The chain bar was dosed against
   pre-regrowth scarcity; the amendment gates graduation on the
   deciles existing.)*
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

## Ops journal (honesty rows, the c1c precedent)

- **2026-08-10 ~02:00 — the slow suffocation, diagnosed and fixed.** Pace
  declined 501 → 57 steps/s over 40 segments. Two false leads recorded
  (thermal throttling; brain growth — the population was 18 frames,
  0.3 MB), then the profile: the segment config inherited
  `snapshot_every_n_cycles = 1` from the teaching protocol, so the
  engine took 2,273 snapshots per segment into the in-memory store, each
  bloated by the agency's unbounded value logs (2M steps of history) —
  measured 13 GB RSS. Fix: one snapshot per segment + the agency logs
  join the between-segment accumulator trim (same stats-window caveat
  already recorded above). Pace after: **753 steps/s at 248 MB** — above
  segment 1, which had been paying the same hidden tax.
- **Compounding incident, resolved:** a case-sensitive kill pattern left
  the old leaked process alive beside its replacement — two writers on
  one snapshot for ~25 minutes. The status lineage was verified
  monotone and consistent with the surviving snapshot (41 rows kept,
  row 41 ≡ snapshot cycles 93,238); no readings lost. The wrapper now
  guards against double-launch, and the runner recycles its process
  every 20 segments as defense in depth.
