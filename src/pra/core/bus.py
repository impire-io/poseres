"""Bus seam (PRA-01 §4, contracts/seams.md §1).

Delivery only — no gating, scoring, learning, or birth. ``publish`` delivers an
event to every subscriber in ascending ``frame_id`` order, exactly once,
synchronously, and returns the results in that order.

With batched evaluation (PRA-01 §7.2) the in-memory Bus does not loop frame by
frame: it delegates the actual per-frame computation to a batched
``FrameProcessor`` (the Engine's ``dim``-grouped FrameStore) and then re-orders
the returned results by ascending ``frame_id``. The ordering and the
"delivery only" contract are the Bus's responsibility; the numerics are the
processor's. The Engine's hot loop drives the same processor directly for
telemetry (array reductions) so it never allocates a FrameResult per frame per
step; ``publish`` is the per-frame delivery path used by the contract and
batched-equivalence tests, sharing the identical underlying computation.
"""

from __future__ import annotations

import bisect
from typing import Protocol, runtime_checkable

from pra.core.contracts import FrameResult, SensorimotorEvent

__all__ = ["Bus", "FrameProcessor", "InMemorySyncBus"]


@runtime_checkable
class FrameProcessor(Protocol):
    """Computes a FrameResult for each requested frame from one event (batched)."""

    def results_for(
        self, event: SensorimotorEvent, frame_ids: list[int]
    ) -> dict[int, FrameResult]: ...


@runtime_checkable
class Bus(Protocol):
    def register(self, frame_id: int) -> int: ...
    def unregister(self, frame_id: int) -> None: ...
    def publish(self, event: SensorimotorEvent) -> list[FrameResult]: ...
    def subscribers(self) -> list[int]: ...


class InMemorySyncBus:
    """Default Bus: synchronous, exactly-once, ascending-``frame_id`` delivery."""

    def __init__(self, processor: FrameProcessor):
        self._processor = processor
        self._frame_ids: list[int] = []  # kept sorted ascending

    def register(self, frame_id: int) -> int:
        idx = bisect.bisect_left(self._frame_ids, frame_id)
        if idx < len(self._frame_ids) and self._frame_ids[idx] == frame_id:
            raise ValueError(f"frame_id {frame_id} already registered")
        self._frame_ids.insert(idx, frame_id)
        return frame_id

    def unregister(self, frame_id: int) -> None:
        idx = bisect.bisect_left(self._frame_ids, frame_id)
        if idx >= len(self._frame_ids) or self._frame_ids[idx] != frame_id:
            raise KeyError(f"frame_id {frame_id} is not registered")
        self._frame_ids.pop(idx)

    def subscribers(self) -> list[int]:
        return list(self._frame_ids)

    def publish(self, event: SensorimotorEvent) -> list[FrameResult]:
        results = self._processor.results_for(event, list(self._frame_ids))
        # delivery order is ascending frame_id (the subscriber order)
        return [results[fid] for fid in self._frame_ids]
