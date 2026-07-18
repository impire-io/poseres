"""NatsSnapshotStore (feature 014, contracts §4; research R6).

The existing four-method ``SnapshotStore`` protocol over a JetStream-shaped
object store reached through the transport seam: the blob is the object, the
canonical metadata JSON is the object's description (metadata-with-object is
atomic — no torn-write marker dance needed), and ids come from the existing
``snapshot_id_for`` so one id scheme rules project-wide. ``list()`` is
newest-first exactly like ``FileSnapshotStore`` (the id is step-sortable).

Failure grammar (FR-005): a missing snapshot id raises ``KeyError`` — the
protocol's own contract, matching the file store — while transport trouble
(server unreachable, bucket gone mid-operation) raises ``RuntimeError`` naming
the store, the operation, and the id. Operations are synchronous and bounded;
a store-backed engine run therefore blocks at each C4 write for the duration
of the network put — the user's explicit backend choice, stated in the docs.

This is Phase D's shareable-brains transport bought once: ``write`` on one
machine, ``list``/``read``/resume on another, per-class §5b guarantees
carried unchanged because the blob is carried unchanged.
"""

from __future__ import annotations

import json

from pra.nats.transport import BusTransport, TransportError
from pra.persistence.store import REQUIRED_METADATA, snapshot_id_for

__all__ = ["NatsSnapshotStore"]

DEFAULT_BUCKET = "pra-snapshots"


class NatsSnapshotStore:
    """SnapshotStore over a JetStream object-store bucket."""

    def __init__(self, transport: BusTransport, bucket: str = DEFAULT_BUCKET):
        self._transport = transport
        self._bucket = bucket
        self._transport.start()

    def _fail(self, operation: str, snapshot_id: str, err: Exception) -> RuntimeError:
        which = f" {snapshot_id!r}" if snapshot_id else ""
        return RuntimeError(
            f"NatsSnapshotStore({self._bucket!r}): {operation}{which} failed: {err}"
        )

    def write(self, blob: bytes, metadata: dict) -> str:
        missing = [k for k in REQUIRED_METADATA if k not in metadata]
        if missing:
            raise ValueError(f"snapshot metadata missing required fields: {missing}")
        snapshot_id = snapshot_id_for(metadata)
        description = json.dumps(metadata, sort_keys=True)
        try:
            self._transport.object_put(self._bucket, snapshot_id, blob, description)
        except (TransportError, KeyError) as err:
            raise self._fail("write", snapshot_id, err) from err
        return snapshot_id

    def read(self, snapshot_id: str) -> bytes:
        try:
            data, _ = self._transport.object_get(self._bucket, snapshot_id)
        except KeyError as err:
            raise KeyError(f"no committed snapshot {snapshot_id!r}") from err
        except TransportError as err:
            raise self._fail("read", snapshot_id, err) from err
        return data

    def list(self) -> list[tuple[str, dict]]:
        try:
            entries = self._transport.object_list(self._bucket)
        except KeyError:
            return []  # no bucket yet = no snapshots yet (mirrors an empty store dir)
        except TransportError as err:
            raise self._fail("list", "", err) from err
        out = [(name, json.loads(desc)) for name, desc in entries]
        out.sort(key=lambda pair: pair[0], reverse=True)  # id is step-sortable
        return out

    def delete(self, snapshot_id: str) -> None:
        try:
            self._transport.object_delete(self._bucket, snapshot_id)
        except KeyError:
            return  # missing bucket/object: deletion is idempotent, like the file store
        except TransportError as err:
            raise self._fail("delete", snapshot_id, err) from err
