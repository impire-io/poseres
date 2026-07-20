# Chapter 41 — The soak before the weeks: C1's deferred questions answered in an afternoon (2026-07-19)

With the staleness program paused and C1 the front, two recorded
deferrals sat under the multi-week run: does reference-scale weight rot
appear at deployment lengths (the ch. 14 open tail), and what does the
ch. 21 drift caveat mean for an unbroken run? Rather than discover the
answers at week two of a live deployment, arc 026 paid for them in
compute: sixteen 500,200-step runs (the C1 cooldown arithmetic),
episodic × continuous, cap off × on, competence drive, instrumented
entirely through snapshots — plus four resumed half-runs to exercise
the persistence guarantee at length.

The headline: **no rot at reference scale over a C1 lifetime.**
Episodic norms are stationary; continuous norms grow slowly and
decelerate but have not plateaued by 500k steps — and since the cap-on
controls show capping is behaviorally free (identical early/late
errors to three decimals), the recorded recommendation is simply to
run C1 with the cap on and close the tail. **Resume is byte-identical
at 500k steps in all four arms** — Doc 06's constitution, now
exercised at deployment length. Two frozen bars failed honestly and
both diagnoses came back "by construction, not defect": continuous
mode fills the population budget and rides it forever at max_frames +
spawn_per_cycle (the evict-then-spawn ordering; measured wall cost of
a ceiling-full brain: ~10%), and snapshot blobs grow ~8 bytes/step
without bound because the per-step error trace is deliberately carried
in-state (feature 003) — 2–20 MB over a three-month C1 run, tolerable,
with a bounded-trace snapshot option named as a future feature that
must first resolve its Doc 06 semantics. Zero src changes; the
mis-anchored bars are recorded as such with the numbers beside them.
**C1 launch posture: GREEN** — cap on, snapshot cadence sized to the
growth, population budgeted at the ceiling. Trail:
`hq/02-DESIGN/validate/C1SOAK-DIAGNOSIS.md`; commits `8ff6808`
(pre-registration), `53437b0` (close).
