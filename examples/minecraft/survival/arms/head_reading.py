"""What did the head learn about digging? (live instrument reading)

The taught brain's event head (feature 040: per-action linear NLMS,
delta = W[a] @ [obs, 1]) is read AT REAL OBSERVATIONS on the live
server — the contexts a foraging life actually faces at the patch —
with no learning and no policy: pure W, frozen from the 45 lessons.
For each context x action we report the three load-bearing channels
(food 6, progress 14, pocket-total 15), whether the completion rule
would fire (delta[pocket] > 1/128), and the resulting itch term
kappa*(progress_after - progress_now) — the number that decides
whether the itch starts and holds a dig or a chew.

World admin (rcon) preps each context BETWEEN samples — an instrument
session, not a life. Fabric matches the lessons: tick rate 100, 50 ms.

Usage: python head_reading.py   (after teach; bridge up; no life running)
"""

from __future__ import annotations

import json
import socket
import time

import n23_runner as R
import numpy as np

from pra.persistence.snapshot import decode

CHANNEL_ORDER = ("pose", "vitals", "env", "blocks", "mining", "pocket", "hand", "grid")
ACTIONS = {0: "forward", 1: "back", 4: "jump", 5: "dig", 7: "idle", 8: "hold", 12: "use"}
FOOD, PROG, POCKET = R.FOOD, 14, 15
KAPPA, KD = R.KAP, R.KD
THRESH = 1.0 / 128.0


class Session:
    def __init__(self, port: int):
        self.sock = socket.create_connection(("127.0.0.1", port), timeout=30)
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

    def tick(self, command: dict) -> dict:
        return self.call({"op": "tick", "tick_ms": R.TICK_MS, "commands": [command]})

    def close(self) -> None:
        self.call({"op": "bye"})
        self.sock.close()


def obs_of(response: dict) -> np.ndarray:
    channels = response["channels"]
    return np.concatenate([np.asarray(channels[name], dtype=float) for name in CHANNEL_ORDER])


def read_context(W: np.ndarray, name: str, obs: np.ndarray, view: dict) -> dict:
    x = np.append(obs, 1.0)
    deficit = min(max(1.0 - float(obs[FOOD]), 0.0), 1.0)
    weight = KD * deficit  # label_beta = 0 in the arms
    progress_now = float(obs[PROG])
    rows = {}
    for a, label in ACTIONS.items():
        delta = W[a] @ x
        completion = float(delta[POCKET]) > THRESH
        if completion:
            progress_after = 1.0 + weight * min(max(float(delta[FOOD]), 0.0), 1.0)
        else:
            progress_after = min(max(progress_now + float(delta[PROG]), 0.0), 1.0)
        rows[label] = {
            "d_food": round(float(delta[FOOD]), 4),
            "d_prog": round(float(delta[PROG]), 4),
            "d_pocket": round(float(delta[POCKET]), 4),
            "completion": completion,
            "itch": round(KAPPA * (progress_after - progress_now), 4),
        }
    best = max(rows, key=lambda k: rows[k]["itch"])
    print(
        f"\n== {name} (food={view.get('food')} held={view.get('held')} "
        f"prog={round(progress_now, 2)} deficit={round(deficit, 2)})"
    )
    for label, r in rows.items():
        mark = " <-- itch argmax" if label == best else ""
        print(
            f"  {label:8s} d_food={r['d_food']:+.4f} d_prog={r['d_prog']:+.4f} "
            f"d_pocket={r['d_pocket']:+.4f} completion={str(r['completion']):5s} "
            f"itch={r['itch']:+.4f}{mark}"
        )
    return {
        "context": name,
        "food": view.get("food"),
        "held": view.get("held"),
        "progress": progress_now,
        "deficit": deficit,
        "actions": rows,
        "itch_argmax": best,
    }


def main() -> int:
    state = decode(R.TAUGHT.read_bytes())
    eh = state.frame_store["event_head"]
    W = np.asarray(eh["W"])
    print(f"head: W{W.shape}, {eh['updates']} taught updates", flush=True)
    print("world:", R.rcon("tick", "rate", "100"), flush=True)

    readings = []
    # classroom-style prep: clean body at the stand, melon ahead
    R.rcon("effect", "clear", "pra")
    R.rcon("clear", "pra")
    R.rcon("kill", "@e[type=item]")
    R.rcon("setblock", *R.CLASSROOM_MELON, "minecraft:melon")
    R.rcon("tp", "pra", *R.STAND)
    R.rcon("effect", "give", "pra", "minecraft:saturation", "2", "255")
    time.sleep(1.2)
    R.rcon("effect", "clear", "pra")
    s = Session(R.BRIDGE_PORT)
    s.tick({"hold_next": 1.0})  # empty pocket: held -> null, deterministic
    r = s.tick({})
    readings.append(read_context(W, "A sated, melon ahead, empty pocket", obs_of(r), r["view"]))

    R.rcon("effect", "give", "pra", "minecraft:hunger", "5", "255")
    time.sleep(1.4)
    R.rcon("effect", "clear", "pra")
    r = s.tick({})
    readings.append(read_context(W, "B HUNGRY, melon ahead, empty pocket", obs_of(r), r["view"]))

    R.rcon("give", "pra", "minecraft:melon_slice", "5")
    time.sleep(0.3)
    r = s.tick({})
    readings.append(
        read_context(W, "C hungry, 5 slices pocketed, hand empty", obs_of(r), r["view"])
    )

    r = s.tick({"hold_next": 1.0})
    readings.append(read_context(W, "D hungry, HOLDING a slice", obs_of(r), r["view"]))

    for _ in range(3):
        r = s.tick({"use_held": 1.0})
    readings.append(read_context(W, "E hungry, MID-CHEW (use held 3 ticks)", obs_of(r), r["view"]))

    s.tick({})  # release the chew
    for _ in range(4):
        r = s.tick({"dig_ahead": 1.0})
    readings.append(read_context(W, "F hungry, MID-DIG (dig held 4 ticks)", obs_of(r), r["view"]))

    s.tick({})
    R.rcon("effect", "give", "pra", "minecraft:saturation", "2", "255")
    time.sleep(1.2)
    R.rcon("effect", "clear", "pra")
    r = s.tick({})
    readings.append(read_context(W, "G SATED, holding a slice, melon ahead", obs_of(r), r["view"]))
    s.close()

    (R.OUT / "head-reading-rows.json").write_text(json.dumps(readings, indent=1))
    print("\nrows -> head-reading-rows.json", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
