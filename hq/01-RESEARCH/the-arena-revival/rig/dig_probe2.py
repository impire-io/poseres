"""Live dig diagnostic 2: the lesson's approach. Walk the step-ups into the
larder exactly as V2's last waypoints do, then dig IMMEDIATELY (the tail's
first tick) vs after a few idle ticks. Measures ticks-to-break."""

import sys, time
import mechanism_check as W


def trial(label: str, idle_first: int) -> None:
    W.rcon("setblock", "15", "-58", "13", "minecraft:melon")
    W.rcon("tp", "pra", "15.5", "-60", "7.5", "0", "0")  # in the branch, before the gate
    time.sleep(0.6)  # tp BEFORE the counter set: the larder reset would zero it
    W.rcon("scoreboard", "players", "set", "laps", "lc", "3")  # gate opens on the game tick
    time.sleep(1.0)
    w = W.Walker()
    try:
        for wx, wz in ((15.5, 8.5), (15.5, 9.5), (15.5, 10.5), (15.5, 11.5), (15.5, 12.5)):
            w.goto(wx, wz)
        for _ in range(idle_first):
            ch, view = w.tick(W.IDLE)
        t0 = time.monotonic()
        ticks = 0
        for _ in range(120):
            ch, view = w.tick(W.DIG)
            ticks += 1
            if W.solid_ahead(ch) < 0.5:
                break
        broke = W.solid_ahead(ch) < 0.5
        print(
            f"{label}: idle_first={idle_first} broke={broke} ticks={ticks} wall={time.monotonic() - t0:.2f}s pos={[round(p, 2) for p in view['pos']]}",
            flush=True,
        )
    finally:
        w.close()
    W.rcon("scoreboard", "players", "set", "laps", "lc", "0")


for rep in range(3):
    trial(f"immediate#{rep + 1}", 0)
    time.sleep(0.5)
for rep in range(2):
    trial(f"idle4#{rep + 1}", 4)
    time.sleep(0.5)
