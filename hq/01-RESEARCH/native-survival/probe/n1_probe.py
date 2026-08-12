"""Bar N1 — the meter is real (instrument bar, before any arm).

A bot that WORKS but never eats: a scripted patrol (jump-forward sides,
quarter turns) that digs whatever solid stands in its way — the
repertoire's own kind of activity, no brain, no meter, and `use_held`
never issued. Every tick the world's own vitals are recorded from the
survival bridge (the exact stack the arms will use). The bar: the food
bar drains under activity, and health follows once the bar is empty,
down to the normal-difficulty floor — measured and published before N2
or N3 run. If no configuration makes the native meter bite, the
reversal fires.

Usage: python n1_probe.py   (bridge must be up with SURVIVAL=1)
Rows to n1-rows.jsonl (one JSON object per tick), summary to
n1-summary.json and stdout.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from pra.anatomy.minecraft import MinecraftTransport, c1_anatomy
from pra.anatomy.ros2 import Ros2Body

OUT = Path(__file__).parent

FORWARD, TURN_RIGHT, JUMP, DIG, HOLD = 0, 3, 4, 5, 8
PATROL = [JUMP] * 6 + [TURN_RIGHT] * 2  # a rough square, jumped not walked
SOLID_AHEAD, HEALTH, FOOD, EDIBLE = 11, 5, 6, 21
FLOOR_HOLD_TICKS = 400  # keep reading after the floor: starvation must STOP there


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bridge-port", type=int, default=25590)
    parser.add_argument("--tick-ms", type=int, default=250)
    parser.add_argument("--max-ticks", type=int, default=40_000)
    args = parser.parse_args()

    views: list[dict] = []
    sensors, actuators = c1_anatomy(survival=True)
    body = Ros2Body(
        sensors,
        actuators,
        MinecraftTransport(
            port=args.bridge_port,
            tick_ms=args.tick_ms,
            tick_budget=120.0,
            on_view=views.append,
        ),
    )
    obs = body.reset()
    assert obs.shape == (33,), f"survival anatomy expected 33 dims, got {obs.shape}"

    rows_path = OUT / "n1-rows.jsonl"
    summary_path = OUT / "n1-summary.json"
    first_drop = None
    food_curve: dict[str, int] = {}  # food points -> first tick seen there
    health_first_fall = None
    food_at_health_fall = None
    floor_tick = None
    floor_health = None
    digs = jumps = 0

    with rows_path.open("w") as rows:
        for t in range(1, args.max_ticks + 1):
            if obs[SOLID_AHEAD] == 1.0:
                action = DIG
            elif t % 500 == 0:
                action = HOLD  # cycle the held kind: the live edible flag, read
            else:
                action = PATROL[t % len(PATROL)]
            if action == DIG:
                digs += 1
            elif action == JUMP:
                jumps += 1
            obs = body.step(action)
            v = views[-1] if views else {}
            food, health = v.get("food"), v.get("health")
            pocket = sum(c for _, c in v.get("inventory", []))
            rows.write(
                json.dumps(
                    {
                        "t": t,
                        "food": food,
                        "health": health,
                        "pos": v.get("pos"),
                        "pocket": pocket,
                        "held": v.get("held"),
                        "edible_flag": float(obs[EDIBLE]),
                        "action": action,
                    }
                )
                + "\n"
            )
            if food is None:
                continue
            key = str(food)
            if key not in food_curve:
                food_curve[key] = t
            if first_drop is None and food < 20:
                first_drop = t
            if health_first_fall is None and health is not None and health < 20:
                health_first_fall = t
                food_at_health_fall = food
            if floor_tick is None and food == 0 and health is not None and health <= 1.0:
                floor_tick = t
                floor_health = health
            if t % 200 == 0:
                rows.flush()
                print(
                    f"t={t} food={food} health={health} pocket={pocket} "
                    f"pos={[round(p, 1) for p in v.get('pos', [])]}",
                    flush=True,
                )
            if floor_tick is not None and t >= floor_tick + FLOOR_HOLD_TICKS:
                break

    held_at_floor = None
    if floor_tick is not None and views:
        held_at_floor = views[-1].get("health")
    summary = {
        "ticks": t,
        "tick_ms": args.tick_ms,
        "first_food_drop_tick": first_drop,
        "food_curve": food_curve,
        "health_first_fall_tick": health_first_fall,
        "food_at_health_fall": food_at_health_fall,
        "floor_tick": floor_tick,
        "floor_health": floor_health,
        "health_after_floor_hold": held_at_floor,
        "digs": digs,
        "jumps": jumps,
        "final_pocket": sum(c for _, c in views[-1].get("inventory", [])) if views else 0,
    }
    summary_path.write_text(json.dumps(summary, indent=1))
    print("N1_SUMMARY " + json.dumps(summary), flush=True)
    body.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
