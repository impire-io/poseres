"""The flood is real (live instrument reading, before any teaching):
sated the channel is silent; dosed hungry, dim 0 follows the registered
curve f = ((d - 0.25)/0.75)^2; the intrusion dims are f-scaled and
change every sample (the swelling, unpredictable signal); eating quiets
it. Rows to flood-rows.json.

    python flood_reading.py   (bridge up with SURVIVAL=1 FLOOD=intrusion)
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "examples" / "minecraft" / "survival" / "arms"))
import n23_runner as R  # noqa: E402 — rcon + the bridge session helpers live here


def curve(food: int) -> float:
    d = max(0.0, 1.0 - food / 20)
    return 0.0 if d <= 0.25 else ((d - 0.25) / 0.75) ** 2


def main() -> int:
    import socket

    checks: list[dict] = []

    def check(name: str, ok: bool, detail) -> None:
        checks.append({"check": name, "pass": bool(ok), "detail": detail})
        print(f"{'PASS' if ok else 'FAIL'}  {name}: {detail}", flush=True)

    print("world:", R.rcon("tick", "rate", "100"), flush=True)
    R.rcon("effect", "clear", "pra")
    R.rcon("clear", "pra")
    R.rcon("kill", "@e[type=item]")
    R.rcon("tp", "pra", *R.STAND)
    R.rcon("effect", "give", "pra", "minecraft:saturation", "2", "255")
    time.sleep(1.2)
    R.rcon("effect", "clear", "pra")

    sock = socket.create_connection(("127.0.0.1", R.BRIDGE_PORT), timeout=30)
    buf = b""

    def call(msg: dict) -> dict:
        nonlocal buf
        sock.sendall((json.dumps(msg) + "\n").encode())
        while b"\n" not in buf:
            chunk = sock.recv(65536)
            if not chunk:
                raise ConnectionError("bridge closed")
            buf += chunk
        line, buf = buf.split(b"\n", 1)
        return json.loads(line)

    def tick(cmd: dict) -> dict:
        return call({"op": "tick", "tick_ms": R.TICK_MS, "commands": [cmd]})

    assert call({"op": "hello", "version": "pra-mc/1"})["channels"]["flood"] == 4

    r = tick({})
    fl, food = r["channels"]["flood"], r["view"]["food"]
    check(
        "sated: the flood is silent", food >= 16 and fl == [0, 0, 0, 0], {"food": food, "flood": fl}
    )

    R.rcon(
        "effect", "give", "pra", "minecraft:hunger", "10", "255"
    )  # 64 units: through any saturation
    time.sleep(2.4)
    R.rcon("effect", "clear", "pra")
    r = tick({})
    fl, food = r["channels"]["flood"], r["view"]["food"]
    expected = curve(food)
    check(
        "starving: dim 0 follows the registered curve",
        abs(fl[0] - expected) < 1e-6 and fl[0] > 0.9,
        {"food": food, "f": round(fl[0], 4), "expected": round(expected, 4)},
    )
    noises = []
    for _ in range(6):
        r = tick({})
        noises.append(tuple(round(v, 4) for v in r["channels"]["flood"][1:]))
    fl = r["channels"]["flood"]
    check(
        "intrusion dims are f-scaled and change every sample",
        len(set(noises)) >= 5 and all(abs(v) <= fl[0] + 1e-9 for n in noises for v in n),
        {"distinct": len(set(noises)), "last": noises[-1]},
    )

    # give slices and eat: the flood must recede as the meal lands
    R.rcon("give", "pra", "minecraft:melon_slice", "16")
    time.sleep(0.3)
    tick({"hold_next": 1.0})
    f_before = tick({})["channels"]["flood"][0]
    for _ in range(60):
        r = tick({"use_held": 1.0})
        if r["view"]["food"] >= 16:
            break
    f_after = r["channels"]["flood"][0]
    check(
        "eating quiets the flood",
        f_after < 0.05 and f_before > 0.9,
        {"f_before": round(f_before, 3), "f_after": round(f_after, 3), "food": r["view"]["food"]},
    )
    call({"op": "bye"})
    sock.close()

    verdict = "FLOOD REAL" if all(c["pass"] for c in checks) else "FLOOD READING FAILED"
    print(verdict, flush=True)
    Path(__file__).parent.joinpath("flood-rows.json").write_text(
        json.dumps({"checks": checks, "verdict": verdict}, indent=1)
    )
    return 0 if all(c["pass"] for c in checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
