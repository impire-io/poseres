# Contract: Configuration + blob format (Doc 06 / Doc 07)

## Configuration

| Parameter | Type | Default | Range / notes | Status |
|---|---|---|---|---|
| `snapshot_every_n_cycles` | int | 0 | ≥ 0; **0 = persistence off** — no store required, no files written, every validated mode byte-identical to the validated build (FR-009) | [D] |

Snapshotting additionally requires a `SnapshotStore` injected into the Engine;
cadence without a store is a no-op (and vice versa). No CLI surface in this
feature — persistence is an engine capability with its own tests.

## Blob format (format_version "1")

- Container: `.npz` (numpy, compressed), loaded with `allow_pickle=False`.
- `meta` entry: JSON string — `format_version` (checked FIRST), full config,
  seed, scoring/policy modes, counters, checkpoint readings, agency scalars,
  RNG bit-generator state, reserved-empty `tool_registry`.
- Array entries: per-dim frame tensors `g{dim}__{name}` (identity, EMAs, 12
  weight tensors), accumulator arrays `acc__*`, agency FIFO arrays `agency__*`.
- **Versioning rule (FR-005)**: an unsupported `format_version` raises
  `SnapshotVersionError` naming the version, before any array is read. Adding
  fields (e.g. a real tool registry) is a version bump.
- **Compatibility rule (FR-008)**: `obs_dim`/`n_actions` must match the booting
  config; mismatch raises `SnapshotCompatibilityError` naming field and both
  values. All other config fields are applied FROM the snapshot.
- Blob bytes are not required to be reproducible across writes (zip
  timestamps); the byte-identity invariant applies to continuation summaries.
