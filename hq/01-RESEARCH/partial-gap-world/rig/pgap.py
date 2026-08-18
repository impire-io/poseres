"""Partial-gap-world rig — the renewal-rate walk (design 0017 axis 2).

The lean-worlds rig (0110, restored from its trail at f05827f)
retargeted at ONE declared world shape — the C-1 total-war larder
(one patch, 2 pre-grown melons) plus 2 age-7 stems — with the
renewal rate as the single walked variable: the world's
random-tick-speed gamerule, set per rung before birth. The two
pre-grown melons sit on the stems' cardinal cells, so both stems are
fruit-blocked at birth and regrowth begins only when a melon is
consumed — renewal is literally re-contested. Subject, fabric,
segments, instruments unchanged from 0110: the blessed 86-dim stack,
worth-taught.bin, tick 100 / 50 ms, seed 1, 3 segments x 5,025
steps, views persisted, every peer act logged, the RecordingPolicy
riding along (its numbers are trail, not claim).

Meter definitions (pre-registered, 0110's): per-segment food>=12
fraction is computed on that segment's own views; the steady-state
below-12 of an arm is 1 - (mean of segments 2 and 3), segment 1
being the hungry-born transient. Starvation loss: any health drop on
a view with food == 0.

    python pgap.py renewal T3      # I0 instrument: melons regrown per game time
    python pgap.py solo T12        # the walk, downward: P0 screen per rung
    python pgap.py hostile T12     # the rung's hostile-86 reading (P1 hunt)
    python pgap.py hostile2 <rung> # P2 replicate, on the frozen rung only
    python pgap.py verdict         # P0 table + band evaluation
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

# retarget the shared machinery at the pgw1 world
R.CONTAINER = "pgw1-minecraft"
R.BRIDGE_PORT = 25593
MC_PORT = 25605
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
PATCH_SITES = ((5, 5), (28, 0), (0, 28))
FARMLAND_RING = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
# the probe builder's declared orders (0110's); the larder is FIXED at
# this topic — melons 2, stems 2 — and only the tick speed walks
MELON_ORDER = ((-2, 0), (2, 0), (0, -2), (0, 2), (-2, -2), (-2, 2), (2, -2), (2, 2))
STEM_ORDER = ((-1, 0), (1, 0), (0, -1), (0, 1))
LARDER = {"patches": ((5, 5),), "melons": 2, "stems": 2}
# The declared renewal ladder (JOURNEY.md, registered before the walk):
# rung name -> random_tick_speed. T3 is the game's own default; T0 is
# the no-renewal floor (C-1 plus two inert stems).
RUNGS = {"T12": 12, "T6": 6, "T3": 3, "T1": 1, "T0": 0}
# where a stem's fruit can land: the cardinal cells of each stem whose
# floor is grass or farmland (the water column at the patch center is
# no valid base) — the instrument's watch list and the walk's geometry
FRUIT_CELLS = ((-2, 0), (-1, -1), (-1, 1), (2, 0), (1, -1), (1, 1))
FROZEN = RIG / "FROZEN.json"


def set_renewal(rung: str) -> None:
    """Set the rung's random-tick-speed gamerule (1.21.11 snake_case,
    with the pre-rename camelCase as fallback), on the record."""
    speed = str(RUNGS[rung])
    out = R.rcon("gamerule", "random_tick_speed", speed)
    if "random_tick_speed" not in out.lower().replace(" ", "_"):
        out = R.rcon("gamerule", "randomTickSpeed", speed)
    print(f"renewal: {rung} random_tick_speed={speed} -> {out}", flush=True)


# ---- world building (0110's, larder fixed) ----------------------------------


def build_lean_patch(cx: int, cz: int, melons: int, stems: int) -> None:
    R.rcon("setblock", str(cx), str(GROUND), str(cz), "minecraft:water")
    for dx, dz in FARMLAND_RING:
        R.rcon(
            "setblock", str(cx + dx), str(GROUND), str(cz + dz), "minecraft:farmland[moisture=7]"
        )
    for dx, dz in STEM_ORDER[:stems]:
        R.rcon(
            "setblock", str(cx + dx), str(GROUND + 1), str(cz + dz), "minecraft:melon_stem[age=7]"
        )
    for dx, dz in MELON_ORDER[:melons]:
        R.rcon("setblock", str(cx + dx), str(GROUND + 1), str(cz + dz), "minecraft:melon")


def reset_sites(cfg: dict) -> None:
    """World-only reset: repair the floor, erase every patch site, build
    the declared config, clear dropped items. No player, no bridge."""
    for what in ("minecraft:air", "minecraft:water"):
        R.rcon(
            "fill",
            "-4",
            str(GROUND),
            "-4",
            "33",
            str(GROUND),
            "33",
            "minecraft:grass_block",
            "replace",
            what,
        )
    for cx, cz in PATCH_SITES:  # erase melons/stems/leftovers at ALL sites
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
    R.rcon("kill", "@e[type=item]")
    for cx, cz in cfg["patches"]:
        build_lean_patch(cx, cz, cfg["melons"], cfg["stems"])
    R.rcon("kill", "@e[type=item]")


def lean_newborn(cfg: dict) -> None:
    """Birth admin: the world reset, then the 0109 newborn sequence
    (needs the bridge up — normalize_hand dials it)."""
    R.rcon("effect", "clear", "pra")
    R.rcon("clear", "pra")
    R.normalize_hand()
    reset_sites(cfg)
    R.rcon("tp", "pra", *STAND)
    R.rcon("effect", "give", "pra", "minecraft:saturation", "2", "255")
    R.rcon("effect", "give", "pra", "minecraft:instant_health", "1", "20")
    time.sleep(1.2)
    R.rcon("effect", "clear", "pra")
    R.rcon("effect", "give", "pra", "minecraft:hunger", "5", "255")
    time.sleep(1.4)
    R.rcon("effect", "clear", "pra")


# ---- I0: the renewal-rate instrument (world fact, no subject, no peer) ------


def renewal_instrument(rung: str, wall_s: int) -> None:
    """Free both stems (no pre-grown melons), then harvest-loop: poll
    the six fruit cells, log and remove every melon the world grows.
    Second edition: the first read zeros at every speed and the
    diagnosis (wheat frozen at age 0 under speed 255, forceloaded)
    showed this server random-ticks only near an online player — so
    the idle peer stands in as the ticking presence, exactly the body
    every real arm has. Pure world measurement otherwise."""
    out = RIG / f"renewal-{rung}.jsonl"
    if out.exists():
        raise SystemExit(f"{out} exists — one reading per rung; move it aside to re-run")
    print("world:", R.rcon("tick", "rate", "100"), flush=True)
    set_renewal(rung)
    cx, cz = LARDER["patches"][0]
    R.rcon("forceload", "add", str(cx - 8), str(cz - 8), str(cx + 8), str(cz + 8))
    peer = start_peer(f"renewal-{rung}", peer="lamp", mode="idle")
    try:
        reset_sites({"patches": LARDER["patches"], "melons": 0, "stems": 2})
        cells = [(cx + dx, GROUND + 1, cz + dz) for dx, dz in FRUIT_CELLS]
        t0 = time.monotonic()
        events = 0
        with out.open("a") as f:
            while time.monotonic() - t0 < wall_s:
                for x, y, z in cells:
                    hit = R.rcon(
                        "execute", "if", "block", str(x), str(y), str(z), "minecraft:melon"
                    )
                    if "passed" in hit.lower():
                        events += 1
                        R.rcon("setblock", str(x), str(y), str(z), "minecraft:air")
                        row = {
                            "rung": rung,
                            "event": events,
                            "wall_s": round(time.monotonic() - t0, 1),
                            "cell": [x, y, z],
                        }
                        f.write(json.dumps(row) + "\n")
                        print(f"GROWN {json.dumps(row)}", flush=True)
                time.sleep(2.0)
            elapsed = time.monotonic() - t0
            game_ticks = elapsed * 100  # tick rate 100
            summary = {
                "rung": rung,
                "tick_speed": RUNGS[rung],
                "events": events,
                "wall_s": round(elapsed, 1),
                "game_ticks": round(game_ticks),
                "per_life_equiv": round(events * (SEGS * SEG_CYCLES * 75 * 5) / game_ticks, 2),
            }
            f.write(json.dumps(summary) + "\n")
            print(f"I0 {json.dumps(summary)}", flush=True)
    finally:
        peer.terminate()
        peer.wait(timeout=10)
        R.rcon("forceload", "remove", "all")


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
    set_renewal(rung)
    shutil.copy(PALATE_TAUGHT, PALATE)
    bridge = start_bridge(name)
    peer = None
    try:
        lean_newborn(LARDER)
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
    out: dict = {"rungs": {}, "frozen": None, "P1": None, "P2": None}
    if FROZEN.exists():
        out["frozen"] = json.loads(FROZEN.read_text())["rung"]
    for rung in RUNGS:
        entry: dict = {"tick_speed": RUNGS[rung]}
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
                m["P0_pass"] = m["starv"] == 0 and m["eats"] >= 3 and m["below12_ss"] <= 0.10
            else:
                m["in_band"] = in_band(m["below12_ss"])
            entry[kind] = m
        if len(entry) > 1:
            out["rungs"][rung] = entry
        solo = entry.get("solo", {})
        host = entry.get("hostile", {})
        if solo.get("P0_pass") and "in_band" in host:
            if host["in_band"] and out["P1"] is None:
                out["P1"] = {"rung": rung, "hostile_below12_ss": host["below12_ss"]}
        rep = entry.get("hostile2", {})
        if "in_band" in rep and out["frozen"] == rung:
            out["P2"] = {
                "rung": rung,
                "hostile2_below12_ss": rep["below12_ss"],
                "P2_pass": rep["in_band"],
            }
    print(json.dumps(out, indent=1))


def main() -> int:
    phase = sys.argv[1] if len(sys.argv) > 1 else ""
    if phase == "verdict":
        verdict()
        return 0
    if phase == "renewal":
        rung = sys.argv[2] if len(sys.argv) > 2 else ""
        if rung not in RUNGS:
            raise SystemExit(f"usage: pgap.py renewal {'|'.join(RUNGS)} [wall_s]")
        wall_s = int(sys.argv[3]) if len(sys.argv) > 3 else 300
        renewal_instrument(rung, wall_s)
        return 0
    if phase in ("solo", "hostile", "hostile2"):
        rung = sys.argv[2] if len(sys.argv) > 2 else ""
        if rung not in RUNGS:
            raise SystemExit(f"usage: pgap.py {phase} {'|'.join(RUNGS)}")
        if phase == "hostile2":
            if not FROZEN.exists() or json.loads(FROZEN.read_text())["rung"] != rung:
                raise SystemExit("hostile2 runs on the FROZEN rung only (Bar P2)")
        arm(f"{rung}-{phase}", rung, hostile=phase.startswith("hostile"))
        return 0
    raise SystemExit(
        "usage: pgap.py renewal <rung>|solo <rung>|hostile <rung>|hostile2 <rung>|verdict"
    )


if __name__ == "__main__":
    raise SystemExit(main())
