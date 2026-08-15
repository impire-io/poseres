"""Bars A2/A3 — aimed contact and the ablation (the-aim README).

The winning form (worth, PILOT-READING.md) at the registered protocol:
6 hungry-born 10,050-step lives per arm, each born with the TAUGHT
brain and the TAUGHT tongue (the palate file restored from the taught
snapshot and the bridge restarted per life, so brain and body state
reset together). A2 runs the full stack (AIM=worth, FLOOD=intrusion);
A3 is the decoupling ablation — AIM_ABLATE=1, the book learns but the
lookup reads naive, everything else byte-identical.

Expressing = a seen-forage chain to satiation (>= 1 chain AND food
reaching >= 17). Registered bars: A2 >= 4/6 expressing with median
first-eat <= 3,000 across expressing lives and >= 1 expressing life
crossing the drops leg (drop seen -> approached -> pocketed -> eaten);
A3 <= 2/6 expressing OR median first-eat >= 2x A2's. R-explore
recorded per life (distinct columns, max Chebyshev reach), no
threshold.

    python a23_arms.py a2
    python a23_arms.py a3
    python a23_arms.py verdict
"""

from __future__ import annotations

import dataclasses
import json
import os
import shutil
import statistics
import sys
from pathlib import Path

OUT = Path(__file__).parent
sys.path.insert(0, str(OUT))
sys.path.insert(0, str(OUT.parent / "native-survival" / "arms"))
sys.path.insert(0, str(OUT.parent / "distal-senses"))
import aim_pilot as AP  # noqa: E402 — the form wiring + bridge lifecycle
import d23_runner as D  # noqa: E402 — curriculum/life machinery
import n23_runner as R  # noqa: E402 — engine/classroom helpers

from pra.persistence.snapshot import decode  # noqa: E402
from pra.persistence.store import InMemorySnapshotStore  # noqa: E402

AP.set_form("worth")  # both arms run the worth-taught brain
ARM_LIVES = 6
LIFE_CYCLES = 134  # 10,050 steps >= the registered 10,000
PALATE = OUT / "worth-palate.json"
TAUGHT_PALATE = OUT / "worth-palate-taught.json"


def _index(sensor_id: str, label: str) -> int:
    offset = 0
    for spec in R.SENSORS:
        if spec.id == sensor_id:
            return offset + spec.labels.index(label)
        offset += spec.width
    raise ValueError(sensor_id)


DROP_PRESENT = _index("drops", "present")
DROP_DIST = _index("drops", "dist")


class RecordingPolicy:
    """Wraps the shipped policy; keeps the drops slice per step (A2's
    drops-leg detection needs seen -> approached, which only the
    observation stream carries)."""

    def __init__(self, inner):
        self.inner = inner
        self.drops: list[tuple[float, float]] = []

    def select_action(self, context, rng) -> int:
        o = context.observation
        self.drops.append((float(o[DROP_PRESENT]), float(o[DROP_DIST])))
        return self.inner.select_action(context, rng)

    def __getattr__(self, name):
        return getattr(self.inner, name)


def run_life():
    state = decode(D.TAUGHT.read_bytes())
    cfg = dataclasses.replace(
        state.config,
        steps_per_episode=75,
        n_cycles=state.cycles_done + LIFE_CYCLES,
        snapshot_every_n_cycles=state.cycles_done + LIFE_CYCLES,
    )
    policy = RecordingPolicy(D.make_policy(cfg, kd=R.KD))
    views: list[dict] = []
    store = InMemorySnapshotStore()
    R.run_engine(
        cfg, policy, dataclasses.replace(state, config=cfg), store, views, R.live_transport
    )
    return views, policy


def drops_leg(views: list[dict], drops: list[tuple[float, float]]) -> bool:
    """A drop seen -> approached (sensed distance shrinks >= 0.1 while
    present) -> pocketed (a collect) -> eaten (a genuine eat within 600
    steps): the full drops leg, from the body's own channel."""
    foods = [v.get("food", 0) for v in views]
    counts = [R.slices_of(v) for v in views]
    rises = {i for i in range(1, len(foods)) if foods[i] > foods[i - 1]}
    for i in range(1, len(counts)):
        if counts[i] - counts[i - 1] <= 0:
            continue  # not a collect
        lo = max(0, i - 200)
        seen = [d for p, d in drops[lo:i] if p > 0.5]
        if (
            len(seen) >= 2
            and max(seen) - seen[-1] >= 0.1
            and any(j in rises for j in range(i, min(i + 600, len(foods))))
        ):
            return True
    return False


def explore(views: list[dict]) -> dict:
    cols = {(round(float(v["pos"][0])), round(float(v["pos"][2]))) for v in views}
    reach = max(
        max(abs(float(v["pos"][0]) - D.BIRTH_STAND[0]), abs(float(v["pos"][2]) - D.BIRTH_STAND[1]))
        for v in views
    )
    return {"columns": len(cols), "reach": round(reach, 1)}


def arm(name: str, ablate: bool) -> None:
    rows = []
    out = OUT / f"{name}-rows.json"
    if out.exists():
        rows = json.loads(out.read_text())
        print(f"{name}: resuming at life {len(rows) + 1}", flush=True)
    for life in range(len(rows) + 1, ARM_LIVES + 1):
        shutil.copy(TAUGHT_PALATE, PALATE)  # born with the taught tongue
        os.environ["AIM_ABLATE"] = "1" if ablate else ""
        bridge = AP.start_bridge("worth")
        try:
            D.hungry_newborn()
            views, policy = run_life()
        finally:
            bridge.terminate()
            bridge.wait(timeout=10)
        chains = D.chains_of(views)
        row = {
            "arm": name,
            "life": life,
            **chains,
            "satiated": max((v.get("food", 0) for v in views), default=0) >= 17,
            "expressed": chains["chains"] >= 1
            and max((v.get("food", 0) for v in views), default=0) >= 17,
            "drops_leg": drops_leg(views, policy.drops),
            "completions": policy.completions_fired,
            "false_completions": policy.false_completions,
            "food_min": min((v.get("food", 0) for v in views), default=None),
            "food_max": max((v.get("food", 0) for v in views), default=None),
            **explore(views),
        }
        rows.append(row)
        out.write_text(json.dumps(rows, indent=1))
        print(f"LIFE {json.dumps(row)}", flush=True)
    print(f"{name.upper()}_ARM_COMPLETE", flush=True)


def verdict() -> None:
    a2 = json.loads((OUT / "a2-rows.json").read_text())
    a3 = json.loads((OUT / "a3-rows.json").read_text())

    def read(rows):
        expressing = [r for r in rows if r["expressed"]]
        eats = [r["first_eat"] for r in expressing if r["first_eat"] is not None]
        return {
            "expressing": len(expressing),
            "median_first_eat": statistics.median(eats) if eats else None,
            "drops_leg_lives": sum(1 for r in expressing if r["drops_leg"]),
        }

    ra2, ra3 = read(a2), read(a3)
    a2_pass = (
        ra2["expressing"] >= 4
        and ra2["median_first_eat"] is not None
        and ra2["median_first_eat"] <= 3000
        and ra2["drops_leg_lives"] >= 1
    )
    a3_pass = ra3["expressing"] <= 2 or (
        ra2["median_first_eat"] is not None
        and ra3["median_first_eat"] is not None
        and ra3["median_first_eat"] >= 2 * ra2["median_first_eat"]
    )
    print(json.dumps({"A2": ra2, "A2_pass": a2_pass, "A3": ra3, "A3_pass": a3_pass}, indent=1))


def main() -> int:
    phase = sys.argv[1] if len(sys.argv) > 1 else ""
    if phase == "verdict":
        verdict()
        return 0
    print("world:", R.rcon("tick", "rate", "100"), flush=True)
    if phase == "a2":
        arm("a2", ablate=False)
    elif phase == "a3":
        arm("a3", ablate=True)
    else:
        raise SystemExit("usage: a23_arms.py a2|a3|verdict")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
