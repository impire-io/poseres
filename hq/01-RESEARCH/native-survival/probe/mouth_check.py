"""Supplementary instrument check (after N1, before the arms): the live
mouth end-to-end — dig a real melon, hold a slice, `use_held`, and watch
the world's own food channel pay. NOT part of any bar; this verifies the
instrument the N2 teaching will rely on, on the real server.

The bot is teleported to a melon first (world admin BETWEEN readings,
like c1e's capture_goal — never during one).

Usage: python mouth_check.py   (bridge up with SURVIVAL=1; run after
provision.py so the patch exists; tp the bot first — see README)
"""

from __future__ import annotations

import argparse
import json
import socket
import sys

DIG, HOLD, USE, IDLE = {"dig_ahead": 1.0}, {"hold_next": 1.0}, {"use_held": 1.0}, {}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bridge-port", type=int, default=25590)
    parser.add_argument("--tick-ms", type=int, default=250)
    args = parser.parse_args()

    sock = socket.create_connection(("127.0.0.1", args.bridge_port), timeout=30)
    buf = b""

    def call(msg: dict) -> dict:
        nonlocal buf
        sock.sendall((json.dumps(msg) + "\n").encode())
        while b"\n" not in buf:
            chunk = sock.recv(65536)
            if not chunk:
                raise ConnectionError("bridge closed")
            buf += chunk
        line, buf = buf.split(b"\n", 1)
        r = json.loads(line)
        assert r.get("ok"), r
        return r

    def tick(command: dict) -> dict:
        return call({"op": "tick", "tick_ms": args.tick_ms, "commands": [command]})

    assert call({"op": "hello", "version": "pra-mc/1"})["channels"]["hand"] == 7

    def slices(r: dict) -> int:
        return dict((n, c) for n, c in r["view"]["inventory"]).get("melon_slice", 0)

    r = tick(IDLE)
    print("start:", r["view"], flush=True)
    for i in range(40):  # the melon ahead breaks in ~1.5 s bare-handed
        r = tick(DIG)
        if slices(r) > 0:
            break
    assert slices(r) > 0, f"no slices after {i + 1} dig ticks: {r['view']}"
    print(f"dug: slices={slices(r)} after {i + 1} dig ticks", flush=True)

    for _ in range(6):  # cycle the held kind to the slice
        r = tick(HOLD)
        if r["view"]["held"] == "melon_slice":
            break
    assert r["view"]["held"] == "melon_slice", r["view"]
    hand = r["channels"]["hand"]
    print(f"held: hand={hand} (edible flag = {hand[2]})", flush=True)
    assert hand[2] == 1, "the edible affordance must read 1 for a held slice"

    food_before, n_before = r["view"]["food"], slices(r)
    for i in range(16):  # ~1.61 s of continuous use, then slack
        r = tick(USE)
        if r["view"]["food"] > food_before:
            break
    food_after, n_after = r["view"]["food"], slices(r)
    print(
        f"ate: food {food_before} -> {food_after}, slices {n_before} -> {n_after}, "
        f"use ticks {i + 1}, eating={r['view']['eating']}",
        flush=True,
    )
    assert food_after > food_before, "use_held paid nothing — the mouth is not real"
    assert n_after == n_before - 1, "a consume must take exactly one slice"
    print("MOUTH_OK", flush=True)
    call({"op": "bye"})
    sock.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
