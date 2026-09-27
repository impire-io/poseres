"""Walker-driven probe recording for H0(a) (instrument amendment 2).

The decode probe asks a world+body question — CAN a linear readout
decode the lap index from the body's own observation on the decision
span? — which is policy-independent. The flat pilot lives turned out
to carry no label variety (life 1: zero lap crossings in 6,000 steps),
so the probe reads instead on trajectories that genuinely visit laps
1..3: the mechanism walker's closed-loop chains, driven through the
live body, with the flattened 73-channel observation recorded every
tick. Registered in JOURNEY.md before the probe ran; the probe's
question, span, labels, and chance band are unchanged.

Records M full chains (default 6) to mc/walk-life<i>.npz in the exact
format the decode probe reads (obs, pos, food). Between chains the
world is left alone — the reset is the world's own larder conditional,
exactly as in a life.

Usage: server + bridge up, then   python probe_walk.py [chains]
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
MC = HERE / "mc"
MC.mkdir(exist_ok=True)
sys.path.insert(0, str(HERE))

import mechanism_check as W  # noqa: E402 — the proven walker machinery

CHANNEL_ORDER = (
    "pose",
    "vitals",
    "env",
    "blocks",
    "mining",
    "pocket",
    "hand",
    "grid",
    "drops",
    "glance",
)

LAP = W.LAP
BRANCH = [
    (9.5, 3.5),
    (14.5, 3.5),
    (15.5, 3.5),
    (15.5, 8.5),
    (15.5, 9.5),
    (15.5, 10.5),
    (15.5, 11.5),
    (15.5, 12.5),
]
EXIT = W.EXIT


def flat_obs(channels: dict) -> list[float]:
    row: list[float] = []
    for key in CHANNEL_ORDER:
        row.extend(float(v) for v in channels[key])
    return row


class RecordingWalker(W.Walker):
    def __init__(self) -> None:
        super().__init__()
        self.obs_rows: list[list[float]] = []
        self.pos_rows: list[list[float]] = []
        self.food_rows: list[float] = []

    def tick(self, command: dict) -> tuple[dict, dict]:
        channels, view = super().tick(command)
        self.obs_rows.append(flat_obs(channels))
        self.pos_rows.append([float(p) for p in view["pos"]])
        self.food_rows.append(float(view.get("food", 20)))
        return channels, view


def main() -> int:
    chains = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    print("world:", W.rcon("tick", "rate", "100"), flush=True)
    W.rcon("effect", "clear", "pra")
    W.rcon("clear", "pra")
    W.rcon("kill", "@e[type=item]")
    for player in ("laps", "armA", "armB", "counted"):
        W.rcon("scoreboard", "players", "set", player, "lc", "0")
    W.rcon("tp", "pra", *W.STAND)
    time.sleep(1.0)
    w = RecordingWalker()
    try:
        for chain in range(1, chains + 1):
            # chain 1 starts at the stand with 0 crossings: 3 full laps.
            # Later chains re-enter the ring via the west straight (below),
            # which the world already counted as crossing 1: 2 more laps.
            for _lap in range(3 if chain == 1 else 2):
                for wx, wz in LAP:
                    w.goto(wx, wz)
            w.goto(9.5, 0.5)
            for wx, wz in BRANCH:
                w.goto(wx, wz)
            time.sleep(0.3)  # the reset conditional on the game's own tick
            for wx, wz in EXIT:
                w.goto(wx, wz)
            for _ in range(10):
                _, view = w.tick(W.IDLE)
                if view["pos"][1] <= -59.5:
                    break
            # ring return: west along the south row, north up the west
            # straight — the lap-line crossing here IS the next chain's
            # first crossing (a diagonal to the stand would wedge on the
            # inner wall; never cut the ring)
            w.goto(0.5, 6.5)
            w.goto(0.5, 0.5)
            print(f"chain {chain}/{chains} done at step {w.steps}", flush=True)
    finally:
        w.close()
    n = len(w.obs_rows)
    np.savez_compressed(
        MC / "walk-life1.npz",
        obs=np.array(w.obs_rows, dtype=np.float32),
        pos=np.array(w.pos_rows, dtype=np.float32),
        food=np.array(w.food_rows, dtype=np.float32),
    )
    print(f"recorded {n} steps over {chains} chains -> mc/walk-life1.npz", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
