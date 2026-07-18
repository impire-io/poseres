# Emission-shift arc — the testbed pair completed, and its first baseline read

Date: 2026-07-18. PLACEMEM-DIAGNOSIS (ch. 33) closed with a testbed note:
the 017 shifting world confounds "knowledge went stale" with "territory
changed". This arc ships the complement — `shift_mode="emission"` on the
shifting world: per-object emission matrices swap at the boundary (drawn
at construction after all other draws, object order; zero RNG at shift
time) while displacements never change, so the latent trajectory
distribution is fixed and only appearance moves. Default mode
`"dynamics"` is the recorded 017 behavior, byte-identical.

## P1 — the first baseline read (pre-registered before running)

The chapter-33 offline place-memory replay (K = 32 episode-start anchors,
fast EMA at `ema_decay`, running min, staleness = fast − best; the
as-registered arithmetic, no revisions), run over captured live
frontier-arm traces on the emission-shift world (seeds 1–3, shift at
6760, same windows), judged with the same frozen bars (post-shift median
> 0, > 4× pre-shift, > 4× the recorded multiregion benign floor 0.110).

**The prediction is deliberately left open — two mechanisms compete.**
(a) *Structural failure again*: post-shift observations come from fresh
emission matrices, landing far from every anchor; nearest-anchor
assignment becomes arbitrary and the signal may not separate.
(b) *Crude detection*: unlike the dynamics shift, ALL post-shift errors
jump at once and every post-shift observation still gets assigned to
*some* anchor whose `fast` then rises above a mastered `best` —
raw-observation places might read an emission shift even though they
cannot read a dynamics shift. Either way the number becomes the recorded
baseline the shift-invariant-memory research is judged against.

## Result: P1 (recorded 2026-07-18)

| seed | pre-shift median | post-shift median | vs 4× pre | vs 4× benign (0.440) |
|---|---|---|---|---|
| (recorded below after the run) | | | | |

## Failure exits

None beyond honesty: both P1 outcomes are recorded baselines, not
gates — the world ships on its unit-tested contracts either way. The
detector research (pose/encoding anchors, spike-robust statistics) is
the successor arc and inherits this baseline.
