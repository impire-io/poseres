"""The larder loop's mechanism check (topic the-long-carry, bar H0 step 2).

A scripted tape walker — NOT the kernel — drives the live body around
the arena and verifies the world's own contract before any brain runs
(instrument before behavior, the 0112 discipline):

  1. the lap counter increments exactly once per taught-direction
     crossing (reads after each lap: 1, 2, 3);
  2. the gate stays obsidian through laps 1-2 and is air at laps 3;
  3. larder entry resets the count to 0 and the gate recloses;
  4. the indicator column mirrors the count (gold rises and falls);
  5. dig -> collect -> eat works on the larder's melons (the mouth
     check relocated);
  6. the exit drop returns the body to the loop and cannot be climbed
     back (jump reach 1 < drop 2);
  7. counting resumes after a chain (a fresh lap reads 1);

and records the gait calibration (steps per block, steps per lap at
the 5x fabric) that sizes every chain-length number in ../arena.md.

Navigation is closed-loop: absolute position from the bridge's
ground-truth view, yaw from the pose channels, auto-jump on the
solid_ahead channel. The walker never reads the scoreboard to steer —
rcon reads happen only BETWEEN legs, as assertions.

Usage: server up + provisioned, bridge on port 25591, then
    python mechanism_check.py
Writes mechanism-report.json beside itself; exit 0 only if every
check passed.
"""

from __future__ import annotations

import json
import math
import socket
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent
CONTAINER = "lc-minecraft"
BRIDGE_PORT = 25591
TICK_MS = 50  # the rig's one temporal fabric: /tick rate 100, 50 ms steps

# the bridge's channels come keyed by sensor: pose [x, z, y, sin_yaw,
# cos_yaw], blocks [solid_ahead, solid_eye, drop_ahead]


def yaw_of(channels: dict) -> float:
    return math.atan2(channels["pose"][3], channels["pose"][4])


def solid_ahead(channels: dict) -> float:
    return channels["blocks"][0]


STAND = ("2.5", "-60", "0.5", "-90", "0")  # on the loop, facing east
LAP = [(9.5, 0.5), (9.5, 6.5), (0.5, 6.5), (0.5, 0.5)]  # clockwise ring
BRANCH = [
    (9.5, 3.5),
    (15.5, 3.5),
    (15.5, 8.5),
    (15.5, 9.5),
    (15.5, 10.5),
    (15.5, 11.5),
    (15.5, 12.5),
]
# the exit route hugs the larder's clear north row (z=12) and west
# column (x=12) — the diagonal clips the patch's melon blocks, which
# are unclimbable walls under the 2-high ceiling (measured, run 2)
EXIT = [(15.5, 12.5), (12.5, 12.5), (12.5, 15.5), (6.5, 15.5), (6.5, 7.5), (6.5, 6.5)]
MELON_AHEAD = (15.5, 13.5)  # faced from the larder entry cell
GATE_BLOCK = ("15", "-60", "9")
INDICATOR = tuple(("25", "-63", str(z)) for z in (10, 11, 12))

FWD = {"forward": 1.0}
JUMP = {"jump_forward": 1.0}
LEFT = {"turn_left": 1.0}
RIGHT = {"turn_right": 1.0}
DIG = {"dig_ahead": 1.0}
HOLD = {"hold_next": 1.0}
USE = {"use_held": 1.0}
IDLE: dict[str, float] = {}


def rcon(*cmd: str) -> str:
    r = subprocess.run(
        ["docker", "exec", CONTAINER, "rcon-cli", "--", *cmd],
        capture_output=True,
        text=True,
        timeout=30,
    )
    return (r.stdout or r.stderr).strip()


def laps_score() -> int:
    out = rcon("scoreboard", "players", "get", "laps", "lc")
    for token in out.split():
        if token.lstrip("-").isdigit():
            return int(token)
    raise RuntimeError(f"unreadable laps score: {out!r}")


def block_is(coords: tuple[str, str, str], block: str) -> bool:
    out = rcon("execute", "if", "block", *coords, f"minecraft:{block}")
    return "passed" in out.lower()


class Walker:
    def __init__(self) -> None:
        self.sock = socket.create_connection(("127.0.0.1", BRIDGE_PORT), timeout=60)
        self.buf = b""
        self.steps = 0
        hello = self.call({"op": "hello", "version": "pra-mc/1"})
        if not hello.get("ok"):
            raise RuntimeError(f"bridge refused hello: {hello}")

    def call(self, msg: dict) -> dict:
        self.sock.sendall((json.dumps(msg) + "\n").encode())
        while b"\n" not in self.buf:
            chunk = self.sock.recv(65536)
            if not chunk:
                raise ConnectionError("bridge closed")
            self.buf += chunk
        line, self.buf = self.buf.split(b"\n", 1)
        return json.loads(line)

    def tick(self, command: dict) -> tuple[dict, dict]:
        r = self.call({"op": "tick", "tick_ms": TICK_MS, "commands": [command]})
        if not r.get("ok"):
            raise RuntimeError(f"tick failed: {r}")
        self.steps += 1
        return r["channels"], r["view"]

    def close(self) -> None:
        try:
            self.call({"op": "bye"})
        finally:
            self.sock.close()

    def goto(self, wx: float, wz: float, timeout_steps: int = 800) -> dict:
        """Waypoint follower: turn in 45-degree steps until roughly aligned,
        then walk, jumping when a block stands ahead. Arrival is horizontal
        (the drop tile 'arrives' mid-fall by design)."""
        start = self.steps
        channels, view = self.tick(IDLE)
        while True:
            x, _, z = view["pos"]
            dx, dz = wx - x, wz - z
            if math.hypot(dx, dz) < 0.45:
                return view
            if self.steps - start > timeout_steps:
                raise RuntimeError(f"goto ({wx},{wz}) timed out at pos {view['pos']}")
            yaw = yaw_of(channels)
            want = math.atan2(-dx, -dz)  # mineflayer forward is (-sin, -cos)
            err = (want - yaw + math.pi) % (2 * math.pi) - math.pi
            if abs(err) > math.pi / 8 + 0.05:
                command = LEFT if err > 0 else RIGHT
            elif solid_ahead(channels) > 0.5:
                command = JUMP
            else:
                command = FWD
            channels, view = self.tick(command)

    def face(self, wx: float, wz: float) -> None:
        channels, view = self.tick(IDLE)
        for _ in range(8):
            x, _, z = view["pos"]
            yaw = yaw_of(channels)
            want = math.atan2(-(wx - x), -(wz - z))
            err = (want - yaw + math.pi) % (2 * math.pi) - math.pi
            if abs(err) <= math.pi / 8 + 0.05:
                return
            channels, view = self.tick(LEFT if err > 0 else RIGHT)
        raise RuntimeError("face: did not align in 8 turns")


def slices_of(view: dict) -> int:
    return dict(tuple(pair) for pair in view.get("inventory", [])).get("melon_slice", 0)


def check(report: dict, name: str, ok: bool, detail: object) -> None:
    report["checks"].append({"name": name, "ok": bool(ok), "detail": detail})
    print(f"{'PASS' if ok else 'FAIL'} {name}: {detail}", flush=True)


def main() -> int:
    report: dict = {"checks": [], "gait": {}}
    print("world:", rcon("tick", "rate", "100"), flush=True)
    rcon("effect", "clear", "pra")
    rcon("clear", "pra")  # between-session admin, the rig's newborn idiom
    rcon("kill", "@e[type=item]")
    rcon("setblock", "15", "-58", "13", "minecraft:melon")  # the check's dig target
    for player in ("laps", "armA", "armB", "counted"):
        rcon("scoreboard", "players", "set", player, "lc", "0")
    rcon("tp", "pra", *STAND)
    time.sleep(1.0)  # let the tp and the close-gate conditional land

    w = Walker()
    try:
        # -- three laps, counter and gate read between legs -------------------
        lap_steps: list[int] = []
        for lap in (1, 2, 3):
            start = w.steps
            for wx, wz in LAP:
                w.goto(wx, wz)
            lap_steps.append(w.steps - start)
            check(
                report,
                f"lap {lap} counted",
                laps_score() == lap,
                {"laps": laps_score(), "steps": lap_steps[-1]},
            )
            gate_should_be_open = lap == 3
            is_open = block_is(GATE_BLOCK, "air")
            check(
                report,
                f"gate after lap {lap}",
                is_open == gate_should_be_open,
                {"open": is_open, "expected_open": gate_should_be_open},
            )
        golds = [block_is(c, "gold_block") for c in INDICATOR]
        check(report, "indicator at laps 3", golds == [True, True, True], golds)

        # -- turn in through the branch and the open gate ---------------------
        w.goto(9.5, 0.5)
        for wx, wz in BRANCH:
            w.goto(wx, wz)
        time.sleep(0.5)  # the reset conditional runs on the game's own tick
        check(report, "larder entry resets", laps_score() == 0, {"laps": laps_score()})
        check(report, "gate recloses", block_is(GATE_BLOCK, "obsidian"), {})
        golds = [block_is(c, "gold_block") for c in INDICATOR]
        check(report, "indicator falls with reset", golds == [False, False, False], golds)

        # -- dig, collect, eat (the mouth check relocated) --------------------
        w.face(*MELON_AHEAD)
        channels, view = w.tick(IDLE)
        for _ in range(160):
            if solid_ahead(channels) < 0.5:
                break
            channels, view = w.tick(DIG)
        for _ in range(12):
            channels, view = w.tick(FWD)
        check(report, "melon dug and collected", slices_of(view) > 0, {"slices": slices_of(view)})
        rcon("effect", "give", "pra", "minecraft:hunger", "3", "127")
        time.sleep(1.4)
        rcon("effect", "clear", "pra")
        channels, view = w.tick(IDLE)
        hungry_food = view.get("food", 20)
        for _ in range(10):
            if view.get("held") == "melon_slice":
                break
            channels, view = w.tick(HOLD)
        for _ in range(45):
            channels, view = w.tick(USE)
        check(
            report,
            "eat lands",
            view.get("food", 0) > hungry_food,
            {"before": hungry_food, "after": view.get("food")},
        )

        # -- exit drop, one-way, counting resumed -----------------------------
        for wx, wz in EXIT:
            w.goto(wx, wz)
        for _ in range(10):
            channels, view = w.tick(IDLE)
            if view["pos"][1] <= -59.5:
                break
        check(report, "drop returns to loop", view["pos"][1] <= -59.5, {"pos": view["pos"]})
        max_y = -61.0
        for _ in range(8):
            channels, view = w.tick(JUMP)
            max_y = max(max_y, view["pos"][1])
        check(report, "drop is one-way", max_y < -58.5, {"max_y": max_y})
        w.goto(0.5, 6.5)
        w.goto(0.5, 0.5)
        check(report, "counting resumes", laps_score() == 1, {"laps": laps_score()})

        # -- gait calibration --------------------------------------------------
        full = lap_steps[1:]  # lap 1 starts from the stand, not the corner
        per_lap = sum(full) / len(full)
        report["gait"] = {
            "lap_steps": lap_steps,
            "steps_per_lap": round(per_lap, 1),
            "steps_per_block": round(per_lap / 30, 2),
            "total_steps": w.steps,
        }
        print("gait:", json.dumps(report["gait"]), flush=True)
    finally:
        w.close()

    passed = all(c["ok"] for c in report["checks"])
    report["passed"] = passed
    (HERE / "mechanism-report.json").write_text(json.dumps(report, indent=1))
    print("MECHANISM", "PASS" if passed else "FAIL", flush=True)
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
