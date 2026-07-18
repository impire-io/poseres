"""NATS at the seams (feature 014, ROADMAP B6).

Opt-in, reference byte-frozen: a live run's telemetry fanned out as subjects,
snapshots through a JetStream object store, and a request/reply control plane
— all through the Engine's existing injection seams, no engine edits. The
in-repo :class:`~pra.nats.fake.FakeBusTransport` carries the whole contract
without a NATS library or server; :class:`NatsTransport` is the thin real
binding behind ``pip install "poseres[nats]"``.
"""

from pra.nats.store import NatsSnapshotStore
from pra.nats.tap import NatsTap
from pra.nats.transport import BusTransport, TransportError

__all__ = ["BusTransport", "NatsSnapshotStore", "NatsTap", "NatsTransport", "TransportError"]


def __getattr__(name: str):
    if name == "NatsTransport":  # lazy: importing pra.nats must not require nats-py
        from pra.nats.transport import NatsTransport

        return NatsTransport
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
