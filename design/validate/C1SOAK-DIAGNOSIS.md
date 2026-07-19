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

## Result (recorded 2026-07-19; 16 runs × 500,200 steps + 4 resumed half-runs)

**S1 — PASS, 8/8 cap-off runs; the deferred rot question is answered
for C1 lengths.** Episodic cap-off is stationary (growth ratios 0.80 /
0.84 / 0.88 / 1.30 from cycle 520 to 2080; the max bounces in a 2–6
band with frame churn, no trend). Continuous cap-off grows slowly —
1.28 / 1.33 / 1.36 / 1.47, all under the 1.5 bar but the last one
narrowly — and the trajectory is *decelerating without having
plateaued* (seed 1 increments per 160 cycles: 0.74 → 0.27 → … → 0.08).
No NaN/inf anywhere. The cap-on controls calibrate the instrument and
the mechanism at once: the capped quantity rides at ≈ 1.20–1.28
exactly as `project_norms` promises, and capping is **measured
behaviorally free** (continuous seed 1: early error 0.1309 with cap
and without; late 0.0328 vs 0.0312).
**S2 — episodic PASS; continuous fails the letter, and the diagnosis
is by-construction.** Continuous population climbs to the frame
budget by ~cycle 960 and rides it forever at **201**: `offline_cycle`
evicts down to `max_frames` = 200 and THEN spawns `spawn_per_cycle`
= 1, so the true steady-state invariant is ≤ max_frames +
spawn_per_cycle — the bar mis-modeled the recorded ordering, not the
ecology. The substantive finding stands: **continuous mode saturates
the population budget** (episodic stabilizes at 6–46) — consistent
with ch. 21's drift caveat (perpetual novelty) — at a measured wall
cost of only ~10% (373–400 s vs 345–358 s per 500k steps): per-step
cost is overhead-dominated, not population-dominated. Births continue
in every run; nothing freezes.
**S3 — size clause fails everywhere, mechanism identified and
verified; resume clause passes everywhere.** Blobs grow 2.0–2.4 MB →
7.6–7.9 MB across ALL arms uniformly — the in-state per-step
pred-error trace (122,577 floats at cycle 520 → 487,428 at 2080,
~8 bytes/step, linear since feature 003 by design; population state
is bounded; nothing leaks). The frozen 1.25× bar mis-modeled a
recorded design property. The clause that matters held: **resume from
cycle 1040 reproduces the cycle-2080 blob byte-for-byte in all four
arms** — Doc 06's guarantee, now exercised at 500k steps.
**S4 — PASS, 4/4 episodic runs** (improvement ≥ 0). Continuous
context rows, recorded not judged: improvements +0.10…+0.25, early
0.13–0.28 → late ~0.03 — learning is strong in continuous mode
despite the world-drift caveat.

## Outcome (recorded 2026-07-19)

1. **No rot at reference scale over a C1 lifetime — the ch. 14
   deferral is answered with trajectories, not conjecture.** Episodic
   norms are stationary; continuous norms decelerate but have not
   plateaued by 500k steps. Since the cap is measured behaviorally
   free, the recorded recommendation is: **C1 runs with
   `weight_norm_cap = 1.2`** — it closes the un-plateaued tail for
   multi-month horizons at zero measured cost. Guidance, not a
   default change (X-rot did not fire).
2. **Two bars failed honestly and bought real intel.** Both X-eco and
   X-snap diagnosed to by-construction mechanisms, not defects — the
   bars mis-modeled recorded designs (evict-then-spawn ordering; the
   in-state error trace). What they quantified matters for C1:
   **budget for a ceiling-sized population** (max_frames + spawn, at
   ~10% wall cost), and **snapshot blobs grow ~8 bytes/step forever**
   (2–20 MB over a 3-month run at C1's 3–30 s cooldowns — tolerable,
   but a named future feature: a bounded-trace snapshot option, which
   must first resolve its Doc 06 semantics, since the trace feeds the
   early/late/improvement reads).
3. **The persistence constitution holds at deployment length**:
   byte-identical resume at 500k steps, all four arms, episodic and
   continuous, cap on and off.
4. **C1 launch posture: GREEN**, with three configuration notes
   recorded above (cap on; snapshot cadence sized to ~8 B/step
   growth; population budget at the ceiling). Zero src changes; the
   soak instrument was snapshots + the run summary, nothing else.
