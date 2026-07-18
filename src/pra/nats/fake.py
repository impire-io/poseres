"""FakeBusTransport (feature 014, contracts §1) — the in-repo instrument.

Implements the full :class:`~pra.nats.transport.BusTransport` contract with no
network anywhere: an ordered journal of every delivered publish, synchronous
subscription dispatch, request/reply with deferrable replies, an in-memory
JetStream-shaped object store, and a scriptable ``set_down()``/``set_up()``
switch — the outage the drop counters are measured against. Every contract
test and the quickstart run on this class (FR-008), exactly as 013's
``FakeTransport`` carried that feature's gate.

Thread notes: the tap's publisher thread publishes while test threads read the
journal, so journal and object-store access sit under one lock. Subscription
and request handlers run synchronously on the calling thread — tests read
effects immediately; handlers must not block (the transport contract).
"""

from __future__ import annotations

import threading
from collections.abc import Callable

from pra.nats.transport import TransportError

__all__ = ["FakeBusTransport"]


def _matches(pattern: str, subject: str) -> bool:
    """NATS-style match: literal tokens, ``*`` (one token), trailing ``>``."""
    pat = pattern.split(".")
    sub = subject.split(".")
    for i, tok in enumerate(pat):
        if tok == ">":
            return i > 0 or len(sub) > 0
        if i >= len(sub):
            return False
        if tok != "*" and tok != sub[i]:
            return False
    return len(pat) == len(sub)


class FakeBusTransport:
    """Scripted, journaling, outage-capable BusTransport (stdlib-only)."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._journal: list[tuple[str, bytes]] = []
        self._subs: list[tuple[str, Callable[[str, bytes], None]]] = []
        self._responders: list[tuple[str, Callable[[bytes, Callable[[bytes], None]], None]]] = []
        self._objects: dict[str, dict[str, tuple[bytes, str]]] = {}
        self._down = False
        self._started = False
        self._closed = False
        self.publish_failures = 0
        self.reconnects = 0

    # -- lifecycle -----------------------------------------------------------
    def start(self) -> None:
        self._started = True

    def close(self) -> None:
        self._closed = True

    @property
    def healthy(self) -> bool:
        return not self._down

    # -- the outage switch (the instrument's whole point) --------------------
    def set_down(self) -> None:
        with self._lock:
            self._down = True

    def set_up(self) -> None:
        with self._lock:
            was_down = self._down
            self._down = False
            if was_down:
                self.reconnects += 1

    # -- telemetry out ---------------------------------------------------------
    def publish(self, subject: str, payload: bytes) -> None:
        with self._lock:
            if self._down:
                self.publish_failures += 1
                return
            self._journal.append((subject, bytes(payload)))
            handlers = [h for pat, h in self._subs if _matches(pat, subject)]
        for handler in handlers:
            handler(subject, payload)

    def subscribe(self, subject: str, handler: Callable[[str, bytes], None]) -> None:
        with self._lock:
            self._subs.append((subject, handler))

    # -- request/reply ---------------------------------------------------------
    def serve_requests(
        self, subject: str, handler: Callable[[bytes, Callable[[bytes], None]], None]
    ) -> None:
        with self._lock:
            self._responders.append((subject, handler))

    def request(self, subject: str, payload: bytes, timeout: float = 5.0) -> bytes:
        with self._lock:
            if self._down:
                raise TransportError(f"request on {subject!r}: transport is down")
            handler = next((h for pat, h in self._responders if _matches(pat, subject)), None)
        if handler is None:
            raise TransportError(f"request on {subject!r}: no responder")
        done = threading.Event()
        box: list[bytes] = []

        def reply(data: bytes) -> None:
            box.append(bytes(data))
            done.set()

        handler(payload, reply)
        if not done.wait(timeout):
            raise TransportError(f"request on {subject!r}: no reply within {timeout}s")
        return box[0]

    # -- discover fan-in: every responder on the subject may answer -----------
    def request_all(self, subject: str, payload: bytes, timeout: float = 5.0) -> list[bytes]:
        """Collect one reply from every matching responder (the discover sweep).
        Test-side helper; the real stack gathers replies until its timeout."""
        with self._lock:
            handlers = [h for pat, h in self._responders if _matches(pat, subject)]
        out: list[bytes] = []
        for handler in handlers:
            done = threading.Event()

            def reply(data: bytes, _done=done) -> None:
                out.append(bytes(data))
                _done.set()

            handler(payload, reply)
            if not done.wait(timeout):
                raise TransportError(f"request on {subject!r}: a responder went silent")
        return out

    # -- object store ----------------------------------------------------------
    def object_put(self, bucket: str, name: str, data: bytes, description: str) -> None:
        with self._lock:
            if self._down:
                raise TransportError(f"object_put {name!r} in {bucket!r}: transport is down")
            self._objects.setdefault(bucket, {})[name] = (bytes(data), str(description))

    def object_get(self, bucket: str, name: str) -> tuple[bytes, str]:
        with self._lock:
            if self._down:
                raise TransportError(f"object_get {name!r} in {bucket!r}: transport is down")
            if bucket not in self._objects:
                raise KeyError(f"no bucket {bucket!r}")
            if name not in self._objects[bucket]:
                raise KeyError(f"no object {name!r} in bucket {bucket!r}")
            data, description = self._objects[bucket][name]
            return data, description

    def object_list(self, bucket: str) -> list[tuple[str, str]]:
        with self._lock:
            if self._down:
                raise TransportError(f"object_list in {bucket!r}: transport is down")
            if bucket not in self._objects:
                raise KeyError(f"no bucket {bucket!r}")
            return [(name, desc) for name, (_, desc) in self._objects[bucket].items()]

    def object_delete(self, bucket: str, name: str) -> None:
        with self._lock:
            if self._down:
                raise TransportError(f"object_delete {name!r} in {bucket!r}: transport is down")
            if bucket not in self._objects:
                raise KeyError(f"no bucket {bucket!r}")
            self._objects[bucket].pop(name, None)

    # -- test-side accessors ---------------------------------------------------
    @property
    def journal(self) -> list[tuple[str, bytes]]:
        with self._lock:
            return list(self._journal)

    def published(self, subject: str) -> list[bytes]:
        """Journal payloads whose subject matches ``subject`` (wildcards ok)."""
        with self._lock:
            return [p for s, p in self._journal if _matches(subject, s)]
