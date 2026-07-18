"""BusTransport seam (feature 014, contracts §1; research R7).

The boundary between the backend's contract logic and message delivery. The
in-repo :class:`~pra.nats.fake.FakeBusTransport` implements it for the entire
test suite (no NATS library, no server — FR-007/FR-008); ``NatsTransport``
below is the thin real binding (added with US4): one asyncio event loop on a
daemon thread, lazy ``nats-py`` import behind a clear install message.

Delivery grades are part of the contract, stated, never hidden:

- ``publish`` is **fire-and-forget**: it never raises for delivery failure and
  never blocks beyond a local enqueue; in a failed state it counts
  ``publish_failures`` and returns (the no-backpressure rule, FR-003).
- ``request`` and the object-store operations are **explicit**: they block up
  to a bounded timeout and fail loudly, naming the operation (FR-005/FR-006).
- Request handlers receive a ``reply`` callable instead of returning bytes, so
  a reply may be deferred (the control plane's snapshot command, research R5)
  — and a handler must never block the delivery thread.
"""

from __future__ import annotations

import threading
from collections.abc import Callable
from typing import Protocol, runtime_checkable

__all__ = ["BusTransport", "NatsTransport", "TransportError"]


class TransportError(RuntimeError):
    """An explicit transport operation failed; the message names the operation."""


@runtime_checkable
class BusTransport(Protocol):
    """Message delivery + object storage, health, and honesty counters."""

    publish_failures: int
    reconnects: int

    def start(self) -> None: ...

    def close(self) -> None: ...

    @property
    def healthy(self) -> bool: ...

    # -- telemetry out (fire-and-forget) ------------------------------------
    def publish(self, subject: str, payload: bytes) -> None: ...

    def subscribe(self, subject: str, handler: Callable[[str, bytes], None]) -> None:
        """Deliver every message whose subject matches (exact, ``*``, or a
        trailing ``>``) to ``handler(subject, payload)``, at most once each."""
        ...

    # -- request/reply (explicit, loud) -------------------------------------
    def serve_requests(
        self, subject: str, handler: Callable[[bytes, Callable[[bytes], None]], None]
    ) -> None:
        """Answer requests on ``subject``: ``handler(payload, reply)`` must
        arrange for ``reply(bytes)`` exactly once (possibly later, from any
        thread) and must not block the delivery thread."""
        ...

    def request(self, subject: str, payload: bytes, timeout: float = 5.0) -> bytes: ...

    # -- object store (explicit, loud) ---------------------------------------
    def object_put(self, bucket: str, name: str, data: bytes, description: str) -> None:
        """Store ``data`` under ``name``, creating the bucket if needed."""
        ...

    def object_get(self, bucket: str, name: str) -> tuple[bytes, str]:
        """Return ``(data, description)``; ``KeyError`` for a missing object."""
        ...

    def object_list(self, bucket: str) -> list[tuple[str, str]]:
        """Return ``(name, description)`` pairs; ``KeyError`` for a missing bucket."""
        ...

    def object_delete(self, bucket: str, name: str) -> None:
        """Remove ``name`` if present (missing is a no-op; missing bucket raises)."""
        ...


# --- the real binding (US4) ----------------------------------------------------


def _import_nats():
    import nats
    import nats.js.api
    import nats.js.errors

    return nats


def _require_nats():
    try:
        return _import_nats()
    except ImportError as err:
        raise ImportError(
            "the NATS client library is not installed; install the optional extra: "
            'pip install "poseres[nats]" — the in-repo FakeBusTransport needs no '
            "library and carries the whole test suite"
        ) from err


class NatsTransport:
    """Thin real binding: one asyncio event loop on a daemon thread.

    Publishes hop onto the loop via ``call_soon_threadsafe`` (non-blocking,
    fire-and-forget, failures counted); requests and object-store operations
    block the caller via ``run_coroutine_threadsafe`` up to a bounded timeout
    and fail loudly. Exercised by the worked example (``examples/nats/``) —
    the quality gate runs on the fake, the 013 stance.
    """

    def __init__(
        self,
        url: str = "nats://127.0.0.1:4222",
        *,
        connect_timeout: float = 5.0,
        op_timeout: float = 10.0,
    ):
        self._nats = _require_nats()
        self._url = url
        self._connect_timeout = float(connect_timeout)
        self._op_timeout = float(op_timeout)
        self._loop = None
        self._thread = None
        self._nc = None
        self._connected = False
        self.publish_failures = 0
        self.reconnects = 0

    # -- lifecycle -------------------------------------------------------------
    def start(self) -> None:
        import asyncio

        if self._loop is not None:
            return
        loop = asyncio.new_event_loop()
        thread = threading.Thread(target=loop.run_forever, daemon=True, name="pra-nats-transport")
        thread.start()
        self._loop, self._thread = loop, thread

        async def _connect():
            async def on_disconnected():
                self._connected = False

            async def on_reconnected():
                self._connected = True
                self.reconnects += 1

            return await self._nats.connect(
                self._url,
                connect_timeout=self._connect_timeout,
                disconnected_cb=on_disconnected,
                reconnected_cb=on_reconnected,
            )

        future = asyncio.run_coroutine_threadsafe(_connect(), loop)
        try:
            self._nc = future.result(self._connect_timeout + 2)
        except Exception as err:
            self.close()
            raise TransportError(f"connect to {self._url!r} failed: {err}") from err
        self._connected = True

    def close(self) -> None:
        import asyncio

        loop, thread, nc = self._loop, self._thread, self._nc
        self._loop = self._thread = self._nc = None
        self._connected = False
        if loop is None:
            return
        if nc is not None:
            try:
                asyncio.run_coroutine_threadsafe(nc.drain(), loop).result(self._op_timeout)
            except Exception:
                pass  # closing is best-effort; the loop stops regardless
        loop.call_soon_threadsafe(loop.stop)
        if thread is not None:
            thread.join(timeout=5.0)
        loop.close()

    @property
    def healthy(self) -> bool:
        return self._connected

    # -- internals -------------------------------------------------------------
    def _run(self, coro, operation: str, timeout: float | None = None):
        import asyncio

        if self._loop is None:
            coro.close()
            raise TransportError(f"{operation}: transport not started")
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        try:
            return future.result(timeout if timeout is not None else self._op_timeout)
        except KeyError:
            raise  # the object-store missing-name/bucket grammar passes through
        except Exception as err:
            raise TransportError(f"{operation} failed: {err}") from err

    def _not_found(self) -> tuple:
        errors = self._nats.js.errors
        names = ("ObjectNotFoundError", "BucketNotFoundError", "NotFoundError")
        return tuple(getattr(errors, n) for n in names if hasattr(errors, n))

    # -- telemetry out (fire-and-forget) ----------------------------------------
    def publish(self, subject: str, payload: bytes) -> None:
        loop, nc = self._loop, self._nc
        if loop is None or nc is None or not self._connected:
            self.publish_failures += 1
            return

        def _count(task) -> None:
            try:
                if task.exception() is not None:
                    self.publish_failures += 1
            except Exception:
                self.publish_failures += 1

        def _do() -> None:
            loop.create_task(nc.publish(subject, payload)).add_done_callback(_count)

        try:
            loop.call_soon_threadsafe(_do)
        except RuntimeError:  # loop shut down between the check and the call
            self.publish_failures += 1

    def subscribe(self, subject: str, handler: Callable[[str, bytes], None]) -> None:
        nc = self._nc

        async def _sub():
            async def cb(msg):
                handler(msg.subject, msg.data)

            await nc.subscribe(subject, cb=cb)

        self._run(_sub(), f"subscribe {subject!r}")

    # -- request/reply -----------------------------------------------------------
    def serve_requests(
        self, subject: str, handler: Callable[[bytes, Callable[[bytes], None]], None]
    ) -> None:
        nc = self._nc

        async def _sub():
            async def cb(msg):
                reply_subject = msg.reply

                def reply(data: bytes) -> None:
                    if reply_subject:
                        self.publish(reply_subject, data)

                handler(msg.data, reply)

            await nc.subscribe(subject, cb=cb)

        self._run(_sub(), f"serve {subject!r}")

    def request(self, subject: str, payload: bytes, timeout: float = 5.0) -> bytes:
        nc = self._nc

        async def _req():
            msg = await nc.request(subject, payload, timeout=timeout)
            return msg.data

        return self._run(_req(), f"request {subject!r}", timeout=timeout + 2)

    # -- object store -------------------------------------------------------------
    async def _bucket(self, bucket: str, *, create: bool):
        js = self._nc.jetstream()
        try:
            return await js.object_store(bucket)
        except self._not_found():
            if not create:
                raise KeyError(f"no bucket {bucket!r}") from None
            return await js.create_object_store(bucket)

    def object_put(self, bucket: str, name: str, data: bytes, description: str) -> None:
        api = self._nats.js.api

        async def _put():
            store = await self._bucket(bucket, create=True)
            meta = api.ObjectMeta(name=name, description=description)
            await store.put(name, data, meta=meta)

        self._run(_put(), f"object_put {name!r} in {bucket!r}")

    def object_get(self, bucket: str, name: str) -> tuple[bytes, str]:
        async def _get():
            store = await self._bucket(bucket, create=False)
            try:
                result = await store.get(name)
            except self._not_found():
                raise KeyError(f"no object {name!r} in bucket {bucket!r}") from None
            return bytes(result.data), (result.info.description or "")

        return self._run(_get(), f"object_get {name!r} in {bucket!r}")

    def object_list(self, bucket: str) -> list[tuple[str, str]]:
        async def _list():
            store = await self._bucket(bucket, create=False)
            infos = await store.list()
            return [(info.name, info.description or "") for info in infos]

        return self._run(_list(), f"object_list in {bucket!r}")

    def object_delete(self, bucket: str, name: str) -> None:
        async def _delete():
            store = await self._bucket(bucket, create=False)
            try:
                await store.delete(name)
            except self._not_found():
                pass  # idempotent, like the file store

        self._run(_delete(), f"object_delete {name!r} in {bucket!r}")
