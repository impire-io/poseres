"""The pra-mc/1 wire protocol: newline-delimited JSON over TCP (feature 027).

One request line, one response line, never pipelined; every response
carries ``ok`` and, when false, ``error`` — which the client raises as
:class:`~pra.anatomy.body.AnatomyError` verbatim. The normative table
lives in specs/027-minecraft-body/contracts/minecraft-adapter.md; the
mineflayer bridge implements the same lines in JavaScript. There is no
fake side of this seam (the owner's rule, 2026-08-13): the adapter is
proven against the live bridge by ``examples/minecraft/contract_check.py``.
"""

from __future__ import annotations

import hashlib
import json
import socket

from pra.anatomy.body import AnatomyError

__all__ = ["PROTOCOL_VERSION", "item_signature", "recv_message", "request", "send_message"]

PROTOCOL_VERSION = "pra-mc/1"


def item_signature(name: str) -> tuple[float, float, float]:
    """The contract's appearance signature: sha256 of the identity string,
    digest bytes 0..2, each mapped to [-1, 1]. The bridge computes the
    same numbers in JavaScript; live tooling verifies against this."""
    digest = hashlib.sha256(name.encode("utf-8")).digest()
    return tuple(b / 127.5 - 1.0 for b in digest[:3])


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
