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

## Result: P1 (recorded 2026-07-18; seeds 1–3 shifting + 1 multiregion, live frontier-arm traces, both statistics per read)

**FAIL — X0 fires, before any drive code, exactly as the gate was built
to do.** Medians over the pre-registered windows:

| seed | pre-shift frontier / scout | post-shift (2 cycles) frontier / scout |
|---|---|---|
| 1 | 0.052 / 0.000 | 0.031 / 0.000 |
| 2 | 0.030 / 0.000 | 0.030 / 0.000 |
| 3 | 0.071 / 0.000 | 0.089 / 0.000 |

Multiregion: scout median 0.000 (frontier 0.039) — that clause passed;
the shifting-world clauses did not: the scout median is zero
*everywhere*, and the frontier median is positive everywhere —
**including on mastered pre-shift ground.**

**The fine-grained diagnosis (40-step bins around the shift, seed 1):**
the shift is not invisible — scout fires on 26% of post-shift reads
(584/2252) with maxima 0.22–0.35 in the memory-straddle window, ~3× the
background — but it also fires pre-shift (maxima 0.21–0.23 at
−120…−80), and the frontier reads 0.03–0.13 medians straight through
the post-shift window. Neither statistic separates the regimes at the
median. The cause is the representation, not the arithmetic: the
err@visit memory is a **200-entry sliding FIFO (~5 episodes)** — the
pre-shift baseline is forgotten within ~200 steps of the shift, so the
"rise" signature exists only in a brief straddle, while on mastered
ground the window always carries residual recent-trend noise that both
trend reads mistake for signal. A quarter-turn of the same lens:
chapter 24's recorded frontier positives were partly this same
recent-trend artifact — the sliding window manufactures "progress
nearby" wherever global error drifts down.

## Outcome (recorded 2026-07-18)

1. **The arc stops at its gate, with zero src changes — a complete
   deliverable by the pre-registered stance.** The mirrored statistic
   (and by the same evidence, any half-comparison over the current
   memory) cannot detect a regime change on real traces, because the
   err@visit memory forgets the baseline faster than the ecology can
   re-encounter stale ground.
2. **The successor question is representation, not drive arithmetic,
   and it is now measured, not conjectured:** predictive LP needs
   errors **indexed by place with a long horizon** (slow decay,
   spatially anchored — not a 5-episode FIFO), so that "what error was
   here when I knew this region" survives long enough to compare
   against "what error is here now". That memory is a Doc 05 design
   change with its own snapshot/scale surface — a named feature, not a
   dial this arc could add honestly.
3. **A retrospective light falls on chapter 24:** the frontier's
   uniformly positive medians on mastered ground mean part of its
   recorded signal is sliding-window trend, not local structure — one
   more reason its live edges matched random's. Recorded here; the
   ch. 24 verdicts stand (they were about arms beating random, not
   about the statistic's semantics).
4. **What ships: nothing but knowledge** — this trail, the spec that
   scoped it, and the sharpened successor (place-indexed error memory,
   with the 017 worlds and the frozen grid still waiting as its
   testbed). Doc 05 guidance unchanged: competence stands.
