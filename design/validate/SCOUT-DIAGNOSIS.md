# Scout arc — does anticipating progress collect the camping bill realized LP left on the table?

Date: 2026-07-18. Question under test: CAMPING-DIAGNOSIS (ch. 31) measured
that camping costs — post-shift the camper recovers worst of all arms
(median post-shift improvement +0.038 vs random's +0.070) — and that the
frontier drive does not collect: its post-shift edge over competence
(14/24, +0.027) equals random's (17/24, +0.027). The mechanism was named:
realized LP is a **lagging indicator** — after a shift, newer errors near a
candidate exceed older ones, so `max(0, older − newer)` reads zero exactly
when progress is available. The scout drive is the mirror:

    scout(ô) = max(0, mean(err@visit, NEWER half) − mean(err@visit, OLDER half))

over the same 2k nearest finite-error remembered neighbors (the frontier's
machinery verbatim, halves swapped; reuses `frontier_neighbors`, no new
constants; silent below 2k finite entries; pure floats, no RNG). Positive
exactly where local error has *risen* — knowledge gone stale, relearning
available now. Flat-high (noise) → 0: the noisy-TV guard inherited by
construction. Flat-low (mastery) → 0: no camping. Falling (frontier's
territory) → 0: the two drives are complementary detectors on a real blend
surface.

Baselines inherited and FROZEN (CAMPING-DIAGNOSIS E1/E2 grid, 24 seeds,
same construction streams — arms do not affect world draws, so same-seed
comparisons are exactly paired): shifting-world post-shift improvement
medians random +0.070 / frontier +0.061 / blend +0.058 / competence +0.038;
multiregion competence beats random 17/24 at every horizon. Clause lesson
applied (ch. 31 outcome §4): bars are competence- AND random-relative,
never random-relative alone.

## Hypotheses (pre-registered, before any run)

- **H-signal (P1, before any drive code).** On real shifting-world traces,
  post-shift the scout statistic at visited candidates is positive where
  the frontier statistic is ≈ 0; pre-shift both are near zero on mastered
  ground; on multiregion traces the scout stays near zero throughout.
- **H-collect (E1, the primary).** A scout-bearing arm beats **both**
  competence and random on post-shift improvement, paired per seed,
  ≥ 13/24 each with positive mean margins, at the 50-cycle horizon.
- **H-no-harm (E1).** Pre-shift (h18/h30) and on the multi-region world,
  scout-bearing arms are noninferior to competence (T7 form,
  mean ≥ −1.9·SE) against the frozen baseline.

## P1 — signal-shape probe (scratchpad; BEFORE any drive code)

Instrument a live frontier-arm run on the shifting world (017 dials,
seeds 1–3): at each drive evaluation, compute BOTH statistics (frontier as
shipped; scout as the mirrored read of the same context) and log them with
the step index. Same on one multiregion run. **Accept:** median scout
signal over the first 2 post-shift cycles > 0 and > 4× the frontier's
median over the same window; pre-shift scout median ≈ 0 (below the
frontier's own pre-shift median); multiregion scout median ≈ 0 at every
read. Fail → the mirror is not the right form; stop and re-design before
any src change (X0).

## E1 — the arms (after the drive ships; protocol pre-registered)

Arms: `scout` (alone) and `scout+competence` (0.5/0.5), each 24 seeds ×
horizons {18, 30, 50} × both worlds (288 runs), same instrument as 017
(engine + `make_world`, post-shift reading from the end-of-run snapshot's
error trace, identical window arithmetic). Judged against the FROZEN 017
rows, paired per seed.

- **Primary (shifting, h50):** H-collect for at least one scout-bearing
  arm — post-shift improvement > competence in ≥ 13/24 AND > random in
  ≥ 13/24, both mean margins > 0.
- **Secondary:** pre-shift noninferiority (h18/h30) vs competence; whole-
  run margins with spreads; post-shift medians tabulated beside the frozen
  four; multiregion noninferiority vs competence at every horizon;
  steering readings recorded (shifting: none defined; multiregion:
  hard-region occupancy, informative only).

## Failure exits (pre-registered stopping rules — a FAIL is data)

- **X0** — P1 fails: the mirrored statistic does not show the shift on
  real traces. Arc stops before any src change; finding recorded; the
  successor question becomes representation (is err@visit memory too
  sparse near revisited ground?), named not improvised.
- **X1** — P1 passes but H-collect fails: the signal sees the shift and
  the policy still cannot collect (lookahead horizon, memory density, or
  the one-step candidate set is the bottleneck). Recorded with the scout's
  post-shift median beside the frozen four; Doc 05 guidance unchanged;
  named successor: lookahead depth / memory-density study.
- **X2** — H-no-harm fails anywhere: ship-blocked regardless of the
  primary; fix openly or land the drive as an inert registry entry plus
  the finding.
- **X3** — byte-identity break in any no-scout configuration: a bug,
  fixed before anything proceeds.

Results are appended as they land; the Outcome section closes the arc.
Scratchpad instruments stay out of git; protocols and tables live here.
