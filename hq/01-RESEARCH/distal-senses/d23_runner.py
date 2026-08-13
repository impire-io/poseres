"""Bars D2/D3 — sense-using teaching, the seen forage, the gate differential.

Teaching (45 lessons, three interleaved classroom variants — the senses
are exercised, not just present):
  V0 adjacent    : the melon one ahead (the old lesson, eat-heavy now)
  V1 walk-to-seen: the melon four blocks ahead — glance sector 0 leads
  V2 turn-to-seen: the melon three blocks to the RIGHT — sector 2 leads
Every lesson is eat-heavy (use x30 = 3-5 chained consumes on the
game-tick chew) with the hunger-dose cycle decorrelated from variants.

D2: a hungry-born 25k-step life (gate on) — >= 5 seen-forage chains
(a collect >= 2 blocks from the birth stand followed by a genuine eat
within 600 steps) AND completions firing with realized gains.
D3: three hungry-born 3,000-step lives per arm (gate on vs off, same
taught brain): the gated arm eats more or first-eats sooner in every
paired comparison.

    python d23_runner.py teach | d2 | d3
"""

from __future__ import annotations

import dataclasses
import json
import sys
import time
from pathlib import Path

import numpy as np

OUT = Path(__file__).parent
sys.path.insert(0, str(OUT.parent / "native-survival" / "arms"))
import n23_runner as R  # noqa: E402  — the shared teach/life machinery

from pra.action.policy import PolicyParams  # noqa: E402
from pra.action.recipe import RecipeMemory, RecipePolicy  # noqa: E402
from pra.anatomy.minecraft import C1_MINING_INDEX, C1_POCKET_TOTAL_INDEX  # noqa: E402
from pra.persistence.snapshot import decode, encode  # noqa: E402
from pra.persistence.store import InMemorySnapshotStore  # noqa: E402

TAUGHT = OUT / "d23-taught.bin"
DEMOS = OUT / "d23-demos.json"
PROGRESS = OUT / "d23-teach-progress.json"

FWD, BACK, TR, DIG, IDLE, HOLD, USE = 0, 1, 3, 5, 7, 8, 12
EAT_TAIL = [HOLD] + [USE] * 30 + [IDLE] * 4  # 3-5 chained consumes, chew 0->1 each

# (stand, melon cell, tape) per variant; all melon cells cleared each
# classroom so exactly one is ever present
VARIANTS = (
    {
        "name": "V0-adjacent",
        "stand": ("5.5", "-60", "2.5", "0", "0"),
        "melon": ("5", "-60", "3"),
        "tape": [DIG] * 40 + [FWD] * 9 + [BACK] * 9 + EAT_TAIL,
    },
    {
        "name": "V1-walk-to-seen",
        "stand": ("10.5", "-60", "2.5", "0", "0"),
        "melon": ("10", "-60", "6"),
        "tape": [FWD] * 15 + [DIG] * 40 + [FWD] * 9 + [BACK] * 9 + EAT_TAIL,
    },
    {
        # facing south (+z), the body's RIGHT is WEST (-x) — measured
        # (the left-handed frame again): the stand sits EAST of the melon
        "name": "V2-turn-to-seen",
        "stand": ("19.5", "-60", "2.5", "0", "0"),
        "melon": ("16", "-60", "2"),
        "tape": [TR] * 2 + [FWD] * 9 + [DIG] * 40 + [FWD] * 6 + [BACK] * 6 + EAT_TAIL,
    },
)
MELON_CELLS = tuple(v["melon"] for v in VARIANTS)
TEACH_SEGS = 45
BIRTH_STAND = (5.5, 2.5)  # chains measure distance from HERE

D2_SEG_CYCLES, D2_SEGS = 67, 5  # 5 x 67 x 75 = 25,125 steps
# life length calibrated to the MEASURED expression latency (D2's first
# eat landed at step 3,275): 80 cycles = 6,000 steps = 2x the latency.
# The first D3 attempt ran 3,000-step lives — shorter than the latency
# itself — and read 0 eats both arms; discarded as instrument
# miscalibration, recorded in the journey.
D3_CYCLES, D3_LIVES = 80, 3


def repair_floor() -> None:
    # lives dig; holes accumulate AND the patch water flows into them
    # (measured: the stand cell became a puddle — the bot bobbed at -61).
    # Repair air AND stray water in the ground layer, then rebuild the
    # patches (their centers are legitimately water) — world admin
    # between readings.
    for what in ("minecraft:air", "minecraft:water"):
        R.rcon("fill", "0", "-61", "0", "30", "-61", "30", "minecraft:grass_block", "replace", what)
    sys.path.insert(0, str(OUT.parent / "native-survival" / "probe"))
    import provision  # noqa: PLC0415 — the probe kit's patch builder

    for cx, cz in ((5, 5), (28, 0), (0, 28)):
        provision.patch(cx, cz)


def classroom(k: int) -> None:
    v = VARIANTS[(k - 1) % len(VARIANTS)]
    repair_floor()
    R.rcon("clear", "pra")
    R.rcon("kill", "@e[type=item]")
    R.normalize_hand()
    for cell in MELON_CELLS:
        R.rcon("setblock", *cell, "minecraft:air")
    R.rcon("setblock", *v["melon"], "minecraft:melon")
    R.rcon("tp", "pra", *v["stand"])
    # dose cycle decorrelated from the variant cycle (index by round)
    sec, amp = R.HUNGER_DOSES[((k - 1) // len(VARIANTS)) % len(R.HUNGER_DOSES)]
    R.rcon("effect", "give", "pra", "minecraft:hunger", sec, amp)
    time.sleep(1.4)
    R.rcon("effect", "clear", "pra")


def teach() -> None:
    state = None
    demos: list[list[list[float]]] = []
    start = 1
    if PROGRESS.exists() and TAUGHT.exists() and DEMOS.exists():
        done = json.loads(PROGRESS.read_text())["segs"]
        if done < TEACH_SEGS:
            state = decode(TAUGHT.read_bytes())
            demos = json.loads(DEMOS.read_text())
            start = done + 1
            print(f"teach: resuming at seg {start}", flush=True)
    for k in range(start, TEACH_SEGS + 1):
        v = VARIANTS[(k - 1) % len(VARIANTS)]
        tape = v["tape"]
        for attempt in range(1, 4):
            classroom(k)
            views: list[dict] = []
            store = InMemorySnapshotStore()
            teacher = R.TapeTeacher(tape)
            cfg = dataclasses.replace(R.BASE, steps_per_episode=len(tape), n_cycles=k)
            resume = (
                None if state is None else dataclasses.replace(state, config=cfg, world_state=None)
            )
            R.run_engine(cfg, teacher, resume, store, views, R.live_transport)
            collects, eats = R.lesson_events(views)
            if collects >= 1 and eats >= 2:  # eat-heavy: the chain, witnessed
                break
            print(
                f"teach seg {k} ({v['name']}) attempt {attempt}: collects={collects} eats={eats}",
                flush=True,
            )
        else:
            raise SystemExit(f"D23 TEACH FAIL seg {k} ({v['name']})")
        state = decode(store.read(store.list()[0][0]))
        demos.append([o.tolist() for o in teacher.observations[-len(tape) :]])
        TAUGHT.write_bytes(encode(dataclasses.replace(R.trim(state), world_state=None)))
        DEMOS.write_text(json.dumps(demos))
        PROGRESS.write_text(json.dumps({"segs": k}))
        if k % 9 == 0:
            print(f"teach {k}/{TEACH_SEGS}", flush=True)
    print(f"TEACHING COMPLETE: {TEACH_SEGS} sense-using lessons", flush=True)


def build_memory() -> RecipeMemory:
    memory = RecipeMemory(pocket_index=C1_POCKET_TOTAL_INDEX, label_index=R.FOOD)
    for demo in json.loads(DEMOS.read_text()):
        memory.add_demonstration([np.asarray(o) for o in demo])
    return memory


def hungry_newborn() -> None:
    repair_floor()
    R.newborn_live()
    for cell in MELON_CELLS:
        R.rcon("setblock", *cell, "minecraft:air")  # nearest food >= 2 blocks
    R.rcon("effect", "give", "pra", "minecraft:hunger", "5", "255")  # born starving
    time.sleep(1.4)
    R.rcon("effect", "clear", "pra")


def make_policy(cfg, kd: float) -> RecipePolicy:
    return RecipePolicy(
        PolicyParams.from_config(cfg),
        build_memory(),
        kappa=R.KAP,
        progress_index=C1_MINING_INDEX,
        pocket_index=C1_POCKET_TOTAL_INDEX,
        lambda_r=R.LAM,
        label_index=R.FOOD,
        label_beta=0.0,
        deficit_index=R.FOOD,
        deficit_kappa=kd,
    )


def run_life_segment(state, cycles: int, kd: float):
    cfg = dataclasses.replace(
        state.config,
        steps_per_episode=75,
        n_cycles=state.cycles_done + cycles,
        snapshot_every_n_cycles=state.cycles_done + cycles,
    )
    policy = make_policy(cfg, kd)
    views: list[dict] = []
    store = InMemorySnapshotStore()
    R.run_engine(
        cfg, policy, dataclasses.replace(state, config=cfg), store, views, R.live_transport
    )
    return R.trim(decode(store.read(store.list()[0][0]))), views, policy


def chains_of(views: list[dict]) -> dict:
    """Seen-forage chains: a collect >= 2 blocks (Chebyshev) from the birth
    stand, followed by a genuine eat within 600 steps."""
    foods = [v.get("food", 0) for v in views]
    counts = [R.slices_of(v) for v in views]
    rises = {i for i in range(1, len(foods)) if foods[i] > foods[i - 1]}
    eats = []
    distant_collects = []
    for i in range(1, len(counts)):
        d = counts[i] - counts[i - 1]
        if d < 0 and any(j in rises for j in range(i - 2, i + 3)):
            eats.append(i)
        elif d > 0:
            x, z = float(views[i]["pos"][0]), float(views[i]["pos"][2])
            if max(abs(x - BIRTH_STAND[0]), abs(z - BIRTH_STAND[1])) >= 2.0:
                distant_collects.append(i)
    chains = 0
    used: set[int] = set()
    for c in distant_collects:
        nxt = next((e for e in eats if c < e <= c + 600 and e not in used), None)
        if nxt is not None:
            chains += 1
            used.add(nxt)
    return {
        "chains": chains,
        "distant_collects": len(distant_collects),
        "eats": len(eats),
        "first_eat": eats[0] if eats else None,
    }


def d2() -> None:
    state = decode(TAUGHT.read_bytes())
    hungry_newborn()
    status = OUT / "d2-status.jsonl"
    all_views: list[dict] = []
    completions = false_completions = 0
    for seg in range(1, D2_SEGS + 1):
        state, views, policy = run_life_segment(state, D2_SEG_CYCLES, kd=R.KD)
        all_views.extend(views)
        completions += policy.completions_fired
        false_completions += policy.false_completions
        row = {
            "seg": seg,
            "steps_cum": len(all_views),
            **chains_of(all_views),
            "completions": completions,
            "false_completions": false_completions,
            "food_min": min((v.get("food", 0) for v in views), default=None),
            "advance": policy.advance_events,
            "out_of_context": policy.out_of_context,
        }
        with status.open("a") as f:
            f.write(json.dumps(row) + "\n")
        print(f"SEG {json.dumps(row)}", flush=True)
    final = chains_of(all_views)
    realized = completions - false_completions
    verdict = {
        **final,
        "completions": completions,
        "realized_completions": realized,
        "d2_chains_pass": final["chains"] >= 5,
        "d2_completions_pass": realized > 0,
    }
    print(f"D2_COMPLETE {json.dumps(verdict)}", flush=True)


def d3() -> None:
    rows = []
    for life in range(1, D3_LIVES + 1):
        for arm, kd in (("on", R.KD), ("off", 0.0)):
            hungry_newborn()
            state = decode(TAUGHT.read_bytes())
            state, views, policy = run_life_segment(state, D3_CYCLES, kd=kd)
            row = {"life": life, "arm": arm, "kd": kd, **chains_of(views)}
            rows.append(row)
            print(f"LIFE {json.dumps(row)}", flush=True)
    (OUT / "d3-rows.json").write_text(json.dumps(rows, indent=1))
    pairs = []
    for life in range(1, D3_LIVES + 1):
        on = next(r for r in rows if r["life"] == life and r["arm"] == "on")
        off = next(r for r in rows if r["life"] == life and r["arm"] == "off")
        first_on = on["first_eat"] if on["first_eat"] is not None else 10**9
        first_off = off["first_eat"] if off["first_eat"] is not None else 10**9
        pairs.append(
            on["eats"] > off["eats"] or (on["eats"] == off["eats"] and first_on < first_off)
        )
    print(f"D3_COMPLETE pairs_won={pairs} d3_pass={all(pairs)}", flush=True)


def main() -> int:
    phase = sys.argv[1] if len(sys.argv) > 1 else ""
    print("world:", R.rcon("tick", "rate", "100"), flush=True)
    if phase == "teach":
        teach()
    elif phase == "d2":
        d2()
    elif phase == "d3":
        d3()
    else:
        raise SystemExit("usage: d23_runner.py teach|d2|d3")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
