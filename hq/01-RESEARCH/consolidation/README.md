# Consolidation — does sleep fix the lottery?

**State:** active
**Started:** 2026-08-11

## Abstract

Episode 0091 isolated the bottleneck with six existence proofs and
four inversions: the quadratic head's *representation* carries
ruin-refusal, but per-seed online convergence over 153 correlated
features is a lottery. The owner chose the named regime
("go with consolidation"): the offline learning loop Doc 0004 has
reserved since the beginning — the brain replays witnessed
experience between waking stretches. The honest general form is
**surprise-prioritized replay**: the head buffers the transitions
that carried the largest prediction error when witnessed (no
channel, action, or event type hand-picked — rare consequential
events dominate by their statistics), and consolidates them in
witnessed order during periodic rests. Sleep after school, then
naps: once after the lessons, then every rest of the life.

## The question

With the identical quadratic head, identical world, identical
lessons, and 0091's bars kept verbatim, does surprise-prioritized
consolidation turn six lucky refusers into a cohort — refusal ≤ 10%
at 24-seed power with the lean and the pacing preserved?

## Instrument (frozen with the bars)

- **The consolidated head**: 0091's `QuadHead` unchanged (per-action
  NLMS, η = 0.5, 153 pairwise-product features, zero-init, no RNG)
  plus a replay buffer: every witnessed transition enters with its
  NLMS residual norm as surprise; the buffer keeps the **top 256**
  by witness-time surprise; **every 500 steps** (the rest) the head
  replays the buffer in witnessed order for **4 passes**. After the
  48-lesson pretraining replay (0091's, replay-book assertion kept),
  one consolidation runs before waking — sleep after school. All
  constants frozen; a degenerate pilot amends openly.
- **Everything else is 0091 verbatim**: the mv-graduates cohort and
  books, the drifting and reactive worlds, the shipped arithmetic
  with only `predict_event_delta` substituted, the sharpness log.
  Anchors: linear 25.2% ruinous (0090), online-quad 27.8% with the
  0.00–1.00 per-seed spread (0091).
- **Arms** (24 seeds): **C1** drift; **C2** reactive. **Pilot**
  seeds 1–8 (C1), published before the arms — including the
  per-seed spread, the number this regime exists to collapse.

## Pre-registered bars (0091's, verbatim)

- **CN1 — refusal:** C1 ruinous trades ≤ **10%**.
- **CN2 — the lean preserved:** C1 median rate paid ≤ **7**.
- **CN3 — no collateral:** C1 seeds with ≥ 1 gem ≥ **18/24**; C2
  seeds with ≥ 3 gems ≥ **12/24**.

Registered readings: the per-seed ruinous spread (0091's 0.00–1.00
is the baseline the regime must collapse); sharpness; buffer
composition at end of life (what surprise actually selected —
published, since the no-fiat claim is testable).

## Reversal condition

If CN1 fails with sharpness ≥ 0.90, arbitration is implicated (the
0091 instrument's original escalation). If CN1 fails with sharpness
< 0.90 and the per-seed spread persists, surprise-prioritized
replay at these constants is refuted as the convergence fix — the
remaining named regimes (feature normalization + lower η; targeted
low-order terms) inherit the license, and a second consolidation
dose (larger buffer, more passes) requires its own registration,
not a quiet retune.

## Verdict

**CN1 FAIL · CN2 PASS · CN3 PASS [measured, 2026-08-11, 24 seeds ×
2 arms] — surprise-prioritized consolidation is refuted at these
constants, and the refutation sharpens the diagnosis again.**

- **CN1 — refusal: FAIL at 0.293** — worse than both anchors
  (linear 0.252, online-quad 0.278); pilot 1's encouraging 0.183
  was eight-seed noise. Per-seed spread fully intact (0.00 → 1.00)
  `[measured]`.
- **CN2/CN3: PASS** (median rate 7; 24/24 life, 23/24 reactive
  pacing) — sleep at least did no collateral harm `[measured]`.
- **Sharpness fell: 0.799 vs the online head's 0.874** — the replay
  actively interfered with trade knowledge `[measured]`. Both
  prioritization forms (witness-time; re-evaluated per rest —
  amendment 1, tried and withdrawn at pilot with raw numbers)
  selected locomotion over consequence: residual-based importance
  is the wrong signal in a churning-head regime, and replaying its
  selections at η = 0.5 amplifies the churn that is the disease.

The reversal fires on its second clause (sharpness < 0.90, spread
persists): the remaining named regimes inherit the 0090 license —
**feature normalization + a lower head η** (now the prime suspect:
the churn itself, not replay volume, is the bottleneck) or targeted
low-order context terms. Per this registration's own rule, any
second consolidation dose needs a fresh registration, not a retune.
