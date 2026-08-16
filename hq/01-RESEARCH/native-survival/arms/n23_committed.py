"""N2/N3 re-run — the committed skill on the palate body (amendment 2, 2026-08-15).

The original arms ran the pre-distal body and were stopped honestly
(N2 ≡ N3 by construction; JOURNEY.md). Since then the record moved:
the palate body exists (design 0013 — worth channel, flood, distal
senses), and the dig-quit defect was diagnosed and closed (design 0014
— commitment, its L2 chain first-eating at step 333). This runner
re-runs the REGISTERED bars N2/N3, unchanged, on the completed stack:

- body: `c1_anatomy(survival=True, flood=True, aim="worth")` (obs 86),
  bridge SURVIVAL=1 FLOOD=intrusion AIM=worth, taught tongue restored
  at birth (worth-palate-taught.json);
- brain: the 45 sense-using lessons of the pilot record
  (worth-taught.bin + worth-demos.json, restored from the-aim's trail
  at commit 2b16fcd — same brain the decree/L2 readings measured);
- policy at life-time: RecipePolicy + deficit gate keyed to the native
  food channel (N2 kd=0.1, N3 kd=0.0 — the registered single-number
  difference) + the commitment mechanisms of design 0014
  (commit_kappa=0.1, explore_defers_holds) in BOTH arms;
- life: hungry-born, free roam (NO decree), 100,500 steps in 10
  segments, world admin at birth only — melons regrow by the game's
  own stems, the world's renewal as registered.

Registered bars, unchanged: N2 food >= 12/20 for >= 80% of the life,
never reaching starvation health-loss, >= 50 genuine eats. N3 (same
brain, gate off): >= 3x more life below 12/20, or starves to
health-loss where N2 did not.

    python n23_committed.py n2
    python n23_committed.py n3
    python n23_committed.py verdict
"""

from __future__ import annotations

import dataclasses
import json
import os
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

OUT = Path(__file__).parent
sys.path.insert(0, str(OUT))
sys.path.insert(0, str(OUT.parent.parent / "distal-senses"))
import d23_runner as D  # noqa: E402 — classroom/life machinery
import n23_runner as R  # noqa: E402 — engine helpers, rcon

from pra.action.policy import PolicyParams  # noqa: E402
from pra.action.recipe import RecipePolicy  # noqa: E402
from pra.anatomy.minecraft import C1_MINING_INDEX, C1_POCKET_TOTAL_INDEX, c1_anatomy  # noqa: E402
from pra.persistence.snapshot import decode  # noqa: E402
from pra.persistence.store import InMemorySnapshotStore  # noqa: E402

BRIDGE_JS = OUT.parent.parent.parent.parent / "examples" / "minecraft" / "bridge" / "bridge.js"

# the palate body (design 0013)
R.SENSORS, R.ACTUATORS = c1_anatomy(survival=True, flood=True, aim="worth")
R.OBS_DIM = sum(s.width for s in R.SENSORS)  # 86
R.N_ACTIONS = sum(len(a.presets) for a in R.ACTUATORS)
R.BASE = dataclasses.replace(R.BASE, obs_dim=R.OBS_DIM, n_actions=R.N_ACTIONS)
D.TAUGHT = OUT / "worth-taught.bin"
D.DEMOS = OUT / "worth-demos.json"
PALATE_TAUGHT = OUT / "worth-palate-taught.json"
PALATE = OUT / "worth-palate.json"

SEGS = 10
SEG_CYCLES = 134  # x 75 x 10 = 100,500 >= the registered 100k
COMMIT_KAPPA = 0.1  # design 0014's measured point
KD = {"n2": R.KD, "n3": 0.0, "confirm": 0.0}  # confirm = the blessed gate-free stack


def start_bridge(name: str) -> subprocess.Popen:
    env = {
        **os.environ,
        "SURVIVAL": "1",
        "FLOOD": "intrusion",
        "AIM": "worth",
        "AIM_ABLATE": "",
        "PALATE_FILE": str(PALATE),
        "SPAWN_ANCHOR": "0,0",
        "MC_PORT": "25602",
        "BRIDGE_PORT": str(R.BRIDGE_PORT),
    }
    log = open(OUT / f"{name}-committed-bridge.log", "a")
    proc = subprocess.Popen(["node", str(BRIDGE_JS)], env=env, stdout=log, stderr=subprocess.STDOUT)
    for _ in range(120):
        try:
            socket.create_connection(("127.0.0.1", R.BRIDGE_PORT), timeout=2).close()
            return proc
        except OSError:
            time.sleep(0.5)
    raise SystemExit(f"bridge never listened — see {name}-committed-bridge.log")


def make_policy(cfg, kd: float) -> RecipePolicy:
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
        commit_kappa=COMMIT_KAPPA,
        explore_defers_holds=True,
    )


def run_segment(state, kd: float):
    cfg = dataclasses.replace(
        state.config,
        steps_per_episode=75,
        n_cycles=state.cycles_done + SEG_CYCLES,
        snapshot_every_n_cycles=state.cycles_done + SEG_CYCLES,
    )
    policy = make_policy(cfg, kd)
    views: list[dict] = []
    store = InMemorySnapshotStore()
    R.run_engine(
        cfg, policy, dataclasses.replace(state, config=cfg), store, views, R.live_transport
    )
    return R.trim(decode(store.read(store.list()[0][0]))), views, policy


def eats_of(views: list[dict]) -> list[int]:
    foods = [v.get("food", 0) for v in views]
    counts = [R.slices_of(v) for v in views]
    rises = {i for i in range(1, len(foods)) if foods[i] > foods[i - 1]}
    eats = []
    for i in range(1, len(counts)):
        if counts[i] < counts[i - 1] and any(j in rises for j in range(i - 2, i + 3)):
            eats.append(i)
    return eats


def arm(name: str) -> None:
    kd = KD[name]
    status = OUT / f"{name}-committed-status.jsonl"
    if status.exists():
        raise SystemExit(f"{status} exists — a life is one act; move it aside to re-run")
    shutil.copy(PALATE_TAUGHT, PALATE)  # born with the taught tongue
    bridge = start_bridge(name)
    try:
        D.hungry_newborn()
        state = decode(D.TAUGHT.read_bytes())
        all_views: list[dict] = []
        completions = false = 0
        for seg in range(1, SEGS + 1):
            state, views, policy = run_segment(state, kd)
            all_views.extend(views)
            completions += policy.completions_fired
            false += policy.false_completions
            foods = [v.get("food", 0) for v in all_views]
            healths = [v.get("health", 20) for v in all_views]
            eats = eats_of(all_views)
            starv = sum(
                1 for i in range(1, len(healths)) if healths[i] < healths[i - 1] and foods[i] == 0
            )
            row = {
                "seg": seg,
                "steps_cum": len(all_views),
                "food_ge12_frac": round(sum(1 for f in foods if f >= 12) / len(foods), 4),
                "eats": len(eats),
                "first_eat": eats[0] if eats else None,
                "food_min": min(foods),
                "food_max": max(foods),
                "health_min": min(healths),
                "starv_loss": starv,  # health drops WITH an empty bar — the registered clause
                "completions": completions,
                "false_completions": false,
                "palate": views[-1].get("palate", {}) if views else {},
            }
            with status.open("a") as f:
                f.write(json.dumps(row) + "\n")
            print(f"SEG {name} {json.dumps(row)}", flush=True)
    finally:
        bridge.terminate()
        bridge.wait(timeout=10)
    print(f"{name.upper()}_COMMITTED_COMPLETE", flush=True)


def verdict() -> None:
    rows = {}
    for name in ("n2", "n3"):
        lines = (OUT / f"{name}-committed-status.jsonl").read_text().splitlines()
        rows[name] = json.loads(lines[-1])
    n2, n3 = rows["n2"], rows["n3"]
    n2_pass = n2["food_ge12_frac"] >= 0.8 and n2["starv_loss"] == 0 and n2["eats"] >= 50
    below_n2 = 1 - n2["food_ge12_frac"]
    below_n3 = 1 - n3["food_ge12_frac"]
    n3_pass = (below_n2 > 0 and below_n3 >= 3 * below_n2) or (
        n3["starv_loss"] > 0 and n2["starv_loss"] == 0
    )
    print(json.dumps({"n2": n2, "N2_pass": n2_pass, "n3": n3, "N3_pass": n3_pass}, indent=1))


def main() -> int:
    phase = sys.argv[1] if len(sys.argv) > 1 else ""
    if phase == "verdict":
        verdict()
        return 0
    if phase not in KD:
        raise SystemExit("usage: n23_committed.py n2|n3|confirm|verdict")
    print("world:", R.rcon("tick", "rate", "100"), flush=True)
    arm(phase)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
