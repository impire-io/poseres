# Election-stream arc — staleness as who goes silent

Date: 2026-07-19. Question under test: chapters 38–39 closed the
population transfer-error read across three statistic families (level,
jump, accumulation) with one shared verdict — the weak half of the
shift cells never separates from benign background — and the ch. 38
per-frame probe exposed why: **election censors the error stream**. A
frame the shift hurt stops clearing the fit gate, leaves the electing
population, and takes its evidence with it. This arc reads the censor
itself as the signal: on a world shift, previously-reliable frames
should go silent *together*, and that mass silence — not any error
magnitude — is the staleness event. The engine already counts
elections in its hot loop; this is the cheapest instrument in the
program.

## The design under test (frozen here, before any run)

- **The traces**: the 14 arc-023 h100 captures, extended with frame
  lifecycle events (birth/evict step indices) by the same copy-patch
  discipline (reads only, no RNG, no float-order change). **I0**: the
  extended capture must reproduce the 023 trace fields
  (t, ep, e, a, ids, errs) **byte-identically** on all 14 traces —
  the extension proven non-perturbing before anything is read.
  Mismatch = XI: fixed first.
- **Granularity**: episodes (the 40-step unit every validated
  mechanism already keys on). A reading for episode E is available at
  E's final step and attributed to it; the detection window covers
  episodes whose final step falls in 6760..7240 (the twelve
  post-shift episodes, inherited); false-alarm spans are episode-ends
  in 2000..6760 (shift traces) and 2000..24000 (benign); firings
  after 7240 on shift traces count neither way (inherited).
- **P1 — the silence statistic (frozen)**: per frame f and episode E,
  present(f, E) = f elected ≥ c times in E. **Established** entering
  E: present in EVERY one of episodes E−M..E−1 (juveniles and
  intermittents filtered by construction; no lookahead). **Silent**
  in E: established entering E, alive through E's end (not evicted at
  or before it — eviction is the ecology's response, a different
  event, excluded via the lifecycle log), and elected ZERO times in
  E. The reading: silent-fraction(E) = silent ÷ established, emitted
  only when established ≥ 4 (below that the fraction is noise; one
  constant, stated). The detector **fires** when silent-fraction > θ.
- **P1 grid (frozen)**: M ∈ {8, 16} × c ∈ {1, 4} × θ ∈ {0.25, 0.50,
  0.75} — 12 settings.
- **P2 — mapped-drop fallback (frozen now; run only if P1 confirms
  nothing)**: the crude population read of the same mechanism, no
  frame identity. Form A: m_E = mean electing count per step over E;
  fire when m_E < q · median(m over the last M episodes), q ∈ {0.5,
  0.75}, M ∈ {8, 16}. Form B: fire when E contains ≥ L zero-election
  steps, L ∈ {1, 4}. Six settings.
- **Bars (the 024 hit/false-alarm form, inherited verbatim)**: ONE
  setting must, on the screening tier (seeds 1–3 + multiregion s1),
  fire in the detection window on ALL SIX shift cells AND fire ZERO
  times across all pre-shift and benign spans — then reproduce both
  clauses on the confirmation tier (seeds 4–6 + multiregion s2, read
  only for screening passes). No per-world tuning. Multiple
  confirmations pin the largest worst-cell peak reading at its θ;
  ties → smaller M, then smaller c, then larger θ.

## E1 — conditional live stage (protocol frozen now, 023/024's form)

Runs only if P1 or P2 confirms, after the detector ships as reviewable
src (opt-in dial, byte-identity at default, snapshot surface). Arms
`scout` (detector-gated exploration) and `scout+competence` (0.5/0.5);
24 seeds × horizons {18, 30, 50} × {dynamics-shift, multiregion},
emission-shift at 8 seeds informative; judged against the frozen 017
rows. H-collect: a scout-bearing arm beats BOTH competence and random
on post-shift improvement ≥ 13/24 paired, positive mean margins, h50
dynamics. H-no-harm: pre-shift + multiregion noninferiority (T7);
byte-identity at default everywhere.

## Failure exits (pre-registered stopping rules — a FAIL is data)

- **XI** — the extended capture is not byte-identical to the 023
  traces: an instrument perturbation, fixed before anything is read.
- **X0** — no P1 setting screens clear AND P2 fails: the election
  stream joins the closed families; the staleness-detection program
  pauses with its map complete (four signal families measured on one
  testbed) and the successor named from what the numbers say, at
  close — not improvised here.
- **X0c** — a screening pass fails confirmation: a search artifact,
  recorded; treated as X0 for that probe.
- **X1** — the gate passes but E1's H-collect fails: the detector
  sees, the policy cannot collect; ships only if H-no-harm holds; the
  acting question is named.
- **X2** — H-no-harm fails: ship-blocked; inert + finding.
- **X3** — byte-identity break in any default configuration: a bug,
  fixed first.

Results are appended as they land; the Outcome section closes the arc.
Scratchpad instruments stay out of git; protocols and tables live here.

## Result: I0 (recorded 2026-07-19)

All 14 extended captures reproduce the 023 trace fields byte-identically
(decompressed comparison, every file). The lifecycle extension is
non-perturbing; 177–188 birth/evict events per trace ride the sidecar.

## Result: P1 (recorded 2026-07-19; screening tier, all 12 settings)

**FAIL at every setting — X0 — and the hardest close of the program so
far: not even the strong cells separate.** Detection-window peaks:
dynamics 0.13–0.25 (s1 again the weak cell: at most 14% of established
frames go silent), emission 0.33–0.50 — but the false-alarm peak is
**0.60–0.67**: the benign world and the pre-shift reference world
produce episodes in which over half the established frames go silent
at once, exceeding every shift cell's peak. At θ = 0.25 the detector
reaches only 3/6 hits with 2–4 false alarms; at zero-false-alarm
thresholds it detects nothing. The readings are nearly invariant to M
and c (identical peaks at M8 c1/c4) — the verdict is robust to the
statistic's own dials. The mechanism is visible in where the false
alarms live: on multiregion the drive moves the policy between
regions, and an episode spent elsewhere silences the other region's
specialists en masse; on the pre-shift reference world the ecology's
own churn does the same. **Self-generated behavioral nonstationarity
produces mass silence indistinguishable from — and larger than — a
world-change's.** Confirmation tier: never read.

## Result: P2 (recorded 2026-07-19; mapped-drop fallback, all 6 settings)

**FAIL — X0, same trade.** Form A (mean-election drop): 5/6 hits at
q = 0.75 only with 51–69 false alarms; 2/6 at q = 0.5 with 5–9. Form B
(zero-election steps): L1 = 2/6 hits at 29 false alarms; L4 = nothing
anywhere. The crude population read inherits the same background.

## Outcome (recorded 2026-07-19)

1. **The election stream joins the closed families, and the map is
   complete: four signal families — error level, error jump, error
   accumulation, election/silence — measured on one frozen testbed,
   one shared verdict.** No passive statistic on any stream this
   engine emits separates a world shift from the system's own
   nonstationarity at honest false-alarm rates. The censorship
   mechanism (ch. 38) was real, but reading the censor directly fails
   for the deeper reason the whole program kept hitting: **the
   detector's background is the brain itself** — an exploring drive
   that moves, an ecology that churns, both producing signatures as
   large as the shifts.
2. **The successor the numbers name is active, not passive: scheduled
   probing.** Every family failed on confounded evidence — "the world
   changed" vs "I changed where I go / who I am." Only a controlled
   probe removes the confound: deliberately re-visit mastered ground
   under a held policy for a probe window and re-test — detection as
   a designed experiment (a Doc 05-level design feature with its own
   spec, costs, and no-harm surface), not a passive read. Named, not
   built here.
3. **The standing alternatives are recorded, not lost**: the ch. 39
   tolerant gate (6/6 within four episodes at ~1.6% false-fire) if a
   deployment can afford wasted exploration, and the program-level
   fact that Doc 05's guidance (competence) never depended on
   detection. With the detection program paused at a complete map,
   the roadmap's front returns to C1.
4. **What ships: nothing but knowledge** — the byte-identity-proven
   lifecycle instrument, the fourth closed family, the
   self-nonstationarity diagnosis, and a named active successor. Doc
   05 guidance unchanged: competence stands.
