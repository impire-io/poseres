# Place-memory arc — does a map that remembers mastery make staleness computable?

Date: 2026-07-18. Question under test: SCOUT-DIAGNOSIS (ch. 32) measured
that no trend statistic over the 200-entry err@visit FIFO can see a regime
change — the baseline is forgotten in ~5 episodes. The named successor is a
representation: **place-indexed, long-horizon error memory**. This arc
freezes the smallest such design, gates it OFFLINE on real traces before
any src change, then (conditional on the gate) ships it opt-in with a
scout drive reading it and measures the chapter-31 question one more time
against the frozen 017 grid.

## The design under test (frozen here, before any run)

**The place map** (`place_memory_size = K`, 0 = off; K = 32 registered for
first results; agency state, curiosity mode only):

- **Allocation**: the first K *episode-start* observations become anchors,
  in order; then the map is frozen. No RNG, no distance threshold.
- **Per-anchor state**: `fast` — EMA (decay = the existing `ema_decay`,
  0.9) of the errors-at-visit assigned to this anchor; `best` — the
  running **minimum** of `fast` after each update; `n` — visit count.
  First sample seeds `fast = best = err` (no zero-init bias).
- **Assignment**: each step's (observation, error-at-visit) updates the
  nearest anchor (L2; ties to lowest index). Steps with no error reading
  update nothing.
- **Staleness**: `stale(a) = max(0, fast_a − best_a)`. Mastered ground:
  fast ≈ best → 0. Never-learned ground: fast tracks best down → ≈ 0.
  Unlearnable ground: fast fluctuates on a plateau the min skims → small
  (the noisy-TV margin P1 measures). **Changed-under-mastery ground: fast
  rises above a best that never forgets → positive and persistent until
  relearned past the old best.** The long horizon is structural (a min
  has no decay), and the only new constant is K.

**The scout drive** (`"scout"` in the registry): value(ô) = staleness of
ô's nearest anchor; 0 with no anchors. Blends on a real surface with
competence/frontier (independent signals).

Baselines inherited and FROZEN (CAMPING-DIAGNOSIS grid, 24 seeds, same
construction streams): shifting post-shift improvement medians random
+0.070 / frontier +0.061 / blend +0.058 / competence +0.038; multiregion
competence > random 17/24 at every horizon. Chapter-32 anchors: FIFO scout
median 0.000 everywhere; frontier median positive everywhere (0.03–0.09).

## Hypotheses (pre-registered, before any run)

- **H-map (P1, offline, before any src change).** Replaying the map over
  captured live traces: post-shift staleness at visited ground separates
  from background — median over the first 2 post-shift cycles > 0 and
  > 4× the pre-shift median (window 2000..shift), and > 4× the
  multiregion median (the noisy-TV/benign margin).
- **H-collect (E1, live).** A scout-bearing arm beats **both** competence
  and random on post-shift improvement, paired per seed, ≥ 13/24 each
  with positive mean margins, at the 50-cycle horizon.
- **H-no-harm (E1).** Pre-shift (h18/h30) and multiregion: scout-bearing
  arms noninferior to competence (T7 form) vs the frozen baseline;
  `place_memory_size = 0` byte-identical everywhere.

## P1 — offline replay gate (scratchpad; BEFORE any src change)

Capture per-step (step, observation, error-at-visit, episode-start flag)
from live frontier-arm runs — shifting world (017 dials, seeds 1–3) and
multiregion (seed 1) — via the ch. 32 probe patch. Replay the frozen map
arithmetic over each trace; read staleness at each step's observation.
**Accept**: H-map's three clauses at every shifting seed. **Fail → X0**:
the representation is still wrong; stop before any src change, record
which clause broke (allocation coverage? min-skimming? assignment?), name
the successor.

## E1 — the arms (conditional on P1; protocol pre-registered)

Arms `scout` and `scout+competence` (0.5/0.5), 24 seeds × horizons
{18, 30, 50} × both worlds (288 runs), the 017 instrument verbatim
(engine + `make_world`, post-shift reading from the end-of-run snapshot's
error trace, identical windows), judged against the frozen 017 rows,
paired per seed. Primary: **H-collect** for at least one scout-bearing
arm. Secondary: pre-shift noninferiority; whole-run margins with spreads;
post-shift medians tabulated beside the frozen four; multiregion
noninferiority; staleness traces recorded (does the signal light where
the shift is?).

## Failure exits (pre-registered stopping rules — a FAIL is data)

- **X0** — P1 fails: recorded with the broken clause; zero src changes
  (the ch. 32 stance); successor named from the specific break, not
  improvised.
- **X1** — P1 passes, H-collect fails: the signal sees, the policy cannot
  collect — the bottleneck moves to acting (one-step lookahead depth,
  exploration ε, candidate set). Recorded beside the frozen four; the map
  ships anyway if H-no-harm holds (it is the reusable representation);
  successor: the acting question, named.
- **X2** — H-no-harm fails: ship-blocked; fix openly or land inert +
  finding.
- **X3** — any byte-identity break at default: a bug; fixed first.

Results are appended as they land; the Outcome section closes the arc.
Scratchpad instruments stay out of git; protocols and tables live here.
