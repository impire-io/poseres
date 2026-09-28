"""Classify every world-counter increment in a recorded life as a REAL lap or a
DITHER (topic the-arena-revival, amendment 5's evidence).

The laps sense (obs channel 73 on the sibling body) is the world's own counter,
sampled every step. An increment is a real lap if, since the previous
increment (or birth), the body's centre visited the loop's three far corners
in order — (9,0), (9,6), (0,6) — i.e. it went around. Otherwise the increment
came from the detector's hitbox loophole (a dither at the lap line).

Usage: python lap_classify.py sap [sib]   (reads mc/<arm>-life*.npz)
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

MC = Path(__file__).parent / "mc"
CORNERS = ((9, 0), (9, 6), (0, 6))
LAPS_CH = 73


def classify(npz: Path) -> dict:
    d = np.load(npz)
    obs, pos = d["obs"], d["pos"]
    n = min(len(obs), len(pos))
    obs, pos = obs[:n], pos[:n]
    if obs.shape[1] <= LAPS_CH:
        return {"life": npz.stem, "note": "no laps sense on this body"}
    laps = obs[:, LAPS_CH]
    incs = [i for i in range(1, n) if laps[i] > laps[i - 1] + 1e-6]
    resets = [i for i in range(1, n) if laps[i] < laps[i - 1] - 1e-6]
    cells = [(int(np.floor(p[0])), int(np.floor(p[2]))) for p in pos]
    real, dither = [], []
    start = 0
    for i in incs:
        seg = cells[start:i]
        k = 0
        for c in seg:
            if k < 3 and c == CORNERS[k]:
                k += 1
        (real if k == 3 else dither).append(i)
        start = i
    return {
        "life": npz.stem,
        "world_increments": len(incs),
        "real_laps": len(real),
        "dither_increments": len(dither),
        "increment_steps": incs,
        "dither_steps": dither,
        "resets": resets,
    }


def main() -> int:
    for arm in sys.argv[1:] or ["sap"]:
        for p in sorted(MC.glob(f"{arm}-life*.npz"), key=lambda q: int(q.stem.split("life")[1])):
            r = classify(p)
            print(r)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
