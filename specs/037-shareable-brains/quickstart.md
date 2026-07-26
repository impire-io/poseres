# Quickstart: sharing a brain

"Here's my rover brain after 100k steps — load it."

## Person A: publish

Run with snapshotting on (any `FileSnapshotStore` directory), then
export the newest snapshot as one portable file:

```bash
pra-brain export --store runs/rover/snapshots --out rover-100k.brain \
    --note "rover brain, 100k steps, seed 7"
```

Prefer a specific snapshot? Name it: `--snapshot snap-000000100000-00500`
(ids come from `pra-brain export`'s output or the store's `list()`).

The file is a plain zip with two members — `manifest.json` (what it
is: sha256 of the blob, snapshot format version, pra version,
obs_dim/n_actions, step/cycle/population, your note, created-at) and
`snapshot.bin` (the snapshot blob, byte-untouched). Same brain + same
manifest = byte-identical file.

## Anyone: look before loading

```bash
pra-brain inspect rover-100k.brain
```

Prints the manifest as JSON. The brain itself is never deserialized —
inspect is safe on any file, including damaged ones.

## Person B: load and resume

```bash
pra-brain import rover-100k.brain --store my-runs/snapshots
```

Import verifies the container version, the snapshot format version,
and the sha256 before writing anything; a damaged or unknown file is
refused loudly and the store stays untouched. On success the directory
is a normal snapshot store — resume exactly as ever:

```python
from pra import Config, Engine
from pra.persistence.store import FileSnapshotStore

store = FileSnapshotStore("my-runs/snapshots")
snapshot_id, meta = store.list()[0]                  # newest
summary = Engine(cfg).run(seed, resume_from=store.read(snapshot_id))
```

The existing resume guards still apply: the seed must match the
snapshot's and the body must be compatible (obs_dim/n_actions) — the
resume path refuses otherwise, exactly as for your own snapshots. A
resumed run is byte-identical to the run person A would have gotten.

## From Python instead of the shell

```python
from pra.persistence.portable import export_brain, import_brain, inspect_brain

manifest = export_brain("rover.brain", store=store,      # or blob=...
                        note="rover, 100k steps",
                        created_at="2026-07-27T12:00:00+00:00")
manifest = inspect_brain("rover.brain")                  # manifest only
blob, manifest = import_brain("rover.brain")             # verified blob
```

`created_at` is caller-injected — the library never reads the clock.

## Honesty note

The sha256 protects against damage and accidental corruption, not
against a motivated forger — it is an integrity check, not a
signature. Load brains from people you trust.
