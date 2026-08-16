"""Hungry-birth probe (instrument reading, not a bar; after the arms'
owner stop at seg 2): the arms' null result — food 20/20 for 20k steps,
zero eats, zero deficit — has two possible attributions: the gate does
not couple, or the deficit never arises. Birth the SAME taught brain
STARVING (food 0, a birth condition set before the life — the same
world-admin class as the sated newborn's saturation refill) and read
1,500 steps with the gate on, then again with the gate off. If the
gated hungry life eats where the ungated eats less or not at all, the
coupling is demonstrated live and the arms' null reduces to a world
fact: vanilla's metabolism never bites a body that parks.

Usage: python hungry_probe.py   (after teach; bridge up; no life running)
"""

from __future__ import annotations

import dataclasses
import json
import time

import n23_runner as R

from pra.action.policy import PolicyParams
from pra.action.recipe import RecipePolicy
from pra.anatomy.minecraft import C1_MINING_INDEX, C1_POCKET_TOTAL_INDEX
from pra.persistence.snapshot import decode
from pra.persistence.store import InMemorySnapshotStore

PROBE_CYCLES = 20  # x 75 steps = 1,500


def probe(arm: str) -> dict:
    memory = R.build_memory()
    state = decode(R.TAUGHT.read_bytes())
    R.newborn_live()
    R.rcon("effect", "give", "pra", "minecraft:hunger", "5", "255")  # born starving
    time.sleep(1.4)
    R.rcon("effect", "clear", "pra")
    kd = 0.0 if arm.endswith("n3") else R.KD
    cfg = dataclasses.replace(
        state.config,
        n_cycles=state.cycles_done + PROBE_CYCLES,
        snapshot_every_n_cycles=state.cycles_done + PROBE_CYCLES,
    )
    policy = RecipePolicy(
        PolicyParams.from_config(cfg),
        memory,
        kappa=R.KAP,
        progress_index=C1_MINING_INDEX,
        pocket_index=C1_POCKET_TOTAL_INDEX,
        lambda_r=R.LAM,
        label_index=R.FOOD,
        label_beta=0.0,
        deficit_index=R.FOOD,
        deficit_kappa=kd,
    )
    views: list[dict] = []
    store = InMemorySnapshotStore()
    R.run_engine(
        cfg, policy, dataclasses.replace(state, config=cfg), store, views, R.live_transport
    )
    cum = {"steps": 0, "ge12": 0, "eats": 0, "collects": 0, "starv": False}
    row = R.segment_row(arm, 1, views, policy, cum)
    foods = [v.get("food", 0) for v in views]
    row["kd"] = kd
    row["food_final"] = foods[-1] if foods else None
    row["food_curve_20"] = foods[:: max(len(foods) // 20, 1)]
    return row


def main() -> int:
    rows = []
    print("world:", R.rcon("tick", "rate", "100"), flush=True)
    for arm in ("probe-hungry", "probe-hungry-n3"):
        row = probe(arm)
        rows.append(row)
        print("PROBE " + json.dumps(row), flush=True)
    (R.OUT / "hungry-probe-rows.json").write_text(json.dumps(rows, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
