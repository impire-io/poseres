# Phase 0 Research: Brain Seeding

All Technical Context items resolved (no `NEEDS CLARIFICATION` remain). The
load-bearing decisions below were settled with the owner (session Q&A,
2026-07-20) and grounded in a code survey of the existing seams. Format:
Decision / Rationale / Alternatives considered.

## R1 — Testbed: the rover world (maps = layouts)

- **Decision**: Use the rover (feature 006) as the seeding testbed; maps A/B/C are
  the rover's obstacle+spawn layout at different draws, same body and physics.
- **Rationale**: The rover is bounded and stationary, so "reached competence" is a
  stable line (unlike the reference EventSource world, which drifts/saturates when
  run unbroken — the B3 finding). It is also the natural "shareable brain"
  demonstrator, aligning the measurement with the product narrative. It produces a
  per-checkpoint prediction-error trajectory through the unchanged `Engine.run`,
  so time-to-competence needs no new telemetry.
- **Alternatives considered**: the reference/ladder synthetic worlds (the
  paired-margin harness already runs there — but drift makes a competence line
  murky and there is nothing watchable). Rejected as the primary testbed; the
  synthetic path remains available for future cross-checks.

## R2 — Maturity control: the permuted rover

- **Decision**: The maturity control matures on a *permuted rover* — a
  construction-time fixed permutation of action semantics and/or observation
  channels — for the identical experience budget, then hops to the real map.
- **Rationale**: It keeps body shape and experience exactly matched while making
  the learned mapping *wrong* for an un-permuted map, so the control isolates a
  head start from *relevant* structure vs. one from mere maturity/size. A pure
  noise world was rejected: the brain must actually mature (grow a real
  population), which requires a learnable world.
- **Alternatives considered**: mature on an existing abstract world — rejected
  because its body shape differs from the rover's, forcing a resize to move it
  onto a rover map and muddying the very comparison the control exists to clean.

## R3 — Competence metric: time-to-threshold

- **Decision**: Competence = smoothed prediction error crossing a pre-registered
  line θ; the per-seed reading is τ = the first checkpoint where smoothed error ≤
  θ. Margins are differences in τ (lower τ = faster).
- **Rationale**: Directly matches the roadmap's "reaches threshold in less
  experience" and makes "does the head start shrink across hops?" a clean scalar
  (Δ of τ-margins). Lower-is-better τ inverts naturally into positive = seeded
  faster.
- **Alternatives considered**: fixed-budget final quality (simpler, but measures
  "how much better," not "how much sooner" — a weaker match to a head-start
  claim). Rejected as primary; final-quality can be reported as context.

## R4 — Randomness ownership: a harness-owned layout seed

- **Decision**: Split rng by ownership (the 009/017 discipline). The rover layout
  is drawn from a `layout_seed` the harness owns; per-episode spawn choice and
  sensor noise come from a world-owned stream derived from it; the brain's
  exploration randomness is owned by the brain (carried in the snapshot for
  seeded/maturity arms, drawn from the run seed for fresh). Map X at seed *s* uses
  `layout_seed = H(s, "A"|"B"|"C")`.
- **Rationale**: All three arms at a given seed must face the *same* new map for
  the pairing to be fair; only the starting brain may differ. Today the rover ties
  its layout to the single engine rng, so the layout is not independently
  addressable — this decouples it. The degenerate path (layout seed == run seed,
  one stream) stays byte-identical to today's rover.
- **Alternatives considered**: vary maps by run seed alone (couples layout to
  brain randomness — the arms would face different maps, breaking pairing).
  Rejected.

## R5 — The resize hop: +1 sensor

- **Decision**: Between B and C the seeded (and maturity) chain grows its body by
  one sensor (obs_dim 10 → 11) via the existing `register_sensor` →
  `apply_pending_tools` → `FrameStore.resize` path, applied identically to all
  chained arms at the same boundary.
- **Rationale**: The smallest honest body change, and the roadmap flags transfer
  *benefit* across `resize()` as genuinely unmeasured (only bit-preservation is
  guaranteed). +1 exercises the grow-and-resume path without confounding the hop
  with a large anatomy change.
- **Alternatives considered**: keep the body fixed on hop 2 (simpler, but does not
  test the "survives a body change" half of the claim); a larger multi-sensor
  growth (more confound, no extra signal). Rejected in favor of +1.

## R6 — Statistical form: reuse the paired ±1.9·SE test

- **Decision**: Per-seed paired margins, one-sided. Superiority PASS iff
  `mean(margin) > +1.9·SE`; non-shrink (noninferiority) PASS iff `mean(Δ) ≥
  −1.9·SE`. Sign-counts, full per-seed spread, and reach-rates always reported
  alongside the verdict.
- **Rationale**: This is the repo's established form (`acceptance.py` `_margins_vs`
  / T7 `T7_NONINFERIORITY_T = 1.9`), so the seeding verdict is comparable to every
  prior arc and inherits its openly-recorded caveats (continuous margins, sign
  degeneracy).
- **Alternatives considered**: a fresh bespoke test (needless divergence from
  precedent). Rejected — reuse the existing form and helpers.

## R7 — Censoring: conservative, with reach-rates

- **Decision**: An arm whose smoothed error never crosses θ within `N_probe` is
  right-censored at `N_probe`; the margin uses the censored value, and per-arm
  reach-rate (fraction reaching θ) is reported separately.
- **Rationale**: Censoring at the budget never inflates a seeded advantage beyond
  what was observed; reach-rate keeps the censoring visible rather than hidden in a
  mean. `N_probe` is pilot-set generously (≥ 2× median fresh τ) so fresh censoring
  is rare.
- **Alternatives considered**: drop censored seeds (biases toward fast learners);
  survival-analysis models (overkill for the pre-registered scalar bars).
  Rejected.

## R8 — θ and budgets: pilot-then-freeze

- **Decision**: The *procedure* is fixed now (θ = the smoothed-error level where
  the median fresh brain has closed p = 0.5 of its initial→plateau gap; `N_pretrain`
  = map-A plateau; `N_probe` ≥ 2× median fresh τ; `W_smooth` = smallest window
  making the fresh median crossing monotone). The *values* are set by an
  exploratory pilot and frozen/committed in `SEEDING-DIAGNOSIS.md` before the
  confirmatory 24-seed run.
- **Rationale**: The honest form of "measurable but not yet measured" — it avoids
  guessing thresholds while guaranteeing no criterion is tuned after the
  confirmatory data (ROADMAP principle 4; the T7 precedent).
- **Alternatives considered**: guess θ/budgets now (risks an unreachable or
  trivial line); tune after seeing confirmatory data (forbidden). Rejected.
