"""Discriminating diagnostic (after the anchored F arm read 1/6 where the
pilot read 3/3): two hungry-born lives back-to-back on the SAME anchored
taught brain — (a) the pilot's exact code path (D.run_life_segment, no
wrapper), (b) the F arm's path (RecordingPolicy wrapper). Rich readings
either way: position trace every 500 steps, food curve, policy watch.
If (a) expresses and (b) does not across repeats, the wrapper is
implicated; if both stall, the pilot's 3/3 was a warm draw on wide
per-life variance and the true rate is the finding.

    python diagnostic.py   (bridge FLOOD=intrusion SPAWN_ANCHOR=0,0)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

OUT = Path(__file__).parent
sys.path.insert(0, str(OUT.parent / "native-survival" / "arms"))
sys.path.insert(0, str(OUT.parent / "distal-senses"))
import d23_runner as D  # noqa: E402
import flood_arms as FA  # noqa: E402 — brings FP patching + RecordingPolicy
import flood_pilot as FP  # noqa: E402
import n23_runner as R  # noqa: E402

FP.set_form("intrusion")


def reading(tag: str, views: list[dict], policy) -> dict:
    foods = [v.get("food", 0) for v in views]
    trace = [
        [i, [round(float(views[i]["pos"][0]), 1), round(float(views[i]["pos"][2]), 1)]]
        for i in range(0, len(views), 500)
    ]
    row = {
        "tag": tag,
        **D.chains_of(views),
        "food_min": min(foods, default=None),
        "food_max": max(foods, default=None),
        "trace": trace,
        "completions": policy.completions_fired,
        "false_completions": policy.false_completions,
        "advance": policy.advance_events,
        "out_of_context": policy.out_of_context,
    }
    if hasattr(policy, "actions"):
        acts = policy.actions
        shares = {}
        for a in acts:
            shares[a] = shares.get(a, 0) + 1
        row["action_shares"] = {str(a): round(n / len(acts), 3) for a, n in sorted(shares.items())}
    return row


def main() -> int:

    from pra.persistence.snapshot import decode

    print("world:", R.rcon("tick", "rate", "100"), flush=True)
    rows = []

    # (a) the pilot's exact path
    D.hungry_newborn()
    state = decode(FP.D.TAUGHT.read_bytes())
    state2, views, policy = D.run_life_segment(state, FA.LIFE_CYCLES, kd=R.KD)
    rows.append(reading("pilot-path", views, policy))
    print("DIAG " + json.dumps(rows[-1]), flush=True)

    # (b) the F arm's wrapper path
    D.hungry_newborn()
    views, policy = FA.run_life(R.KD)
    rows.append(reading("wrapper-path", views, policy))
    print("DIAG " + json.dumps(rows[-1]), flush=True)

    (OUT / "diagnostic-rows.json").write_text(json.dumps(rows, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
