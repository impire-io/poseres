"""Bar D1 — the senses are real (live instrument reading, before any
teaching). Verifies on the real server: the glance reports the adjacent
melon at the correct sector/distance/signature and rotates with turns;
a freshly dug drop appears in the drops channel, its bearing tracks
body turns, its distance shrinks walking toward it, and pickup empties
the channel. Rows to d1-rows.json.

Usage: python d1_reading.py   (SURVIVAL=1 bridge on 25590, world up)
"""

from __future__ import annotations

import hashlib
import json
import socket
import subprocess
import time

BRIDGE_PORT = 25590
STAND = ("5.5", "-60", "2.5", "0", "0")
DROPS, GLANCE = slice(0, 8), slice(0, 32)  # within their own channels


def rcon(*cmd: str) -> str:
    r = subprocess.run(
        ["docker", "exec", "n1-minecraft", "rcon-cli", "--", *cmd],
        capture_output=True,
        text=True,
        timeout=30,
    )
    return (r.stdout or r.stderr).strip()


def signature(name: str) -> list[float]:
    d = hashlib.sha256(name.encode()).digest()
    return [round(b / 127.5 - 1.0, 6) for b in d[:3]]


class Session:
    def __init__(self) -> None:
        self.sock = socket.create_connection(("127.0.0.1", BRIDGE_PORT), timeout=30)
        self.buf = b""
        hello = self.call({"op": "hello", "version": "pra-mc/1"})
        assert hello["channels"]["drops"] == 8 and hello["channels"]["glance"] == 32

    def call(self, msg: dict) -> dict:
        self.sock.sendall((json.dumps(msg) + "\n").encode())
        while b"\n" not in self.buf:
            chunk = self.sock.recv(65536)
            if not chunk:
                raise ConnectionError("bridge closed")
            self.buf += chunk
        line, self.buf = self.buf.split(b"\n", 1)
        return json.loads(line)

    def tick(self, command: dict) -> dict:
        return self.call({"op": "tick", "tick_ms": 50, "commands": [command]})


def sector(glance: list[float], k: int) -> dict:
    return {
        "dist": round(glance[k * 4], 4),
        "sig": [round(v, 6) for v in glance[k * 4 + 1 : k * 4 + 4]],
    }


def drops_row(drops: list[float]) -> dict:
    return {
        "present": drops[0],
        "sin_b": round(drops[1], 3),
        "cos_b": round(drops[2], 3),
        "dist": round(drops[3], 3),
        "count": round(drops[4], 3),
        "sig": [round(v, 6) for v in drops[5:8]],
    }


def main() -> int:
    rows: dict = {"checks": []}

    def check(name: str, ok: bool, detail) -> None:
        rows["checks"].append({"check": name, "pass": bool(ok), "detail": detail})
        print(f"{'PASS' if ok else 'FAIL'}  {name}: {detail}", flush=True)

    print("world:", rcon("tick", "rate", "100"), flush=True)
    rcon("effect", "clear", "pra")
    rcon("clear", "pra")
    rcon("kill", "@e[type=item]")
    rcon("setblock", "5", "-60", "3", "minecraft:melon")
    rcon("tp", "pra", *STAND)
    time.sleep(0.8)
    s = Session()

    r = s.tick({})
    g = r["channels"]["glance"]
    mel = signature("melon")
    s0 = sector(g, 0)
    check(
        "glance: melon ahead at sector 0, one block",
        s0["dist"] == round(1 / 16, 4) and s0["sig"] == mel,
        s0,
    )
    others = [sector(g, k) for k in range(8)]
    check("glance: full row (context)", True, others)

    for _ in range(4):
        r = s.tick({"turn_right": 1.0})
    g = r["channels"]["glance"]
    s4 = sector(g, 4)
    check(
        "glance rotates: after 180, the melon is in sector 4",
        s4["dist"] == round(1 / 16, 4) and s4["sig"] == mel,
        s4,
    )
    for _ in range(4):
        r = s.tick({"turn_right": 1.0})

    # dig the melon: a real drop spawns ahead
    for _ in range(40):
        r = s.tick({"dig_ahead": 1.0})
        if r["channels"]["drops"][0] == 1:
            break
    d = drops_row(r["channels"]["drops"])
    check(
        "drops: a dug drop appears, roughly ahead, slice signature",
        d["present"] == 1 and d["cos_b"] > 0.5 and d["sig"] == signature("melon_slice"),
        d,
    )

    # the dug drop sits inside pickup range and the world takes it during
    # any next tick (measured, first run) — bearing geometry needs a drop
    # OUTSIDE pickup range: summon one four blocks ahead
    for _ in range(6):
        s.tick({})  # let any near drop get collected
    rcon("kill", "@e[type=item]")
    rcon("tp", "pra", *STAND)
    rcon(
        "summon",
        "minecraft:item",
        "5.5",
        "-60",
        "6.5",
        '{Item:{id:"minecraft:melon_slice",count:1}}',
    )
    time.sleep(0.5)
    r = s.tick({})
    far = drops_row(r["channels"]["drops"])
    check(
        "drops: a summoned drop four blocks ahead reads ahead at ~0.5 range",
        far["present"] == 1 and far["cos_b"] > 0.9 and 0.35 < far["dist"] < 0.65,
        far,
    )

    r = s.tick({"turn_right": 1.0})
    r = s.tick({"turn_right": 1.0})
    d90 = drops_row(r["channels"]["drops"])
    check(
        "drops bearing tracks a 90-degree right turn (sin NEGATIVE: the "
        "target is on the turn_left side; sin positive = turn_right side)",
        d90["present"] == 1 and d90["sin_b"] < -0.5 and abs(d90["cos_b"]) < 0.6,
        d90,
    )
    r = s.tick({"turn_left": 1.0})
    r = s.tick({"turn_left": 1.0})

    dist_before = drops_row(r["channels"]["drops"])["dist"]
    picked = None
    shrank = False
    for i in range(30):
        r = s.tick({"forward": 1.0})
        d = drops_row(r["channels"]["drops"])
        if d["present"] == 1 and d["dist"] < dist_before:
            shrank = True
        if d["present"] == 0:
            picked = i + 1
            break
    slices = dict((n, c) for n, c in r["view"]["inventory"]).get("melon_slice", 0)
    check(
        "drops: distance shrinks walking in; pickup empties the channel",
        shrank and picked is not None and slices > 0,
        {"dist_before": dist_before, "steps_to_pickup": picked, "slices": slices},
    )

    s.call({"op": "bye"})
    all_pass = all(c["pass"] for c in rows["checks"])
    rows["verdict"] = "D1 MET" if all_pass else "D1 FAILED"
    print(rows["verdict"], flush=True)
    import pathlib

    pathlib.Path(__file__).parent.joinpath("d1-rows.json").write_text(json.dumps(rows, indent=1))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
