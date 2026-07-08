# Phase 1 Data Model: State Persistence

## 1. Configuration addition

| Field | Type | Default | Validation |
|---|---|---|---|
| `snapshot_every_n_cycles` | int | 0 | ≥ 0; 0 = persistence off (no store needed, no files, validated modes byte-frozen) |

## 2. SystemState (the deserialized form; research R2)

| Part | Contents |
|---|---|
| `format_version` | `"1"` — checked before anything else |
| `config` | every Config field in force (body fields validated on restore; the rest applied) |
| `seed`, `scoring_mode`, `policy_mode` | run identity |
| `frame_store` | `next_id`; per-dim groups: `frame_ids`, `is_candidate`, `age_cycles`, `recon_err_ema`, `pred_err_ema`, `effort_ema`, and the 12 weight tensors (`W1,b1,W2,b2,Dc1,dc1,Dc2,dc2,T1,tb1,T2,tb2`) |
| `counters` | `cycles_done`, `obs_steps`, `obs_after_warm`, `lost_after_warm`, `warmed`, `pop_sum` |
| `accumulators` | `map_fractions`, `pred_errors`, `population_by_cycle`, checkpoint readings so far (`{cycle: (best_dim, population)}`) |
| `agency` | present iff curiosity mode: `pred_error_history`, `observation_memory` (arrays), `values`, `lp_terms`, `novelty_terms`, `directed_steps`, `total_steps` |
| `rng_state` | the single generator's `bit_generator.state` (JSON-safe dict) |
| `tool_registry` | reserved, empty list (Doc 06 §2 — component not yet built) |

**Rules**: capture only at a cycle boundary (C4); apply = full reconstruction —
after `apply`, every array equals the captured one exactly (unit-tested);
byte-identical continuation is the integration-tested consequence (FR-003).

## 3. Blob encoding (research R3)

`.npz` (compressed): one `meta` entry = JSON string (everything non-array),
arrays under stable keys (`g{dim}__{tensor}`, `agency__*`, `acc__*`). Load with
`allow_pickle=False`. Version mismatch → `SnapshotVersionError` before any array
is read. Body mismatch → `SnapshotCompatibilityError` naming field + both values.

## 4. Store entities (research R5)

- `SnapshotStore` (protocol): `write(blob: bytes, metadata: dict) → str`,
  `read(id) → bytes`, `list() → list[tuple[str, dict]]` newest-first,
  `delete(id)`.
- `metadata` (FR-006): `timestamp` (float, wall clock — not part of any
  byte-compared artifact), `step`, `cycle`, `population`, `format_version`.
- `FileSnapshotStore(directory)`: `<id>.npz` files; write = temp + `os.replace`;
  `list` parses committed files only. `InMemorySnapshotStore`: dict-backed
  substitute (contract test + embedding).
- `snapshot_id = f"snap-{step:012d}-{cycle:05d}"` — unique per safe point,
  sortable = newest-first ordering key.

## 5. Engine surface

- `Engine(config, ..., snapshot_store=None)` + config cadence → capture+write at
  end of each Nth offline cycle (and nothing else).
- `Engine.run(seed, resume_from=blob_or_state)` → version/compat checks, world
  rebuilt from seed prefix, RNG state overwritten, frames/counters/accumulators
  /agency applied, warmup + completed cycles skipped, remainder runs normally.
