# Surface Contract: The Event Pathway (feature 040)

The v1 public surface grows **additively only** (Doc 0008 policy: keyword-only
additions are legal in minor releases; anything else is a break). This file is
the checklist the surface-guard diff is verified against.

## New inventory entries (`tests/contract/surface_inventory.py`)

| Path | Kind | Family |
|---|---|---|
| `pra.action.policy.CompletionItchPolicy` | class | drive |
| `pra.anatomy.minecraft.C1_MINING_INDEX` | constant | world-body |
| `pra.anatomy.minecraft.C1_POCKET_TOTAL_INDEX` | constant | world-body |

## Existing entries whose element grows (keyword-only-legal, no inventory change)

| Path | Change |
|---|---|
| `pra.config.Config` | + field `event_head_eta: float = 0.0` |
| `pra.action.policy.PolicyContext` | + defaulted field `predict_event_delta` |
| `pra.__version__` | `1.1.0` → `1.2.0` |

## Promised behavior (the contract, testable)

1. **Off-path identity**: with `event_head_eta = 0.0` (default), every run's
   summary, RNG stream, and snapshot bytes are identical to v1.1.0.
2. **Head accessor**: `PolicyContext.predict_event_delta(a)` returns the
   per-action predicted observation delta (`float64[obs_dim]`) when the head
   is on, `None` when off; it never mutates state and never consumes RNG.
3. **CompletionItchPolicy**: constructor keywords as in data-model.md;
   selection draw order identical to `CuriosityLookaheadPolicy` (one ε
   uniform; one integer on the random path; none on the directed path);
   attributes `completions_fired`, `false_completions`,
   `progress_pred_error_ema`, `last_was_directed` readable at any time.
4. **Snapshots**: blobs written with the head on decode in v1.2.0+; blobs
   without the key (older or feature-off) load with a cold-started head when
   the config-in-force enables it. `FORMAT_VERSION` is unchanged.
5. **Constants**: `C1_MINING_INDEX == 14`, `C1_POCKET_TOTAL_INDEX == 15` for
   the current C1 sensor specs, derived not hard-coded.

## Explicitly not promised (internal by default)

- `FrameStore`'s event-head methods and state layout (`event_learn`,
  `event_predict`, the `event_head` state key) — internal seams, free to move.
- The engine's learning call site.
- The recommended operating point (η = 0.5, κ = 0.25, threshold 1/128) — it is
  documentation of the measured G3 values, not API.
