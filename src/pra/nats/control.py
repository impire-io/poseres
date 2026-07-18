"""The control plane (feature 014, contracts §3; research R5).

Request/reply on ``pra.v1.run.<id>.ctrl`` with exactly three v1 commands —
``inspect`` (read-only, answers in every state), ``pause``/``resume``
(boundary-exact via the tap's gate, idempotent), and ``snapshot`` (honest
deferred fulfillment: the reply arrives when the engine's own C4 cadence
write is observed, because that is the only place a snapshot is
well-defined). Every malformed or unknown request gets an error reply naming
the problem; the run thread never observes any of it.

Handlers run on the transport's delivery thread and never block: the deferred
snapshot reply is a registered waiter, invoked later from the engine thread's
store write (or from ``finish()`` when completion beats the boundary).
"""

from __future__ import annotations

from collections.abc import Callable

from pra.nats import subjects

__all__ = ["ControlPlane"]


def _error(reply: Callable[[bytes], None], tap, message: str) -> None:
    tap.control_errors += 1
    reply(subjects.to_bytes({"ok": False, "error": message}))


class ControlPlane:
    """Answers one run's control subject and the discover sweep."""

    def __init__(self, tap):
        self._tap = tap

    # -- pra.v1.run.<id>.ctrl --------------------------------------------------
    def handle(self, payload: bytes, reply: Callable[[bytes], None]) -> None:
        tap = self._tap
        tap.control_requests += 1
        try:
            request = subjects.from_bytes(payload)
        except ValueError:
            _error(reply, tap, "request must be a JSON object")
            return
        cmd = request.get("cmd")
        if cmd == "inspect":
            reply(
                subjects.to_bytes(
                    {
                        "ok": True,
                        "run": tap.run_id,
                        "state": tap.state,
                        "steps": tap.steps,
                        "episodes": tap.episodes,
                        "census": tap.census(),
                        "counters": {
                            "events_mirrored": tap.events_mirrored,
                            "events_published": tap.events_published,
                            "events_dropped": tap.events_dropped,
                            "publish_failures": tap.transport.publish_failures,
                            "reconnects": tap.transport.reconnects,
                            "census_published": tap.census_published,
                            "control_requests": tap.control_requests,
                            "control_errors": tap.control_errors,
                        },
                    }
                )
            )
        elif cmd == "pause":
            if tap.state == "completed":
                _error(reply, tap, "run has completed; nothing to pause")
                return
            already = tap.state == "paused"
            position = tap.pause()
            reply(
                subjects.to_bytes(
                    {"ok": True, "state": "paused", "position": position, "already": already}
                )
            )
        elif cmd == "resume":
            if tap.state == "completed":
                _error(reply, tap, "run has completed; nothing to resume")
                return
            already = tap.state == "running"
            tap.resume()
            reply(subjects.to_bytes({"ok": True, "state": "running", "already": already}))
        elif cmd == "snapshot":
            if tap.state == "completed":
                _error(reply, tap, "run has completed; no further snapshot boundary")
                return
            if not tap.snapshot_configured():
                _error(
                    reply,
                    tap,
                    "run is not snapshot-configured: inject a store via tap.wrap_store(...) "
                    "and set snapshot_every_n_cycles > 0",
                )
                return

            def waiter(snapshot_id: str, meta: dict) -> None:
                if not snapshot_id:  # completion beat the next boundary
                    _error(reply, tap, "run completed before the next snapshot boundary")
                    return
                reply(
                    subjects.to_bytes(
                        {
                            "ok": True,
                            "snapshot_id": snapshot_id,
                            "step": meta["step"],
                            "cycle": meta["cycle"],
                        }
                    )
                )

            tap.add_snapshot_waiter(waiter)
        else:
            _error(reply, tap, f"unknown cmd {cmd!r} (known: inspect, pause, resume, snapshot)")

    # -- pra.v1.discover -------------------------------------------------------
    def handle_discover(self, payload: bytes, reply: Callable[[bytes], None]) -> None:
        tap = self._tap
        reply(
            subjects.to_bytes(
                {
                    "run": tap.run_id,
                    "state": tap.state,
                    "subjects": subjects.run_subjects(tap.run_id),
                }
            )
        )
