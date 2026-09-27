"""Live dig diagnostic (revival, 2026-09-27): how many 50 ms ticks does the
lesson melon take to break, in the body's current state vs healed? Uses the
mechanism walker; touches only the lesson melon and the body's effects."""

import sys, time
import mechanism_check as W


def trial(label: str) -> None:
    W.rcon("setblock", "15", "-58", "13", "minecraft:melon")
    W.rcon("tp", "pra", "15.5", "-58", "12.5", "0", "0")
    time.sleep(1.0)
    w = W.Walker()
    try:
        ch, view = w.tick(W.IDLE)
        food0, hp0 = view.get("food"), view.get("health")
        t0 = time.monotonic()
        ticks = 0
        for _ in range(120):
            ch, view = w.tick(W.DIG)
            ticks += 1
            if W.solid_ahead(ch) < 0.5:
                break
        broke = W.solid_ahead(ch) < 0.5
        print(
            f"{label}: food={food0} health={hp0} broke={broke} ticks={ticks} wall={time.monotonic() - t0:.2f}s",
            flush=True,
        )
    finally:
        w.close()


state = sys.argv[1] if len(sys.argv) > 1 else "as-is"
if state == "healed":
    W.rcon("effect", "give", "pra", "minecraft:saturation", "2", "255")
    W.rcon("effect", "give", "pra", "minecraft:instant_health", "1", "20")
    time.sleep(1.5)
    W.rcon("effect", "clear", "pra")
elif state == "starved":
    W.rcon("effect", "give", "pra", "minecraft:hunger", "5", "255")
    time.sleep(1.5)
    W.rcon("effect", "clear", "pra")
trial(state)
