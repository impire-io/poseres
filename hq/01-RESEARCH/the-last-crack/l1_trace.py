"""Bar L1 — attribute every dig release: the clip's band or the ε-gate.

1,500 steps in the parked-decree geometry (the-aim v4). After each
delegated frame the trace replicates the itch's own value table
(drive + recipe hold + κ·(progress_after − progress_now), completion
and label paths exact) and records the chosen action, the directed
flag (the ε-gate's own testimony), DIG's value and predicted Δ̂, and
the best competitor. Post-run, every release of a held dig is
classified: EXPLORE (random frame) or DIRECTED — and directed
releases are placed against the clip's predicted band
progress_now ≥ 1 − Δ̂ − 0.05.

    python l1_trace.py    (rows to l1-trace.json, summary printed)
"""

from __future__ import annotations

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

STEPS = 1_500
DIG = 5


def value_table(inner, ctx):
    """The CompletionItchPolicy value computation, replicated read-only
    (policy.py lines 248-275) — same drive, same recipe hold, same
    clipped itch, same completion/label paths."""
    obs = ctx.observation
    now = float(obs[inner.progress_index])
    lw = inner._label_weight(obs)
    rows = {}
    for a in range(ctx.n_actions):
        pred = ctx.predict_decoded(a)
        if pred is None:
            continue
        v = float(ctx.drive_value_of(pred))
        if inner.potential_of is not None:
            v += float(inner.potential_of(a))
        d = ctx.predict_event_delta(a)
        dprog = None
        if d is not None:
            if float(d[inner.pocket_index]) > inner.completion_threshold:
                pa = 1.0
                if inner.label_index is not None:
                    pa += lw * min(max(float(d[inner.label_index]), 0.0), 1.0)
            else:
                pa = min(max(now + float(d[inner.progress_index]), 0.0), 1.0)
            v += inner.kappa * (pa - now)
            dprog = float(d[inner.progress_index])
        rows[a] = (v, dprog)
    return now, rows


class TracingDecree(DC.DecreePolicy):
    def __init__(self, inner):
        super().__init__(inner)
        self.rows: list[dict] = []

    def select_action(self, context, rng) -> int:
        o = context.observation
        self.drops.append((float(o[DC.DROP_PRESENT]), float(o[DC.DROP_DIST])))
        steer = self._steer(o)
        if steer is not None:
            self.steered += 1
            self.rows.append(
                {"who": "decree", "a": int(steer), "mine": round(float(o[DC.MINING]), 3)}
            )
            return steer
        self.delegated += 1
        action = self.inner.select_action(context, rng)
        now, table = value_table(self.inner, context)
        dig_v, dig_d = table.get(DIG, (None, None))
        rival_a, (rival_v, _) = max(
            ((a, va) for a, va in table.items() if a != DIG), key=lambda kv: kv[1][0]
        )
        self.rows.append(
            {
                "who": "head",
                "a": int(action),
                "directed": bool(self.inner.last_was_directed),
                "mine": round(now, 3),
                "dig_v": None if dig_v is None else round(dig_v, 5),
                "dig_dprog": None if dig_d is None else round(dig_d, 4),
                "rival_a": int(rival_a),
                "rival_v": round(rival_v, 5),
            }
        )
        return action


def main() -> int:
    import dataclasses

    from pra.persistence.snapshot import decode
    from pra.persistence.store import InMemorySnapshotStore

    print("world:", R.rcon("tick", "rate", "100"), flush=True)
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
    rows = policy.rows
    (OUT / "l1-trace.json").write_text(json.dumps(rows))

    releases = []
    for i in range(1, len(rows)):
        prev, cur = rows[i - 1], rows[i]
        if prev["a"] == DIG and cur["a"] != DIG and prev["mine"] > 0.1:
            kind = (
                "decree"
                if cur["who"] == "decree"
                else ("directed" if cur.get("directed") else "explore")
            )
            band = None
            if kind == "directed" and cur.get("dig_dprog") is not None:
                band = cur["mine"] >= 1.0 - cur["dig_dprog"] - 0.05
            releases.append(
                {
                    "at": i,
                    "kind": kind,
                    "mine": cur["mine"] if cur["who"] == "head" else prev["mine"],
                    "in_clip_band": band,
                    "dig_v": cur.get("dig_v"),
                    "rival_v": cur.get("rival_v"),
                    "rival_a": cur.get("rival_a"),
                }
            )
    n = len(releases)
    directed = [r for r in releases if r["kind"] == "directed"]
    summary = {
        "steps": len(rows),
        "releases": n,
        "explore_releases": sum(1 for r in releases if r["kind"] == "explore"),
        "directed_releases": len(directed),
        "decree_releases": sum(1 for r in releases if r["kind"] == "decree"),
        "directed_in_clip_band": sum(1 for r in directed if r["in_clip_band"]),
        "directed_release_progress": [r["mine"] for r in directed],
        "explore_release_progress": [r["mine"] for r in releases if r["kind"] == "explore"],
        "eats": D.chains_of(views)["eats"],
    }
    print(json.dumps(summary, indent=1), flush=True)
    (OUT / "l1-summary.json").write_text(json.dumps(summary, indent=1))
    (OUT / "l1-releases.json").write_text(json.dumps(releases, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
