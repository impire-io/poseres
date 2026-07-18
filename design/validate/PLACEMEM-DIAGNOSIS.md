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

## Result: P1 (recorded 2026-07-18; offline replay over live traces, shifting seeds 1–3 + multiregion seed 1)

**FAIL — X0, twice, with one openly-amended design revision in between.**

As registered (fast EMA, min of fast): staleness medians — multiregion
**0.110**; shifting pre-shift 0.113 / 0.088 / 0.168, post-shift 0.064 /
0.082 / 0.122. Every clause broken: benign ground reads ~0.1 staleness,
and **post-shift reads LOWER than pre-shift in all three seeds.**

Amendment, recorded before the retry: the registered X0 allowed no
design revision — stricter than the house norm (CHANNELWEIGHT X1
granted two recorded revisions for design iteration distinct from
criterion tuning). Amended to permit **one** recorded revision with the
accept bars untouched. Revision 1 (constant-free double smoothing:
`smooth = EMA(fast)` at the same decay, `best = min(smooth)`,
staleness = smooth − best): multiregion 0.108; pre 0.108 / 0.085 /
0.160, post 0.062 / 0.085 / 0.119. **No material change — the floor is
not EMA fluctuation noise. The revision budget is spent; X0 closes the
arc with zero src changes.**

**The diagnosis, in two layers (the recorded value of this arc):**

1. *Min-skimming is real but shallow*: per-step errors-at-visit are
   spiky, so a running min under any smoothing this fast skims a
   ~0.1 staleness floor onto benign ground. Curable in principle
   (spike-robust per-cell statistics), and not the binding break.
2. *The binding break is the anchor space*: a displacement-set shift
   changes **where the brain goes** — the visited observation
   distribution itself moves — so post-shift trajectories rarely
   revisit the anchors whose `best` encodes pre-shift mastery, and
   place-anchored comparison has nothing to compare (post < pre
   staleness is the fingerprint: late-life traffic concentrates on
   anchors with no mastered baseline). Observation-space places are
   **not shift-invariant** in this world family.

## Outcome (recorded 2026-07-18)

1. **The arc closes at its gate with zero src changes** — the second
   consecutive arc to do so, and the pre-registration priced that
   outcome in as a complete deliverable.
2. **The successor question is now sharply posed, in two named parts:**
   (i) *representation space* — error memory must be anchored in a
   space invariant to the change being detected (the frame's own
   pose/encoding space is the in-system candidate: the emission map
   survives the 017 shift, so encoded places should too), and
   (ii) *statistics* — per-cell error summaries robust to the spiky
   per-step series (median-of-means, not EMA minima). Both are Doc
   05-adjacent design research; neither is a dial.
3. **A testbed note, recorded for the next design:** the 017 shifting
   world changes the visited distribution along with the dynamics —
   any staleness detector validated there must survive that
   confound, or a complementary world (emission-shift at fixed
   dynamics) should join the ladder first.
4. **What ships: nothing but knowledge** — this trail, the spec that
   scoped it, and the two-part successor. Doc 05 guidance unchanged:
   competence stands. The 017 worlds and frozen grid remain the
   waiting testbed.
