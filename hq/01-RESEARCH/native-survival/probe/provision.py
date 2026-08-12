"""One-time world provisioning for the native-survival probe (bar N1).

The DECLARED config, built once before the bot ever joins — this is
world setup, not a steward; after this script exits, nothing outside
the game touches the world again:

- difficulty normal, mob spawning off (predation deferred and named)
- spawn pinned at (0, -60, 0), radius 0
- melon patches at spawn plus at distance so foraging can move: each is
  a water-hydrated farmland ring with four age-7 melon stems (the
  game's own regrowth) and eight pre-grown melon blocks (day-one stock;
  the four axial ones sit beside a stem, so digging them re-opens the
  stem's growth slot — the world's renewal without one rcon call).

Usage: python provision.py   (container n1-minecraft must be up)
"""

from __future__ import annotations

import subprocess
import sys

CONTAINER = "n1-minecraft"
GROUND = -61  # superflat surface block; feet stand at -60
PATCHES = ((5, 5), (28, 0), (0, 28))  # spawn-side, and two at distance


def rcon(*cmd: str) -> str:
    r = subprocess.run(
        ["docker", "exec", CONTAINER, "rcon-cli", "--", *cmd],
        capture_output=True,
        text=True,
        timeout=30,
    )
    out = (r.stdout or r.stderr).strip()
    print(f"rcon {' '.join(cmd)} -> {out}", flush=True)
    return out


def setblock(x: int, y: int, z: int, block: str) -> None:
    rcon("setblock", str(x), str(y), str(z), block)


def patch(cx: int, cz: int) -> None:
    setblock(cx, GROUND, cz, "minecraft:water")
    for dx, dz in ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)):
        setblock(cx + dx, GROUND, cz + dz, "minecraft:farmland[moisture=7]")
    for dx, dz in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        setblock(cx + dx, GROUND + 1, cz + dz, "minecraft:melon_stem[age=7]")
    for dx, dz in ((-2, 0), (2, 0), (0, -2), (0, 2), (-2, -2), (-2, 2), (2, -2), (2, 2)):
        setblock(cx + dx, GROUND + 1, cz + dz, "minecraft:melon")


def main() -> int:
    if "normal" not in rcon("difficulty").lower():
        rcon("difficulty", "normal")
    # 1.21.11 renamed the gamerules to snake_case: spawn_mobs is this
    # version's name for the declared doMobSpawning (spawnRadius is gone
    # from the rule set entirely; the default scatter is accepted — pose
    # is spawn-anchor-relative and the patches surround the spawn)
    rcon("gamerule", "spawn_mobs", "false")
    rcon("setworldspawn", "0", "-60", "0")
    # load the patch chunks for provisioning only; afterwards the world
    # loads by player proximity — the game's own rule
    rcon("forceload", "add", "-16", "-16", "48", "48")
    for cx, cz in PATCHES:
        patch(cx, cz)
    rcon("forceload", "remove", "all")
    print("provisioned: normal difficulty, no mobs, melon patches at", PATCHES, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
