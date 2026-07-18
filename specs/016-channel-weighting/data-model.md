# Data Model: Learned Channel Weighting

## ChannelStats (new, on `FrameStore`; allocated only when on)

| Field | Shape / type | Init | Meaning |
|---|---|---|---|
| `m` | `(obs_dim,)` float64 | 0 | per-channel mean EMA |
| `v` | `(obs_dim,)` float64 | 0 | per-channel variance EMA |
| `cov` | `(obs_dim,)` float64 | 0 | per-channel lag-1 covariance EMA |
| `n` | `(obs_dim,)` float64 | 0 | per-channel sample counts |
| `w` | `(obs_dim,)` float64 | 1 | current weights ∈ [floor, 1]; the only member the judge/learner read |

State transitions:
- **update** (every `online_step`, before forward passes): the registered
  EMA arithmetic; `cov` only advances when `prev_obs` exists.
- **recompute** (episode starts only, `prev_obs is None`): `ready = n ≥
  ceil(1/(1−β))`; `ρ̂ = clip(cov/(v+1e−6), 0, 1)`; ready channels get
  `clip(ρ̂ / (max ready ρ̂ + 1e−6), floor, 1)`, unready stay 1.
- **resize** (anatomy change): grow → append zeros (m/v/cov/n) and ones
  (w); shrink → truncate.
- **snapshot**: all five arrays copied into `state_dict()["channel_stats"]`
  when on; absent otherwise. Restore is verbatim; absence → fresh init.

## Config (two new fields, both [D])

| Field | Type | Default | Validation | Meaning |
|---|---|---|---|---|
| `channel_weight_floor` | float | **0.0** | `0 ≤ f ≤ 1` | 0 = off (pinned validated behavior, byte-identical); > 0 = on, value is w_min. Recommended 0.2 (transport-anchored; E1a-measured). |
| `channel_stats_decay` | float | 0.995 | `0 ≤ β < 1` | estimator EMA decay; read only when on (P1-pinned). |

## Snapshot format (additive-optional; FORMAT_VERSION unchanged)

| Key | Present | Content |
|---|---|---|
| `chanw__m`, `chanw__v`, `chanw__cov`, `chanw__n`, `chanw__w` | only when the snapshotted run had the feature on | the five arrays |
| `meta["channel_stats"]` | same condition | `true` |

Feature-off snapshots are bit-identical to the pre-016 format. Pre-016
blobs decode with no `channel_stats` entry → fresh init on load.

## Run summary (ON-only fields; agency-fields pattern)

When the feature is on, the serialized summary carries a
`channel_weighting` block: `{floor, decay, final_weights (rounded),
ready_channels}`. When off, the block is absent and the summary is
byte-identical to the pre-016 serialization.

## Untouched

`FrameState`, `FrameGroup._GROUP_FIELDS` (the estimator is store-level,
not per-frame/per-group), the recorder's error-norm definitions, every
existing config field, the engine's step/cycle structure.
