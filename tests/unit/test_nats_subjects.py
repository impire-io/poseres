"""Feature 014 T001/T002 — the subject scheme, the wire form, and the fake
transport's own mechanics (contracts §1, §5.2; research R4/R7)."""

from __future__ import annotations

import threading

import pytest

from pra.nats import subjects
from pra.nats.fake import FakeBusTransport, _matches
from pra.nats.transport import BusTransport, TransportError

# --- T001: scheme, run ids, wire form -----------------------------------------


def test_subject_scheme_names_are_versioned_and_run_scoped():
    s = subjects.run_subjects("r1")
    assert s == {
        "status": "pra.v1.run.r1.status",
        "step": "pra.v1.run.r1.tele.step",
        "episode": "pra.v1.run.r1.tele.episode",
        "census": "pra.v1.run.r1.tele.census",
        "snapshot": "pra.v1.run.r1.tele.snapshot",
        "view_static": "pra.v1.run.r1.tele.view.static",
        "view_live": "pra.v1.run.r1.tele.view.live",
        "ctrl": "pra.v1.run.r1.ctrl",
    }
    assert subjects.DISCOVER_SUBJECT == "pra.v1.discover"


@pytest.mark.parametrize("bad", ["", "a.b", "a*", "a>b", "a b", 'a"b', "a\tb", None, 7])
def test_run_id_rejection_paths(bad):
    with pytest.raises(ValueError):
        subjects.validate_run_id(bad)


def test_default_run_id_shape_and_uniqueness():
    a, b = subjects.default_run_id(), subjects.default_run_id()
    assert a.startswith("run-") and len(a) == 12
    assert a != b
    subjects.validate_run_id(a)


def test_wire_form_is_byte_deterministic_and_ascii():
    payload = {"run": "r1", "seq": 3, "obs": [0.1, -2.5], "note": "π"}
    data = subjects.to_bytes(payload)
    assert data == subjects.to_bytes(dict(payload))  # same keys, same bytes
    assert data.decode("ascii")  # ensure_ascii really held
    assert subjects.from_bytes(data) == {"run": "r1", "seq": 3, "obs": [0.1, -2.5], "note": "π"}


def test_wire_form_rejects_non_objects():
    with pytest.raises(ValueError):
        subjects.from_bytes(b"[1,2]")
    with pytest.raises(ValueError):
        subjects.from_bytes(b"not json")


# --- T002: the fake transport (the instrument) --------------------------------


def test_subject_matching_rules():
    assert _matches("a.b.c", "a.b.c")
    assert _matches("a.*.c", "a.b.c")
    assert _matches("a.>", "a.b.c")
    assert not _matches("a.b", "a.b.c")
    assert not _matches("a.b.c.d", "a.b.c")
    assert not _matches("a.*.d", "a.b.c")


def test_fake_satisfies_the_transport_protocol():
    assert isinstance(FakeBusTransport(), BusTransport)


def test_journal_preserves_publish_order_and_wildcard_reads():
    t = FakeBusTransport()
    t.publish("pra.v1.run.r.tele.step", b"1")
    t.publish("pra.v1.run.r.tele.episode", b"2")
    t.publish("pra.v1.run.r.status", b"3")
    assert [s for s, _ in t.journal] == [
        "pra.v1.run.r.tele.step",
        "pra.v1.run.r.tele.episode",
        "pra.v1.run.r.status",
    ]
    assert t.published("pra.v1.run.r.tele.>") == [b"1", b"2"]


def test_subscribe_dispatches_matching_messages():
    t = FakeBusTransport()
    got: list[tuple[str, bytes]] = []
    t.subscribe("a.>", lambda s, p: got.append((s, p)))
    t.publish("a.b", b"x")
    t.publish("c.d", b"y")
    assert got == [("a.b", b"x")]


def test_down_state_drops_and_counts_then_reconnects():
    t = FakeBusTransport()
    t.set_down()
    t.publish("a.b", b"x")  # fire-and-forget: no raise, counted, not journaled
    assert t.publish_failures == 1 and t.journal == []
    assert not t.healthy
    with pytest.raises(TransportError):
        t.request("a.ctrl", b"{}", timeout=0.1)
    with pytest.raises(TransportError):
        t.object_put("bucket", "name", b"data", "{}")
    t.set_up()
    t.set_up()  # only a real transition counts
    assert t.reconnects == 1 and t.healthy


def test_request_reply_immediate_and_deferred():
    t = FakeBusTransport()
    t.serve_requests("a.ctrl", lambda p, reply: reply(b"pong:" + p))
    assert t.request("a.ctrl", b"ping") == b"pong:ping"

    # deferred: the handler stores the reply callable; another thread answers
    box: list = []
    t.serve_requests("b.ctrl", lambda p, reply: box.append(reply))

    def answer():
        box[0](b"later")

    thread = threading.Timer(0.05, answer)
    thread.start()
    try:
        assert t.request("b.ctrl", b"", timeout=2.0) == b"later"
    finally:
        thread.join()


def test_request_paths_fail_loudly():
    t = FakeBusTransport()
    with pytest.raises(TransportError):  # nobody serving
        t.request("nobody.home", b"", timeout=0.1)
    t.serve_requests("quiet.ctrl", lambda p, reply: None)  # never replies
    with pytest.raises(TransportError):
        t.request("quiet.ctrl", b"", timeout=0.05)


def test_object_store_mechanics():
    t = FakeBusTransport()
    t.object_put("bucket", "snap-1", b"blob", '{"step": 1}')
    data, desc = t.object_get("bucket", "snap-1")
    assert data == b"blob" and desc == '{"step": 1}'
    assert t.object_list("bucket") == [("snap-1", '{"step": 1}')]
    with pytest.raises(KeyError):
        t.object_get("bucket", "missing")
    with pytest.raises(KeyError):
        t.object_list("no-such-bucket")
    t.object_delete("bucket", "snap-1")
    t.object_delete("bucket", "snap-1")  # idempotent
    assert t.object_list("bucket") == []
