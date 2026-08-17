"""Bar 2 — the peers sense, read live at known configurations (D1-style).

Instrument bars before behavior bars (Doc 0012 §9): before any
learnability claim, the sense must read correctly at known
configurations and move correctly under known movements. World admin
(rcon) preps each context BETWEEN samples — an instrument session,
not a life. Structural facts are ASSERTED (presence flips, distance
scales and caps, bearing rotates with the body's own frame, count
counts, signatures are stable across reconnects and distinct across
names, and match sha256 bytes 0..2 -> [-1, 1]); bearing SIGN
conventions are MEASURED and printed for declaration, never assumed
(the left-handed yaw frame, D1's lesson).

Usage: python peers_reading.py
  (cw1 up; PEERS=1 bridge up on 25592 with the subject 'pra' spawned;
   no peers in-world — the script starts/stops its own idle peers)
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

RIG = Path(__file__).parent
REPO = RIG.parents[3]
sys.path.insert(0, str(REPO / "examples" / "minecraft" / "survival" / "arms"))
import n23_runner as R  # noqa: E402 — rcon + bridge session machinery

R.CONTAINER = "lw1-minecraft"
R.BRIDGE_PORT = 25592
MC_PORT = 25604
STAND = ("5.5", "-60", "2.5", "0", "0")  # facing +z (south), the arms' stand
SUBJECT = ("5.5", "-60", "2.5")
FAR = ("60", "-60", "60")  # > 16 blocks: out of the declared range

PASSES = []


def check(name: str, ok: bool, detail: str = "") -> None:
    PASSES.append(ok)
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  [{detail}]" if detail else ""), flush=True)


def expected_sig(name: str) -> list[float]:
    d = hashlib.sha256(name.encode()).digest()
    return [d[0] / 127.5 - 1, d[1] / 127.5 - 1, d[2] / 127.5 - 1]


def close(a: float, b: float, tol: float = 0.06) -> bool:
    return abs(a - b) <= tol


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
        time.sleep(0.8)

    def stop(self) -> None:
        self.proc.terminate()
        self.proc.wait(timeout=10)
        time.sleep(0.8)


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

    def peers(self) -> list[float]:
        r = self.call({"op": "tick", "tick_ms": 50, "commands": [{}]})
        return list(map(float, r["channels"]["peers"]))

    def close(self) -> None:
        self.call({"op": "bye"})
        self.sock.close()


def main() -> int:
    rows = {}
    s = Session()
    R.rcon("tp", "pra", *STAND)
    time.sleep(0.8)

    rook = Peer("rook")
    rook.tp(*FAR)
    v = rows["A-out-of-range"] = s.peers()
    check("A absent beyond range: all zeros", all(x == 0.0 for x in v), str(v))

    x, _, z = (float(c) for c in SUBJECT)
    rook.tp(str(x), "-60", str(z + 4))  # 4 ahead (subject faces +z)
    v = rows["B-4-ahead"] = s.peers()
    check("B present", v[0] == 1.0, str(v))
    check("B ahead: cos_b ~ +1, sin_b ~ 0", close(v[2], 1.0) and close(v[1], 0.0), str(v[1:3]))
    check("B dist 4/16", close(v[3], 0.25), str(v[3]))
    check("B count 1/8", close(v[4], 0.125), str(v[4]))

    rook.tp(str(x), "-60", str(z - 4))  # 4 behind
    v = rows["C-4-behind"] = s.peers()
    check("C behind: cos_b ~ -1", close(v[2], -1.0), str(v[2]))

    rook.tp(str(x + 4), "-60", str(z))  # 4 east (+x)
    v = rows["D-4-east"] = s.peers()
    check("D beam: |sin_b| ~ 1, cos_b ~ 0", close(abs(v[1]), 1.0) and close(v[2], 0.0), str(v[1:3]))
    east_sign = 1.0 if v[1] > 0 else -1.0
    print(f"MEASURED  east (+x) with subject facing +z reads sin_b sign {east_sign:+.0f}")

    rook.tp(str(x - 4), "-60", str(z))  # 4 west
    v = rows["E-4-west"] = s.peers()
    check("E west flips the sign", close(v[1], -east_sign * 1.0, 0.12), str(v[1]))

    # the body's own turn moves the peer across the sense (the property
    # that makes approach learnable): subject faces +x, rook still 4 east
    rook.tp(str(x + 4), "-60", str(z))
    R.rcon("tp", "pra", *SUBJECT, "-90", "0")  # yaw -90: facing +x (measured frame)
    time.sleep(0.8)
    v = rows["F-turned-east"] = s.peers()
    turned_ok = close(v[2], 1.0) and close(v[1], 0.0)
    check("F subject turned toward: peer reads ahead", turned_ok, str(v[1:3]))
    R.rcon("tp", "pra", *STAND)
    time.sleep(0.8)

    rook.tp(str(x), "-60", str(z + 8))
    v = rows["G-8-ahead"] = s.peers()
    check("G dist 8/16", close(v[3], 0.5), str(v[3]))
    rook.tp(str(x), "-60", str(z + 15.5))
    v = rows["G-15.5-ahead"] = s.peers()
    check("G dist ~ cap near range edge", v[0] == 1.0 and v[3] > 0.9, str(v[3]))

    sig_first = rows["B-4-ahead"][5:8]
    check(
        "H signature = sha256('rook') bytes 0..2",
        all(close(a, b, 0.02) for a, b in zip(sig_first, expected_sig("rook"), strict=True)),
        f"{sig_first} vs {expected_sig('rook')}",
    )
    rook.stop()
    rook = Peer("rook")  # reconnect: same name, same signature
    rook.tp(str(x), "-60", str(z + 4))
    v = rows["I-reconnect"] = s.peers()
    check(
        "I signature stable across reconnect",
        all(close(a, b, 0.02) for a, b in zip(v[5:8], sig_first, strict=True)),
        str(v[5:8]),
    )

    fern = Peer("fern")
    fern.tp(str(x), "-60", str(z + 9))  # second peer, farther
    v = rows["J-two-peers"] = s.peers()
    check("J count 2/8", close(v[4], 0.25), str(v[4]))
    check(
        "J nearest wins: signature stays rook's",
        all(close(a, b, 0.02) for a, b in zip(v[5:8], sig_first, strict=True)),
        str(v[5:8]),
    )
    rook.tp(*FAR)
    v = rows["K-fern-nearest"] = s.peers()
    check(
        "K fern's signature differs and matches sha256('fern')",
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
