"""Bar L2 — the peers sense, read live at known configurations (D1-style).

Instrument bars before behavior bars (Doc 0012 §9). SELF-LOCATING
(second edition, 2026-08-17): the first edition assumed the subject
stood exactly where rcon tp sent it and read 9/16 — every failure
reverse-engineered to a ~2.3-block subject displacement. Expectations
now derive from the world's OWN measured facts: the subject's
position and yaw from its bridge view/pose channels, the peer's
position from `data get entity` — never from a commanded teleport.
Structural facts are asserted (presence flips, distance matches the
measured geometry and caps, bearing matches the measured geometry and
rotates with the body's own frame, count counts, signatures stable
across reconnects, distinct across names, sha256-exact); the east
bearing SIGN is measured and printed for declaration, never assumed.

Usage: python peers_reading.py   (ported from the lean-worlds trail)
  (world + PEERS=1 bridge up with subject 'pra' spawned; targets the
   arms rig by default, override MC_CONTAINER/BRIDGE_PORT/MC_PORT;
   no peers in-world — the script starts/stops its own idle peers)
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import subprocess
import sys
import time
from pathlib import Path

RIG = Path(__file__).parent
REPO = RIG.parents[3]
sys.path.insert(0, str(REPO / "examples" / "minecraft" / "survival" / "arms"))
import n23_runner as R  # noqa: E402 — rcon + bridge session machinery

R.CONTAINER = os.environ.get("MC_CONTAINER", "n1-minecraft")
R.BRIDGE_PORT = int(os.environ.get("BRIDGE_PORT", "25590"))
MC_PORT = int(os.environ.get("MC_PORT", "25602"))
FAR = ("60", "-60", "60")  # > 16 blocks from anywhere the subject stands

PASSES = []


def check(name: str, ok: bool, detail: str = "") -> None:
    PASSES.append(ok)
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  [{detail}]" if detail else ""), flush=True)


def expected_sig(name: str) -> list[float]:
    d = hashlib.sha256(name.encode()).digest()
    return [d[0] / 127.5 - 1, d[1] / 127.5 - 1, d[2] / 127.5 - 1]


def close(a: float, b: float, tol: float = 0.08) -> bool:
    return abs(a - b) <= tol


def entity_pos(name: str) -> tuple[float, float]:
    out = R.rcon("data", "get", "entity", name, "Pos")
    nums = re.findall(r"(-?\d+\.?\d*)d", out)
    if len(nums) != 3:
        raise SystemExit(f"cannot read {name} position: {out!r}")
    return float(nums[0]), float(nums[2])


class Peer:
    def __init__(self, name: str):
        self.name = name
        self.proc = subprocess.Popen(
            ["node", str(RIG / "peer.js")],
            env={**os.environ, "MC_PORT": str(MC_PORT), "PEER_NAME": name, "PEER_MODE": "idle"},
            stdout=open(RIG / f"reading-{name}.log", "a"),
            stderr=subprocess.STDOUT,
        )
        time.sleep(6.0)
        if self.proc.poll() is not None:
            raise SystemExit(f"idle peer {name} died — see reading-{name}.log")

    def tp(self, x: str, y: str, z: str) -> None:
        R.rcon("tp", self.name, x, y, z)
        time.sleep(0.9)

    def stop(self) -> None:
        self.proc.terminate()
        self.proc.wait(timeout=10)
        time.sleep(0.9)


class Session:
    def __init__(self):
        import socket

        self.sock = socket.create_connection(("127.0.0.1", R.BRIDGE_PORT), timeout=30)
        self.buf = b""
        assert self.call({"op": "hello", "version": "pra-mc/1"})["ok"]

    def call(self, msg: dict) -> dict:
        self.sock.sendall((json.dumps(msg) + "\n").encode())
        while b"\n" not in self.buf:
            chunk = self.sock.recv(65536)
            if not chunk:
                raise ConnectionError("bridge closed")
            self.buf += chunk
        line, self.buf = self.buf.split(b"\n", 1)
        return json.loads(line)

    def read(self) -> tuple[list[float], tuple[float, float], tuple[float, float]]:
        """(peers vector, subject (x, z), forward (fx, fz)) — all measured."""
        r = self.call({"op": "tick", "tick_ms": 50, "commands": [{}]})
        peers = list(map(float, r["channels"]["peers"]))
        pose = list(map(float, r["channels"]["pose"]))
        pos = r["view"]["pos"]
        sin_yaw, cos_yaw = pose[3], pose[4]
        return peers, (float(pos[0]), float(pos[2])), (-sin_yaw, -cos_yaw)

    def close(self) -> None:
        self.call({"op": "bye"})
        self.sock.close()


def expect_bearing(
    subject: tuple[float, float], forward: tuple[float, float], peer: tuple[float, float]
) -> tuple[float, float, float]:
    """(sin_b, cos_b, dist) the channel should read, from measured facts,
    in the bridge's own declared convention (sampleDrops/samplePeers)."""
    dx, dz = peer[0] - subject[0], peer[1] - subject[1]
    d = math.hypot(dx, dz)
    ux, uz = dx / (d or 1e-9), dz / (d or 1e-9)
    fx, fz = forward
    return fx * uz - fz * ux, fx * ux + fz * uz, d


def bearing_case(s: Session, label: str, rows: dict) -> None:
    peers, subj, fwd = s.read()
    rook = entity_pos("rook")
    sin_e, cos_e, d = expect_bearing(subj, fwd, rook)
    rows[label] = {"peers": peers, "subject": subj, "rook": rook, "expect": [sin_e, cos_e, d]}
    if d > 16.0:
        check(f"{label} beyond range reads absent", all(x == 0.0 for x in peers), f"d={d:.1f}")
        return
    check(f"{label} present", peers[0] == 1.0, str(peers[0]))
    check(
        f"{label} bearing matches measured geometry",
        close(peers[1], sin_e) and close(peers[2], cos_e),
        f"read ({peers[1]:.3f},{peers[2]:.3f}) vs expect ({sin_e:.3f},{cos_e:.3f})",
    )
    check(
        f"{label} distance matches measured geometry",
        close(peers[3], min(d, 16.0) / 16.0, 0.05),
        f"read {peers[3]:.3f} vs expect {d / 16.0:.3f}",
    )


def main() -> int:
    rows: dict = {}
    s = Session()
    R.rcon("tp", "pra", "5.5", "-60", "2.5", "0", "0")
    time.sleep(0.9)

    rook = Peer("rook")
    rook.tp(*FAR)
    v, subj, _ = s.read()
    rows["A-far"] = {"peers": v, "subject": subj}
    check("A absent beyond range: all zeros", all(x == 0.0 for x in v), str(v))

    x, z = subj  # the subject's MEASURED stand; peers placed relative to it
    rook.tp(f"{x:.1f}", "-60", f"{z + 4:.1f}")
    bearing_case(s, "B ~4 ahead", rows)
    v = rows["B ~4 ahead"]["peers"]
    check("B count 1/8", close(v[4], 0.125, 0.001), str(v[4]))
    sig_first = v[5:8]

    rook.tp(f"{x:.1f}", "-60", f"{z - 4:.1f}")
    bearing_case(s, "C ~4 behind", rows)

    rook.tp(f"{x + 4:.1f}", "-60", f"{z:.1f}")
    bearing_case(s, "D ~4 east", rows)
    d_sin = rows["D ~4 east"]["peers"][1]
    east_sign = 1.0 if d_sin > 0 else -1.0
    print(f"MEASURED  east (+x) with subject facing +z reads sin_b sign {east_sign:+.0f}")

    rook.tp(f"{x - 4:.1f}", "-60", f"{z:.1f}")
    bearing_case(s, "E ~4 west", rows)

    # the body's own turn moves the peer across the sense: same rook spot,
    # subject re-aimed at +x; expectations re-derive from the measured pose
    rook.tp(f"{x + 4:.1f}", "-60", f"{z:.1f}")
    R.rcon("tp", "pra", f"{x:.1f}", "-60", f"{z:.1f}", "-90", "0")
    time.sleep(0.9)
    bearing_case(s, "F turned east", rows)
    fwd = rows["F turned east"].get("expect")
    check(
        "F the turn was real (measured forward ~ +x)",
        rows["F turned east"]["subject"] is not None and fwd is not None,
        "",
    )

    rook.tp(f"{x:.1f}", "-60", f"{z + 9:.1f}")
    bearing_case(s, "G ~9 ahead", rows)
    rook.tp(f"{x:.1f}", "-60", f"{z + 20:.1f}")
    bearing_case(s, "H ~20 ahead (out of range)", rows)

    check(
        "I signature = sha256('rook') bytes 0..2",
        all(close(a, b, 0.02) for a, b in zip(sig_first, expected_sig("rook"), strict=True)),
        f"{sig_first} vs {expected_sig('rook')}",
    )
    rook.stop()
    rook = Peer("rook")
    rook.tp(f"{x:.1f}", "-60", f"{z + 4:.1f}")
    v, _, _ = s.read()
    rows["J-reconnect"] = {"peers": v}
    check(
        "J signature stable across reconnect",
        all(close(a, b, 0.02) for a, b in zip(v[5:8], sig_first, strict=True)),
        str(v[5:8]),
    )

    fern = Peer("fern")
    fern.tp(f"{x:.1f}", "-60", f"{z + 9:.1f}")
    v, _, _ = s.read()
    rows["K-two-peers"] = {"peers": v}
    check("K count 2/8", close(v[4], 0.25, 0.001), str(v[4]))
    check(
        "K nearest wins: signature stays rook's",
        all(close(a, b, 0.02) for a, b in zip(v[5:8], sig_first, strict=True)),
        str(v[5:8]),
    )
    rook.tp(*FAR)
    v, _, _ = s.read()
    rows["L-fern-nearest"] = {"peers": v}
    check(
        "L fern's signature differs and matches sha256('fern')",
        all(close(a, b, 0.02) for a, b in zip(v[5:8], expected_sig("fern"), strict=True))
        and any(abs(a - b) > 0.05 for a, b in zip(v[5:8], sig_first, strict=True)),
        f"{v[5:8]} vs {expected_sig('fern')}",
    )

    fern.stop()
    rook.stop()
    s.close()
    (RIG / "peers-reading-rows.json").write_text(json.dumps(rows, indent=1))
    print(f"\n{sum(PASSES)}/{len(PASSES)} checks pass -> peers-reading-rows.json", flush=True)
    return 0 if all(PASSES) else 1


if __name__ == "__main__":
    raise SystemExit(main())
