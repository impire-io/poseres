"""C1E — the real life at 5x (run plan: hq/02-DESIGN/validate/C1E-RUN-PLAN.md,
registered before launch).

One fresh brain, the real vanilla world (port 25601, bridge 25581): taught by
the P0 protocol at the grove IN THE LIFE'S OWN FABRIC (5x world, 50 ms steps —
amendment 1, after attempt 1's death), then released. Segmented resume-chain;
rows to c1e-status.jsonl; stop file c1e-STOP. The grove is stewarded by a
keep-mode setblock loop (the world's renewal rule, recorded in the plan).
"""

from __future__ import annotations

import dataclasses
import json
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import p0_runner as p  # noqa: E402
import parallel_gates as pg  # noqa: E402

from pra.action.policy import PolicyParams  # noqa: E402
from pra.anatomy.minecraft import (  # noqa: E402
    C1_MINING_INDEX,
    C1_POCKET_TOTAL_INDEX,
    MinecraftTransport,
)
from pra.anatomy.ros2 import Ros2Body  # noqa: E402
from pra.core.engine import Engine  # noqa: E402
from pra.persistence.snapshot import decode, encode  # noqa: E402
from pra.persistence.store import InMemorySnapshotStore  # noqa: E402

OUT = Path(__file__).parent

# ---- Amendment 2: two registered arms — lives versus provisioning ----
# arm A "respawn": death recorded not terminal — pocket cleared, body to
#   the bed, energy 1.0, fresh per-life LAB childhood (grace 1500 / full
#   3000; corpse/life 4250). The brain is never touched.
# arm B "oneshot": one life, childhood re-dosed 3x (grace 4500 / full
#   9000; corpse ~8743 > measured ~5000 expression delay). Death stops.
ARMS = {
    "respawn": {
        "prefix": "c1e-a",
        "container": "c1e-minecraft-1",
        "bridge_port": 25581,
        "grace": 1_500,
        "ramp": 1_500,
        "respawn": True,
        "childhood_end": 3_000,
    },
    "oneshot": {
        "prefix": "c1e-b",
        "container": "c1e2-minecraft-1",
        "bridge_port": 25582,
        "grace": 4_500,
        "ramp": 4_500,
        "respawn": False,
        "childhood_end": 9_000,
    },
}
ARM_NAME = sys.argv[1] if len(sys.argv) > 1 else ""
if ARM_NAME not in ARMS:
    if __name__ == "__main__":
        raise SystemExit(f"usage: c1e_runner.py respawn|oneshot (got {ARM_NAME!r})")
    ARM_NAME = "respawn"  # imported (e.g. the tape pilot): arm paths go unused
ARM = ARMS[ARM_NAME]

STATUS = OUT / f"{ARM['prefix']}-status.jsonl"
LATEST = OUT / f"{ARM['prefix']}-latest.json"
SNAP = OUT / f"{ARM['prefix']}-snapshot.bin"
STOPFILE = OUT / f"{ARM['prefix']}-STOP"

SEED = 1
BRIDGE_PORT = ARM["bridge_port"]
CONTAINER = ARM["container"]
GROVE = (8, -60, 9)  # the column; the bot works from (8.5, -60, 8.5), MC rot 0
STAND = ("8.5", "-60", "8.5", "0", "0")
GROVE_XZ = (8.5, 8.5)  # dwell is measured from HERE (R2 re-key; lab coords struck)
TEACH_SEGS = 45
TEACH_TICK_MS = 50  # amendment 1: ONE temporal fabric — teaching at the life's own pace
LIFE_TICK_MS = 50  # M* = 5
SEG_CYCLES = 81  # ~10k steps per life segment (81 cycles x 124 steps = 10,044)
TARGET_STEPS = 2_000_000
GOAL_CHAINS = 2_000
GOAL_MIN_STEPS = 1_000_000
FUTILITY_WINDOW = 500_000
CHILDHOOD_END = ARM["childhood_end"]
KAP = 0.25

# the real-world teaching tape, amendment 1 (measured post-mortem, attempt 1):
# a dig is CLIENT-side wall-clock — ~3.0 s (60-61 steps at 50 ms) at ANY world
# multiplier — so the dig run is 70 consecutive held digs (measured 60 + margin;
# idle releases the hold, so no padding inside the run). At 5x the drop
# far-scatters past pickup range half the time (measured 2/4 lost vs 0/4 at
# 1x), so the tape TEACHES collection: walk into the drop zone and back
# (9 forward + 9 back ~ 1.9 blocks, the probes' collect-walk). The craft
# tail keeps attempt 1's wall spacing (one op per 250 ms) as 4 idles per op.
_TAIL_OPS = [8, 9, 11, 8, 9, 9, 11]  # hold log, put, take planks; hold planks, put x2, take sticks
REAL_TAPE = (
    [5] * 70 + [0] * 9 + [1] * 9 + [x for op in _TAIL_OPS for x in (op, 7, 7, 7, 7)] + [7]
)
assert len(REAL_TAPE) == 124

# steps_per_episode follows the tape: p.BASE carries 22 (the old tape's
# length) and would truncate every 124-step lesson to its first 22 digs
BASE33 = dataclasses.replace(
    p.BASE, obs_dim=33, event_head_eta=0.5, steps_per_episode=len(REAL_TAPE)
)


def rcon(*cmd: str) -> str:
    r = subprocess.run(
        ["docker", "exec", CONTAINER, "rcon-cli", "--", *cmd],
        capture_output=True,
        text=True,
        timeout=30,
    )
    return (r.stdout or r.stderr).strip()


def steward_loop(stop_evt: threading.Event):
    """The world's renewal: the grove column regrows if dug (keep-mode only
    places into air — a block mid-break is untouched). ~2,000 game ticks at
    100 TPS is 20 s wall."""
    while not stop_evt.is_set():
        try:
            rcon("setblock", str(GROVE[0]), str(GROVE[1]), str(GROVE[2]), "minecraft:oak_log", "keep")
        except Exception:
            pass
        stop_evt.wait(20.0)


def respawn_world():
    """The game's respawn: wealth lost, knowledge kept, body to the bed.
    The world keeps the bed clear (run 3: the bot built a pedestal in its
    own stand cell; every respawn then landed it a block up, where its own
    drops fall vertically out of pickup range)."""
    rcon("clear", "pra")
    rcon("kill", "@e[type=item]")
    rcon("setblock", "8", "-60", "8", "minecraft:air")
    rcon("tp", "pra", *STAND)


# amendment 3 — hungry teaching (the 0083 protocol, restored): lesson
# starting energy cycles so the meter is WITNESSED moving; run 1 measured
# four exact zero-income corpse-line deaths with every lesson at 1.0
TEACH_ENERGY_CYCLE = (1.0, 0.7, 0.4)
_teach_start_energy: list[float] = []  # set per lesson by teach(); empty = 1.0


class RealLife:
    """The meter over the real body: sensed pocket-total gains feed (+0.1),
    tapered per-arm drain. The energy channel is 33. Arm A respawns on death
    (recorded, not terminal — a fresh per-life childhood, brain untouched);
    arm B records the death and the run stops at the segment boundary.
    Per-life first-income ticks are the R7 lives reading."""

    def __init__(self, inner, views=None):
        self.inner = inner
        self.views = views  # the world's own record; amendment 5's pay source
        self.energy = _teach_start_energy[-1] if _teach_start_energy else 1.0
        self.tick = 0  # the CURRENT life's tick
        self.death_tick: int | None = None  # first death (arm B's stop)
        self.life_lengths: list[int] = []  # completed lives (arm A)
        self.first_gains: list[int] = []  # first-income tick per life, -1 = none yet
        self._prev_total: float | None = None

    @property
    def n_actions(self):
        return self.inner.n_actions

    @property
    def obs_dim(self):
        return self.inner.obs_dim + 1

    def _true_total(self, obs) -> float:
        """Amendment 5: the world's own pocket count (unbounded). The sensed
        pocket channel saturates at 64 items (min(n,64)/64 in the bridge) —
        measured: a 155-item pocket reads 1.0 and every gain is invisible,
        the meter starves the rich. The world pays on what actually happened."""
        if self.views:
            return float(sum(c for _, c in self.views[-1].get("inventory", [])))
        return float(obs[C1_POCKET_TOTAL_INDEX]) * 64.0

    def reset(self):
        obs = self.inner.reset()
        self._prev_total = self._true_total(obs)
        if not self.first_gains:
            self.first_gains.append(-1)
        return np.append(obs, self.energy)

    def step(self, action):
        obs = self.inner.step(action)
        self.tick += 1
        ramp = min(1.0, max(0.0, (self.tick - ARM["grace"]) / ARM["ramp"]))
        self.energy -= 0.0005 * ramp
        total = self._true_total(obs)
        if self._prev_total is not None and total > self._prev_total + 1e-9:
            self.energy = min(1.0, self.energy + 0.1)
            if self.first_gains[-1] == -1:
                self.first_gains[-1] = self.tick
        self._prev_total = total
        if self.energy <= 0.0:
            if self.death_tick is None:
                self.death_tick = self.tick
            if ARM["respawn"]:
                self.life_lengths.append(self.tick)
                self.first_gains.append(-1)
                respawn_world()
                self.energy = 1.0
                self.tick = 0
                self._prev_total = None  # re-read after the cleared pocket lands
            else:
                self.energy = 0.0
        return np.append(obs, self.energy)

    def state_dict(self):
        return {
            "__life": [
                [self.energy, self.tick, -1 if self.death_tick is None else self.death_tick],
                list(self.life_lengths),
                list(self.first_gains),
            ]
        }

    def load_state_dict(self, s):
        head, lengths, gains = s["__life"]
        e, t, d = head
        self.energy, self.tick = float(e), int(t)
        self.death_tick = None if d == -1 else int(d)
        self.life_lengths = [int(x) for x in lengths]
        self.first_gains = [int(x) for x in gains]


def run_real(seed, cfg, policy, tick_ms, resume_state=None, store=None, views=None, boxes=None):
    def transport():
        return MinecraftTransport(
            port=BRIDGE_PORT,
            tick_ms=tick_ms,
            tick_budget=120.0,
            on_view=(views.append if views is not None else None),
        )

    inner = Ros2Body.factory(p.SENSORS, p.ACTUATORS, transport=transport)
    mounted = []

    def factory(cfg_, rng):
        body = inner(dataclasses.replace(cfg_, obs_dim=cfg_.obs_dim - 1), rng)
        mounted.append(body)
        world = RealLife(body, views=views)
        if boxes is not None:
            boxes.append(world)
        return world

    engine = Engine(cfg, world_factory=factory, snapshot_store=store, policy=policy)
    try:
        return engine.run(seed, resume_from=resume_state)
    finally:
        for body in mounted:
            body.close()


def teach() -> bytes:
    """45 wood segments in the life's own fabric (5x world, 50 ms steps —
    amendment 1); the grove rebuilt and the bot re-placed per lesson. Returns
    the taught snapshot; asserts one stick craft per segment."""
    rcon("tick", "rate", "100")
    state = None
    for k in range(1, TEACH_SEGS + 1):
        # a lesson whose drop far-scatters out of the collect-walk's lane
        # (measured ~15% at 5x) is simply repeated — the parent demonstrates
        # again; a failed attempt leaves no trace in the taught state
        for attempt in range(1, 4):
            rcon("kill", "@e[type=item]")
            rcon("setblock", str(GROVE[0]), str(GROVE[1]), str(GROVE[2]), "minecraft:oak_log")
            rcon("tp", "pra", *STAND)
            time.sleep(0.5)
            # amendment 3: the lesson's starting energy — the meter witnessed
            _teach_start_energy.clear()
            _teach_start_energy.append(TEACH_ENERGY_CYCLE[(k - 1) % len(TEACH_ENERGY_CYCLE)])
            views: list = []
            store = InMemorySnapshotStore()
            teacher = pg.TapeTeacher(REAL_TAPE)
            cfg = dataclasses.replace(BASE33, n_cycles=k)
            if state is None:
                run_real(SEED, cfg, teacher, TEACH_TICK_MS, store=store, views=views)
            else:
                resume = dataclasses.replace(state, config=cfg, world_state=None)
                run_real(
                    SEED, cfg, teacher, TEACH_TICK_MS, resume_state=resume, store=store, views=views
                )
            crafts = len(p.stick_crafts(views))
            if crafts == 1:
                break
            print(f"teach seg {k} attempt {attempt}: stick crafts {crafts} != 1", flush=True)
        else:
            raise SystemExit(f"C1E TEACH FAIL seg {k}: no clean lesson in 3 attempts")
        state = decode(store.read(store.list()[0][0]))
        if k % 9 == 0:
            print(f"teach {k}/{TEACH_SEGS}", flush=True)
    _teach_start_energy.clear()  # the life itself is born at 1.0
    return encode(state)


def grove_dwell(views):
    """R2 re-keyed: share of steps within Chebyshev 2 of the grove stand
    (the lab-coordinate dwell of attempts 1-2 is struck from the record)."""
    inside = 0
    positions = set()
    for v in views:
        x, z = float(v["pos"][0]), float(v["pos"][2])
        if max(abs(x - GROVE_XZ[0]), abs(z - GROVE_XZ[1])) <= 2.0:
            inside += 1
        positions.add((round(x), round(z)))
    n = max(len(views), 1)
    return inside / n, len(positions)


def make_policy(cfg, goal_xz):
    pol_box: list = []
    policy = pg.CtxItch(
        PolicyParams.from_config(cfg),
        kappa=KAP,
        progress_index=C1_MINING_INDEX,
        pocket_index=C1_POCKET_TOTAL_INDEX,
        potential_of=pg.head_potential(pol_box, goal_xz),
    )
    pol_box.append(policy)
    return policy


def capture_goal() -> tuple[float, float]:
    """Amendment 4: the goal is the taught stand's own senses. The bridge's
    pose channels are spawn-anchor-relative; a hand-computed absolute goal
    aimed the hold at world (0,1) — eleven blocks off — in every prior run.
    Read the pose AT the stand and let that be the goal."""
    rcon("tp", "pra", *STAND)
    time.sleep(0.8)
    sock = socket.create_connection(("127.0.0.1", BRIDGE_PORT), timeout=30)
    buf = b""

    def call(msg):
        nonlocal buf
        sock.sendall((json.dumps(msg) + "\n").encode())
        while b"\n" not in buf:
            chunk = sock.recv(65536)
            if not chunk:
                raise ConnectionError("bridge closed")
            buf += chunk
        line, buf = buf.split(b"\n", 1)
        return json.loads(line)

    assert call({"op": "hello", "version": "pra-mc/1"})["ok"]
    r = call({"op": "tick", "tick_ms": LIFE_TICK_MS, "commands": []})
    sock.close()
    pose = r["channels"]["pose"]
    px, pz = r["view"]["pos"][0], r["view"]["pos"][2]
    assert abs(px - 8.5) < 1.0 and abs(pz - 8.5) < 1.0, f"not at the stand: {px},{pz}"
    return float(pose[0]), float(pose[1])


def trim(state):
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


def main():
    if SNAP.exists():
        state = decode(SNAP.read_bytes())
        prior = [json.loads(x) for x in STATUS.read_text().splitlines()] if STATUS.exists() else []
        cum = prior[-1] if prior else {}
        print(f"resuming at cycles_done={state.cycles_done}", flush=True)
    else:
        blob = teach()
        state = trim(decode(blob))
        state = dataclasses.replace(state, world_state=None)
        SNAP.write_bytes(encode(state))
        cum = {}
        print("TEACHING COMPLETE — the life begins at 5x", flush=True)

    goal_file = OUT / f"{ARM['prefix']}-goal.json"
    if goal_file.exists():  # a resumed run keeps its captured goal
        goal_xz = tuple(json.loads(goal_file.read_text()))
    else:
        goal_xz = capture_goal()
        goal_file.write_text(json.dumps(list(goal_xz)))
        print(f"GOAL captured at the stand: {goal_xz}", flush=True)

    rcon("tick", "rate", "100")  # M* = 5
    stop_evt = threading.Event()
    threading.Thread(target=steward_loop, args=(stop_evt,), daemon=True).start()

    chains_cum = int(cum.get("chains_cum", 0))
    steps_cum = int(cum.get("steps_cum", 0))
    last_chain_step = int(cum.get("last_chain_step", 0))
    seg = int(cum.get("seg", 0))
    stop_reason = None
    seg_in_proc = 0

    while stop_reason is None:
        if seg_in_proc >= 20:
            print("RECYCLE after 20 segments", flush=True)
            stop_evt.set()
            return 0
        seg_in_proc += 1
        seg += 1
        t0 = time.monotonic()
        # snapshot exactly at the segment's final cycle (a flat cadence does
        # not divide the post-teach offset — run 3 snapshotted mid-segment
        # and lost 45 brain-cycles); world_state RIDES the chain — nulling
        # it here (run 3's defect) reset the meter and lives every segment
        cfg = dataclasses.replace(
            state.config,
            n_cycles=state.cycles_done + SEG_CYCLES,
            snapshot_every_n_cycles=state.cycles_done + SEG_CYCLES,
        )
        state = dataclasses.replace(state, config=cfg)
        policy = make_policy(cfg, goal_xz)
        views: list = []
        boxes: list = []
        store = InMemorySnapshotStore()
        run_real(
            SEED, cfg, policy, LIFE_TICK_MS,
            resume_state=state, store=store, views=views, boxes=boxes,
        )
        world = boxes[-1]
        state = trim(decode(store.read(store.list()[0][0])))

        n = len(views)
        steps_cum += n
        chains_seg = 0
        log_at = planks_at = None
        counts: dict = {}
        for i, name, delta in p.inv_events(views):
            counts[name] = counts.get(name, 0) + delta
            if name == "oak_log":
                log_at = i
            elif name == "oak_planks" and log_at is not None:
                planks_at = i
            elif name == "stick" and planks_at is not None:
                chains_seg += 1
                last_chain_step = steps_cum - n + i
                log_at = planks_at = None
        chains_cum += chains_seg
        dwell, unique = grove_dwell(views)
        row = {
            "arm": ARM_NAME,
            "seg": seg,
            "steps_cum": steps_cum,
            "chains_seg": chains_seg,
            "chains_cum": chains_cum,
            "last_chain_step": last_chain_step,
            "logs": counts.get("oak_log", 0),
            "sticks": counts.get("stick", 0),
            "dwell_pct": round(dwell, 2),
            "unique": unique,
            "energy": round(world.energy, 3),
            "death_tick": world.death_tick,
            "deaths": len(world.life_lengths),
            "life_tick": world.tick,
            "life_lengths": world.life_lengths[-8:],
            "first_gains": world.first_gains[-8:],
            "pred_ema": round(policy.progress_pred_error_ema, 4),
            "steps_per_s": round(n / max(time.monotonic() - t0, 1e-9), 1),
            "wall": round(time.monotonic() - t0, 1),
        }

        if not ARM["respawn"] and world.death_tick is not None:
            stop_reason = f"DEATH at life-tick {world.death_tick}"
        elif chains_cum >= GOAL_CHAINS and steps_cum >= GOAL_MIN_STEPS:
            stop_reason = f"GOAL {chains_cum} chains at {steps_cum} steps"
        elif steps_cum - last_chain_step >= FUTILITY_WINDOW and steps_cum > CHILDHOOD_END:
            stop_reason = "FUTILITY 500k steps without a chain"
        elif STOPFILE.exists():
            stop_reason = "MANUAL stop file"
        elif steps_cum >= TARGET_STEPS:
            stop_reason = "TARGET 2M steps"
        if stop_reason:
            row["stop"] = stop_reason

        with STATUS.open("a") as f:
            f.write(json.dumps(row) + "\n")
        LATEST.write_text(json.dumps(row, indent=1))
        SNAP.write_bytes(encode(state))
        if seg % 12 == 0 or stop_reason or steps_cum % 200_000 < 11_000:
            print(f"MILESTONE {json.dumps(row)}", flush=True)

    stop_evt.set()
    print(
        f"C1E_STOPPED arm={ARM_NAME} {stop_reason} after {steps_cum} steps, "
        f"{chains_cum} chains, {len(world.life_lengths)} deaths",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
