# Feature Specification: Place-Indexed Error Memory (The Map That Remembers Mastery)

**Feature Branch**: `019-place-memory`
**Created**: 2026-07-18
**Status**: Draft
**Input**: User description: "Place-indexed long-horizon error memory — the
representation predictive LP needs (research arc 019). Chapter 32 measured
why every trend statistic fails: the err@visit memory is a ~5-episode
sliding FIFO, so the pre-change baseline is forgotten before stale ground
is re-encountered. This feature gives the brain a small map of anchor
places, each remembering its current error level and the best level ever
achieved there — so 'what error was here when I knew this region' survives
indefinitely and 'knowledge went stale here' becomes computable. A scout
drive reads it. Gated offline before any code (replay on captured traces),
then measured against the frozen 017 grid with chapter-31's
competence-AND-random-relative bars."

## Overview

Chapter 32 stopped the scout drive at its gate: no comparison over a
sliding window can see a regime change, because the window forgets the
baseline in ~5 episodes. The fix is a representation, and the smallest one
that works is nearly constant-free: **K anchor observations** (allocated
deterministically from episode-start observations until the map is full —
no randomness, no distance threshold), each holding two numbers — a **fast
EMA** of the prediction errors observed in its neighborhood (reusing the
existing `ema_decay`), and a **running minimum of that EMA**: the best
error level the brain ever achieved near that place. Mastery, once
reached, is never forgotten by the map.

**Staleness** at a place is then `max(0, fast − best)`: zero while
performance sits at its historical best (mastered), zero while a region
has never been learned (fast ≈ best ≈ high, tracking together), and
positive exactly when errors *rise above what was once achieved* — the
signature of a world that changed under mastered knowledge. The **scout
drive** values a lookahead candidate by the staleness of its nearest
anchor. The noisy-TV guard is structural: an unlearnable region's fast EMA
fluctuates around a plateau it never improves on, so fast − best stays
near the fluctuation floor, not the signal scale — and the offline gate
measures exactly this margin before any code ships.

One dial: `place_memory_size` (0 = off — byte-identical, no state, no
RNG). The memory lives in the agency bookkeeping (curiosity mode only),
rides snapshots when on, and the drive is opt-in via the registry like
every drive before it.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Stale ground is detected and re-engaged (Priority: P1)

On the shifting world, a scout-bearing brain sees staleness light up where
its mastered knowledge went quiet-wrong, steers back, and recovers faster
than both the camper and undirected exploration.

**Independent Test**: offline replay first (captured traces, no code);
then live arms at 24 seeds vs the frozen 017 baselines.

**Acceptance Scenarios**:

1. **Given** captured shifting-world traces, **When** the anchor memory is
   replayed over them, **Then** post-shift staleness separates from
   pre-shift background by the pre-registered margin (the offline gate,
   before any src change).
2. **Given** the live scout arms at 24 seeds, **Then** the pre-registered
   primary (post-shift recovery beats both competence and random) is
   decided — PASS or an honestly recorded FAIL.

---

### User Story 2 - The map costs nothing when off, little when on (Priority: P1)

Any configuration with `place_memory_size = 0` (default) is byte-identical
to the current build. With the map on but the world benign (multi-region,
pre-shift), staleness stays near zero and scout-bearing arms are
noninferior to competence.

**Acceptance Scenarios**:

1. **Given** the default config, **Then** RNG stream, behavior, summaries,
   and snapshot bytes are unchanged (the standing byte-identity family).
2. **Given** the map on, **When** a run snapshots mid-life, **Then** the
   resumed run continues byte-identically (anchors, EMAs, and minima
   travel).

---

### Edge Cases

- **Cold map**: no anchors yet → scout reads 0 (silent, like every drive's
  cold start).
- **Unvisited anchors**: first sample seeds fast = best (staleness 0) —
  no zero-init bias, no warm-up constant.
- **Continuous mode**: anchor allocation keys on virtual episode starts,
  the boundary every mechanism already honors.
- **No RNG anywhere**: allocation is first-K-by-episode-start; assignment
  is nearest-anchor; ties break by lowest index.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST maintain, when `place_memory_size = K > 0`
  and the run is in curiosity mode, K anchor observations allocated from
  episode-start observations in order until full, then frozen; each anchor
  holds a fast error EMA (decay = `ema_decay`) and the running minimum of
  that EMA, updated from each step's error-at-visit under nearest-anchor
  assignment (ties to the lowest index). No randomness is consumed.
- **FR-002**: The system MUST provide a `"scout"` drive in the registry
  valuing a candidate observation by `max(0, fast − best)` of its nearest
  anchor; 0 with no anchors. Opt-in via `drive_weights` only.
- **FR-003**: `place_memory_size = 0` (default) MUST be byte-identical to
  the current build in every mode; the map's state MUST ride snapshots
  when on (ON-only additive keys) and resume byte-identically.
- **FR-004**: The research protocol in
  `design/validate/PLACEMEM-DIAGNOSIS.md` is normative: the offline replay
  gate (P1) runs before any src change; E1 bars are frozen before any run;
  the 017 grid is the frozen baseline; exits are binding.

### Key Entities

- **Place map**: K anchors × (observation, fast EMA, best-ever EMA, visit
  count) — agency state, snapshot-carried when on.
- **Scout drive**: registry id `"scout"`, reads staleness at the nearest
  anchor.
- **Trail** (`design/validate/PLACEMEM-DIAGNOSIS.md`).

## Success Criteria *(mandatory)*

- **SC-001**: The offline gate decides the representation question on real
  traces before any code: post-shift staleness separates from pre-shift
  and from benign-world background by the frozen margins.
- **SC-002**: The live primary is decided at 24-seed power against the
  frozen 017 baselines (beat both competence and random post-shift), PASS
  or recorded FAIL.
- **SC-003**: No harm: byte-identity off; pre-shift and multi-region
  noninferiority vs competence on.
- **SC-004**: Outcome propagated (Doc 05, Doc 07, ROADMAP, JOURNEY ch. 33)
  whatever the verdict.

## Assumptions

- Errors-at-visit (the per-step mean elect prediction error already
  recorded by the agency) are the right error signal for the map — the
  same quantity every drive already consumes.
- First-K-by-episode-start allocation covers the visited space adequately
  at reference scale (K default candidate: 32; frozen in the
  pre-registration); smarter allocation (drift, replacement) is named
  future work, not v1.
- Feature numbering follows the branch (`019-place-memory`); JOURNEY
  chapter 33.
