# Implementation Plan: Learned Channel Weighting (The L3-Noise Remedy)

**Branch**: `016-channel-weighting` | **Date**: 2026-07-18 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/016-channel-weighting/spec.md`

## Summary

Ship the remedy chapter 25 named, opt-in and reference-preserving: a
per-channel whiteness estimator (lag-1 autocorrelation of the observation
stream — amplitude-invariant, learning-free, un-gameable) living on
`FrameStore`, producing one weight vector `w ∈ [floor, 1]^obs_dim` at
episode starts, applied simultaneously to the survival norms (weighted
numerator AND denominator of `fit_quality` / `honest_pred_err`) and the
learning path (`encode` consumes `w⊙obs`; `learn_placement` backprops
`(recon − obs)⊙w` with the weighted input in the encoder outer product;
`learn_transition` inherits leg B through its `encode` calls). Two config
dials: `channel_weight_floor` (0.0 = off = byte-identical pinned behavior;
0.2 is the transport-anchored recommendation) and `channel_stats_decay`
(0.995, pinned by probe P1). Estimator state (m, v, cov, n, w) rides the
snapshot under additive-optional keys — no format bump; pre-016 blobs load
unchanged.

The science governs the build: `design/validate/CHANNELWEIGHT-DIAGNOSIS.md`
is pre-registered and already past its gate — P1 pinned β = 0.995 with
max-normalized shaping (separation margin 0.809 at episode 10, identical at
every dose because whiteness is amplitude-invariant), E1a confirmed the
transport prediction with oracle weights on both legs (f = 0.2 at σ_d = 1.0
lands the unweighted σ_d = 0.2 surface; corruption healed to 0.98–1.02× the
healthy baseline; f = 0 full exclusion FAILS — the floor is load-bearing),
and E1b broke the conveyor live (8/8 seeds mature frames, winners 0.11–0.28
under bars 0.30–0.51). What remains after the code ships: E2
(identification), E3 (live rescue, 8 → 24 seeds), E4 (no-harm), outcome +
propagation.

## Technical Context

**Language/Version**: Python ≥ 3.12 (repo `.venv` runs 3.14; unchanged).
**Primary Dependencies**: numpy only — no new dependencies, no extras
changes.
**Storage**: none new — five `(obs_dim,)` float64 arrays inside the
existing snapshot npz under `chanw__*` keys, written only when the feature
is on.
**Testing**: pytest — unit (estimator math on constructed streams, weighted
norm/learning identities, no-RNG twin-engine proof), integration (ON smoke
on L3 noise, summary-fields gating, snapshot ON round-trip, OFF blob format
equality), plus the untouched byte-frozen suite.
**Project Type**: core-package extension (`src/pra/core/frame.py`,
`src/pra/config.py`, `src/pra/persistence/snapshot.py`,
`src/pra/harness/report.py`) + tests.
**Performance Goals**: estimator update is ~6·obs_dim flops per step,
weight recompute O(obs_dim) per episode; the off path adds one branch and
zero float work.
**Constraints**:
- **Byte-frozen reference** (FR-005/SC-004): default `Config()` reproduces
  the pinned seed-1 values, determinism, ladder streams, and snapshot bytes
  exactly; the off path performs no float work and no RNG.
- **No RNG ever** (FR-006): the feature consumes zero random draws even
  when ON — ON/OFF twin runs see identical world event streams (this is
  what makes E4's paired reads exact).
- **Judging and learning agree** (FR-003): one `w`, used identically in
  norms and gradients; weights recompute only at episode boundaries
  (FR-004, the `prev_obs is None` key — virtual boundaries included).
- **Telemetry meaning preserved** (FR-008): recorder norms stay unweighted;
  survival EMAs are the weighted quantities; summary fields appear only
  when ON (agency-fields pattern).
- **Snapshot completeness** (FR-007, Doc 06 §2): estimator state travels;
  resume byte-identical to uninterrupted; OFF blobs bit-identical to the
  pre-016 format; pre-016 blobs load with default init.
- **Anatomy resize** (FR-009): stats extend with zeros and w = 1 for new
  channels (full weight until ready), truncate on shrink.
- **The trail is normative** (FR-010): E-gates in pre-registered order;
  exits binding; the recorded L3 FAIL never amended.
**Scale/Scope**: validated at the ladder's recorded scale (obs_dim = 20);
the no-new-scale-rule argument (estimator convergence is per-step and
obs_dim-independent while the protection window grows at scale) lands as a
one-line note beside PRA-01 §8.8.

## Constitution Check

Constitution file remains the unfilled template; gating against project
rules (AGENTS.md) and the spec:

| Gate | Requirement | Status |
|---|---|---|
| Regression | validated behavior byte-frozen; T1–T6 + ladder + snapshots reproduce | PASS — off path is the textually-current expressions behind one branch; guarded by the pinned baseline, determinism, stream, and blob-format tests |
| Opt-in | new capability leaves existing modes' RNG stream, behavior, serialized summaries untouched | PASS — `channel_weight_floor = 0.0` default; summary fields gated ON-only |
| Diagnose before fixing | mechanism measured before remedy; remedy gated before code | PASS — parent arc measured the mechanism; this arc's E1 oracle gate passed before this plan's code stage |
| Honest measurement | spreads, paired reads, pre-registered bars, FAIL is data | PASS — trail doc carries all bars and exits; E3 confirmatory at 24 seeds; E4 paired per seed via the no-RNG constraint |
| Reference-preserving parameters | inert defaults; effective forms where scale-dependent | PASS — 0.0-off idiom (`weight_norm_cap` precedent); no new scale rule needed, argument recorded |
| Research in scratchpad | probes stay out of git; conclusions land in the trail | PASS — P1/E1a/E1b already followed it |
| Quality gate | ruff format + ruff check + pytest, none skipped | PASS — gated in tasks |

## Project Structure

### Documentation (this feature)

```text
specs/016-channel-weighting/
├── spec.md, plan.md, research.md, data-model.md, quickstart.md
├── checklists/requirements.md
├── contracts/channel-weighting.md   # estimator / application / off-path / snapshot contracts
└── tasks.md                         # (/speckit-tasks output)
```

### Source Code (repository root)

```text
src/pra/core/frame.py            # ChannelStats state + update + episode-start recompute on
                                 #   FrameStore; w threaded through FrameGroup.encode /
                                 #   fit_quality / honest_pred_err / learn_placement /
                                 #   learn_transition (w=None → textually current math);
                                 #   state_dict / load_state_dict / resize coverage
src/pra/config.py                # channel_weight_floor (0.0 = off), channel_stats_decay
                                 #   (0.995) + validation
src/pra/persistence/snapshot.py  # chanw__* keys + meta flag, additive-optional
                                 #   (world_state/streams pattern); decode → default init
src/pra/harness/report.py        # echo the two params in the report config block when on

tests/unit/test_channel_weighting.py        # NEW — estimator math, weighted identities,
                                            #   no-RNG twin proof, resize
tests/integration/test_channel_weighting_runs.py  # NEW — ON smoke, summary gating,
                                            #   OFF-explicit byte equality
tests/integration/test_snapshot_completeness.py   # EXTEND — ON round-trip, OFF blob
                                            #   format equality, pre-016 blob + ON refill
```

## Design (frozen by the trail doc; transcribed for the implementer)

**Estimator state** — five `(obs_dim,)` float64 arrays on `FrameStore`,
allocated only when `channel_weight_floor > 0`: `m` (mean EMA), `v`
(variance EMA), `cov` (lag-1 covariance EMA), `n` (sample counts), `w`
(current weights, init 1.0). Update at the top of `online_step`, exactly:

```
m ← β·m + (1−β)·obs
d = obs − m                       # post-update m
v ← β·v + (1−β)·d²
cov ← β·cov + (1−β)·d·(prev_obs − m)   # only when prev_obs is not None
n ← n + 1
```

**Recompute** at episode starts only (`prev_obs is None`), before the
step's forward passes:

```
ready = n ≥ ceil(1/(1−β))         # 200 steps at β = 0.995
ρ̂ = clip(cov / (v + 1e−6), 0, 1)
w[ready]  = clip(ρ̂ / (max ρ̂ over ready + 1e−6), floor, 1)
w[~ready] = 1
```

**Application** — `FrameGroup` methods take `w: np.ndarray | None = None`;
`None` is the exact current code path (no multiplications). When given:
`encode` uses `x = w⊙obs`; `fit_quality`/`honest_pred_err` divide weighted
numerator by `‖obs⊙w‖ + ε`; `learn_placement` uses `e = (recon − obs)⊙w`
and `gW1 = clip(ghe ⊗ x)`; `learn_transition` inherits via its `encode`
calls. `effort` and pose-space math untouched. The scratchpad E1
instruments (a `FrameGroup` subclass and a live monkeypatch) already
exercised exactly these formulas — the implementation transcribes them.

**Store plumbing** — `FrameStore` owns the weight vector and passes it to
every group call when on; `resize` extends `m/v/cov/n` with zeros and `w`
with ones; `state_dict`/`load_state_dict` carry a `"channel_stats"` dict
when on, defaulting to fresh init when absent (pre-016 blobs, OFF
snapshots). Multi-stream needs nothing: all streams already funnel through
the one `online_step`.

**Engine** — one call site: `online_step` already receives per-step
observations and the episode-boundary signal (`prev_obs is None`); the
estimator hooks ride inside `FrameStore`, so `engine.py` needs no edits
beyond none at all (target: zero engine diffs; if plumbing forces one, it
must be a pure pass-through recorded in the tasks).

## Verification

- Quality gate at every commit: `./.venv/bin/ruff format --check . &&
  ./.venv/bin/ruff check . && ./.venv/bin/pytest -q` — green, none skipped.
- The byte-identity family (pinned baseline, determinism, ladder streams,
  blob formats) with the feature absent-by-default.
- The twin-engine no-RNG proof: same seed, ON vs OFF, identical world
  observation streams and frame-birth draws.
- Then the trail's remaining E-steps (E2/E3/E4) run against the shipped
  code via `pra-validate ladder --config` overrides and scratchpad trace
  instruments, results appended to the trail.
