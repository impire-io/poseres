"""Rung 1 — the invisible peer (contested-worlds, Bar 1).

Two arms on the cw1 world, identical in every declared respect except
the peer's presence:

- subject: the blessed stack, exactly `n23_committed.py confirm` —
  `c1_anatomy(survival=True, flood=True, aim="worth")` (obs 86/13),
  worth-taught.bin + worth-demos.json, palate restored at birth,
  RecipePolicy kappa=0.25 lambda_r=0.25, deficit gate OFF,
  commit_kappa=0.1, explore_defers_holds — hungry-born, free roam,
  world admin at birth only;
- peer (paired arm only): a scripted mineflayer body ("rook",
  peer.js), fixed non-adaptive policy — cycle the three patches,
  dig melons, walk over drops — joining after birth admin, before
  segment 1. The subject's 86 channels carry no player-entity sense
  (measured: the glance senses blocks, the drops sense ground items,
  the bridge ignores other collectors), so the peer reaches the
  subject only through world effects. Every peer act is logged.

The instrument (pre-registered operationalization of Bar 1): a
measurement-only policy wrapper captures the event head's predicted
delta for the chosen action each step (`context.predict_event_delta`,
read-only, no RNG — the wrapped policy's draws are bit-identical to an
unwrapped run) and settles it against the realized observation next
step. Primary metric: mean over all observation channels and steps of
|predicted - realized| per segment; the arm number is the mean of the
three segment means. Bar 1 PASSES on a paired/solo rise >= 25%; a rise
< 10% across all segments fires the topic's reversal condition.
Per-channel-group means are recorded for diagnosis alongside the
honest food/eat outcomes.

    python rung1.py solo      # 3 segments x 5,025 steps
    python rung1.py paired    # same, with the peer
    python rung1.py verdict
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

RIG = Path(__file__).parent
REPO = RIG.parents[3]
ARMS = REPO / "examples" / "minecraft" / "survival" / "arms"
PROBE = REPO / "examples" / "minecraft" / "survival" / "probe"
BRIDGE_JS = REPO / "examples" / "minecraft" / "bridge" / "bridge.js"
sys.path.insert(0, str(ARMS))
sys.path.insert(0, str(PROBE))
import d23_runner as D  # noqa: E402 — classroom/life machinery
import n23_runner as R  # noqa: E402 — engine helpers, rcon
import numpy as np  # noqa: E402
import provision  # noqa: E402 — the probe kit's patch builder

from pra.action.policy import PolicyParams  # noqa: E402
from pra.action.recipe import RecipePolicy  # noqa: E402
from pra.anatomy.minecraft import C1_MINING_INDEX, C1_POCKET_TOTAL_INDEX, c1_anatomy  # noqa: E402
from pra.persistence.snapshot import decode  # noqa: E402
from pra.persistence.store import InMemorySnapshotStore  # noqa: E402

# retarget the arms rig at the cw1 world (the n23_committed idiom:
# module-global patching is how a rig re-aims the shared machinery)
R.CONTAINER = "cw1-minecraft"
R.BRIDGE_PORT = 25591
provision.CONTAINER = R.CONTAINER
MC_PORT = 25603
R.SENSORS, R.ACTUATORS = c1_anatomy(survival=True, flood=True, aim="worth")
R.OBS_DIM = sum(s.width for s in R.SENSORS)  # 86
R.N_ACTIONS = sum(len(a.presets) for a in R.ACTUATORS)  # 13
R.BASE = dataclasses.replace(R.BASE, obs_dim=R.OBS_DIM, n_actions=R.N_ACTIONS)
D.TAUGHT = ARMS / "worth-taught.bin"
D.DEMOS = ARMS / "worth-demos.json"
PALATE_TAUGHT = ARMS / "worth-palate-taught.json"
PALATE = RIG / "palate.json"  # rig-local working copy; never the arms'

GROUPS = []
_off = 0
for _s in R.SENSORS:
    GROUPS.append((_s.id, _off, _s.width))
    _off += _s.width

SEGS = 3
SEG_CYCLES = 67  # x 75 = 5,025 steps/segment; 15,075/arm >= 3 x 1,500 registered
COMMIT_KAPPA = 0.1  # design 0015's blessed point
KD = 0.0  # deficit gate OFF — the blessed gate-free stack


class RecordingPolicy:
    """Measurement-only wrapper: per-channel online event-head error.

    Never draws from the RNG and reads only the pure delta accessor, so
    the inner policy's stream and selections are untouched. Settles the
    previous step's captured prediction against the realized observation
    before delegating selection."""

    def __init__(self, inner):
        self.inner = inner
        self._pred: np.ndarray | None = None
        self._prev: np.ndarray | None = None
        self.err_sum = np.zeros(R.OBS_DIM)
        self.n = 0
        self.n_missing = 0

    def select_action(self, context, rng) -> int:
        obs = context.observation
        if self._prev is not None and self._pred is not None:
            realized = np.asarray(obs, dtype=float) - self._prev
            self.err_sum += np.abs(self._pred - realized)
            self.n += 1
        action = self.inner.select_action(context, rng)
        delta = context.predict_event_delta(action)
        if delta is None:
            self._pred = None
            self.n_missing += 1
        else:
            self._pred = np.array(delta, dtype=float, copy=True)
        self._prev = np.array(obs, dtype=float, copy=True)
        return action

    def report(self) -> dict:
        n = max(self.n, 1)
        per_channel = self.err_sum / n
        return {
            "pred_n": self.n,
            "pred_missing": self.n_missing,
            "pred_err_all": round(float(per_channel.mean()), 6),
            "pred_err_groups": {
                gid: round(float(per_channel[start : start + width].mean()), 6)
                for gid, start, width in GROUPS
            },
        }


def start_bridge(name: str) -> subprocess.Popen:
    env = {
        **os.environ,
        "SURVIVAL": "1",
        "FLOOD": "intrusion",
        "AIM": "worth",
        "AIM_ABLATE": "",
        "PALATE_FILE": str(PALATE),
        "SPAWN_ANCHOR": "0,0",
        "MC_PORT": str(MC_PORT),
        "BRIDGE_PORT": str(R.BRIDGE_PORT),
    }
    log = open(RIG / f"{name}-bridge.log", "a")
    proc = subprocess.Popen(["node", str(BRIDGE_JS)], env=env, stdout=log, stderr=subprocess.STDOUT)
    for _ in range(120):
        try:
            socket.create_connection(("127.0.0.1", R.BRIDGE_PORT), timeout=2).close()
            return proc
        except OSError:
            time.sleep(0.5)
    raise SystemExit(f"bridge never listened — see {name}-bridge.log")


def start_peer(name: str) -> subprocess.Popen:
    env = {**os.environ, "MC_PORT": str(MC_PORT), "PEER_NAME": "rook"}
    log = open(RIG / f"{name}-peer.log", "a")
    proc = subprocess.Popen(
        ["node", str(RIG / "peer.js")], env=env, stdout=log, stderr=subprocess.STDOUT
    )
    time.sleep(8.0)  # spawn + first walk; presence is verified in the log
    if proc.poll() is not None:
        raise SystemExit(f"peer died at start — see {name}-peer.log")
    return proc


def make_policy(cfg) -> RecipePolicy:
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
        deficit_kappa=KD,
        commit_kappa=COMMIT_KAPPA,
        explore_defers_holds=True,
    )


def run_segment(state):
    cfg = dataclasses.replace(
        state.config,
        steps_per_episode=75,
        n_cycles=state.cycles_done + SEG_CYCLES,
        snapshot_every_n_cycles=state.cycles_done + SEG_CYCLES,
    )
    inner = make_policy(cfg)
    rec = RecordingPolicy(inner)
    views: list[dict] = []
    store = InMemorySnapshotStore()
    R.run_engine(cfg, rec, dataclasses.replace(state, config=cfg), store, views, R.live_transport)
    return R.trim(decode(store.read(store.list()[0][0]))), views, inner, rec


def arm(name: str) -> None:
    status = RIG / f"{name}-status.jsonl"
    if status.exists():
        raise SystemExit(f"{status} exists — a life is one act; move it aside to re-run")
    print("world:", R.rcon("tick", "rate", "100"), flush=True)
    shutil.copy(PALATE_TAUGHT, PALATE)
    bridge = start_bridge(name)
    peer = None
    try:
        D.hungry_newborn()
        if name == "paired":
            peer = start_peer(name)  # after birth admin, before segment 1
        state = decode(D.TAUGHT.read_bytes())
        all_views: list[dict] = []
        for seg in range(1, SEGS + 1):
            state, views, inner, rec = run_segment(state)
            all_views.extend(views)
            foods = [v.get("food", 0) for v in all_views]
            healths = [v.get("health", 20) for v in all_views]
            row = {
                "arm": name,
                "seg": seg,
                "steps_cum": len(all_views),
                **rec.report(),
                "completions": inner.completions_fired,
                "false_completions": inner.false_completions,
                "progress_pred_ema": round(inner.progress_pred_error_ema, 4),
                "food_ge12_frac": round(sum(1 for f in foods if f >= 12) / len(foods), 4),
                "eats": len(eats_of(all_views)),
                "food_min": min(foods),
                "health_min": min(healths),
            }
            with status.open("a") as f:
                f.write(json.dumps(row) + "\n")
            print(f"SEG {json.dumps(row)}", flush=True)
    finally:
        if peer is not None:
            peer.terminate()
            peer.wait(timeout=10)
        bridge.terminate()
        bridge.wait(timeout=10)
    print(f"{name.upper()}_COMPLETE", flush=True)


def eats_of(views: list[dict]) -> list[int]:
    foods = [v.get("food", 0) for v in views]
    counts = [R.slices_of(v) for v in views]
    rises = {i for i in range(1, len(foods)) if foods[i] > foods[i - 1]}
    return [
        i
        for i in range(1, len(counts))
        if counts[i] < counts[i - 1] and any(j in rises for j in range(i - 2, i + 3))
    ]


def verdict() -> None:
    rows = {}
    for name in ("solo", "paired"):
        lines = (RIG / f"{name}-status.jsonl").read_text().splitlines()
        rows[name] = [json.loads(x) for x in lines]
    solo = [r["pred_err_all"] for r in rows["solo"]]
    paired = [r["pred_err_all"] for r in rows["paired"]]
    solo_mean = sum(solo) / len(solo)
    paired_mean = sum(paired) / len(paired)
    rise = (paired_mean - solo_mean) / solo_mean
    per_seg_rise = [(p - s) / s for s, p in zip(solo, paired, strict=True)]
    print(
        json.dumps(
            {
                "solo_segs": solo,
                "paired_segs": paired,
                "solo_mean": round(solo_mean, 6),
                "paired_mean": round(paired_mean, 6),
                "rise": round(rise, 4),
                "per_seg_rise": [round(x, 4) for x in per_seg_rise],
                "bar1_pass": rise >= 0.25,
                "reversal_fired": all(x < 0.10 for x in per_seg_rise),
            },
            indent=1,
        )
    )


def main() -> int:
    phase = sys.argv[1] if len(sys.argv) > 1 else ""
    if phase == "verdict":
        verdict()
        return 0
    if phase not in ("solo", "paired"):
        raise SystemExit("usage: rung1.py solo|paired|verdict")
    arm(phase)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
