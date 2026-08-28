"""The larder-loop arm runner (topic the-long-carry) — flat first.

Reuses the survival rig's machinery verbatim (n23_runner: body, engine
wiring, transport, lesson events, snapshot hygiene) pointed at the
arena world, with the curriculum relocated to the loop. Deficit gate
OFF (0103's blessed stack), the 0119 life-policy construction exactly.

Two rig decisions, registered here and in JOURNEY.md before any teach:

- **The parent's hands are closed-loop.** The d23 tape grammar walked
  <= 4 blocks; the arena's lap is 30 blocks / ~146 steps and open-loop
  tapes accumulate gait drift. The WaypointTeacher is still the
  parent — a deterministic scripted controller choosing every action —
  but it steers from the body's own observation channels (anchor-
  relative pose, solid_ahead), the same loop the mechanism walker
  proved. Same teacher for every arm; arm-symmetric by construction.
- **Uniform lesson episodes.** Every lesson runs steps_per_episode =
  340 (the longest variant's budget), idle-padded after the tail, so
  the engine config never varies across the taught chain's resume.
  Demos are trimmed to the active span.

Curriculum (45 lessons, three variants interleaved, dose cycle
decorrelated by round — the d23 discipline relocated):
  V0 larder-eat : born at the larder entry, melon one ahead — dig,
                  collect, eat (the d23 V0, relocated)
  V1 the-lap    : one full lap from the birth stand THROUGH the
                  junction (continue) and across the lap line
  V2 turn-in    : counter at 2, stand before the lap line: cross it
                  (earning lap 3), walk to the junction, turn in
                  through the open gate, dig, eat — the closing act

    python lc_runner.py teach            # flat teach -> mc/flat-*
    python lc_runner.py lives <from> <to>  # flat pilot lives (1-based)
"""

from __future__ import annotations

import dataclasses
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
MC = HERE / "mc"
MC.mkdir(exist_ok=True)
ARMS = HERE.parents[3] / "examples" / "minecraft" / "survival" / "arms"
sys.path.insert(0, str(ARMS))
sys.path.insert(0, str(HERE))

import arena_provision as ARENA  # noqa: E402
import n23_runner as R  # noqa: E402 — the shared machinery, re-pointed:

R.CONTAINER = ARENA.CONTAINER  # lc-minecraft
R.BRIDGE_PORT = 25591

from pra.action.policy import PolicyParams  # noqa: E402
from pra.action.recipe import RecipeMemory, RecipePolicy  # noqa: E402
from pra.anatomy.minecraft import C1_MINING_INDEX, C1_POCKET_TOTAL_INDEX  # noqa: E402
from pra.anatomy.ros2.specs import SensorSpec  # noqa: E402
from pra.persistence.snapshot import decode, encode  # noqa: E402
from pra.persistence.store import InMemorySnapshotStore  # noqa: E402

# the sibling's one added sense (bar H0(c)): the world's own lap counter,
# published by the LAPS-enabled bridge from the buried indicator column.
# Appended LAST so every flat offset — teacher steering indices included —
# is unchanged; the flat body simply does not declare it.
LAPS_SENSOR = SensorSpec(id="laps", topic="laps", width=1, labels=("frac",))
FLAT_SENSORS = list(R.SENSORS)


def set_arm_body(arm: str) -> int:
    """Point the shared machinery at the arm's declared body; returns obs_dim."""
    sensors = FLAT_SENSORS + ([LAPS_SENSOR] if arm == "sib" else [])
    R.SENSORS = sensors
    return sum(s.width for s in sensors)


TEACH_SEGS = 45
EPISODE = 340  # one uniform lesson budget (module doc)
LIFE_CYCLES = 80  # x 75 steps = 6,000 — the d23-calibrated life length
KD = 0.0  # deficit gate OFF, identical across arms

# observation indices for the teacher's own steering (pose + blocks)
OBS_X, OBS_Z, OBS_SIN, OBS_COS, OBS_SOLID = 0, 1, 3, 4, 11
ANCHOR_SCALE = 64.0  # bridge pose channels: (coord - anchor) / 64

EAT_TAIL = [R.HOLD] + [R.USE] * 30 + [R.IDLE] * 4
V0_TAIL = [R.DIG] * 40 + [R.FWD] * 9 + [R.BACK] * 5 + EAT_TAIL

BIRTH_STAND = ARENA.BIRTH_STAND
LAP_WAYPOINTS = [(9.5, 0.5), (9.5, 6.5), (0.5, 6.5), (0.5, 0.5)]
BRANCH_WAYPOINTS = [
    (9.5, 3.5),
    (14.5, 3.5),
    (15.5, 3.5),
    (15.5, 8.5),
    (15.5, 9.5),
    (15.5, 10.5),
    (15.5, 11.5),
    (15.5, 12.5),
]

VARIANTS = (
    {
        "name": "V0-larder-eat",
        "stand": ("15.5", "-58", "12.5", "0", "0"),  # facing the (15,13) melon
        "laps": 0,
        "waypoints": [],
        "tail": V0_TAIL,
    },
    {
        "name": "V1-the-lap",
        "stand": BIRTH_STAND,
        "laps": 0,
        "waypoints": list(LAP_WAYPOINTS),
        "tail": [R.IDLE] * 4,
    },
    {
        "name": "V2-turn-in",
        "stand": ("0.5", "-60", "5.5", "180", "0"),  # before the lap line, facing north
        "laps": 2,
        "waypoints": [(0.5, 0.5), (9.5, 0.5)] + list(BRANCH_WAYPOINTS),
        "tail": V0_TAIL,
    },
)


def paths(arm: str) -> dict[str, Path]:
    return {
        "taught": MC / f"{arm}-taught.bin",
        "demos": MC / f"{arm}-demos.json",
        "progress": MC / f"{arm}-teach-progress.json",
        "lives": HERE / f"{arm}-lives.jsonl",
    }


def laps_score() -> int:
    out = R.rcon("scoreboard", "players", "get", "laps", "lc")
    for token in out.split():
        if token.lstrip("-").isdigit():
            return int(token)
    raise RuntimeError(f"unreadable laps score: {out!r}")


class WaypointTeacher:
    """The parent's hands, closed-loop (module doc): waypoints, then a
    fixed tail tape, then idle padding to the episode budget."""

    def __init__(self, waypoints: list[tuple[float, float]], tail: list[int]):
        self.waypoints = list(waypoints)
        self.tail = list(tail)
        self.i_tail = 0
        self.observations: list[np.ndarray] = []
        self.active_len = 0
        self.done = False

    def select_action(self, context, rng) -> int:
        obs = np.array(context.observation, copy=True)
        self.observations.append(obs)
        if self.waypoints:
            x, z = obs[OBS_X] * ANCHOR_SCALE, obs[OBS_Z] * ANCHOR_SCALE
            wx, wz = self.waypoints[0]
            dx, dz = wx - x, wz - z
            if math.hypot(dx, dz) < 0.45:
                self.waypoints.pop(0)
                return self.select_action_from(obs)
            yaw = math.atan2(obs[OBS_SIN], obs[OBS_COS])
            want = math.atan2(-dx, -dz)  # mineflayer forward is (-sin, -cos)
            err = (want - yaw + math.pi) % (2 * math.pi) - math.pi
            if abs(err) > math.pi / 8 + 0.05:
                return R.TL if err > 0 else R.TR
            if obs[OBS_SOLID] > 0.5:
                return R.JUMP
            return R.FWD
        return self.select_action_from(obs)

    def select_action_from(self, obs) -> int:
        if self.waypoints:
            return R.FWD  # unreachable guard; navigation continues next step
        if self.i_tail < len(self.tail):
            self.i_tail += 1
            if self.i_tail == len(self.tail):
                self.done = True
                self.active_len = len(self.observations)
            return self.tail[self.i_tail - 1]
        return R.IDLE


def classroom(k: int) -> None:
    v = VARIANTS[(k - 1) % len(VARIANTS)]
    R.rcon("effect", "clear", "pra")
    R.rcon("clear", "pra")
    R.rcon("kill", "@e[type=item]")
    R.normalize_hand()
    R.rcon("tp", "pra", *v["stand"])  # tp BEFORE the counter set: the larder
    # zone's reset conditional would zero a preset while the body stands there
    for player, value in (("laps", v["laps"]), ("armA", 0), ("armB", 0), ("counted", 0)):
        R.rcon("scoreboard", "players", "set", player, "lc", str(value))
    R.rcon("setblock", "15", "-58", "13", "minecraft:melon")  # the lesson melon
    sec, amp = R.HUNGER_DOSES[((k - 1) // len(VARIANTS)) % len(R.HUNGER_DOSES)]
    R.rcon("effect", "give", "pra", "minecraft:hunger", sec, amp)
    time.sleep(1.4)
    R.rcon("effect", "clear", "pra")


def lesson_gate(k: int, views: list[dict], teacher: WaypointTeacher) -> tuple[bool, str]:
    name = VARIANTS[(k - 1) % len(VARIANTS)]["name"]
    collects, eats = R.lesson_events(views)
    if name == "V1-the-lap":
        laps = laps_score()
        return teacher.done and laps == 1, f"done={teacher.done} laps={laps}"
    if name == "V2-turn-in":
        laps = laps_score()
        return teacher.done and eats >= 2 and laps == 0, (
            f"done={teacher.done} eats={eats} laps={laps}"
        )
    return collects >= 1 and eats >= 2, f"collects={collects} eats={eats}"


def teach(arm: str = "flat") -> None:
    p = paths(arm)
    state = None
    demos: list[list[list[float]]] = []
    start = 1
    if p["progress"].exists() and p["taught"].exists() and p["demos"].exists():
        done = json.loads(p["progress"].read_text())["segs"]
        if done < TEACH_SEGS:
            state = decode(p["taught"].read_bytes())
            demos = json.loads(p["demos"].read_text())
            start = done + 1
            print(f"{arm} teach: resuming at seg {start}", flush=True)
        else:
            print(f"{arm} teach: already complete", flush=True)
            return
    obs_dim = set_arm_body(arm)
    for k in range(start, TEACH_SEGS + 1):
        v = VARIANTS[(k - 1) % len(VARIANTS)]
        for attempt in range(1, 4):
            classroom(k)
            views: list[dict] = []
            store = InMemorySnapshotStore()
            teacher = WaypointTeacher(v["waypoints"], v["tail"])
            cfg = dataclasses.replace(
                R.BASE, obs_dim=obs_dim, steps_per_episode=EPISODE, n_cycles=k
            )
            resume = (
                None if state is None else dataclasses.replace(state, config=cfg, world_state=None)
            )
            R.run_engine(cfg, teacher, resume, store, views, R.live_transport)
            ok, detail = lesson_gate(k, views, teacher)
            if ok:
                break
            print(f"{arm} teach seg {k} ({v['name']}) attempt {attempt}: {detail}", flush=True)
        else:
            raise SystemExit(f"{arm} TEACH FAIL seg {k} ({v['name']})")
        state = decode(store.read(store.list()[0][0]))
        demos.append([o.tolist() for o in teacher.observations[: max(teacher.active_len, 1)]])
        p["taught"].write_bytes(encode(dataclasses.replace(R.trim(state), world_state=None)))
        p["demos"].write_text(json.dumps(demos))
        p["progress"].write_text(json.dumps({"segs": k}))
        if k % 9 == 0:
            print(f"{arm} teach {k}/{TEACH_SEGS}", flush=True)
    print(f"{arm} TEACHING COMPLETE", flush=True)


def build_memory(arm: str) -> RecipeMemory:
    memory = RecipeMemory(pocket_index=C1_POCKET_TOTAL_INDEX, label_index=R.FOOD)
    for demo in json.loads(paths(arm)["demos"].read_text()):
        memory.add_demonstration([np.asarray(o) for o in demo])
    return memory


FUTILITY_KILL = 300  # stall steps before a recipe goes temporarily dead
FUTILITY_FORGIVE = 0.25  # stall decay per unselected step (slow revival)


class LoggingRecipePolicy(RecipePolicy):
    """The 0119 life policy plus amendment 5 (futility erosion) and the
    decode probe's observation log (telemetry only, nothing fed back).

    Futility (the owner's steer, 2026-08-28): the stalled-pointer signal
    the policy already computes erodes the selected recipe's standing —
    stall + 1 per selected step without pointer advance, reset on real
    advance, − FUTILITY_FORGIVE per unselected step; a recipe at stall
    >= FUTILITY_KILL is dead until forgiveness revives it; with every
    recipe dead, selection yields None and the curiosity wanderer
    resumes. The re-check cadence emerges from the constants; the world
    is never touched. Identical across arms."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.obs_log: list[np.ndarray] = []
        self.stall: dict[int, float] = {}
        self.disengagements = 0
        self._last_recipe_id: int | None = None
        self._last_ptr = -1

    def _select_recipe(self, ctx):
        live_best, live_v = None, -np.inf
        for r in self.memory.recipes:
            if self.stall.get(id(r), 0.0) >= FUTILITY_KILL:
                continue
            v = ctx.drive_value_of(r.terminal)
            if self.label_index is not None:
                v += self._label_weight(ctx.observation) * float(r.terminal[self.label_index])
            if v > live_v:
                live_best, live_v = r, v
        chosen = live_best
        chosen_id = None if chosen is None else id(chosen)
        for r in self.memory.recipes:
            rid = id(r)
            if rid != chosen_id:
                self.stall[rid] = max(0.0, self.stall.get(rid, 0.0) - FUTILITY_FORGIVE)
        if chosen_id is not None:
            if chosen_id == self._last_recipe_id and self._prev_ptr == self._last_ptr:
                self.stall[chosen_id] = self.stall.get(chosen_id, 0.0) + 1.0
            elif chosen_id == self._last_recipe_id and self._prev_ptr > self._last_ptr:
                self.stall[chosen_id] = 0.0  # real progress forgives outright
            if self.stall.get(chosen_id, 0.0) >= FUTILITY_KILL:
                self.disengagements += 1
        if self._last_recipe_id is not None and chosen_id is None:
            self.disengagements += 1
        self._last_recipe_id = chosen_id
        self._last_ptr = self._prev_ptr
        return chosen

    def select_action(self, context, rng) -> int:
        self.obs_log.append(np.array(context.observation, copy=True))
        return super().select_action(context, rng)


def hungry_newborn() -> None:
    """Between-lives world admin (never during a life): larder floor
    repaired, patch rebuilt, counter zeroed, a starving 20-health body
    at the birth stand."""
    R.rcon("effect", "clear", "pra")
    R.rcon("clear", "pra")
    R.rcon("kill", "@e[type=item]")
    R.normalize_hand()
    R.rcon("fill", "12", "-59", "12", "18", "-59", "18", "minecraft:bedrock")
    ARENA.patch()
    R.rcon("kill", "@e[type=item]")
    R.rcon("tp", "pra", *BIRTH_STAND)
    for player in ("laps", "armA", "armB", "counted"):
        R.rcon("scoreboard", "players", "set", player, "lc", "0")
    R.rcon("effect", "give", "pra", "minecraft:saturation", "2", "255")
    R.rcon("effect", "give", "pra", "minecraft:instant_health", "1", "20")
    time.sleep(1.2)
    R.rcon("effect", "clear", "pra")
    R.rcon("effect", "give", "pra", "minecraft:hunger", "5", "255")  # born starving
    time.sleep(1.4)
    R.rcon("effect", "clear", "pra")


def in_cell(pos, x: int, z: int) -> bool:
    return math.floor(pos[0]) == x and math.floor(pos[2]) == z


def chain_metrics(positions: list[list[float]]) -> dict:
    """The world's own counters reconstructed from the pos trace with the
    command blocks' exact logic (A-then-B crossing; larder box entry)."""
    arm_a = arm_b = counted = 0
    crossings = 0
    entries = 0
    peeks = 0
    in_larder = in_deep_branch = False
    for pos in positions:
        a = in_cell(pos, 0, 3) and pos[1] < -59
        b = in_cell(pos, 0, 2) and pos[1] < -59
        if a and not arm_b:
            arm_a = 1
        if b and arm_a and not counted:
            crossings += 1
            counted = 1
        if b and not arm_a and not counted:
            arm_b = 1
        if not a and not b:
            arm_a = arm_b = counted = 0
        larder = 12 <= pos[0] < 19 and 12 <= pos[2] < 19 and pos[1] > -58.5
        if larder and not in_larder:
            entries += 1
        in_larder = larder
        deep = math.floor(pos[0]) == 15 and 5 <= pos[2] < 9 and pos[1] < -59
        if deep and not in_deep_branch:
            peeks += 1
        in_deep_branch = deep
    return {
        "lap_crossings": crossings,
        "chains": entries,  # gate-guaranteed: entry requires 3 counted laps
        "branch_visits": peeks,
        "wasted_peeks": max(peeks - entries, 0),
    }


def life(arm: str, life_no: int) -> dict:
    p = paths(arm)
    set_arm_body(arm)
    hungry_newborn()
    state = decode(p["taught"].read_bytes())
    cfg = dataclasses.replace(
        state.config,
        steps_per_episode=75,
        n_cycles=state.cycles_done + LIFE_CYCLES,
        snapshot_every_n_cycles=state.cycles_done + LIFE_CYCLES,
    )
    policy = LoggingRecipePolicy(
        PolicyParams.from_config(cfg),
        build_memory(arm),
        kappa=R.KAP,
        progress_index=C1_MINING_INDEX,
        pocket_index=C1_POCKET_TOTAL_INDEX,
        lambda_r=R.LAM,
        label_index=R.FOOD,
        label_beta=0.0,
        deficit_index=R.FOOD,
        deficit_kappa=KD,
    )
    views: list[dict] = []
    store = InMemorySnapshotStore()
    t0 = time.monotonic()
    R.run_engine(
        cfg, policy, dataclasses.replace(state, config=cfg), store, views, R.live_transport
    )
    positions = [v["pos"] for v in views]
    foods = [v.get("food", 0) for v in views]
    healths = [v.get("health", 20) for v in views]
    collects, eats = R.lesson_events(views)
    starv = any(
        h1 < h0 and f0 == 0 for h0, f0, h1 in zip(healths, foods, healths[1:], strict=False)
    )
    np.savez_compressed(
        MC / f"{arm}-life{life_no}.npz",
        obs=np.array(policy.obs_log, dtype=np.float32),
        pos=np.array(positions, dtype=np.float32),
        food=np.array(foods, dtype=np.float32),
    )
    row = {
        "arm": arm,
        "life": life_no,
        "steps": len(views),
        "obs_rows": len(policy.obs_log),
        **chain_metrics(positions),
        "laps_rcon_end": laps_score(),  # drift cross-check vs reconstruction
        "collects": collects,
        "eats": eats,
        "food_min": min(foods, default=None),
        "food_mean": round(sum(foods) / max(len(foods), 1), 1),
        "starv_loss": starv,
        "completions": policy.completions_fired,
        "false_completions": policy.false_completions,
        "advance": policy.advance_events,
        "out_of_context": policy.out_of_context,
        "disengagements": policy.disengagements,
        "dead_recipes_end": sum(1 for s in policy.stall.values() if s >= FUTILITY_KILL),
        "steps_per_s": round(len(views) / max(time.monotonic() - t0, 1e-9), 1),
    }
    with p["lives"].open("a") as f:
        f.write(json.dumps(row) + "\n")
    print(f"LIFE {json.dumps(row)}", flush=True)
    return row


def lives_done(arm: str) -> int:
    lp = paths(arm)["lives"]
    return sum(1 for _ in lp.read_text().splitlines()) if lp.exists() else 0


def main() -> int:
    phase = sys.argv[1] if len(sys.argv) > 1 else ""
    print("world:", R.rcon("tick", "rate", "100"), flush=True)
    if phase == "teach" and len(sys.argv) > 2 and sys.argv[2] in ("flat", "sib"):
        teach(sys.argv[2])
        return 0
    if phase == "lives" and len(sys.argv) > 4 and sys.argv[2] in ("flat", "sib"):
        arm = sys.argv[2]
        for n in range(int(sys.argv[3]), int(sys.argv[4]) + 1):
            if lives_done(arm) >= n:
                print(f"{arm} life {n}: already done", flush=True)
                continue
            life(arm, n)
        return 0
    if phase == "rounds" and len(sys.argv) > 3:
        # the H0(c) schedule: flat and sib lives interleaved round-robin
        # against world drift (the 0119 amendment-1 precedent)
        for rnd in range(int(sys.argv[2]), int(sys.argv[3]) + 1):
            for arm in ("flat", "sib"):
                if lives_done(arm) >= rnd:
                    print(f"round {rnd} {arm}: already done", flush=True)
                    continue
                life(arm, rnd)
        return 0
    raise SystemExit(
        "usage: lc_runner.py teach flat|sib | lives flat|sib <from> <to> | rounds <from> <to>"
    )


if __name__ == "__main__":
    raise SystemExit(main())
