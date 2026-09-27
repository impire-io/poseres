"""One-time provisioning of the larder loop (topic the-long-carry, bar H0).

The DECLARED arena, built once before the bot ever joins — world setup,
not a steward; after this script exits, nothing outside the game touches
the world again (classroom prep and newborn admin excepted, exactly as
the survival rig already does between engine sessions). See ../arena.md
for the registered design this implements.

Geometry (feet level S = the y the body stands at; superflat surface
block at y=-61, natural feet at -60):

- Loop: single-file ring corridor, cells on the perimeter of x 0..9,
  z 0..6 (30 tiles/lap), S=-60, carved from a solid bedrock block —
  walls, floor, and roof are all uncarved bedrock, dig-proof.
- Junction: east side (9,3); the branch leaves through (10,3)..(15,3),
  bends south (15,4)..(15,8) — the bend hides the gate from the loop.
- Gate (15,9): obsidian 2-high when closed (stone would fall to ~150
  steps of barehanded digging; obsidian is ~5,000 — effectively never),
  air when open. Opened by the world's counter at laps >= 3, closed
  whenever laps < 3.
- Step-ups (15,10) S=-59 and (15,11) S=-58 lift the corridor to the
  larder level; the return drop is 2 blocks, one-way by jump reach.
- Larder: interior x 12..18, z 12..18 at S=-58 with the probe kit's
  melon patch (hydrated farmland, 4 age-7 stems, 8 day-one melons)
  centered at (15,15).
- Exit: a roofed corridor at S=-58 from the larder's west wall along
  z=15 to x=6, north along x=6 to z=7, ending in a roof hole over loop
  cell (6,6): a 2-block drop back onto the loop.
- Lighting: glowstone ceilings over every corridor — uniform, and
  unreachable by dig_ahead (feet/eye level only).

The counter (buried at y=-63, never in any sightline, running on the
game's own tick): scoreboard objective `lc`; a two-zone direction
detector on the west straight (A at z=3, B at z=2, crossed A-then-B
when walking the taught direction) so a backward wander cannot inflate
the count; gate open/close conditionals on `laps`; a larder-entry zone
that resets `laps` to 0; and a buried indicator column at (25,-63,
10..12) mirroring laps as gold blocks — the world-readable form the
sibling sense and the runner's telemetry both read.

Usage: python arena_provision.py   (container lc-minecraft must be up)
"""

from __future__ import annotations

import subprocess
import sys

CONTAINER = "lc-minecraft"

# feet levels
S_LOOP = -60
S_LARDER = -58

GATE = (15, 9)  # gate cell (x, z) at loop feet level
PATCH = (15, 15)  # melon patch center in the larder
INDICATOR = (25, -63)  # x, y of the buried lap-indicator column; z 10..12
ZONE_A = (0, 3)  # lap-line arm A (crossed first in the taught direction)
ZONE_B = (0, 2)  # lap-line arm B
MACHINERY_Y = -63

BIRTH_STAND = ("2.5", "-60", "0.5", "-90", "0")  # on the loop, facing east


def rcon(*cmd: str) -> str:
    r = subprocess.run(
        ["docker", "exec", CONTAINER, "rcon-cli", "--", *cmd],
        capture_output=True,
        text=True,
        timeout=30,
    )
    out = (r.stdout or r.stderr).strip()
    print(f"rcon {' '.join(cmd)[:100]} -> {out[:120]}", flush=True)
    return out


def fill(x1: int, y1: int, z1: int, x2: int, y2: int, z2: int, block: str) -> None:
    rcon("fill", str(x1), str(y1), str(z1), str(x2), str(y2), str(z2), block)


def setblock(x: int, y: int, z: int, block: str) -> None:
    rcon("setblock", str(x), str(y), str(z), block)


def command_block(
    x: int, z: int, command: str, kind: str = "repeating", cond: bool = False
) -> None:
    states = "[facing=east" + (",conditional=true" if cond else "") + "]"
    nbt = '{auto:1b,Command:"' + command + '"}'
    setblock(x, MACHINERY_Y, z, f"minecraft:{kind}_command_block{states}{nbt}")


def carve() -> None:
    # the solid the arena is carved from (dig-proof by material)
    fill(-2, -61, -2, 26, -56, 22, "minecraft:bedrock")
    # loop ring, S=-60
    fill(0, -60, 0, 9, -59, 0, "minecraft:air")  # north straight
    fill(0, -60, 6, 9, -59, 6, "minecraft:air")  # south straight
    fill(0, -60, 1, 0, -59, 5, "minecraft:air")  # west straight
    fill(9, -60, 1, 9, -59, 5, "minecraft:air")  # east straight
    # branch: junction opening, east run, southward bend
    fill(10, -60, 3, 15, -59, 3, "minecraft:air")
    fill(15, -60, 4, 15, -59, 8, "minecraft:air")
    # gate, closed
    fill(GATE[0], -60, GATE[1], GATE[0], -59, GATE[1], "minecraft:obsidian")
    # step-ups to the larder level; the approach cells get 3-high
    # clearance — a 1-block step-up needs ~2.4 blocks of headroom over
    # the LOWER cell or the jump arc bonks the ceiling (measured on the
    # first walker run: stuck at the gate cell under a 2-high ceiling)
    fill(15, -60, 9, 15, -58, 9, "minecraft:air")  # over the gate cells
    fill(15, -59, 10, 15, -57, 10, "minecraft:air")
    fill(15, -58, 11, 15, -57, 11, "minecraft:air")
    # re-close the gate after the clearance carve
    fill(GATE[0], -60, GATE[1], GATE[0], -59, GATE[1], "minecraft:obsidian")
    # larder interior
    fill(12, -58, 12, 18, -57, 18, "minecraft:air")
    # exit corridor at S=-58 and the one-way drop over loop cell (6,6)
    fill(6, -58, 15, 11, -57, 15, "minecraft:air")
    fill(6, -58, 7, 6, -57, 14, "minecraft:air")
    fill(6, -58, 6, 6, -57, 6, "minecraft:air")


def light() -> None:
    # glowstone ceilings: loop (skipping the drop hole at x=6, z=6)
    fill(0, -58, 0, 9, -58, 0, "minecraft:glowstone")
    fill(0, -58, 6, 5, -58, 6, "minecraft:glowstone")
    fill(7, -58, 6, 9, -58, 6, "minecraft:glowstone")
    fill(0, -58, 1, 0, -58, 5, "minecraft:glowstone")
    fill(9, -58, 1, 9, -58, 5, "minecraft:glowstone")
    # branch + gate ceiling (the gate and step-up cells carry raised
    # ceilings for jump headroom; their glowstone rides one higher)
    fill(10, -58, 3, 15, -58, 3, "minecraft:glowstone")
    fill(15, -58, 4, 15, -58, 8, "minecraft:glowstone")
    setblock(15, -57, 9, "minecraft:glowstone")
    setblock(15, -56, 10, "minecraft:glowstone")
    setblock(15, -56, 11, "minecraft:glowstone")
    # larder + exit ceilings
    fill(12, -56, 12, 18, -56, 18, "minecraft:glowstone")
    fill(6, -56, 15, 11, -56, 15, "minecraft:glowstone")
    fill(6, -56, 7, 6, -56, 14, "minecraft:glowstone")


def patch() -> None:
    """The probe kit's melon patch, relocated to the larder floor."""
    cx, cz = PATCH
    setblock(cx, -59, cz, "minecraft:water")
    for dx, dz in ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)):
        setblock(cx + dx, -59, cz + dz, "minecraft:farmland[moisture=7]")
    for dx, dz in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        setblock(cx + dx, -58, cz + dz, "minecraft:melon_stem[age=7]")
    for dx, dz in ((-2, 0), (2, 0), (0, -2), (0, 2), (-2, -2), (-2, 2), (2, -2), (2, 2)):
        setblock(cx + dx, -58, cz + dz, "minecraft:melon")


def zone(xz: tuple[int, int], s: int = S_LOOP, dxz: tuple[int, int] = (0, 0)) -> str:
    x, z = xz
    dx, dz = dxz
    return f"@a[x={x},y={s},z={z},dx={dx},dy=1,dz={dz}]"


def machinery() -> None:
    rcon("scoreboard", "objectives", "add", "lc", "dummy")
    for player in ("laps", "armA", "armB", "counted"):
        rcon("scoreboard", "players", "set", player, "lc", "0")
    a, b = zone(ZONE_A), zone(ZONE_B)
    both = zone(ZONE_B, dxz=(0, 1))  # the A+B column as one box
    gx, gz = GATE
    gate_cells = f"{gx} -60 {gz} {gx} -59 {gz}"
    ix, iy = INDICATOR
    # the two-zone direction detector: A then B counts, B then A does not
    command_block(
        30,
        0,
        f"execute if entity {a} if score armB lc matches 0 run scoreboard players set armA lc 1",
    )
    command_block(
        30,
        1,
        f"execute if entity {b} if score armA lc matches 1 "
        "if score counted lc matches 0 "
        "run scoreboard players add laps lc 1",
    )
    command_block(31, 1, "scoreboard players set counted lc 1", kind="chain", cond=True)
    command_block(30, 2, f"execute unless entity {both} run scoreboard players set armA lc 0")
    command_block(31, 2, "scoreboard players set armB lc 0", kind="chain", cond=True)
    command_block(32, 2, "scoreboard players set counted lc 0", kind="chain", cond=True)
    command_block(
        30,
        3,
        f"execute if entity {b} if score armA lc matches 0 "
        "if score counted lc matches 0 "
        "run scoreboard players set armB lc 1",
    )
    # the gate: open at laps >= 3, closed below (idempotent both ways)
    command_block(
        30, 4, f"execute if score laps lc matches 3.. run fill {gate_cells} minecraft:air"
    )
    command_block(
        30, 5, f"execute if score laps lc matches ..2 run fill {gate_cells} minecraft:obsidian"
    )
    # larder entry resets the count (the gate-close conditional recloses)
    command_block(
        30,
        6,
        f"execute if entity {zone((12, 12), s=S_LARDER, dxz=(6, 6))} "
        "run scoreboard players set laps lc 0",
    )
    # the indicator column: laps mirrored as gold blocks, world-readable
    for k in range(1, 4):
        cz = 10 + (k - 1)
        command_block(
            30,
            6 + 2 * k - 1,
            f"execute if score laps lc matches {k}.. "
            f"run setblock {ix} {iy} {cz} minecraft:gold_block",
        )
        command_block(
            30,
            6 + 2 * k,
            f"execute if score laps lc matches ..{k - 1} "
            f"run setblock {ix} {iy} {cz} minecraft:bedrock",
        )


def main() -> int:
    if "normal" not in rcon("difficulty").lower():
        rcon("difficulty", "normal")
    rcon("gamerule", "spawn_mobs", "false")  # 1.21.11 snake_case rule names
    rcon("gamerule", "command_block_output", "false")
    # the design theorem extended (first decode-probe read, 2026-08-28):
    # any monotone exogenous SENSED signal is a progress channel — the
    # day clock (env.sin/cos_time) and rain (env.rain) decoded the lap
    # index beyond the chance band. The arena pins both; the channels
    # become constants and carry nothing.
    rcon("gamerule", "advance_time", "false")
    rcon("gamerule", "advance_weather", "false")
    rcon("time", "set", "6000")
    rcon("weather", "clear")
    rcon("setworldspawn", "2", "-60", "0")
    rcon("forceload", "add", "-16", "-16", "48", "48")
    carve()
    light()
    patch()
    machinery()
    rcon("forceload", "remove", "all")
    print("provisioned: the larder loop (gate closed, laps 0)", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
