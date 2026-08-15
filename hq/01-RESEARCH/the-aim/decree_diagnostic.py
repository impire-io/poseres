"""Decree diagnostic — who is in charge at the melon, and what do they do?

1,500 steps under the v4 decree, logging per frame: controller
(decree|head), action, mining progress, aim s0 / glance d0, drop
present, pocket, food. Discriminates:
  H1  the head never holds a dig at the melon (walks off, snap-back
      dance — no 30-step consecutive dig ever forms)
  H2  digs form but die: interleaved decree steer frames release the
      held intention (any non-dig command aborts a dig)
  H3  digs complete but the collect/eat tail never follows.

    python decree_diagnostic.py    (rows to decree-diagnostic.json)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

OUT = Path(__file__).parent
sys.path.insert(0, str(OUT))
sys.path.insert(0, str(OUT.parent / "native-survival" / "arms"))
sys.path.insert(0, str(OUT.parent / "distal-senses"))
import a23_arms as A  # noqa: E402
import aim_pilot as AP  # noqa: E402
import d23_runner as D  # noqa: E402
import decree_control as DC  # noqa: E402
import n23_runner as R  # noqa: E402

STEPS = 1_500


class TracingDecree(DC.DecreePolicy):
    def __init__(self, inner):
        super().__init__(inner)
        self.trace: list[dict] = []

    def select_action(self, context, rng) -> int:
        o = context.observation
        self.drops.append((float(o[DC.DROP_PRESENT]), float(o[DC.DROP_DIST])))
        steer = self._steer(o)
        action = steer if steer is not None else self.inner.select_action(context, rng)
        self.trace.append(
            {
                "who": "decree" if steer is not None else "head",
                "a": int(action),
                "mine": round(float(o[DC.MINING]), 2),
                "aim0": round(float(o[DC.AIM_S[0]]), 2),
                "d0": round(float(o[DC.GLANCE_D[0]]), 3),
                "drop": round(float(o[DC.DROP_PRESENT]), 1),
                "pocket": round(float(o[DC.POCKET]), 3),
                "food": round(float(o[DC.FOOD]), 2),
            }
        )
        return action


def main() -> int:
    import dataclasses

    from pra.persistence.snapshot import decode
    from pra.persistence.store import InMemorySnapshotStore

    print("world:", R.rcon("tick", "rate", "100"), flush=True)
    import os
    import shutil

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
        policy = TracingDecree(D.make_policy(cfg, kd=R.KD))
        views: list[dict] = []
        store = InMemorySnapshotStore()
        R.run_engine(
            cfg, policy, dataclasses.replace(state, config=cfg), store, views, R.live_transport
        )
    finally:
        bridge.terminate()
        bridge.wait(timeout=10)
    (OUT / "decree-diagnostic.json").write_text(json.dumps(policy.trace))

    # the discriminating summary
    t = policy.trace
    at_melon = [r for r in t if r["aim0"] > 0 and r["d0"] <= 0.07]
    head_at_melon = [r for r in at_melon if r["who"] == "head"]
    digs_at_melon = [r for r in head_at_melon if r["a"] == 5]
    runs, cur = [], 0  # consecutive dig-intention frames (any controller)
    for r in t:
        cur = cur + 1 if r["a"] == 5 else 0
        if cur:
            runs.append(cur)
    longest_dig = max(runs, default=0)
    mine_max = max((r["mine"] for r in t), default=0)
    steer_breaks = sum(
        1 for i in range(1, len(t)) if t[i]["who"] == "decree" and t[i - 1]["mine"] > 0.05
    )
    from collections import Counter

    head_actions = Counter(r["a"] for r in t if r["who"] == "head")
    summary = {
        "steps": len(t),
        "at_melon_frames": len(at_melon),
        "head_at_melon": len(head_at_melon),
        "head_digs_at_melon": len(digs_at_melon),
        "longest_dig_run": longest_dig,
        "mining_max": mine_max,
        "decree_frames_breaking_a_dig": steer_breaks,
        "head_action_histogram": dict(sorted(head_actions.items())),
        "eats": D.chains_of(views)["eats"],
        "food_final": views[-1].get("food") if views else None,
    }
    print(json.dumps(summary, indent=1), flush=True)
    (OUT / "decree-diagnostic-summary.json").write_text(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
