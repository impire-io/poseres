"""The declared walk, mechanized (JOURNEY.md 2026-08-18): per rung,
solo P0 screen then hostile; a P0 fail disqualifies the rung; the
walk stops at the first hostile below-12 steady-state in 0.10-0.90
(freezing stays a hand act).

    python walk.py T6 T3 T1
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

RIG = Path(__file__).parent
PY = sys.executable


def metrics(name: str) -> dict:
    rows = [json.loads(x) for x in (RIG / f"{name}-status.jsonl").read_text().splitlines()]
    ss = [r["food_ge12_seg"] for r in rows if r["seg"] >= 2]
    return {
        "below12_ss": round(1 - sum(ss) / len(ss), 4),
        "eats": rows[-1]["eats_cum"],
        "starv": rows[-1]["starv_cum"],
    }


def main() -> int:
    for rung in sys.argv[1:]:
        subprocess.run([PY, str(RIG / "sep.py"), "solo", rung], check=True)
        m = metrics(f"{rung}-solo")
        print(f"S0 {rung} {json.dumps(m)}", flush=True)
        if not (m["starv"] == 0 and m["eats"] >= 3 and m["below12_ss"] <= 0.10):
            print(f"S0 FAIL {rung} — rung disqualified, no hostile arm", flush=True)
            continue
        subprocess.run([PY, str(RIG / "sep.py"), "hostile", rung], check=True)
        h = metrics(f"{rung}-hostile")
        print(f"S1 {rung} {json.dumps(h)}", flush=True)
        if 0.10 <= h["below12_ss"] <= 0.90:
            print(f"BAND HIT {rung} — the walk stops; freezing is a hand act", flush=True)
            break
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
