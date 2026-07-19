"""The pra-mc/1 wire protocol: newline-delimited JSON over TCP (feature 027).

One request line, one response line, never pipelined; every response
carries ``ok`` and, when false, ``error`` — which the client raises as
:class:`~pra.anatomy.body.AnatomyError` verbatim. The normative table
lives in specs/027-minecraft-body/contracts/minecraft-adapter.md; this
module is the framing both sides of the seam share (the transport and
the in-repo FakeBridge — the mineflayer bridge implements the same
lines in JavaScript).
"""

from __future__ import annotations

import json
import socket

from pra.anatomy.body import AnatomyError

__all__ = ["PROTOCOL_VERSION", "recv_message", "request", "send_message"]

PROTOCOL_VERSION = "pra-mc/1"

_MAX_LINE = 1 << 20  # a state payload fits; a runaway peer does not


def send_message(sock: socket.socket, message: dict) -> None:
    sock.sendall(json.dumps(message, separators=(",", ":")).encode() + b"\n")


def recv_message(rfile) -> dict:
    """Read one JSON line from a socket makefile; EOF and junk are loud."""
    line = rfile.readline(_MAX_LINE)
    if not line:
        raise AnatomyError("bridge connection closed (EOF) — restart the bridge and resume")
    if not line.endswith(b"\n"):
        raise AnatomyError("bridge sent an over-long or unterminated line")
    try:
        message = json.loads(line)
    except ValueError as exc:
        raise AnatomyError(f"bridge sent invalid JSON: {exc}") from None
    if not isinstance(message, dict):
        raise AnatomyError("bridge sent a non-object JSON line")
    return message


def request(sock: socket.socket, rfile, message: dict) -> dict:
    """One round-trip; a transport-level failure or ok=false is loud."""
    try:
        send_message(sock, message)
    except OSError as exc:
        raise AnatomyError(f"bridge connection lost while sending: {exc}") from None
    response = recv_message(rfile)
    if not response.get("ok", False):
        raise AnatomyError(str(response.get("error", "bridge refused the request")))
    return response
