# Change-point arc — a jump detector where level bars discard the signal

Date: 2026-07-19. Question under test: TRANSFERSTALE-DIAGNOSIS (ch. 38)
closed the windowed-median level family — no (resolution × window)
setting reaches the 4× bracket, because the benign floor and the
post-shift response trade against each other — while showing the signal
itself is immediate and real: first-bin elevation on all six shift
cells at ~2× the *trailing* background, decaying as the brain relearns.
A level bar compares against a cross-world floor; the trajectory says
the information lives in the **jump against the stream's own recent
past**. This arc asks the successor question ch. 38 named: does a
self-normalized change-point statistic on the transfer stream detect
every shift with zero false alarms — judged by hit/false-alarm counts,
not level ratios?

## The design under test (frozen here, before any run)

- **The traces**: the 14 arc-023 captures, reused verbatim (the
  instrument of record: h100 frontier-arm runs, dynamics/emission
  seeds 1–6, multiregion seeds 1–2; per-step honest errors with
  electing-frame ids; capture protocol recorded in
  TRANSFERSTALE-DIAGNOSIS). Screening tier = seeds 1–3 + multiregion
  s1; confirmation tier = seeds 4–6 + multiregion s2, **read only for
  a setting that clears every screening bar** (the 023 rule, kept).
- **The signal**: transfer errors, e ∈ {1..K}, K = 5, inherited; two
  registered spaces from the ch. 38 margin map's shallow corner —
  `global` (one stream: the per-step mean electing error at transfer
  steps) and `ctx1` (four per-cell streams keyed by the last action;
  readings per cell, the detector fires if ANY cell fires — the
  multiple-comparison cost is borne openly by the false-alarm bar).
- **P1 statistic — Z-jump (frozen)**: at each new sample x of a
  stream, T = the last `n_test` samples (x included), R = the `n_ref`
  samples before T; z = (median(T) − median(R)) / (MAD(R) + 1e-9),
  MAD = median absolute deviation about median(R). No reading until
  T and R are both full (per stream; fill epochs recorded). The
  detector **fires** at any sample with z > θ.
- **The grid (frozen)**: space {global, ctx1} × n_test {10, 20} ×
  n_ref {60, 120} × θ {4, 6, 8} — 24 settings, offline replay only.
- **The spans (all inherited)**: false-alarm spans = pre-shift
  2000..6760 on every shift trace AND the whole benign read
  2000..24000 on multiregion; detection window = 6760..7240 (the 022
  early-detection span: the ch. 38 trajectory puts arrival in the
  first bin, so two cycles is generous without being vacuous).
  Post-shift firings after 7240 on shift traces count neither way
  (the world really is shifted; they are recorded as the latency/
  persistence read).
- **Bars — hit/false-alarm form, pre-registered fresh**: ONE setting
  must, on the screening tier, (a) fire at least once inside the
  detection window on ALL SIX shift cells (both modes, every seed),
  AND (b) fire ZERO times across all six pre-shift spans and the full
  benign span. Any such setting is then re-read on the confirmation
  tier and must reproduce (6/6 hits, zero false alarms). No per-world
  tuning, no post-hoc θ. If several settings confirm, pin the one
  with the largest worst-cell peak-z inside the detection window at
  its θ; ties → global over ctx1, then smaller n_test, n_ref, θ.

## P2 — Page–Hinkley fallback (frozen now; run only if P1 confirms nothing)

Same streams, same spans, same bars, same two-tier rule. Standardized
increment at each sample: s = (x − median(R)) / (MAD(R) + 1e-9) with
n_ref ∈ {60, 120}; PH statistic m ← max(0, m + s − δ), δ ∈ {1, 2};
fire when m > λ, λ ∈ {10, 20, 40}; m resets to 0 on firing. Grid:
space {global, ctx1} × n_ref × δ × λ = 24 settings. The PH form
accumulates sustained small elevation where Z-jump needs a sharp
window contrast — the two failure modes are complementary.

## E1 — conditional live stage (protocol frozen now, 023's form)

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

- **X0** — no P1 setting screens clear AND P2 fails: the change-point
  family on this stream closes; the election-stream space (ch. 38
  successor ii) becomes the program's front door; best numbers
  recorded.
- **X0c** — screening pass fails confirmation: a search artifact,
  recorded; treated as X0 for that probe.
- **X1** — gate passes, E1 H-collect fails: the detector sees, the
  policy cannot collect; ships only if H-no-harm holds; the acting
  question is named.
- **X2** — H-no-harm fails: ship-blocked; inert + finding.
- **X3** — byte-identity break in any default configuration: a bug,
  fixed first.

Results are appended as they land; the Outcome section closes the arc.
Scratchpad instruments stay out of git; protocols and tables live here.
