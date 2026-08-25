"""the-opaque-world arm runner — flat / tower / bind-pred on live Minecraft.

Reuses the survival rig's machinery verbatim (n23_runner + d23_runner:
classroom prep, tapes, lesson gates, hungry newborns, meters) with the
0118 composition scaffolding patched in per arm and the tier-2 sidecar
riding beside every taught/resumed blob. Deficit gate OFF in every arm
(0103's blessed stack); the frame mechanism is the ONLY variable.

    python opaque_runner.py teach flat|tower|bind-pred
    python opaque_runner.py lives <round_from> <round_to>   # interleaved
"""

from __future__ import annotations

import dataclasses
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
MC = HERE / "mc"
MC.mkdir(exist_ok=True)
ARMS = Path("/Users/calmera/Impire/pra/examples/minecraft/survival/arms")
sys.path.insert(0, str(ARMS))
sys.path.insert(0, str(HERE))

import compose  # noqa: E402
import d23_runner as D  # noqa: E402
import n23_runner as R  # noqa: E402
from compose import RUN, ComposedFrameStore, t2_load_bytes, t2_state_bytes  # noqa: E402

import pra.core.engine as engine_mod  # noqa: E402
from pra.action.policy import PolicyParams  # noqa: E402
from pra.action.recipe import RecipeMemory, RecipePolicy  # noqa: E402
from pra.anatomy.minecraft import C1_MINING_INDEX, C1_POCKET_TOTAL_INDEX  # noqa: E402
from pra.core.frame import FrameStore  # noqa: E402
from pra.persistence.snapshot import decode, encode  # noqa: E402
from pra.persistence.store import InMemorySnapshotStore  # noqa: E402

MODES = {"flat": None, "tower": "tower", "bind-pred": "bind-pred"}
TEACH_SEGS = 45
LIFE_CYCLES = 80  # x 75 steps = 6,000 — the d23-calibrated life length
LIVES_PER_ARM = 8
KD = 0.0  # deficit gate OFF: 0103's blessed stack, identical across arms


def paths(arm: str) -> dict[str, Path]:
    return {
        "taught": MC / f"{arm}-taught.bin",
        "side": MC / f"{arm}-taught-t2.bin",
        "demos": MC / f"{arm}-demos.json",
        "progress": MC / f"{arm}-teach-progress.json",
        "telemetry": MC / f"{arm}-teach-telemetry.jsonl",
        "lives": MC / f"{arm}-lives.jsonl",
    }


def composed_row(store) -> dict:
    t2 = store.t2
    alive = set()
    for g in store._groups.values():
        alive.update(int(f) for f in g.frame_ids)
    dangling = sum(
        1
        for g in t2._groups.values()
        for i in range(g.size)
        if int(g.ref_ids[i]) >= 0 and int(g.ref_ids[i]) not in alive
    )
    return {
        "t2_population": t2.population_size,
        "t2_map_rate": round(t2.mapped_steps / max(t2.total_steps, 1), 4),
        "arb_t2_share": round(store.arb_t2 / max(store.arb_total, 1), 4),
        "base_population": store.population_size,
        "orphan_events": store.orphan_events,
        "dangling_now": dangling,
    }


class Patched:
    """FrameStore patch scoped to one engine run; RUN carries seed/mode/
    sidecar for the ComposedFrameStore the engine constructs."""

    def __init__(self, arm: str, side_blob: bytes | None):
        self.mode = MODES[arm]
        self.side_blob = side_blob

    def __enter__(self):
        RUN["seed"] = R.SEED
        RUN["mode"] = self.mode or "tower"
        RUN["stores"] = []
        RUN["t2_blob"] = self.side_blob if self.mode else None
        engine_mod.FrameStore = ComposedFrameStore if self.mode else FrameStore
        return self

    def __exit__(self, *exc):
        engine_mod.FrameStore = FrameStore
        RUN["t2_blob"] = None
        return False


def teach(arm: str) -> None:
    p = paths(arm)
    mode = MODES[arm]
    state = None
    side_blob: bytes | None = None
    demos: list[list[list[float]]] = []
    start = 1
    if p["progress"].exists() and p["taught"].exists() and p["demos"].exists():
        done = json.loads(p["progress"].read_text())["segs"]
        if done < TEACH_SEGS:
            state = decode(p["taught"].read_bytes())
            side_blob = p["side"].read_bytes() if mode and p["side"].exists() else None
            demos = json.loads(p["demos"].read_text())
            start = done + 1
            print(f"{arm} teach: resuming at seg {start}", flush=True)
        else:
            print(f"{arm} teach: already complete", flush=True)
            return
    for k in range(start, TEACH_SEGS + 1):
        v = D.VARIANTS[(k - 1) % len(D.VARIANTS)]
        tape = v["tape"]
        for attempt in range(1, 4):
            D.classroom(k)
            views: list[dict] = []
            store = InMemorySnapshotStore()
            teacher = R.TapeTeacher(tape)
            cfg = dataclasses.replace(R.BASE, steps_per_episode=len(tape), n_cycles=k)
            resume = (
                None if state is None else dataclasses.replace(state, config=cfg, world_state=None)
            )
            with Patched(arm, side_blob):
                R.run_engine(cfg, teacher, resume, store, views, R.live_transport)
                live_store = RUN["stores"][-1] if mode else None
            collects, eats = R.lesson_events(views)
            if collects >= 1 and eats >= 2:
                break
            print(
                f"{arm} teach seg {k} ({v['name']}) attempt {attempt}: "
                f"collects={collects} eats={eats}",
                flush=True,
            )
        else:
            raise SystemExit(f"{arm} TEACH FAIL seg {k} ({v['name']})")
        state = decode(store.read(store.list()[0][0]))
        if mode:
            side_blob = t2_state_bytes(live_store.t2)
            # sidecar round-trip byte-exactness, checked live every lesson
            probe = live_store.t2.__class__(live_store.t2.cfg, R.SEED)
            t2_load_bytes(probe, side_blob)
            assert t2_state_bytes(probe) == side_blob, "sidecar round-trip differs live"
            p["side"].write_bytes(side_blob)
            with p["telemetry"].open("a") as f:
                f.write(json.dumps({"seg": k, **composed_row(live_store)}) + "\n")
        demos.append([o.tolist() for o in teacher.observations[-len(tape) :]])
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


def life(arm: str, life_no: int) -> dict:
    p = paths(arm)
    mode = MODES[arm]
    D.hungry_newborn()
    state = decode(p["taught"].read_bytes())
    side_blob = p["side"].read_bytes() if mode else None
    cfg = dataclasses.replace(
        state.config,
        steps_per_episode=75,
        n_cycles=state.cycles_done + LIFE_CYCLES,
        snapshot_every_n_cycles=state.cycles_done + LIFE_CYCLES,
    )
    policy = RecipePolicy(
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
    with Patched(arm, side_blob):
        R.run_engine(
            cfg, policy, dataclasses.replace(state, config=cfg), store, views, R.live_transport
        )
        live_store = RUN["stores"][-1] if mode else None
    foods = [v.get("food", 0) for v in views]
    healths = [v.get("health", 20) for v in views]
    starv = any(
        h1 < h0 and f0 == 0 for h0, f0, h1 in zip(healths, foods, healths[1:], strict=False)
    )
    row = {
        "arm": arm,
        "life": life_no,
        "steps": len(views),
        **D.chains_of(views),
        "food_min": min(foods, default=None),
        "food_mean": round(sum(foods) / max(len(foods), 1), 1),
        "starv_loss": starv,
        "completions": policy.completions_fired,
        "false_completions": policy.false_completions,
        "advance": policy.advance_events,
        "out_of_context": policy.out_of_context,
        "steps_per_s": round(len(views) / max(time.monotonic() - t0, 1e-9), 1),
    }
    if mode:
        row.update(composed_row(live_store))
    with p["lives"].open("a") as f:
        f.write(json.dumps(row) + "\n")
    print(f"LIFE {json.dumps(row)}", flush=True)
    return row


def main() -> int:
    phase = sys.argv[1] if len(sys.argv) > 1 else ""
    print("world:", R.rcon("tick", "rate", "100"), flush=True)
    if phase == "teach" and len(sys.argv) > 2 and sys.argv[2] in MODES:
        teach(sys.argv[2])
        return 0
    if phase == "lives" and len(sys.argv) > 3:
        lo, hi = int(sys.argv[2]), int(sys.argv[3])
        for rnd in range(lo, hi + 1):
            for arm in ("flat", "tower", "bind-pred"):  # interleaved rounds
                done = 0
                lp = paths(arm)["lives"]
                if lp.exists():
                    done = sum(1 for _ in lp.read_text().splitlines())
                if done >= rnd:
                    print(f"round {rnd} {arm}: already done", flush=True)
                    continue
                life(arm, rnd)
        return 0
    raise SystemExit("usage: opaque_runner.py teach <arm> | lives <from> <to>")


if __name__ == "__main__":
    raise SystemExit(main())
