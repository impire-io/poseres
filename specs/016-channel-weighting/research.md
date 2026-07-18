# Research: Learned Channel Weighting

All load-bearing decisions were resolved by measurement in
`design/validate/CHANNELWEIGHT-DIAGNOSIS.md` (P1 and E1a/E1b recorded
2026-07-18) before this plan's code stage — the house "diagnose before
fixing" rule applied to a remedy. This file records the decisions and where
each was settled.

## R1 — Estimator statistic: whiteness (lag-1 autocorrelation), not residual floors

- **Decision**: per-channel lag-1 autocorrelation of the observation
  stream, EMAs `m/v/cov/n`, ρ̂ = clip(cov/(v+ε), 0, 1).
- **Rationale**: reads only the observation stream — zero circularity
  (down-weighting the encoder input cannot starve the estimator's own
  evidence), zero anti-gaming surface (no frame state enters the metric it
  is judged by), and **amplitude-invariant** (P1 measured identical
  separation margins at every dose — the failure mode that killed the
  alternative is structurally absent).
- **Alternatives considered**: (a) achievable-floor/variance ratio from
  population-best residuals — rejected: bootstrap deadlock in both init
  polarities, measured-weak contrast exactly at judging ages under
  corruption (0.215 vs 0.20 from the parent arc's E2 numbers), and a
  per-frame `(F, obs_dim)` state footprint; recon-based variants actively
  wrong (static autoencodes through the bottleneck, parent E2 side finding).
  (b) Hybrid whiteness-gate × floor-magnitude — retained as the
  pre-registered X1 fallback only; no current world needs it.

## R2 — Estimator constants: β = 0.995, max-normalized shaping (P1, measured)

- **Decision**: `channel_stats_decay = 0.995`; weights
  `clip(ρ̂/max ready ρ̂, floor, 1)`; readiness `n ≥ ceil(1/(1−β))` = 200
  steps (derived, not a constant).
- **Rationale**: the unique passing combination — separation margin 0.809
  at episode 10 (bar 0.5), no-suppression minima 0.910/0.926 on
  structured/reference (bar 0.9, where β = 0.99 dips to 0.86), smallest
  post-warmup drift (0.05 vs 0.13/0.34). Ready threshold sits at 5
  episodes, inside the 25-episode warmup at every scale (protection window
  grows with obs_dim while convergence stays per-step).
- **Alternatives**: β ∈ {0.98, 0.99} and plain-clip shaping — measured out
  in P1 (recorded table in the trail).

## R3 — Floor semantics: one dial, 0 = off, value = w_min; 0.2 recommended

- **Decision**: `channel_weight_floor: float = 0.0` — the 0-off idiom
  (`weight_norm_cap` precedent); when on, the value is the lower weight
  bound; full exclusion unreachable.
- **Rationale**: the transport argument anchors 0.2 (weighted σ_d = 1.0 ≡
  unweighted σ_d = 0.2, a measured PASS — E1a confirmed: same min every
  age, depth ratios 1.04–1.16), and E1a *measured* full exclusion failing
  (f = 0: min 8 at age 24 at both doses — with static fully silenced,
  spare capacity is free and the 0.02/dim price cannot hold the elbow).
  The floor is load-bearing, not a safety margin.
- **Alternatives**: separate boolean + floor (two dials for one idea —
  rejected); hard exclusion w ∈ {0,1} (measured worse, and permanently
  blinds channels that later become meaningful).

## R4 — Locus and cadence: global on FrameStore, recompute at episode starts

- **Decision**: one global weight vector on `FrameStore`; stats update
  every `online_step`; `w` recomputed only when `prev_obs is None`.
- **Rationale**: channel quality is a world property, not a frame property
  (per-frame weights would hand each frame a knob on its own judge and
  multiply state ×F); `FrameStore` already receives every observation,
  owns persistence and resize hooks, and keeps the engine diff at zero.
  Episode-start recompute keeps every within-episode judgment in one norm
  (the fair-judge window must not drift mid-window) and rides the same
  boundary key as the norm-cap projection — continuous mode's virtual
  boundaries included for free. Multi-stream: all streams funnel through
  the one `online_step`; the merged stream is the estimator's input.
- **Alternatives**: engine-level state (needs signature changes, new
  snapshot home); per-frame weights (gaming surface, cost); per-step
  recompute (mid-episode norm drift under the fair judge).

## R5 — Snapshot: additive-optional keys, no format bump

- **Decision**: `state_dict()["channel_stats"]` = {m, v, cov, n, w} when
  on; snapshot packs `chanw__*` arrays + a meta flag only when present;
  decode tolerates absence → fresh init.
- **Rationale**: the exact pattern of `world_state` / `streams` /
  `current_dims` (features 008/009/010 — none bumped the format);
  feature-off blobs stay bit-identical to the pre-016 format; pre-016
  blobs resume byte-identically under their config-in-force, and loading
  one with the feature newly enabled starts the estimator fresh — stated
  openly (the frontier NaN-deque precedent).

## R6 — Telemetry split: recorder unweighted, survival EMAs weighted

- **Decision**: `pred_error_early/late/improvement` keep their all-channel
  unweighted definitions; the per-frame survival EMAs accumulate the
  weighted fits; summary carries the feature's fields only when on.
- **Rationale**: dose curves must stay comparable with the parent arc's
  record (the E3 secondary bars are stated on the unweighted norm, ceiling
  ≈ 0.23 at σ_d = 1.0); the weighted quantities are what the ecology
  judges, and that is the honest reading for them; the ON-only summary
  fields follow the agency-fields byte-identity pattern (recorder
  precedent).

## R7 — Resize: new channels at full weight until ready

- **Decision**: `resize` extends m/v/cov/n with zeros, w with ones; shrink
  truncates.
- **Rationale**: a grown channel (mid-run tool registration, Doc 02) is
  judged only after one estimator time constant of samples — the same
  optimistic-until-evidence stance the ready gate gives young runs.

## R8 — Scale rules: none needed, argument recorded

- **Decision**: no effective form for either new parameter; a one-line
  note lands beside PRA-01 §8.8.
- **Rationale**: the estimator's convergence is per-step and independent
  of `obs_dim`; the relevant safety margin grows automatically
  (`effective_min_age_cycles` scales up while readiness stays 200 steps),
  so weights are always converged long before judgments at any scale.
