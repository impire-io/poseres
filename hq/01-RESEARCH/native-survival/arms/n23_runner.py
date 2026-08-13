"""N2/N3 arms — native sustenance and the deficit-gate ablation.

Frozen plan: ../ARMS-PLAN.md (wiring, doses, fabric, readings). All
shipped components: `c1_anatomy(survival=True)` over the SURVIVAL=1
bridge, `RecipePolicy` (041) with the 042 deficit gate keyed to the
native food channel (`label_index = deficit_index = 6`), taught by 45
hungry dig->collect->eat lessons; both arms inherit the same taught
brain and the same recipe demonstrations. N3 differs by exactly one
number: `deficit_kappa 0.1 -> 0.0`.

    python n23_runner.py pilot   # fake-bridge wiring pilot (no wall-clock)
    python n23_runner.py teach   # 45 live lessons -> n23-taught.bin + demos
    python n23_runner.py n2      # the gated life (100,500 steps)
    python n23_runner.py n3      # the ablation life (same brain, gate off)
"""

from __future__ import annotations

import dataclasses
import json
import math
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

from pra.action.policy import PolicyParams
from pra.action.recipe import RecipeMemory, RecipePolicy
from pra.anatomy.minecraft import (
    C1_MINING_INDEX,
    C1_POCKET_TOTAL_INDEX,
    FakeBridge,
    MinecraftTransport,
    c1_anatomy,
)
from pra.anatomy.ros2 import Ros2Body
from pra.config import Config
from pra.core.engine import Engine
from pra.persistence.snapshot import decode, encode
from pra.persistence.store import InMemorySnapshotStore

OUT = Path(__file__).parent
SEED = 1
BRIDGE_PORT = 25590
CONTAINER = "n1-minecraft"
TICK_MS = 50  # one temporal fabric: /tick rate 100, 50 ms steps (c1e amendment 1)

SENSORS, ACTUATORS = c1_anatomy(survival=True)
OBS_DIM = sum(s.width for s in SENSORS)  # 33
N_ACTIONS = sum(len(a.presets) for a in ACTUATORS)  # 13


def _channel_index(sensor_id: str, label: str) -> int:
    offset = 0
    for spec in SENSORS:
        if spec.id == sensor_id:
            return offset + spec.labels.index(label)
        offset += spec.width
    raise ValueError(sensor_id)


FOOD = _channel_index("vitals", "food")  # 6: the meter AND the pay (plan)
HEALTH = _channel_index("vitals", "health")

FWD, BACK, TL, TR, JUMP, DIG, PLACE, IDLE, HOLD = range(9)
USE = 12
# dig is client-wall-clock (~1.5 s melon ~ 30 steps at 50 ms); the eat is
# server-tick (32 game ticks ~ 7 steps at 5x) — the plan's stated asymmetry
LIVE_TAPE = [DIG] * 40 + [FWD] * 9 + [BACK] * 9 + [HOLD] + [USE] * 12 + [IDLE] * 4
FAKE_TAPE = [DIG] * 8 + [FWD] * 2 + [BACK] * 2 + [HOLD] + [USE] * 8 + [IDLE] * 3

TEACH_SEGS = 45
KD = 0.1  # deficit_kappa — episode 0085's measured point of record
KAP = 0.25  # completion itch
LAM = 0.25  # recipe hold
STAND = ("5.5", "-60", "2.5", "0", "0")  # patch-(5,5) stand, facing the classroom melon
CLASSROOM_MELON = ("5", "-60", "3")
PATCHES = ((5, 5), (28, 0), (0, 28))
HUNGER_DOSES = (("5", "255"), ("3", "127"), ("3", "63"))  # full / medium / light

LIFE_CYCLES = 1_340  # x 75 steps = 100,500 >= the registered 100k
SEG_CYCLES = 134
TAUGHT = OUT / "n23-taught.bin"
DEMOS = OUT / "n23-demos.json"

BASE = Config(
    obs_dim=OBS_DIM,
    n_actions=N_ACTIONS,
    episode_mode="continuous",
    policy_mode="curiosity",
    drive_weights=(("frontier", 1.0),),
    weight_norm_cap=1.2,
    event_head_eta=0.5,
    steps_per_episode=len(LIVE_TAPE),
    episodes_per_cycle=1,
    warmup_episodes=0,
    snapshot_every_n_cycles=1,
    n_cycles=1,
    # effective_n_cycles = max(n_cycles, max(horizon_checkpoints)) — the
    # default checkpoints reach 50 and would silently stretch every lesson
    horizon_checkpoints=(1,),
)


def rcon(*cmd: str) -> str:
    r = subprocess.run(
        ["docker", "exec", CONTAINER, "rcon-cli", "--", *cmd],
        capture_output=True,
        text=True,
        timeout=30,
    )
    return (r.stdout or r.stderr).strip()


class TapeTeacher:
    """The parent's hands: replay the tape, remember what was seen."""

    def __init__(self, tape: list[int]):
        self.tape = tape
        self.i = 0
        self.observations: list[np.ndarray] = []

    def select_action(self, context, rng) -> int:
        self.observations.append(np.array(context.observation, copy=True))
        action = self.tape[self.i % len(self.tape)]
        self.i += 1
        return action


def run_engine(cfg, policy, resume_state, store, views, make_transport):
    factory = Ros2Body.factory(SENSORS, ACTUATORS, transport=lambda: make_transport(views))
    mounted: list = []

    def world_factory(cfg_, rng):
        body = factory(cfg_, rng)
        mounted.append(body)
        return body

    engine = Engine(cfg, world_factory=world_factory, snapshot_store=store, policy=policy)
    try:
        return engine.run(SEED, resume_from=resume_state)
    finally:
        for body in mounted:
            body.close()


def slices_of(view: dict) -> int:
    return dict((n, c) for n, c in view.get("inventory", [])).get("melon_slice", 0)


def lesson_events(views: list[dict]) -> tuple[int, int]:
    """(collects, genuine eats) across one lesson's views."""
    collects = eats = 0
    for prev, cur in zip(views, views[1:], strict=False):
        d = slices_of(cur) - slices_of(prev)
        if d > 0:
            collects += 1
        elif d < 0 and cur.get("food", 0) > prev.get("food", 0):
            eats += 1
    return collects, eats


def trim(state):
    """c1e's snapshot hygiene: bound the unbounded telemetry tails."""
    agency = state.agency
    if agency is not None:
        agency = dict(agency)
        for key in ("values", "lp_terms", "novelty_terms"):
            agency[key] = agency[key][-5000:]
    return dataclasses.replace(
        state,
        agency=agency,
        map_fractions=state.map_fractions[-5000:],
        pred_errors=state.pred_errors[-5000:],
        population_by_cycle=state.population_by_cycle[-5000:],
    )


# ---- teaching ----------------------------------------------------------------


def classroom_live(k: int) -> None:
    rcon("kill", "@e[type=item]")
    rcon("setblock", *CLASSROOM_MELON, "minecraft:melon")
    rcon("tp", "pra", *STAND)
    sec, amp = HUNGER_DOSES[(k - 1) % len(HUNGER_DOSES)]
    rcon("effect", "give", "pra", "minecraft:hunger", sec, amp)
    time.sleep(1.4)  # the dose is game-time (<=100 ticks = 1 s wall at 5x); let it land
    rcon("effect", "clear", "pra")


def classroom_fake(bridge: FakeBridge, k: int) -> None:
    w = bridge.world
    w.dug.discard((0, -2))  # the classroom melon, restored
    w.x, w.z, w.yaw = 0.0, -1.0, math.pi  # the stand, facing it
    w.digging = None
    w.using = None
    w.health = 20
    w.food = (0, 10, 15)[(k - 1) % 3]  # the hungry-teaching dose cycle


def teach(fake: FakeBridge | None, segs: int, make_transport) -> None:
    tape = FAKE_TAPE if fake else LIVE_TAPE
    cfg0 = dataclasses.replace(BASE, steps_per_episode=len(tape))
    state = None
    demos: list[list[list[float]]] = []
    for k in range(1, segs + 1):
        for attempt in range(1, 4):
            if fake:
                classroom_fake(fake, k)
            else:
                classroom_live(k)
            views: list[dict] = []
            store = InMemorySnapshotStore()
            teacher = TapeTeacher(tape)
            cfg = dataclasses.replace(cfg0, n_cycles=k)
            resume = (
                None if state is None else dataclasses.replace(state, config=cfg, world_state=None)
            )
            run_engine(cfg, teacher, resume, store, views, make_transport)
            collects, eats = lesson_events(views)
            if collects >= 1 and eats >= 1:
                break
            print(f"teach seg {k} attempt {attempt}: collects={collects} eats={eats}", flush=True)
        else:
            raise SystemExit(f"N2 TEACH FAIL seg {k}: no clean lesson in 3 attempts")
        state = decode(store.read(store.list()[0][0]))
        demos.append([o.tolist() for o in teacher.observations[-len(tape) :]])
        if k % 9 == 0:
            print(f"teach {k}/{segs}", flush=True)
    TAUGHT.write_bytes(encode(dataclasses.replace(trim(state), world_state=None)))
    DEMOS.write_text(json.dumps(demos))
    print(f"TEACHING COMPLETE: {segs} lessons, {len(demos)} demonstrations kept", flush=True)


# ---- the lives ---------------------------------------------------------------


def newborn_live() -> None:
    """Between-phases world admin (never during a life): a fresh 20/20 body
    with an empty pocket at the stand, patches re-provisioned."""
    sys.path.insert(0, str(OUT.parent / "probe"))
    import provision  # noqa: PLC0415 — the probe kit's patch builder, reused

    rcon("effect", "clear", "pra")
    rcon("clear", "pra")
    rcon("kill", "@e[type=item]")
    for cx, cz in PATCHES:
        provision.patch(cx, cz)
    rcon("kill", "@e[type=item]")
    rcon("tp", "pra", *STAND)
    rcon("effect", "give", "pra", "minecraft:saturation", "2", "255")
    rcon("effect", "give", "pra", "minecraft:instant_health", "1", "20")
    time.sleep(1.2)
    rcon("effect", "clear", "pra")


def newborn_fake(bridge: FakeBridge) -> None:
    w = bridge.world
    w.inventory = {}
    w.held = None
    w.grid = []
    w.dug.discard((0, -2))
    w.x, w.z, w.yaw = 0.0, -1.0, math.pi
    w.digging = None
    w.using = None
    w.food = 20
    w.health = 20


def build_memory() -> RecipeMemory:
    memory = RecipeMemory(pocket_index=C1_POCKET_TOTAL_INDEX, label_index=FOOD)
    for demo in json.loads(DEMOS.read_text()):
        memory.add_demonstration([np.asarray(o) for o in demo])
    return memory


def segment_row(arm, seg, views, policy, cum) -> dict:
    n = max(len(views), 1)
    foods = [v.get("food", 0) for v in views]
    healths = [v.get("health", 20) for v in views]
    collects, eats = lesson_events(views)
    starv = any(
        h1 < h0 and f0 == 0 for h0, f0, h1 in zip(healths, foods, healths[1:], strict=False)
    )
    columns = set()
    dwell = [0] * len(PATCHES)
    for v in views:
        x, z = float(v["pos"][0]), float(v["pos"][2])
        columns.add((round(x), round(z)))
        for i, (cx, cz) in enumerate(PATCHES):
            if max(abs(x - cx), abs(z - cz)) <= 2.0:
                dwell[i] += 1
    cum["steps"] += len(views)
    cum["ge12"] += sum(1 for f in foods if f >= 12)
    cum["eats"] += eats
    cum["collects"] += collects
    cum["starv"] = cum["starv"] or starv
    return {
        "arm": arm,
        "seg": seg,
        "steps_cum": cum["steps"],
        "frac12_seg": round(sum(1 for f in foods if f >= 12) / n, 3),
        "frac12_cum": round(cum["ge12"] / max(cum["steps"], 1), 3),
        "eats_seg": eats,
        "eats_cum": cum["eats"],
        "collects_cum": cum["collects"],
        "food_min": min(foods, default=None),
        "food_mean": round(sum(foods) / n, 1),
        "health_min": min(healths, default=None),
        "starv_loss": cum["starv"],
        "dwell": [round(d / n, 2) for d in dwell],
        "unique": len(columns),
        "completions": policy.completions_fired,
        "false_completions": policy.false_completions,
        "advance": policy.advance_events,
        "out_of_context": policy.out_of_context,
        "pred_ema": round(policy.progress_pred_error_ema, 4),
    }


def bars(cum) -> dict:
    return {
        "frac12": round(cum["ge12"] / max(cum["steps"], 1), 3),
        "frac12_pass": cum["ge12"] / max(cum["steps"], 1) >= 0.80,
        "eats": cum["eats"],
        "eats_pass": cum["eats"] >= 50,
        "starv_loss": cum["starv"],
        "starv_pass": not cum["starv"],
    }


def life(arm: str, fake: FakeBridge | None, cycles: int, seg_cycles: int, make_transport):
    kd = 0.0 if arm.endswith("n3") else KD  # N3: exactly one number differs
    memory = build_memory()
    status = OUT / f"{arm}-status.jsonl"
    snap = OUT / f"{arm}-snapshot.bin"
    stopfile = OUT / f"{arm}-STOP"
    if snap.exists():
        state = decode(snap.read_bytes())
        rows = [json.loads(x) for x in status.read_text().splitlines()]
        last = rows[-1]
        cum = {
            "steps": last["steps_cum"],
            "ge12": int(round(last["frac12_cum"] * last["steps_cum"])),
            "eats": last["eats_cum"],
            "collects": last["collects_cum"],
            "starv": last["starv_loss"],
        }
        seg = last["seg"]
        print(f"{arm}: resuming at cycles_done={state.cycles_done}", flush=True)
    else:
        state = decode(TAUGHT.read_bytes())
        cum = {"steps": 0, "ge12": 0, "eats": 0, "collects": 0, "starv": False}
        seg = 0
        if fake:
            newborn_fake(fake)
        else:
            newborn_live()
    target = decode(TAUGHT.read_bytes()).cycles_done + cycles
    first_segment = seg == 0
    while state.cycles_done < target:
        if stopfile.exists():
            print(f"{arm}: MANUAL stop file", flush=True)
            return
        seg += 1
        t0 = time.monotonic()
        cfg = dataclasses.replace(
            state.config,
            n_cycles=min(state.cycles_done + seg_cycles, target),
            snapshot_every_n_cycles=min(state.cycles_done + seg_cycles, target),
        )
        policy = RecipePolicy(
            PolicyParams.from_config(cfg),
            memory,
            kappa=KAP,
            progress_index=C1_MINING_INDEX,
            pocket_index=C1_POCKET_TOTAL_INDEX,
            lambda_r=LAM,
            label_index=FOOD,
            label_beta=0.0,
            deficit_index=FOOD,
            deficit_kappa=kd,
        )
        views: list[dict] = []
        store = InMemorySnapshotStore()
        run_engine(
            cfg, policy, dataclasses.replace(state, config=cfg), store, views, make_transport
        )
        if first_segment and views and views[0].get("food", 0) < 18:
            raise SystemExit(f"{arm}: newborn prep failed — first view {views[0]}")
        first_segment = False
        state = trim(decode(store.read(store.list()[0][0])))
        row = segment_row(arm, seg, views, policy, cum)
        row["steps_per_s"] = round(len(views) / max(time.monotonic() - t0, 1e-9), 1)
        if state.cycles_done >= target:
            row["bars"] = bars(cum)
        with status.open("a") as f:
            f.write(json.dumps(row) + "\n")
        snap.write_bytes(encode(state))
        print(f"SEG {json.dumps(row)}", flush=True)
    print(f"{arm}_COMPLETE {json.dumps(bars(cum))}", flush=True)


# ---- phases ------------------------------------------------------------------


def live_transport(views: list) -> MinecraftTransport:
    return MinecraftTransport(
        port=BRIDGE_PORT, tick_ms=TICK_MS, tick_budget=120.0, on_view=views.append
    )


def main() -> int:
    global TAUGHT, DEMOS
    phase = sys.argv[1] if len(sys.argv) > 1 else ""
    if phase == "pilot":
        TAUGHT = OUT / "pilot-taught.bin"
        DEMOS = OUT / "pilot-demos.json"
        with FakeBridge(survival=True) as bridge:

            def fake_transport(views: list) -> MinecraftTransport:
                return MinecraftTransport(
                    port=bridge.port, tick_ms=1, tick_budget=60.0, on_view=views.append
                )

            teach(bridge, 5, fake_transport)
            life("pilot-n2", bridge, cycles=100, seg_cycles=50, make_transport=fake_transport)
        return 0
    if phase == "teach":
        print("world:", rcon("tick", "rate", "100"), flush=True)
        teach(None, TEACH_SEGS, live_transport)
        return 0
    if phase in ("n2", "n3"):
        print("world:", rcon("tick", "rate", "100"), flush=True)
        life(phase, None, cycles=LIFE_CYCLES, seg_cycles=SEG_CYCLES, make_transport=live_transport)
        return 0
    raise SystemExit("usage: n23_runner.py pilot|teach|n2|n3")


if __name__ == "__main__":
    sys.exit(main())
