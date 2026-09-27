"""Live dig diagnostic 3: does a dig that begins mid-jump take 5x (mineflayer's
not-on-ground rule)? Stand at the lesson's dig cell, jump, dig at once — vs
jump, settle four idle ticks, dig."""

import time
import mechanism_check as W


def trial(label: str, idle_after_jump: int) -> None:
    W.rcon("setblock", "15", "-58", "13", "minecraft:melon")
    W.rcon("tp", "pra", "15.5", "-58", "12.3", "0", "0")
    time.sleep(0.8)
    w = W.Walker()
    try:
        w.tick(W.IDLE)
        ch, view = w.tick(W.JUMP)
        for _ in range(idle_after_jump):
            ch, view = w.tick(W.IDLE)
        t0 = time.monotonic()
        ticks = 0
        for _ in range(170):
            ch, view = w.tick(W.DIG)
            ticks += 1
            if W.solid_ahead(ch) < 0.5:
                break
        print(
            f"{label}: idle_after_jump={idle_after_jump} broke={W.solid_ahead(ch) < 0.5} ticks={ticks} wall={time.monotonic() - t0:.2f}s pos={[round(p, 2) for p in view['pos']]}",
            flush=True,
        )
    finally:
        w.close()


for rep in range(2):
    trial(f"jump-then-dig#{rep + 1}", 0)
    time.sleep(0.5)
for rep in range(2):
    trial(f"jump-idle4-dig#{rep + 1}", 4)
    time.sleep(0.5)
