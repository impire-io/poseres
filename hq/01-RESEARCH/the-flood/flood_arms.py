"""The F bars (the-flood README): intrusion won R-form and runs here.

F1 (initiation): 6 flooded hungry-born 6,000-step lives — >= 4 express
(>= 1 genuine eat) with median first-eat < 3,000.
F2 (the flood releases): in every flooded life that reaches food >= 16,
the following 1,000 steps show no action above 50% share, use_held
below 10%, and >= 5 unique columns.
F3 (the flood carries it): 6 silenced lives (bridge FLOOD=off — the
channel present and zeroed), SAME intrusion-taught brain: flooded
expression >= 4/6, silenced <= 2/6, gap >= 2.

    python flood_arms.py flooded    (bridge FLOOD=intrusion)
    python flood_arms.py silenced   (bridge FLOOD=off)
    python flood_arms.py verdict
"""

from __future__ import annotations

import dataclasses
import json
import statistics
import sys
from pathlib import Path

OUT = Path(__file__).parent
sys.path.insert(0, str(OUT.parent / "native-survival" / "arms"))
sys.path.insert(0, str(OUT.parent / "distal-senses"))
import d23_runner as D  # noqa: E402
import flood_pilot as FP  # noqa: E402 — patches the shared machinery to obs 77
import n23_runner as R  # noqa: E402

from pra.persistence.snapshot import decode  # noqa: E402
from pra.persistence.store import InMemorySnapshotStore  # noqa: E402

FP.set_form("intrusion")  # both arms run the intrusion-taught brain
ARM_LIVES = 6
LIFE_CYCLES = 80  # 6,000 steps
USE_ACTION = 12


class RecordingPolicy:
    """Wraps the shipped policy; records the chosen action stream (F2)."""

    def __init__(self, inner):
        self.inner = inner
        self.actions: list[int] = []

    def select_action(self, context, rng) -> int:
        action = self.inner.select_action(context, rng)
        self.actions.append(action)
        return action

    def __getattr__(self, name):
        return getattr(self.inner, name)


def run_life(kd: float):
    state = decode(FP.D.TAUGHT.read_bytes())
    cfg = dataclasses.replace(
        state.config,
        steps_per_episode=75,
        n_cycles=state.cycles_done + LIFE_CYCLES,
        snapshot_every_n_cycles=state.cycles_done + LIFE_CYCLES,
    )
    policy = RecordingPolicy(D.make_policy(cfg, kd))
    views: list[dict] = []
    store = InMemorySnapshotStore()
    R.run_engine(
        cfg, policy, dataclasses.replace(state, config=cfg), store, views, R.live_transport
    )
    return views, policy


def f2_windows(views: list[dict], actions: list[int]) -> list[dict]:
    """Post-satiation windows: from each first-reach of food >= 16, the
    next 1,000 steps' action shares and unique columns."""
    windows = []
    i = 0
    foods = [v.get("food", 0) for v in views]
    while i < len(foods):
        if foods[i] >= 16 and (i == 0 or foods[i - 1] < 16):
            lo, hi = i, min(i + 1000, len(foods))
            acts = actions[max(lo - 1, 0) : hi - 1]  # action k produces view k+1
            if len(acts) < 200:
                break  # too little tail to judge
            shares: dict[int, float] = {}
            for a in acts:
                shares[a] = shares.get(a, 0) + 1
            shares = {a: n / len(acts) for a, n in shares.items()}
            columns = {(round(float(v["pos"][0])), round(float(v["pos"][2]))) for v in views[lo:hi]}
            windows.append(
                {
                    "at": lo,
                    "max_share": round(max(shares.values()), 3),
                    "use_share": round(shares.get(USE_ACTION, 0.0), 3),
                    "unique": len(columns),
                    "pass": max(shares.values()) <= 0.5
                    and shares.get(USE_ACTION, 0.0) < 0.10
                    and len(columns) >= 5,
                }
            )
        i += 1
    return windows


def arm(name: str, kd: float) -> None:
    rows = []
    for life in range(1, ARM_LIVES + 1):
        D.hungry_newborn()
        views, policy = run_life(kd)
        row = {
            "arm": name,
            "life": life,
            **D.chains_of(views),
            "f2_windows": f2_windows(views, policy.actions),
            "food_max": max((v.get("food", 0) for v in views), default=None),
        }
        rows.append(row)
        print(f"LIFE {json.dumps(row)}", flush=True)
    (OUT / f"f-{name}-rows.json").write_text(json.dumps(rows, indent=1))
    print(f"{name.upper()}_ARM_COMPLETE", flush=True)


def verdict() -> None:
    flooded = json.loads((OUT / "f-flooded-rows.json").read_text())
    silenced = json.loads((OUT / "f-silenced-rows.json").read_text())
    fx = sum(1 for r in flooded if r["eats"] > 0)
    sx = sum(1 for r in silenced if r["eats"] > 0)
    firsts = [r["first_eat"] for r in flooded if r["first_eat"] is not None]
    median_first = statistics.median(firsts) if firsts else None
    all_windows = [w for r in flooded for w in r["f2_windows"]]
    out = {
        "f1_expressed": f"{fx}/{ARM_LIVES}",
        "f1_median_first_eat": median_first,
        "f1_pass": fx >= 4 and median_first is not None and median_first < 3000,
        "f2_windows": len(all_windows),
        "f2_pass": bool(all_windows) and all(w["pass"] for w in all_windows),
        "f3_flooded": fx,
        "f3_silenced": sx,
        "f3_pass": fx >= 4 and sx <= 2 and (fx - sx) >= 2,
    }
    (OUT / "f-verdict.json").write_text(json.dumps(out, indent=1))
    print("F_VERDICT " + json.dumps(out), flush=True)


def main() -> int:
    phase = sys.argv[1] if len(sys.argv) > 1 else ""
    if phase == "flooded":
        print("world:", R.rcon("tick", "rate", "100"), flush=True)
        arm("flooded", R.KD)
    elif phase == "silenced":
        print("world:", R.rcon("tick", "rate", "100"), flush=True)
        arm("silenced", R.KD)  # same policy config; the BRIDGE silences the flood
    elif phase == "verdict":
        verdict()
    else:
        raise SystemExit("usage: flood_arms.py flooded|silenced|verdict")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
