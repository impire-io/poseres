"""Bar A1 — the aim is real (live instrument reading, before any arm).

Both forms read against the live world, one palate carried between them
(PALATE_FILE across bridge restarts — the tongue is body state):

Phase W (AIM=worth, born naive): a SEEN melon reads zero worth on the
naive book; one scripted meal (dig -> collect -> eat) prices the chain;
the melon sector then reads 1.0 relative worth while an unpriced stone
behind reads 0 — priced vs unpriced in one sample; the channel is plain
and ungained (hungry == sated, exactly); the drop slot prices a summoned
melon_slice at 1.0 and a stick at 0.

Phase S (AIM=salience, the SAME book, no new meal): sated everything is
plain; hungry the unpriced stone fades by the measured g = 1 - f toward
the glance's own "nothing" (dist toward OPEN) while the priced melon
sector stays; a summoned unpriced drop's presence fades to 1 - f, a
priced one stays at 1.

Rows to a1-rows.json; bridge logs beside it.

    python a1_reading.py    (n1-minecraft up; starts its own bridge per form)
"""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

OUT = Path(__file__).parent
sys.path.insert(0, str(OUT.parent / "native-survival" / "arms"))
import n23_runner as R  # noqa: E402 — rcon + the shared constants

BRIDGE_JS = OUT.parent.parent.parent / "examples" / "minecraft" / "bridge" / "bridge.js"
PALATE = OUT / "a1-palate.json"
STAND = ("5.5", "-60", "2.5", "0", "0")  # V0 stand, facing the classroom melon
MELON = ("5", "-60", "3")  # sector 0 (ahead), distance 1
STONE = ("5", "-60", "1")  # sector 4 (behind), distance 1 — the unpriced appearance
OTHER_MELONS = (("10", "-60", "6"), ("16", "-60", "2"))  # V1/V2 cells, cleared
DROP_SPOT = ("5.5", "-60", "6.5")  # 4 blocks ahead: in drops range, out of pickup
FWD, BACK, DIG, IDLE, HOLD, USE = 0, 1, 5, 7, 8, 12
MEAL_TAPE = [DIG] * 40 + [FWD] * 9 + [BACK] * 9 + [HOLD] + [USE] * 30 + [IDLE] * 4
COMMANDS = {
    FWD: {"forward": 1.0},
    BACK: {"back": 1.0},
    DIG: {"dig_ahead": 1.0},
    IDLE: {},
    HOLD: {"hold_next": 1.0},
    USE: {"use_held": 1.0},
}

checks: list[dict] = []


def check(name: str, ok: bool, detail) -> None:
    checks.append({"check": name, "pass": bool(ok), "detail": detail})
    print(f"{'PASS' if ok else 'FAIL'}  {name}: {detail}", flush=True)


def flood_of(food: int) -> float:
    d = max(0.0, 1.0 - food / 20)
    return 0.0 if d <= 0.25 else ((d - 0.25) / 0.75) ** 2


class Bridge:
    """One bridge process per form; the reading owns its lifecycle."""

    def __init__(self, aim: str):
        env = {
            **os.environ,
            "SURVIVAL": "1",
            "AIM": aim,
            "PALATE_FILE": str(PALATE),
            "SPAWN_ANCHOR": "0,0",
            "MC_PORT": "25602",
            "BRIDGE_PORT": str(R.BRIDGE_PORT),
        }
        self.log = open(OUT / f"a1-bridge-{aim}.log", "w")
        self.proc = subprocess.Popen(
            ["node", str(BRIDGE_JS)], env=env, stdout=self.log, stderr=subprocess.STDOUT
        )
        self.buf = b""
        for _ in range(120):
            try:
                self.sock = socket.create_connection(("127.0.0.1", R.BRIDGE_PORT), timeout=2)
                break
            except OSError:
                time.sleep(0.5)
        else:
            raise SystemExit(f"bridge (AIM={aim}) never listened — see its log")

    def call(self, msg: dict) -> dict:
        self.sock.sendall((json.dumps(msg) + "\n").encode())
        while b"\n" not in self.buf:
            chunk = self.sock.recv(65536)
            if not chunk:
                raise ConnectionError("bridge closed")
            self.buf += chunk
        line, self.buf = self.buf.split(b"\n", 1)
        return json.loads(line)

    def tick(self, cmd: dict) -> dict:
        return self.call({"op": "tick", "tick_ms": R.TICK_MS, "commands": [cmd]})

    def sample(self) -> dict:
        return self.tick({})

    def close(self) -> None:
        try:
            self.call({"op": "bye"})
        except Exception:
            pass
        self.sock.close()
        self.proc.terminate()
        self.proc.wait(timeout=10)
        self.log.close()


def sector(glance: list[float], k: int) -> list[float]:
    return glance[4 * k : 4 * k + 4]


def classroom() -> None:
    R.rcon("clear", "pra")
    R.rcon("kill", "@e[type=item]")
    for cell in OTHER_MELONS:
        R.rcon("setblock", *cell, "minecraft:air")
    R.rcon("setblock", *MELON, "minecraft:melon")
    R.rcon("setblock", *STONE, "minecraft:stone")
    R.rcon("tp", "pra", *STAND)


def sate() -> None:
    R.rcon("effect", "clear", "pra")
    R.rcon("effect", "give", "pra", "minecraft:saturation", "2", "255")
    time.sleep(1.2)
    R.rcon("effect", "clear", "pra")


def dose_hungry(bridge: Bridge, target: int = 10) -> int:
    for _ in range(6):
        R.rcon("effect", "give", "pra", "minecraft:hunger", "5", "255")
        time.sleep(1.4)
        R.rcon("effect", "clear", "pra")
        food = bridge.sample()["view"]["food"]
        if food <= target:
            return food
    raise SystemExit(f"could not dose below {target} (food={food})")


def summon_drop(item: str) -> None:
    R.rcon("kill", "@e[type=item]")
    R.rcon("summon", "minecraft:item", *DROP_SPOT, '{Item:{id:"minecraft:' + item + '",count:1}}')
    time.sleep(0.6)  # the entity settles


def phase_worth() -> None:
    if PALATE.exists():
        PALATE.unlink()  # born naive
    bridge = Bridge("worth")
    try:
        hello = bridge.call({"op": "hello", "version": "pra-mc/1"})
        check(
            "W0 handshake: aim channel width 9",
            hello["channels"].get("aim") == 9,
            hello["channels"],
        )
        classroom()
        sate()
        r = bridge.sample()
        aim, s0 = r["channels"]["aim"], sector(r["channels"]["glance"], 0)
        seen = s0[0] < 0.1 and max(abs(v) for v in s0[1:]) > 0.05
        check(
            "W1 naive book: the melon is SEEN yet reads zero worth",
            seen and all(v == 0 for v in aim),
            {"glance_s0": s0, "aim": aim},
        )
        food0 = dose_hungry(bridge)
        for a in MEAL_TAPE:
            r = bridge.tick(COMMANDS[a])
        palate = r["view"]["palate"]
        check(
            "W-meal: one scripted meal prices the chain (melon + melon_slice)",
            palate.get("melon", 0) > 0 and palate.get("melon_slice", 0) > 0,
            {"food_before": food0, "food_after": r["view"]["food"], "palate": palate},
        )
        classroom()  # the melon was dug; rebuild the scene
        sate()
        book_before = bridge.sample()["view"]["palate"]
        check(
            "W-guard: the saturation dose paid nothing (no held use)",
            book_before == palate,
            {"palate": book_before},
        )
        r = bridge.sample()
        aim, glance = r["channels"]["aim"], r["channels"]["glance"]
        check(
            "W2 priced vs unpriced in one sample: melon sector 1.0, stone 0",
            abs(aim[0] - 1.0) < 1e-6 and aim[4] == 0,
            {"aim": aim},
        )
        sated_aim, sated_glance = aim, glance
        food = dose_hungry(bridge)
        r = bridge.sample()
        aim, glance = r["channels"]["aim"], r["channels"]["glance"]
        plain = max(
            abs(a - b) for a, b in zip(sector(glance, 4), sector(sated_glance, 4), strict=True)
        )
        check(
            "W3 plain and ungained: worth identical hungry, senses unfaded",
            abs(aim[0] - sated_aim[0]) < 1e-9 and aim[4] == sated_aim[4] and plain < 0.05,
            {"food": food, "aim_s0": aim[0], "stone_sector_drift": plain},
        )
        sate()
        summon_drop("stick")
        a_stick = bridge.sample()["channels"]["aim"]
        summon_drop("melon_slice")
        a_slice = bridge.sample()["channels"]["aim"]
        check(
            "W4 the drop slot prices: stick 0, melon_slice 1.0",
            a_stick[8] == 0 and abs(a_slice[8] - 1.0) < 1e-6,
            {"stick": a_stick[8], "melon_slice": a_slice[8]},
        )
        R.rcon("kill", "@e[type=item]")
    finally:
        bridge.close()


def phase_salience() -> None:
    bridge = Bridge("salience")  # the SAME book: PALATE_FILE carries the tongue
    try:
        hello = bridge.call({"op": "hello", "version": "pra-mc/1"})
        classroom()
        sate()
        r = bridge.sample()
        palate = r["view"]["palate"]
        check(
            "S0 persistence: no aim channel, the book survived the restart",
            "aim" not in hello["channels"] and palate.get("melon", 0) > 0,
            {"channels": hello["channels"], "palate": palate},
        )
        glance = r["channels"]["glance"]
        s_melon, s_stone = sector(glance, 0), sector(glance, 4)
        check(
            "S1 sated everything is plain: melon AND stone fully visible",
            s_melon[0] < 0.1
            and s_stone[0] < 0.1
            and max(abs(v) for v in s_melon[1:]) > 0.05
            and max(abs(v) for v in s_stone[1:]) > 0.05,
            {"melon_s0": s_melon, "stone_s4": s_stone},
        )
        sated = {"melon": s_melon, "stone": s_stone}
        food = dose_hungry(bridge)
        r = bridge.sample()
        food = r["view"]["food"]
        f = flood_of(food)
        g = 1 - f  # the unpriced gain the instrument owes the formula
        glance = r["channels"]["glance"]
        s_melon, s_stone = sector(glance, 0), sector(glance, 4)
        melon_drift = max(abs(a - b) for a, b in zip(s_melon, sated["melon"], strict=True))
        dist_err = abs((1 - s_stone[0]) - g * (1 - sated["stone"][0]))
        sig_err = max(abs(s_stone[j] - g * sated["stone"][j]) for j in range(1, 4))
        check(
            "S2 hungry: the priced melon stays, the unpriced stone fades by 1-f",
            f > 0.05 and melon_drift < 0.02 and dist_err < 0.02 and sig_err < 0.02,
            {
                "food": food,
                "f": round(f, 4),
                "melon_drift": round(melon_drift, 4),
                "stone_dist": [sated["stone"][0], s_stone[0]],
                "dist_err": round(dist_err, 4),
                "sig_err": round(sig_err, 4),
            },
        )
        summon_drop("stick")
        d_stick = bridge.sample()["channels"]["drops"]
        summon_drop("melon_slice")
        d_slice = bridge.sample()["channels"]["drops"]
        check(
            "S3 the drop fades by its price: stick presence 1-f, slice 1",
            abs(d_stick[0] - g) < 0.05 and abs(d_slice[0] - 1.0) < 0.05,
            {"f": round(f, 4), "stick_present": d_stick[0], "slice_present": d_slice[0]},
        )
        R.rcon("kill", "@e[type=item]")
    finally:
        bridge.close()


def cleanup() -> None:
    R.rcon("setblock", *STONE, "minecraft:air")
    R.rcon("setblock", *MELON, "minecraft:melon")
    R.rcon("kill", "@e[type=item]")
    R.rcon("clear", "pra")
    sate()


def main() -> int:
    print("world:", R.rcon("tick", "rate", "100"), flush=True)
    try:
        phase_worth()
        phase_salience()
    finally:
        cleanup()
        (OUT / "a1-rows.json").write_text(json.dumps(checks, indent=2))
    failed = [c["check"] for c in checks if not c["pass"]]
    print(f"\n{len(checks) - len(failed)}/{len(checks)} PASS", flush=True)
    if failed:
        print("FAILED:", *failed, sep="\n  ", flush=True)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
