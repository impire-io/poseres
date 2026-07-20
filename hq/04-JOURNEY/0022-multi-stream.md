# Chapter 22 — Feature 009: multi-stream — the merge does no harm, and a protocol gets caught (2026-07-13)

ROADMAP B4, design-first: K world instances of one hidden structure
(identical construction seeding, per-stream generators assigned
afterward from spawn keys), K independent explorers, one brain, merged
by a fixed episode round-robin (`e mod K`). The design's two load-bearing
choices: **randomness split by ownership** (stream generators carry world
noise and policy exploration; the brain generator carries
births/proposals/decay, consumed in merge order — the roadmap's
"per-stream seeds, merged deterministically" made concrete), and
**cadence in total experience** (consolidation counts merged episodes,
so equal schedules mean equal experience at every K — chapter 21's
lesson now doing load-bearing work). Every within-episode mechanism is
episode-local and therefore stream-local for free; K=1 is the untouched
validated path (frozen baseline still green through the loop refactor);
K>1 snapshots fail loudly naming B5. Pre-registered before measuring:
episodic streams under the random policy are near-exchangeable — the
reference-world comparison is the *null case*; continuous mode is where
streams genuinely differ.

The measurement then caught the measurer. The pre-registered 8-seed
comparison **FAILed its noninferiority bar** (mean margins −0.040/−0.046
at K=2/4, just past the bounds) — against the pre-registered null. The
diagnosis found the flaw in the protocol, not the regime: the bar
borrowed T7's *paired* form, but a K>1 run necessarily uses different
generator realizations than K=1, so the "paired" margins were unpaired
differences of two seed-noise draws (spread ≈ √2 × the improvement std —
the exact unpaired signature) and eight seeds were underpowered. At 24
seeds the margins collapse to ≈ 0 (−0.0044 and −0.0030, bounds −0.025
and −0.030): **noninferiority PASSES at both K** — merged experience
matches focused experience per observation, the safety result B4 needed,
and the null confirmed. Both protocols and the amendment are in the
record (specs/009-multi-stream/reading.md), plus the general lesson, now
written down: a pairing bar is only as good as what the arms actually
share; cross-realization comparisons need unpaired power stated up
front. The continuous-rover reading (K explorers at K positions of one
arena) is recorded investigatory at n=3 — the substantive multi-stream
research (directed policies, longer horizons, world-side wall-clock
parallelism, the external bus backend) now has its instrument. Gate: 277
tests green (10 new). Fourth feature closed in one day; Phase B has one
item left (B5, holding three named snapshot debts).
