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

## Result: I0 (recorded 2026-07-19; 14 traces recaptured, XI fired, reconciliation recorded before any extended reading)

**The recorded 022 rows do not reproduce exactly under the registered
arithmetic — or under any of five nearby interpretations** (global
running best; transfer filter e ∈ {1..4} — the 1-based-counter reading
of "t mod 40 ∈ {1..K}"; error↔action join lag ±1; lag+1 × {1..4};
lower-middle median). The 022 scratchpad is retired and its exact join
details were never recorded, so row-level fidelity is untestable. The
reconciliation, openly:

- **Every recorded conclusion reproduces.** At ctx2/W16 (clean
  arithmetic, 022 spans) staleness moves the right way in ALL SIX shift
  cells — dynamics 0.004→0.046 / 0.000→0.091 / 0.000→0.028, emission
  0.013→0.040 / 0.003→0.019 / 0.000→0.021 — the benign floor is 0.030
  (recorded 0.027), the across-grid benign collapse is monotone
  0.180→0.030 (recorded 0.163→0.027), and the 022 bars still FAIL at
  the 022 spans (max post 0.091 < 4× benign 0.120): same verdict, same
  blocker (the floor clause), same trend.
- **The row decimals do not.** The recorded pre-shift medians
  (0.007–0.028) sit ~0.02 above the clean replay's (0.000–0.013); a
  deliberate +1 join misalignment (context shifted one action late)
  recreates that inflated pre-shift scale (0.024/0.018/0.008 dynamics)
  but not the recorded posts — the closest single explanation is an
  unrecorded join detail in the 022 instrument, and no tested variant
  lands the decimals exactly.
- **Consequence, recorded**: the 022 ratios (2.5–7.2×) most likely
  *understated* the clean transfer statistic's separation — the clean
  replay's dynamics ratios at ctx2/W16 are 11× and two divisions by
  ~zero. The finding sharpens, the verdict does not change.

**Instrument of record from here on**: the arithmetic registered in
this document (clean join, e ∈ {1..5}, per-cell best, even-window
median = mean of the middle pair), replayed on the 14 recaptured
traces. The extended reading proceeds on this instrument; the recorded
022 rows stay in TRANSFERSIG-DIAGNOSIS as that arc's evidence, with
this section as the bridge between the two.

## Result: P1 (recorded 2026-07-19; screening tier, all 32 settings, fresh spans)

**FAIL at every setting — X0 — and the 022 trend is now explained, not
extended.** The benign floor does keep collapsing with resolution
(0.203 at global/W8 → 0.010 at ctx2⊗phase/W64, monotone as 022 saw)
but the post-shift response dies faster than the floor falls: at every
deep/long setting the dynamics posts go to ~0 (windows in fine cells
never turn over — or never fill: ctx4 and the W≥32 deep rows are
degenerate on 2–3 samples/episode), while every shallow setting with a
live response carries a floor its post cannot 4×-clear. The balanced
read makes it precise — worst-cell margin, post ÷ max(4·pre,
4·benign), across the plane:

| setting | worst-cell margin |
|---|---|
| **ctx1/W8** | **0.211** (the plane's maximum) |
| global/W8 · W16 · W32 | 0.206 · 0.198 · 0.197 |
| phase/W8 · W16 | 0.175 · 0.171 |
| ctx2/W16 (the 022 corner) | 0.114 |
| everything deeper/longer | lower or degenerate |

The maximum sits at the SHALLOW corner: 022's "still improving" was
the floor leg only, and the whole windowed-median family tops out ~5×
short of the bracket. Secondary reads, recorded: the early-detection
row at ctx1/W8 (022 spans) is pre 0.087–0.154 → post 0.147–0.247 —
elevation on all six cells inside the first two cycles; the per-cycle
trajectory at ctx1/W8 puts the elevation in the FIRST post-shift bin
(dynamics first-bin 0.168/0.205/0.334 vs pre medians 0.091–0.154,
emission 0.243/0.193/0.146 vs 0.087–0.131) decaying back over ~6–16
cycles as the brain relearns. **No latency problem — a contrast
problem.** The confirmation tier was never read (no screening pass),
per the registered rule.

## Result: P2 (recorded 2026-07-19; per-frame fallback, screening tier)

**FAIL — X0, and directionally dead, the arc's sharpest finding.**
Post ≈ pre at every W (W8: dynamics 0.143→0.138 / 0.123→0.133 /
0.121→0.113; emission s1 *falls*, 0.165→0.124) and the benign floors
(0.090–0.166) are the highest of the whole arc. The mechanism is
visible in the construction: **election censors the signal**. A frame
the shift hurt stops clearing the fit gate, so it leaves the electing
population — and with it the reading — while the frames still electing
post-shift are precisely the unhurt ones. Per-frame self-comparison
removes the population-composition noise it was built to remove *and*
the staleness signal, which lives in exactly the frames that go
silent.

## Outcome (recorded 2026-07-19)

1. **The question 022 left open is answered end-to-end: no windowed-
   median level statistic on the transfer stream reaches the 4×
   bracket.** The floor leg and the response leg trade against each
   other across the full (resolution × window) plane; their best
   balance (ctx1/W8, margin 0.21) is ~5× short, and the trend 022
   recorded as "still improving" inverts once both legs are read
   together. This closes the statistic family, not the signal: the
   transfer stream still shows immediate, universal, ~2× contrast on
   every shift cell.
2. **Frame-level self-comparison is structurally censored.** The fit
   gate deletes stale frames from the electing population, so any
   statistic over *electing* frames' errors reads survivors. The
   damage signal at frame level is not "my errors rose" — it is "I
   stopped electing," a stream the engine already counts.
3. **The fifth gate-stop, zero src changes — and the successors are
   named by the numbers, not conjecture.** (i) A **change-point form
   on the same transfer stream**: the trajectory shows the signal
   arrives in the first post-shift bin at ~2× its own trailing
   background and decays as relearning proceeds — a level bar against
   a cross-world floor discards exactly this; the successor statistic
   is self-normalized (its own trailing distribution as the
   reference), judged by hit/false-alarm counts on the shift/benign
   testbed pair, bars pre-registered fresh. (ii) **The election stream
   as the fallback space** (from P2's censorship mechanism): mapped
   fraction and refused elections of previously-mastered frames —
   staleness as *who goes silent*, not *whose error rises*.
4. **What ships: nothing but knowledge** — the I0 reconciliation (the
   instrument of record for the program, with the 022 decimals
   bridged), the measured plane, the censorship mechanism, and two
   named successors. Doc 05 guidance unchanged: competence stands.
