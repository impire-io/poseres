# Chapter 32 — The scout that never left camp: a gate does its job (2026-07-18)

The shortest arc in the record, and deliberately so. Chapter 31 named
the frontier's failure mechanism — realized LP is a lagging indicator —
and the obvious fix wrote itself: the **scout drive**, the same
2k-neighbor statistic with the halves swapped (`max(0, newer − older)`),
positive where local error has *risen* — stale knowledge, the shift
signature — zero on flat-high noise and flat-low mastery, no new
constants. The pre-registration froze the bars competence- AND
random-relative (the chapter-31 clause lesson), pointed the arc at the
frozen 017 grid as an exactly-paired baseline, and put one probe in
front of all code: P1, the signal shapes on *real traces*, with X0
saying stop if the mirror can't see the shift.

It can't — and the reason is worth more than the drive would have been.
On live frontier-arm traces the scout median is zero everywhere,
post-shift included, while the frontier median is positive everywhere —
**including on mastered pre-shift ground** (0.03–0.07). Fine-grained
bins show the shift is not invisible (scout fires on 26% of post-shift
reads, maxima ~3× background in the memory-straddle window) but not
separable: it also fires pre-shift, and the frontier reads positive
straight through. The cause is representation, not arithmetic: the
err@visit memory is a **200-entry sliding FIFO (~5 episodes)** — the
pre-shift baseline is forgotten within ~200 steps of the shift, and the
window's residual recent-trend noise feeds both statistics wherever
global error drifts. A retrospective light on chapter 24, recorded
openly: part of the frontier's recorded signal was this same
sliding-window trend, one more reason its live edges matched random's.

The arc stopped at X0 with **zero src changes** — the pre-registered
complete deliverable. What it bought: the successor is now measured,
not conjectured — predictive LP needs **place-indexed, long-horizon
error memory** (slow decay, spatially anchored: "what error was here
when I knew this region" must survive long enough to compare with "what
error is here now"), a Doc 05 design feature with its own
snapshot/scale surface. The 017 worlds and their 576-run grid still
wait as its testbed. Doc 05 guidance unchanged: competence stands.
Trail: `hq/02-DESIGN/validate/SCOUT-DIAGNOSIS.md` (pre-registration, P1,
outcome), `specs/018-predictive-lp/spec.md`; commits `2e90c99`
(spec + pre-registration), and this close.
