# Contract: SnapshotStore seam + Engine persistence surface (Doc 06 §3)

## 1. SnapshotStore — durable, opaque, atomic

```python
class SnapshotStore(Protocol):
    def write(self, blob: bytes, metadata: dict) -> str: ...  # snapshot_id
    def read(self, snapshot_id: str) -> bytes: ...
    def list(self) -> list[tuple[str, dict]]: ...  # newest first
    def delete(self, snapshot_id: str) -> None: ...
```

**Default:** `FileSnapshotStore(directory)` — one `<id>.npz` per snapshot;
write goes to a temp name then `os.replace` (atomic commit: `read`/`list` never
see a partial write, FR-004). **Substitute:** `InMemorySnapshotStore` (contract
test double). Blobs are **opaque** to the store — it never parses frame
contents (Doc 06 §4.1).
**Metadata MUST include** timestamp, step, cycle, population, format_version
(FR-006); `list()` orders newest first.
**MUST NOT:** interpret blobs, mutate them, or collapse the event-log /
pose-index concerns into this store (Doc 06 §4.2 — those remain named, unbuilt
seams).
**Contract test:** a substitute store passes the same write/read/list/delete
semantics; the engine accepts it unchanged.

## 2. Engine persistence surface

- **Taking**: `Engine(config, snapshot_store=store)` with
  `config.snapshot_every_n_cycles = N > 0` writes a snapshot at the end of every
  Nth offline cycle — the C4 safe point — and nowhere else (FR-002). With the
  default (0 / no store): zero behavior change, zero files (FR-009).
- **Restoring**: `Engine.run(seed, resume_from=blob)` — checks format version
  (reject unsupported, FR-005), validates body compatibility (`obs_dim`,
  `n_actions`; reject with a clear error, FR-008), applies the snapshot's
  config-in-force, rebuilds the world from the seed prefix, overwrites the
  generator state, reconstructs population/counters/accumulators/drive state,
  and runs the remaining cycles.
- **Invariant (FR-003, SC-001):** resumed continuation ≡ uninterrupted run,
  byte-compared on the canonical summary, in both `random` and `curiosity`
  policy modes.

## Cross-seam invariants

- Snapshot capture consumes no RNG and performs no float mutation on run state.
- The blob carries the config in force; body fields are validated, the rest are
  applied on restore (the configuration is part of state, Doc 06 §2).
