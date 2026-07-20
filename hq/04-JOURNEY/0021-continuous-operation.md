# Chapter 21 — Feature 008: continuous operation — the slow loop was always a cadence (2026-07-13)

ROADMAP B3, the first engine-semantics change since the anatomy layer, and
the roadmap demanded the design in writing first. The design's core
finding made the implementation almost disappear: **every episode-keyed
mechanism already keys off the transition-chain break and the within-span
index** — the norm cap projects when `prev_obs is None`, the fair judge
counts `t < K`, warmup counts spans, consolidation was always "every N
episodes of experience," never "after N resets." So continuous mode is
one changed line in the episode loop (reset → carry the trailing
observation, which episodic mode discards) plus an engine-enforced
**single boot** — `reset()` called exactly once, the world's one chance
to prepare (a homing routine, a login): the contract C2 was promised,
proven against a guard world that raises on any second call. Virtual
episodes carry everything else untouched; zero store/scorer/drive/body
edits.

The design surfaced one real problem before code did: continuous resume
cannot ride Doc 06's world-from-seed rule (a world's mid-run state is the
product of its whole action history). Answer: an optional world-state
capture protocol (`state_dict`/`load_state_dict` — in-repo worlds
implement it in a few lines; the Body delegates per-instance; the
snapshot blob gains an optional entry written only in continuous mode, so
episodic blobs carry no trace and old blobs decode unchanged), and a loud
capture-time failure for worlds that can't — external-world capture stays
B5's, named. The spec's original "seed-derivable" resume claim was
amended openly when the design refuted it.

The reading (pre-registered guess, half wrong, recorded): on the
**reference world** continuous operation collapses learning — improvement
−0.17 mean, `best_dim` → 1, 8/8 seeds — because the unbounded latent walk
drifts and the tanh emission saturates; the guess predicted the
improvement hit but called structure "less affected," and it collapsed
hardest (parsimony working correctly on a degenerated world). The
discriminator run settled the attribution: on the **bounded** rover arena
continuous mode is healthy (improvement in-band, `best_dim` 2/2/2, no
collapse). The mode works; **continuous deployments need recurrent
worlds** — the reference world is an episodic instrument, and the
guidance for C1/C2 is now written down with a reproducible drift
signature. Gate: 267 tests green (18 new). Trail:
`specs/008-continuous-operation/` (spec with its open amendment, research
R1–R10, contracts, reading.md).
