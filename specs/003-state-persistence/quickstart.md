# Quickstart: State Persistence

## 1. Snapshot a run, restore it, continue (US1)

```python
from pra.config import Config
from pra.core.engine import Engine
from pra.persistence.store import FileSnapshotStore

cfg = Config(snapshot_every_n_cycles=10)
store = FileSnapshotStore("snapshots/")
Engine(cfg, snapshot_store=store).run(1)  # writes a snapshot every 10 cycles

snap_id, meta = store.list()[0]  # newest first
blob = store.read(snap_id)
summary = Engine(cfg).run(1, resume_from=blob)  # byte-identical continuation
```

## 2. Confirm the validated behavior is untouched (US3)

```bash
./.venv/bin/pra-validate suite          # T1–T6, byte-identical, zero snapshot files
./.venv/bin/pra-validate determinism --seed 1
```

## 3. Quality gate

```bash
./.venv/bin/ruff format --check . && ./.venv/bin/ruff check . && ./.venv/bin/pytest -q
```

## 4. Scenario → check map

| Spec scenario | How to verify |
|---|---|
| US1 — byte-identical continuation (both modes) | `tests/integration/test_snapshot_resume.py` |
| US2 — atomicity, versioning, metadata | `tests/unit/test_snapshot_blob.py` |
| US3 — baseline frozen, zero files by default | `tests/integration/test_snapshot_resume.py::test_baseline_*` |
| US4 — body-compat rejection | `tests/integration/test_snapshot_resume.py::test_incompatible_*` |
| Store seam substitutability | `tests/contract/test_snapshot_store_contract.py` |

## 5. Oracle

The oracle is the uninterrupted run itself: the continuation must byte-match it
through the same canonical-summary machinery the determinism check uses.
