# Contract: Configuration additions (Doc 07)

Every new parameter is a field of the existing frozen `Config` with the default
below; construction rejects out-of-range values before any run starts. All are
first-class, none are scale rules (validated at the reference scale first —
plan: Scale/Scope).

## Drive block

| Parameter | Type | Default | Range / notes | Status |
|---|---|---|---|---|
| `drive_weights` | mapping name → float | `{"curiosity": 1.0}` | non-empty; finite weights ≥ 0; names must match the registered drive roster one-to-one | [D] |
| `w_progress` | float | 1.0 | ≥ 0; curiosity learning-progress weight | [O] tunable |
| `w_novelty` | float | 1.0 | ≥ 0; curiosity novelty weight | [O] tunable |
| `lp_recent_window` | int | 60 | ≥ 1; steps in the recent error window | [O] tunable |
| `lp_baseline_window` | int | 600 | > `lp_recent_window`; steps in the baseline window | [O] tunable |
| `novelty_memory_size` | int | 200 | ≥ 1; bounded recent-observation FIFO depth | [O] tunable |

## Policy block

| Parameter | Type | Default | Range / notes | Status |
|---|---|---|---|---|
| `policy_mode` | enum | `random` | `random` \| `curiosity`; **`random` is the pinned validation baseline** — every existing mode keeps it and stays byte-identical (FR-008) | [D] |
| `exploration_epsilon` | float | 0.1 | in [0, 1]; uniform-random override probability | [D] |
| `lookahead_min_age_cycles` | int | 2 | ≥ 0; best-frame maturity bar below which the policy stays random (Doc 05 §4.3) | [D] |

## Behavioral requirements

- **Immutability (FR-003).** All fields above are frozen at construction; no
  runtime process may write them. Attempted mutation raises.
- **Baseline pinning (FR-008).** With `policy_mode="random"` (default) the RNG
  consumption, behavior, and serialized summaries of every existing mode are
  byte-identical to the validated build. `pra-validate agency` selects
  `curiosity` for its curious arm explicitly.
- **Determinism (FR-007).** The config plus seed fully determine an agency run;
  re-runs are byte-identical.
- **Counter-drive path (US5).** Adding a second drive = extending
  `drive_weights` and registering the drive in configuration — no code change
  to Engine, policy, or harness.
