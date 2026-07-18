# Context-memory arc — anchor on what the brain did, not what it saw

Date: 2026-07-18. Question under test: chapters 32–34 eliminated two anchor
spaces for staleness detection (sliding FIFOs forget the baseline;
raw-observation places are not shift-invariant — a dynamics shift moves
where the brain goes, an emission shift repaints what it sees) and left a
measured bracket: any detector must separate post-shift staleness from
background by **4× on both shift modes**, from raw-observation starting
points of < 1× (dynamics) and ~1.5× (emission), with the benign floor at
~0.11. This arc tests the third anchor space — **the agent's own
behavior**, which no world change can move.

## The design under test (frozen here, before any run)

- **Cell index**: the last `m` actions (a window over the action stream;
  cells = `n_actions^m`; deterministic indexing, no anchors, no distance
  metric, no allocation). Within-episode only: the context resets at
  episode boundaries (the first m−1 steps of an episode update no cell).
- **Per-cell state**: a bounded deque of the last `W` errors-at-visit;
  the cell statistic is the **median** of a full window (no reading until
  the window fills once); `best` = the running **minimum of full-window
  medians**; staleness = `max(0, median − best)`. Medians kill the spike
  floor that broke the ch. 33 arithmetic; a min over medians ratchets on
  structure, not luck.
- **Why this space is shift-invariant**: the index is chosen by the
  policy, not the world. After a *dynamics* shift the same action context
  leads somewhere else — errors at that index jump. After an *emission*
  shift it leads to the same place repainted — errors jump. In both
  cases the comparison "error now at this context vs the best I ever had
  at this context" is well-posed, which is exactly what broke for
  observation anchors.
- **Constants**: `m` and `W`, pinned by the P1 scan below (grid frozen:
  m ∈ {2, 3, 4}, W ∈ {16, 32}); one (m, W) must clear every bar — no
  per-world tuning.

Baselines inherited and FROZEN: the ch. 34 bracket above; the 017 grid
(post-shift improvement medians random +0.070 / frontier +0.061 /
competence +0.038) for the conditional live stage; benign floor 0.110
(multiregion, ch. 33 replay).

## Hypotheses (pre-registered, before any run)

- **H-invariant (P1).** At one pinned (m, W), post-shift staleness
  medians clear the full bracket on BOTH shift modes: > 0, > 4× the
  pre-shift median, > 4× the benign (multiregion) median — seeds 1–3
  each, every seed.
- **H-collect (E1, conditional on P1).** A scout-bearing arm (the drive
  reading context staleness) beats both competence and random on
  post-shift improvement, ≥ 13/24 paired, positive mean margins, at the
  50-cycle horizon, on the dynamics-shift world (the recorded-FAIL
  configuration); the emission-shift world is read informatively.
- **H-no-harm (E1).** Pre-shift and multiregion noninferiority vs
  competence (T7 form); byte-identity at default everywhere.

## P1 — offline gate (scratchpad; BEFORE any src change)

Capture per-step (step, action, error-at-visit) from live frontier-arm
runs — dynamics-shift seeds 1–3, emission-shift seeds 1–3 (017 dials,
shift at 6760), multiregion seed 1 — via a logging world wrapper (actions)
joined with the ch. 32 drive patch (errors). Replay the frozen arithmetic
at every (m, W) in the grid; windows: pre = steps 2000..6760, post =
6760..7240, benign = 2000..12000. **Accept**: H-invariant at one (m, W).
**X0**: no grid point clears both modes → record the best point's numbers,
close with zero src changes (the third gate-stop protocol), and name what
the numbers say is missing.

## E1 — conditional live stage (protocol pre-registered)

Arms `scout` and `scout+competence` (0.5/0.5) at the P1-pinned (m, W),
24 seeds × horizons {18, 30, 50} × {dynamics-shift, multiregion} with
emission-shift at 8 seeds informative; the 017 instrument verbatim;
judged against the frozen 017 rows. Primary: H-collect. Secondary:
pre-shift/multiregion noninferiority; post-shift medians tabulated beside
the frozen four; staleness traces.

## Failure exits

- **X0** — P1 fails (above). **X1** — P1 passes, H-collect fails: the
  signal sees, the policy cannot collect; the map ships if H-no-harm
  holds (reusable instrument), the acting question is named. **X2** —
  H-no-harm fails: ship-blocked; fix openly or inert + finding. **X3** —
  byte-identity break: a bug, fixed first.

Results are appended as they land; the Outcome section closes the arc.

## Result: P1 (recorded 2026-07-18; 7 captured traces, full (m, W) grid)

**FAIL at every grid point — X0, the third gate-stop.** Representative
medians (pre → post), best cells: emission mode separates directionally
but weakly at every setting (e.g. m=3, W=32: 0.035 → 0.066; m=2, W=16:
0.088 → 0.135 — ~1.5–2×, never 4×); dynamics mode stays blind (post ≈
pre or lower; s1 post < pre at all six settings); the benign floor never
approaches zero (0.022–0.068 across the grid — windowed medians still
ride the within-life drift). Full table in the run log; no (m, W)
clears any mode at 4×.

## Outcome (recorded 2026-07-18)

1. **Three anchor spaces, one ceiling — the space was never the
   problem.** Sliding FIFOs (ch. 32), observation places (ch. 33), and
   action contexts (this arc) all top out at ~1–2× separation with a
   persistent benign floor. The common factor is the **signal**: the
   per-step errors-at-visit stream is a *tracking* error — it moves
   with ecology churn, election composition, and ongoing learning
   everywhere, and that nonstationarity is the background no indexing
   scheme can cancel.
2. **The project has already learned this lesson once, one level
   down.** THRESHOLD-DIAGNOSIS found that all-step EMAs score
   within-episode tracking rather than structure, and the remedy was
   the fair judge: score the first K steps of an episode — transfer to
   a fresh context, not tracking of the current one. The staleness
   question needs the same move at the drive level: a **transfer-error
   stream** (episode-start prediction errors, before within-episode
   adaptation masks the damage) as the input to any staleness memory —
   named here as the successor's signal, with all three failed spaces
   available for retry on top of it once the signal is right.
3. **The arc closes at its gate with zero src changes** — the third
   consecutive gate-stop, each cheaper than the last (this one reused
   every instrument), and jointly worth more than any of them alone:
   the staleness-detection program now has measured brackets on both
   world modes, three eliminated spaces, and a named signal-level
   diagnosis with an in-house precedent for the fix.
4. **What ships: nothing but knowledge.** Doc 05 guidance unchanged —
   competence stands. The testbed pair and the frozen grids wait.
