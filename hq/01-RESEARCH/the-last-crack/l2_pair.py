"""Bar L2 — the convicted fix, back-to-back with its baseline.

Same parked-decree geometry, same taught brain and tongue, 1,500 steps
per arm on the same classroom: BASELINE (flags off — the shipped
knife-edge vote) then COMMITTED (commit_kappa = 0.1 — above the
largest measured flip margin 0.069 — and explore_defers_holds, the
ε-gate yielding to a live hold). Read: digs run to the world's own
break (progress ≥ 0.8 collapsing to ≤ 0.1 with slices pocketed within
100 frames), collects, eats, first-eat. Bar: committed ≥ 5 breaks and
≥ 1 full dig → collect → eat chain where baseline reads 0.

    python l2_pair.py    (rows to l2-rows.json)
"""

from __future__ import annotations

import dataclasses
import itertools
import json
import os
import shutil
import sys
from pathlib import Path

OUT = Path(__file__).parent
sys.path.insert(0, str(OUT.parent / "the-aim"))
sys.path.insert(0, str(OUT.parent / "native-survival" / "arms"))
sys.path.insert(0, str(OUT.parent / "distal-senses"))
import a23_arms as A  # noqa: E402
import aim_pilot as AP  # noqa: E402
import d23_runner as D  # noqa: E402
import decree_control as DC  # noqa: E402
import n23_runner as R  # noqa: E402

from pra.action.policy import PolicyParams  # noqa: E402
from pra.action.recipe import RecipePolicy  # noqa: E402
from pra.anatomy.minecraft import C1_MINING_INDEX, C1_POCKET_TOTAL_INDEX  # noqa: E402
from pra.persistence.snapshot import decode  # noqa: E402
from pra.persistence.store import InMemorySnapshotStore  # noqa: E402

STEPS = 1_500
DIG = 5
COMMIT_KAPPA = 0.1  # > the largest L1-measured flip margin (0.069)


def make_policy(cfg, kd: float, committed: bool) -> RecipePolicy:
    # d23_runner.make_policy plus the-last-crack's two opt-in flags
    return RecipePolicy(
        PolicyParams.from_config(cfg),
        D.build_memory(),
        kappa=R.KAP,
        progress_index=C1_MINING_INDEX,
        pocket_index=C1_POCKET_TOTAL_INDEX,
        lambda_r=R.LAM,
        label_index=R.FOOD,
        label_beta=0.0,
        deficit_index=R.FOOD,
        deficit_kappa=kd,
        commit_kappa=COMMIT_KAPPA if committed else 0.0,
        explore_defers_holds=committed,
    )


class MiniTrace(DC.DecreePolicy):
    def __init__(self, inner):
        super().__init__(inner)
        self.mine: list[float] = []
        self.acts: list[int] = []

    def select_action(self, context, rng) -> int:
        o = context.observation
        self.drops.append((float(o[DC.DROP_PRESENT]), float(o[DC.DROP_DIST])))
        self.mine.append(float(o[DC.MINING]))
        steer = self._steer(o)
        action = steer if steer is not None else self.inner.select_action(context, rng)
        if steer is not None:
            self.steered += 1
        else:
            self.delegated += 1
        self.acts.append(int(action))
        return action


def breaks_of(mine: list[float], acts: list[int], slices: list[int]) -> int:
    n = 0
    for i in range(1, len(mine)):
        if acts[i - 1] == DIG and mine[i - 1] >= 0.8 and mine[i] <= 0.1:
            if any(slices[j] > slices[i - 1] for j in range(i, min(i + 100, len(slices)))):
                n += 1
    return n


def arm(name: str, committed: bool) -> dict:
    shutil.copy(A.TAUGHT_PALATE, A.PALATE)
    os.environ["AIM_ABLATE"] = ""
    bridge = AP.start_bridge("worth")
    try:
        D.hungry_newborn()
        state = decode(D.TAUGHT.read_bytes())
        cycles = STEPS // 75
        cfg = dataclasses.replace(
            state.config,
            steps_per_episode=75,
            n_cycles=state.cycles_done + cycles,
            snapshot_every_n_cycles=state.cycles_done + cycles,
        )
        policy = MiniTrace(make_policy(cfg, kd=R.KD, committed=committed))
        views: list[dict] = []
        store = InMemorySnapshotStore()
        R.run_engine(
            cfg, policy, dataclasses.replace(state, config=cfg), store, views, R.live_transport
        )
    finally:
        bridge.terminate()
        bridge.wait(timeout=10)
    slices = [R.slices_of(v) for v in views]
    chains = D.chains_of(views)
    row = {
        "arm": name,
        "breaks": breaks_of(policy.mine, policy.acts, slices),
        "collects": sum(1 for i in range(1, len(slices)) if slices[i] > slices[i - 1]),
        **chains,
        "longest_dig_run": max(
            (len(list(g)) for k, g in itertools.groupby(policy.acts) if k == DIG),
            default=0,
        ),
        "steered": policy.steered,
        "delegated": policy.delegated,
        "food_min": min((v.get("food", 0) for v in views), default=None),
        "food_max": max((v.get("food", 0) for v in views), default=None),
    }
    print(f"ARM {json.dumps(row)}", flush=True)
    return row


REPEATS = 3  # single 1,500-step arms measured 7-vs-1 break variance on the
# same config (JOURNEY.md) — the pair is powered by repeats, totals compared


def main() -> int:
    print("world:", R.rcon("tick", "rate", "100"), flush=True)
    rows = []
    for r in range(1, REPEATS + 1):
        rows.append({"repeat": r, **arm("baseline", committed=False)})
        rows.append({"repeat": r, **arm("committed", committed=True)})
    (OUT / "l2-rows.json").write_text(json.dumps(rows, indent=1))
    base = [r for r in rows if r["arm"] == "baseline"]
    com = [r for r in rows if r["arm"] == "committed"]
    b_breaks = sum(r["breaks"] for r in base)
    c_breaks = sum(r["breaks"] for r in com)
    c_eats = sum(r["eats"] for r in com)
    ok = c_breaks >= 5 and b_breaks == 0 and c_eats >= 1
    print(
        f"L2 {'PASS' if ok else 'FAIL'}: baseline breaks={b_breaks} "
        f"| committed breaks={c_breaks} eats={c_eats}",
        flush=True,
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
