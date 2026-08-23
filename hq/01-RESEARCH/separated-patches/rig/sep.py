"""Separated-patches rig — the distance walk (design 0017 axis 2, last arm).

The 0111 rig restored from its trail (d940e7e) with ONE walked
variable: separation. Two patches — A at (5,5) beside the spawn
stand, B at (5+D, 5) — each holding C-1's total-war larder (2
pre-grown melons, no stems, no renewal). Subject, fabric, segments,
meters unchanged from 0110/0111: the blessed 86-dim stack,
worth-taught.bin, tick 100 / 50 ms, seed 1, 3 segments x 5,025
steps, views persisted, every peer act logged.

Meter definitions (pre-registered, 0110's): per-segment food>=12
fraction on that segment's own views; steady-state below-12 =
1 - mean(segments 2 and 3). Starvation loss: any health drop on a
view with food == 0.

    python sep.py solo D12       # the walk, outward: S0 screen per rung
    python sep.py hostile D12    # the rung's hostile-86 reading (S1 hunt)
    python sep.py hostile2 <rung> # S2 replicate, frozen rung only
    python sep.py verdict
"""

from __future__ import annotations

import dataclasses
import gzip
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
BRIDGE_JS = REPO / "examples" / "minecraft" / "bridge" / "bridge.js"
sys.path.insert(0, str(ARMS))
import d23_runner as D  # noqa: E402 — build_memory, MELON_CELLS
import n23_runner as R  # noqa: E402 — engine helpers, rcon
import numpy as np  # noqa: E402

from pra.action.policy import PolicyParams  # noqa: E402
from pra.action.recipe import RecipePolicy  # noqa: E402
from pra.anatomy.minecraft import C1_MINING_INDEX, C1_POCKET_TOTAL_INDEX, c1_anatomy  # noqa: E402
from pra.persistence.snapshot import decode  # noqa: E402
from pra.persistence.store import InMemorySnapshotStore  # noqa: E402

# retarget the shared machinery at the pgw2 world
R.CONTAINER = "pgw2-minecraft"
R.BRIDGE_PORT = 25594
MC_PORT = 25606
R.SENSORS, R.ACTUATORS = c1_anatomy(survival=True, flood=True, aim="worth")
R.OBS_DIM = sum(s.width for s in R.SENSORS)  # 86
R.N_ACTIONS = sum(len(a.presets) for a in R.ACTUATORS)  # 13
R.BASE = dataclasses.replace(R.BASE, obs_dim=R.OBS_DIM, n_actions=R.N_ACTIONS)
D.TAUGHT = ARMS / "worth-taught.bin"
D.DEMOS = ARMS / "worth-demos.json"
PALATE_TAUGHT = ARMS / "worth-palate-taught.json"
PALATE = RIG / "palate.json"

GROUPS = []
_off = 0
for _s in R.SENSORS:
    GROUPS.append((_s.id, _off, _s.width))
    _off += _s.width

SEGS = 3
SEG_CYCLES = 67
COMMIT_KAPPA = 0.1
KD = 0.0

GROUND = -61
STAND = ("5.5", "-60", "2.5", "0", "0")
SITE_A = (5, 5)
# the declared separation ladder (JOURNEY.md, registered before the
# walk): patch B due east of A at distance D; melons 2+2, no renewal
RUNGS = {"D12": 12, "D24": 24, "D48": 48}
# every site any rung can touch, plus the probe kit's provisioned
# patches — the birth admin erases them ALL before building the rung
ERASE_SITES = ((5, 5), (28, 0), (0, 28), (17, 5), (29, 5), (53, 5))
FARMLAND_RING = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
MELON_ORDER = ((-2, 0), (2, 0), (0, -2), (0, 2), (-2, -2), (-2, 2), (2, -2), (2, 2))
FROZEN = RIG / "FROZEN.json"


def rung_patches(rung: str) -> tuple[tuple[int, int], tuple[int, int]]:
    d = RUNGS[rung]
    return (SITE_A, (SITE_A[0] + d, SITE_A[1]))


# ---- world building (0110's, two sites, larder fixed) ------------------------


def build_patch(cx: int, cz: int) -> None:
    R.rcon("setblock", str(cx), str(GROUND), str(cz), "minecraft:water")
    for dx, dz in FARMLAND_RING:
        R.rcon(
            "setblock", str(cx + dx), str(GROUND), str(cz + dz), "minecraft:farmland[moisture=7]"
        )
    for dx, dz in MELON_ORDER[:2]:
        R.rcon("setblock", str(cx + dx), str(GROUND + 1), str(cz + dz), "minecraft:melon")


def lean_newborn(rung: str) -> None:
    """Birth admin: repair the floor, erase every site any rung can
    touch, build the declared two-patch config, then the 0109 newborn
    sequence."""
    for what in ("minecraft:air", "minecraft:water"):
        R.rcon(
            "fill",
            "-4",
            str(GROUND),
            "-4",
            "56",
            str(GROUND),
            "33",
            "minecraft:grass_block",
            "replace",
            what,
        )
    for cx, cz in ERASE_SITES:
        R.rcon(
            "fill",
            str(cx - 3),
            str(GROUND + 1),
            str(cz - 3),
            str(cx + 3),
            str(GROUND + 1),
            str(cz + 3),
            "minecraft:air",
        )
    for cell in D.MELON_CELLS:  # the teaching variants' classroom cells
        R.rcon("setblock", *cell, "minecraft:air")
    R.rcon("effect", "clear", "pra")
    R.rcon("clear", "pra")
    R.rcon("kill", "@e[type=item]")
    R.normalize_hand()
    for cx, cz in rung_patches(rung):
        build_patch(cx, cz)
    R.rcon("kill", "@e[type=item]")
    R.rcon("tp", "pra", *STAND)
    R.rcon("effect", "give", "pra", "minecraft:saturation", "2", "255")
    R.rcon("effect", "give", "pra", "minecraft:instant_health", "1", "20")
    time.sleep(1.2)
    R.rcon("effect", "clear", "pra")
    R.rcon("effect", "give", "pra", "minecraft:hunger", "5", "255")
    time.sleep(1.4)
    R.rcon("effect", "clear", "pra")


# ---- instruments (0109's, unchanged) ----------------------------------------


class RecordingPolicy:
    """Measurement-only wrapper: per-channel online event-head error.
    Trail only at this topic — the meters carry the bars (0109)."""

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
        "PEERS": "0",
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


def start_peer(name: str, peer: str = "rook", mode: str = "hostile") -> subprocess.Popen:
    env = {**os.environ, "MC_PORT": str(MC_PORT), "PEER_NAME": peer, "PEER_MODE": mode}
    log = open(RIG / f"{name}-peer.log", "a")
    proc = subprocess.Popen(
        ["node", str(RIG / "peer.js")], env=env, stdout=log, stderr=subprocess.STDOUT
    )
    time.sleep(8.0)
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


def eats_of(views: list[dict]) -> list[int]:
    foods = [v.get("food", 0) for v in views]
    counts = [R.slices_of(v) for v in views]
    rises = {i for i in range(1, len(foods)) if foods[i] > foods[i - 1]}
    return [
        i
        for i in range(1, len(counts))
        if counts[i] < counts[i - 1] and any(j in rises for j in range(i - 2, i + 3))
    ]


def starv_of(views: list[dict]) -> int:
    healths = [v.get("health", 20) for v in views]
    foods = [v.get("food", 0) for v in views]
    return sum(1 for i in range(1, len(healths)) if healths[i] < healths[i - 1] and foods[i] == 0)


# ---- arms --------------------------------------------------------------------


def arm(name: str, rung: str, hostile: bool) -> None:
    status = RIG / f"{name}-status.jsonl"
    if status.exists():
        raise SystemExit(f"{status} exists — a life is one act; move it aside to re-run")
    print("world:", R.rcon("tick", "rate", "100"), flush=True)
    shutil.copy(PALATE_TAUGHT, PALATE)
    bridge = start_bridge(name)
    peer = None
    try:
        lean_newborn(rung)
        if hostile:
            peer = start_peer(name)
        state = decode(D.TAUGHT.read_bytes())
        all_views: list[dict] = []
        for seg in range(1, SEGS + 1):
            state, views, inner, rec = run_segment(state)
            with gzip.open(RIG / f"{name}-views-seg{seg}.jsonl.gz", "wt") as vf:
                for v in views:
                    vf.write(json.dumps(v) + "\n")
            seg_collects, seg_eats = R.lesson_events(views)
            all_views.extend(views)
            foods_seg = [v.get("food", 0) for v in views]
            row = {
                "arm": name,
                "seg": seg,
                "steps_cum": len(all_views),
                **rec.report(),
                "completions": inner.completions_fired,
                "false_completions": inner.false_completions,
                "food_ge12_seg": round(sum(1 for f in foods_seg if f >= 12) / len(foods_seg), 4),
                "eats_cum": len(eats_of(all_views)),
                "collects_seg": seg_collects,
                "eats_seg": seg_eats,
                "starv_cum": starv_of(all_views),
                "food_min_seg": min(foods_seg),
                "health_min_seg": min(v.get("health", 20) for v in views),
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


def arm_metrics(rows: list[dict]) -> dict:
    ss = [r["food_ge12_seg"] for r in rows if r["seg"] >= 2]
    return {
        "below12_ss": round(1 - sum(ss) / len(ss), 4),
        "eats": rows[-1]["eats_cum"],
        "starv": rows[-1]["starv_cum"],
        "food_min": min(r["food_min_seg"] for r in rows),
        "health_min": min(r["health_min_seg"] for r in rows),
    }


def in_band(x: float) -> bool:
    return 0.10 <= x <= 0.90


def verdict() -> None:
    out: dict = {"rungs": {}, "frozen": None, "S1": None, "S2": None}
    if FROZEN.exists():
        out["frozen"] = json.loads(FROZEN.read_text())["rung"]
    for rung in RUNGS:
        entry: dict = {"distance": RUNGS[rung]}
        for kind in ("solo", "hostile", "hostile2"):
            p = RIG / f"{rung}-{kind}-status.jsonl"
            if not p.exists():
                continue
            rows = [json.loads(x) for x in p.read_text().splitlines()]
            if len(rows) < SEGS:
                entry[kind] = {"incomplete": len(rows)}
                continue
            m = arm_metrics(rows)
            if kind == "solo":
                m["S0_pass"] = m["starv"] == 0 and m["eats"] >= 3 and m["below12_ss"] <= 0.10
            else:
                m["in_band"] = in_band(m["below12_ss"])
            entry[kind] = m
        if len(entry) > 1:
            out["rungs"][rung] = entry
        solo = entry.get("solo", {})
        host = entry.get("hostile", {})
        if solo.get("S0_pass") and "in_band" in host:
            if host["in_band"] and out["S1"] is None:
                out["S1"] = {"rung": rung, "hostile_below12_ss": host["below12_ss"]}
        rep = entry.get("hostile2", {})
        if "in_band" in rep and out["frozen"] == rung:
            out["S2"] = {
                "rung": rung,
                "hostile2_below12_ss": rep["below12_ss"],
                "S2_pass": rep["in_band"],
            }
    print(json.dumps(out, indent=1))


def main() -> int:
    phase = sys.argv[1] if len(sys.argv) > 1 else ""
    if phase == "verdict":
        verdict()
        return 0
    if phase in ("solo", "hostile", "hostile2"):
        rung = sys.argv[2] if len(sys.argv) > 2 else ""
        if rung not in RUNGS:
            raise SystemExit(f"usage: sep.py {phase} {'|'.join(RUNGS)}")
        if phase == "hostile2":
            if not FROZEN.exists() or json.loads(FROZEN.read_text())["rung"] != rung:
                raise SystemExit("hostile2 runs on the FROZEN rung only (Bar S2)")
        arm(f"{rung}-{phase}", rung, hostile=phase.startswith("hostile"))
        return 0
    raise SystemExit("usage: sep.py solo <rung>|hostile <rung>|hostile2 <rung>|verdict")


if __name__ == "__main__":
    raise SystemExit(main())
