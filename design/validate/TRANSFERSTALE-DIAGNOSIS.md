# Extended transfer-staleness probe — deeper cells, longer windows, held-out confirmation

Date: 2026-07-19. Question under test: TRANSFERSIG-DIAGNOSIS (ch. 36)
found the vein — staleness statistics on the **transfer stream** move the
right way in all six shift cells on both world-change modes, with ratios
to 7.2× where the tracking stream managed ~1× — and still closed X0: two
seeds sat at ~1.5×, the benign floor was not 4×-cleared, and the frozen
grid ended exactly where its own trend (deeper cells, longer windows,
every number improving monotonically) was still climbing. Extending that
grid post hoc was refused as tuning; the successor was named from the
measured trend, to be pre-registered fresh. This document is that fresh
pre-registration: **richer context cells and longer windows on the
transfer stream**, with **per-frame transfer error** as the frozen
fallback space — and, new to this arc, a **held-out confirmation tier**,
so that a wider grid cannot buy a pass by search.

## The design under test (frozen here, before any run)

- **The signal (022 verbatim)**: per-step honest prediction errors (mean
  over electing frames; steps with no electing frame yield no sample),
  filtered to episode-relative transfer steps e ∈ {1..K}, **K = 5** (the
  fair judge's recorded `score_window_steps` scale value, inherited, not
  invented). e counts transitions within an episode: the reset step
  carries no error, so err_e at in-episode step e is the error of the
  transition into step e, and the actions available before err_e are the
  episode's first e actions.
- **The statistics (021 cell arithmetic, verbatim)**: per cell, a bounded
  window of the last W transfer errors, summarized by its **median** once
  full (no reading before first fill); per-cell **best** = running
  minimum of that cell's full-window medians; a **staleness reading** at
  every transfer visit to a full-window cell = max(0, median − best); a
  window-summary = the **median of readings** whose global step falls in
  the span. Even-length medians are the mean of the middle pair.
- **The cell spaces (8, frozen)** — the "richer cells" axis:
  - `global` (one cell), `ctx1`, `ctx2` — the 022 spaces, kept as
    bridges;
  - `ctx3`, `ctx4` — deeper action context (last m in-episode actions
    strictly before the error; a cell is indexable when e ≥ m; **no
    cross-episode context** — the 021 rule);
  - `phase` (cell = e itself, 5 cells) — the cheapest refinement: the
    e = 1 error is the purest transfer read, e = 5 the most adapted;
  - `ctx1⊗phase`, `ctx2⊗phase` (cell = context × e) — context cells
    that do not mix adaptation depths.
  Cells are `4^m` (n_actions = 4), times 5 where ⊗phase.
- **The windows axis**: W ∈ {8, 16, 32, 64}. Grid = 8 spaces × 4 = 32
  settings. A setting whose required span produces **no readings** (no
  cell ever fills) is recorded as *degenerate* — never as a pass; the
  expectation that ctx4 and long-W deep cells starve on a 5-sample/40-step
  stream is itself part of what this grid measures.
- **The step-spans (fresh where stated, with the rationale recorded
  now)**:
  - *pre* = steps 2000..6760 — inherited verbatim (ch. 33–36).
  - *post* = steps 6760..10600 — **fresh**. Rationale, not tuning: the
    transfer stream carries 5 of every 40 steps, 8× sparser than the
    tracking stream the ch. 33–35 bracket was built on; a 3840-step span
    (96 episodes) carries 480 global transfer readings — **reading-count
    parity** with the 480 tracking readings the recorded bracket's
    480-step post window read. The 022 post window (6760..7240) is
    recorded per setting as the *early-detection context row*, not a bar.
  - *benign* = steps 2000..24000 on the multiregion world — **fresh**
    (h100 traces, below); the 022 benign span (2000..12000) is recorded
    as the bridge row.
- **The traces**: live frontier-arm runs (`policy_mode="curiosity"`,
  `drive_weights=(("frontier", 1.0),)`, defaults otherwise), **h100**
  (`n_cycles=100` → 625 episodes → 25 000 steps), 017 dials:
  `world="shifting"` with `shift_after_steps=6760` in both
  `shift_mode="dynamics"` and `"emission"`; `world="multiregion"` with
  `region_noise_levels=(0.0, 0.3)`. Determinism makes the first 13 000
  steps of each seed byte-identical to a 022-length run — the I0 gate
  below leans on exactly this. Capture is per step: global step, episode
  index, in-episode index, action, mean electing error, and the
  per-electing-frame (frame_id, error) list (for P2), via a scratchpad
  copy-patch of `online_step` (adds reads only, no RNG, no float-order
  change) plus a passive world wrapper for actions.
- **Two tiers, one rule**: the *screening* tier is dynamics seeds 1–3,
  emission seeds 1–3, multiregion seed 1 (the 022 seeds). The
  *confirmation* tier — dynamics 4–6, emission 4–6, multiregion seed 2 —
  is captured together with the screen but **read only for a setting
  that has already cleared every screening bar**. A screening pass that
  fails confirmation is recorded as the search artifact the two-tier
  design exists to catch, and does not count.
- **Bars (the ch. 34 bracket, 4× form, on the fresh spans)**: ONE
  setting must show post-shift staleness median > 0, > 4× its pre-shift
  median, AND > 4× the benign median — on BOTH shift modes, EVERY seed —
  first on the screening tier, then reproduced in full on the
  confirmation tier. No per-world tuning. If several settings confirm,
  the pinned setting is the one with the largest worst-cell margin
  (min over the six cells of post ÷ max(4·pre, 4·benign)); ties break to
  the shallower space, then the smaller W.

## I0 — instrument reproduction (before any extended reading)

Replay the 022 grid ({global, ctx1, ctx2} × {8, 16}) on the recaptured
screening traces over the 022 spans (post 6760..7240, benign
2000..12000). The recorded rows must reproduce: best setting ctx2/W16 —
dynamics 0.028→0.072 / 0.007→0.051 / 0.008→0.028, emission 0.020→0.056 /
0.019→0.062 / 0.017→0.026, benign floor 0.027; and the recorded benign
trend across the grid (0.163 → 0.027). Mismatch = **XI**: stop, reconcile
the arithmetic openly, record the reconciliation here — no extended
reading before the instrument is proven faithful.

## P1 — the extended grid (offline; zero src changes)

Replay all 32 settings on the screening traces at the fresh spans.
**Accept**: the bar clause above (screen, then confirm). Secondary,
recorded either way: the early-detection context row per setting; the
post-shift staleness trajectory (per-cycle bins, 6760..10600) for the
best setting — the E1-relevant read of how fast the signal arrives.

## P2 — per-frame transfer error (frozen fallback; run only if P1 confirms nothing)

The composition-noise-free read the 022 outcome named: every comparison
is a frame against its own past. Per frame f, the stream of its own
honest transfer errors at steps where it elects (captured with ids);
window W ∈ {8, 16, 32} over that stream, median / per-frame best /
staleness by the same arithmetic; the per-step reading at a transfer
step = the **median staleness over frames electing at that step** whose
windows are full. Same spans, same bars, same two-tier rule. Degenerate
cells recorded as such (a frame needs W electing transfer visits to
read at all).

## E1 — conditional live stage (protocol frozen now, mirroring 021)

Runs only if P1 or P2 confirms a setting, and after the detector ships
as reviewable src (its own spec-flow step; byte-identity at default,
opt-in dial, snapshot surface). Arms `scout` and `scout+competence`
(0.5/0.5) reading the pinned statistic; 24 seeds × horizons {18, 30, 50}
× {dynamics-shift, multiregion}, emission-shift at 8 seeds informative;
the 017 instrument verbatim; judged against the frozen 017 rows.
**H-collect** (primary): a scout-bearing arm beats BOTH competence and
random on post-shift improvement, ≥ 13/24 paired each, positive mean
margins, at h50 on dynamics-shift. **H-no-harm**: pre-shift and
multiregion noninferiority vs competence (T7 form); byte-identity at
default everywhere.

## Failure exits (pre-registered stopping rules — a FAIL is data)

- **XI** — I0 mismatch: reconcile first, openly; nothing else is read.
- **X0** — no setting screens clear in P1 AND P2 fails: the fifth
  gate-stop, zero src; the best setting's numbers recorded; the
  successor named from what the numbers say, at close — not improvised
  here.
- **X0c** — a setting screens clear but fails confirmation (either
  probe): recorded as a search artifact; treated as X0 for that probe.
- **X1** — the gate passes but E1's H-collect fails: the signal sees,
  the policy cannot collect; the detector ships (or stays) only if
  H-no-harm holds; the acting question is named.
- **X2** — H-no-harm fails: ship-blocked; inert registry entry plus the
  finding.
- **X3** — byte-identity break in any default configuration: a bug,
  fixed before anything proceeds.

Results are appended as they land; the Outcome section closes the arc.
Scratchpad instruments stay out of git; protocols and tables live here.
