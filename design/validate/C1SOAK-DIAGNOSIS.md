# C1-readiness soak — the deferred lifetime questions, answered before the weeks are spent

Date: 2026-07-19. Question under test: ROADMAP names C1 (a multi-week
continuously-learning deployment) as the front, and two recorded
deferrals sit directly under it. LONGEVITY-DIAGNOSIS (ch. 13–14) found
weight-norm runaway at *scale* over ~2400–4800 episodes and shipped
`weight_norm_cap` as a scale default, leaving open "whether
reference-scale long lifetimes eventually need the cap too" — a
multi-week run is that lifetime, ~20–40× the longest validated runs.
And chapter 21 recorded that the reference world drifts and saturates
when run unbroken (an instrument property of the world, not the
brain). This arc pays for those answers with hours of compute instead
of weeks of wall-clock: an accelerated soak at the C1 order of steps,
reading the brain-health invariants that do not depend on the world's
drift.

## The design under test (frozen here, before any run)

- **Length**: `n_cycles = 2080` → (25 + 2080·6)·40 = **500,200 steps**
  per run. C1 arithmetic: three weeks at the 3–30 s/action cooldown
  band is ~0.06–0.6M actions; the soak sits in the upper middle.
- **Arms (2 × 2, reference defaults otherwise)**:
  `episode_mode` ∈ {episodic (control), continuous (the C1 mode)} ×
  `weight_norm_cap` ∈ {0.0 (reference default), 1.2 (the recorded
  scale value — the §8.8 effective form is scale-free, so the same
  factor applies)}. Drive: competence 1.0, `policy_mode="curiosity"`
  (Doc 05 guidance — the drive C1 will run). Seeds 1–4 per arm
  (16 runs; the bars below are structural per-run invariants, not
  paired statistics).
- **Instrument**: `snapshot_every_n_cycles = 40` into a file store —
  52 checkpoints per run; every reading below comes from decoded
  blobs and the run summary, zero engine changes. Per checkpoint:
  the **capped quantity** exactly as `project_norms` defines it
  (per frame and weight tensor, ‖W‖_F ÷ (init scale · expected-init
  root), the number the cap would clamp at 1.2), blob byte size,
  population, `next_frame_id`; per run: the pred-error trace,
  NaN/inf scan over every tensor of every checkpoint.
- **Resume spot-check** (seed 1, each arm): resume from the
  cycle-1040 blob, run to the end, and compare the final cycle-2080
  blob byte-for-byte against the uninterrupted run's — Doc 06's
  guarantee, exercised for the first time at 500k steps.

## Bars (pre-registered; anchors stated)

- **S1 — no rot at reference scale**: for every cap-off run, the max
  capped quantity at the final checkpoint is ≤ **1.5×** its value at
  the cycle-520 checkpoint (post-maturation baseline; the scale-rot
  signature was unbounded multiples, so 1.5× is generous headroom for
  slow maturation), AND no NaN/inf anywhere. Cap-on rows recorded as
  the control (expected ≈ ≤ 1.2 by construction).
- **S2 — the ecology stays alive**: population within
  [min_frames, max_frames] at every checkpoint; `next_frame_id`
  strictly rises from first to last checkpoint (births continue);
  final population > 0.
- **S3 — bounded state, exact resume**: final blob size ≤ **1.25×**
  the cycle-520 blob size; every resume spot-check byte-identical.
- **S4 — error sanity, episodic arms only**: whole-run improvement
  ≥ 0 (pred_error_late ≤ pred_error_early) for every episodic run.
  Continuous arms' error rows are recorded as context, NOT a bar —
  the ch. 21 world-drift caveat applies to them by record.

## Failure exits (pre-registered stopping rules — a FAIL is data)

- **X-rot** — S1 fails cap-off while cap-on holds: the eighth rule
  extends to reference-scale long lifetimes; the remedy is config
  guidance (C1 runs with the cap on), propagated to Doc 07/PRA-01 as
  a recorded recommendation — no default change without its own arc.
- **X-snap** — S3 fails: a persistence bug; fixed before anything
  else is read (the Doc 06 guarantee is constitutional).
- **X-eco** — S2 fails: diagnosed before interpretation (an ecology
  that freezes or explodes at long horizons is its own finding).
- **X-mixed** — S1 fails on BOTH cap settings: the mechanism is not
  (only) norm growth; diagnose before remedy, successor named from
  the trajectories.
- **PASS-clean** — everything green: C1 launches on reference
  defaults, recorded with the trajectories as the evidence.

Results are appended as they land; the Outcome section closes the arc.
Scratchpad instruments stay out of git; protocols and tables live here.
