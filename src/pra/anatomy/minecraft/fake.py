"""FakeBridge: the deterministic in-repo bridge (features 027/030/031/033).

A voxel *sketch* — flat ground, a wall, a tall pillar, two pits, wood
columns — that speaks the full pra-mc/1 protocol on a localhost socket,
so the entire adapter code path (framing, handshake, tick round-trip,
delivery, the state seam) runs in this repository's quality gate with no
Minecraft, Node, or Docker anywhere. Its physics is the *shape* of the
channel contract, not a Minecraft simulation. Everything is pure
arithmetic — no RNG, no wall clock — so same-command runs are
byte-identical.

Feature 033 (the property body): items are *names* ("cobblestone",
"oak_log", …) whose signatures and placeability the channels derive the
same way the live bridge does — no material classes anywhere. Digging is
a held intention with per-material durations and sensed progress; any
other command releases it (vanilla: letting go resets the cracks).

``state`` returns the complete world (pose, tick, time, edits, pocket,
held kind, staging grid, mid-dig progress); ``load_state`` restores it
exactly: fake-mode resume is class 1 (Doc 06 §5b), proven byte-for-byte.

``survival=True`` is the native-survival instrument (research topic
native-survival, 2026-08-11; ships only on promotion): the world gains
its own metabolism — integer food/health points that the vitals channel
reads live, a deterministic drain under the world's own clock, health
following once food runs out (normal-difficulty floor: half a heart) —
a melon column whose slices are the edible kind, the hand's edible
affordance flag, and `use_held`: apply the held item, a held intention
exactly the dig's shape (any other command releases it), consuming one
held edible after its vanilla-proportioned duration when the body is
hungry. All still pure arithmetic; the state seam carries it.
"""

from __future__ import annotations

import hashlib
import json
import math
import socket
import threading
from collections import deque

from pra.anatomy.minecraft.protocol import PROTOCOL_VERSION, send_message

__all__ = ["FakeBridge", "item_signature"]

_GROUND_Y = 64.0
_TIME_STEP = 25  # ticks of the 24000-tick day per control tick

# the fixed layout: feet-level solids, eye-level solids (tall), pits, wood.
# The (-1, 0) wood column is the starter (feature 030 pilot diagnosis).
_WOOD_SOLIDS = frozenset({(-1, 0), (-2, 3), (5, -1)})
_FEET_SOLIDS = frozenset({(3, z) for z in range(-2, 3)} | {(-4, 0)} | _WOOD_SOLIDS)
_EYE_SOLIDS = frozenset({(-4, 0)})  # the pillar is tall; the wall is chest-high
_PITS = frozenset({(0, 4), (1, 4)})

# world facts (the game's, not a brain ontology): what an item is called
# when mined, whether it maps to a placeable block, how long it takes to
# break (ticks at the 250 ms posture, vanilla-proportioned: ~0.75 s mineral
# bare-handed, ~3 s wood)
_MINERAL_ITEM = "cobblestone"
_WOOD_ITEM = "oak_log"
_PLACEABLE = frozenset({"cobblestone", "oak_log", "oak_planks"})  # stick is not a block
_DIG_TICKS_MINERAL = 3
_DIG_TICKS_WOOD = 12

# native-survival instrument facts (survival worlds only): one melon column,
# vanilla-proportioned at the 250 ms posture — the block breaks in ~1.5 s and
# yields slices (deterministic 3, no drop RNG), a slice is edible and NOT
# placeable, eating takes ~1.6 s and pays 2 of 20 food points; food drains
# one point per drain interval, and once it is gone health follows down to
# the normal-difficulty starvation floor (half a heart).
_MELON_SOLIDS = frozenset({(0, -2)})
_MELON_ITEM = "melon_slice"
_MELON_YIELD = 3
_EDIBLE = frozenset({_MELON_ITEM})
_DIG_TICKS_MELON = 6
_EAT_TICKS = 6
_EAT_PAY = 2  # food points per consumed slice (vanilla melon)
_FOOD_DRAIN_TICKS = 40  # one food point per interval (10 s at the 250 ms posture)
_STARVATION_FLOOR = 1  # health points; normal difficulty stops at half a heart


def item_signature(name: str) -> tuple[float, float, float]:
    """The appearance signature (feature 033, contract): sha256 of the item
    name, bytes 0..2, each mapped to [-1, 1]. Identical in both bridges —
    stable, distinguishing, semantics-free."""
    digest = hashlib.sha256(name.encode("utf-8")).digest()
    return tuple(b / 127.5 - 1.0 for b in digest[:3])


class _World:
    """The deterministic sketch. All mutable state lives here."""

    def __init__(self, survival: bool = False) -> None:
        self.survival = survival
        self.x = 0.0
        self.z = 0.0
        self.yaw = 0.0  # radians; 0 faces +z, matching the mineflayer convention
        self.tick = 0
        self.time = 0
        self.dug: set[tuple[int, int]] = set()
        self.placed: dict[tuple[int, int], str] = {}  # column -> the item placed there
        self.inventory: dict[str, int] = {}  # item name -> count (the pocket)
        self.held: str | None = None  # the held kind (an item name)
        self.grid: list[str] = []  # <=4 staged item names, column-first
        self.digging: tuple[tuple[int, int], int] | None = None  # (column, progress ticks)
        self.food = 20  # food points (vanilla's integers; survival worlds drain them)
        self.health = 20  # health points; follows once food runs out
        self.using: int | None = None  # ticks the use intention has been held

    # ---- geometry -------------------------------------------------------------
    def _ahead(self) -> tuple[int, int]:
        dx, dz = -math.sin(self.yaw), math.cos(self.yaw)
        return round(self.x + dx), round(self.z + dz)

    def _feet_solid(self, column: tuple[int, int]) -> bool:
        if column in self.dug:
            return False
        if self.survival and column in _MELON_SOLIDS:
            return True
        return column in _FEET_SOLIDS or column in self.placed

    def _step_to(self, column: tuple[int, int]) -> None:
        self.x, self.z = float(column[0]), float(column[1])

    def _dig_ticks(self, column: tuple[int, int]) -> int:
        if column in self.placed:
            return _DIG_TICKS_MINERAL
        if column in _WOOD_SOLIDS:
            return _DIG_TICKS_WOOD
        return _DIG_TICKS_MELON if column in _MELON_SOLIDS else _DIG_TICKS_MINERAL

    def _dig_yield(self, column: tuple[int, int]) -> tuple[str, int]:
        if column in self.placed:
            return self.placed[column], 1
        if column in _WOOD_SOLIDS:
            return _WOOD_ITEM, 1
        return (_MELON_ITEM, _MELON_YIELD) if column in _MELON_SOLIDS else (_MINERAL_ITEM, 1)

    def _block_name(self, column: tuple[int, int]) -> str:
        """The sketch's SURFACE name (what a glance ray sees) — the block,
        not its drop: the melon column is a `melon` block."""
        if column in self.placed:
            return self.placed[column]
        if column in _WOOD_SOLIDS:
            return _WOOD_ITEM
        return "melon" if column in _MELON_SOLIDS else _MINERAL_ITEM

    def _glance(self) -> list[float]:
        """The glance's SHAPE over the sketch (distal-senses; the live
        bridge is the evidence instrument — doctrine): eight egocentric
        sectors, one feet-level ray each to 16, distance + signature."""
        out: list[float] = []
        for k in range(8):
            a = self.yaw - k * math.pi / 4
            dx, dz = -math.sin(a), math.cos(a)
            dist, sig = 1.0, (0.0, 0.0, 0.0)
            for i in range(1, 17):
                column = (round(self.x + dx * i), round(self.z + dz * i))
                if self._feet_solid(column):
                    dist, sig = i / 16.0, item_signature(self._block_name(column))
                    break
            out.extend([dist, *sig])
        return out

    def _kinds(self) -> list[str]:
        return sorted(name for name, count in self.inventory.items() if count > 0)

    def _gain(self, name: str, count: int = 1) -> None:
        self.inventory[name] = self.inventory.get(name, 0) + count

    def _offer(self) -> tuple[str, int] | None:
        """The world's pocket-craft rules (vanilla-exact matching): one log
        alone offers its species' planks; two same planks offer sticks."""
        if len(self.grid) == 1 and self.grid[0].endswith("_log"):
            return self.grid[0].replace("_log", "_planks"), 4
        if (
            len(self.grid) == 2
            and self.grid[0] == self.grid[1]
            and self.grid[0].endswith("_planks")
        ):
            return "stick", 4
        return None

    # ---- commands (the contract's twelve; survival adds the mouth) ---------------
    def apply(self, command: dict) -> None:
        name = next(iter(command)) if command else None
        if name != "dig_ahead":
            self.digging = None  # releasing the intention resets the cracks
        if name != "use_held":
            self.using = None  # the use intention releases the same way
        if name is None:  # idle
            return
        if len(command) > 1:
            raise ValueError(f"command carries {len(command)} keys, expected one")
        if name == "forward":
            ahead = self._ahead()
            if not self._feet_solid(ahead) and ahead not in _PITS:
                self._step_to(ahead)
        elif name == "back":
            dx, dz = -math.sin(self.yaw), math.cos(self.yaw)
            behind = (round(self.x - dx), round(self.z - dz))
            if not self._feet_solid(behind) and behind not in _PITS:
                self._step_to(behind)
        elif name == "turn_left":
            self.yaw += math.pi / 4
        elif name == "turn_right":
            self.yaw -= math.pi / 4
        elif name == "jump_forward":
            ahead = self._ahead()
            if not self._feet_solid(ahead):  # jumping clears pits, not walls
                self._step_to(ahead)
        elif name == "dig_ahead":
            ahead = self._ahead()
            if not self._feet_solid(ahead):
                self.digging = None
                return
            progress = self.digging[1] + 1 if self.digging and self.digging[0] == ahead else 1
            if progress >= self._dig_ticks(ahead):
                self._gain(*self._dig_yield(ahead))
                if ahead in self.placed:
                    del self.placed[ahead]
                else:
                    self.dug.add(ahead)
                self.digging = None
            else:
                self.digging = (ahead, progress)
        elif name == "place_ahead":
            ahead = self._ahead()
            if (
                not self._feet_solid(ahead)
                and self.held is not None
                and self.held in _PLACEABLE
                and self.inventory.get(self.held, 0) > 0
            ):
                self.dug.discard(ahead)
                self.placed[ahead] = self.held
                self.inventory[self.held] -= 1
        elif name == "hold_next":
            cycle: list[str | None] = [None] + self._kinds()
            index = cycle.index(self.held) if self.held in cycle else 0
            self.held = cycle[(index + 1) % len(cycle)]
        elif name == "grid_put":
            if (
                self.held is not None
                and self.inventory.get(self.held, 0) > 0
                and len(self.grid) < 4
            ):
                self.inventory[self.held] -= 1
                self.grid.append(self.held)
        elif name == "grid_take":
            for staged in self.grid:
                self._gain(staged)
            self.grid = []
        elif name == "take_result":
            offer = self._offer()
            if offer is not None:
                self.grid = []  # the offer's inputs are exactly the staging
                self._gain(offer[0], offer[1])
        elif name == "use_held" and self.survival:
            # apply the held item — no edibility check in the actuator (the
            # classifier-free mouth): only a held edible on a hungry body
            # progresses; everything else is a world no-op, never an error
            if (
                self.held is None
                or self.inventory.get(self.held, 0) == 0
                or self.held not in _EDIBLE
                or self.food >= 20
            ):
                self.using = None
                return
            self.using = (self.using or 0) + 1
            if self.using >= _EAT_TICKS:
                self.inventory[self.held] -= 1
                self.food = min(20, self.food + _EAT_PAY)
                self.using = None
        else:
            raise ValueError(f"unknown command {name!r}")

    def advance(self) -> None:
        self.tick += 1
        self.time = (self.time + _TIME_STEP) % 24000
        if self.survival and self.tick % _FOOD_DRAIN_TICKS == 0:
            if self.food > 0:
                self.food -= 1
            elif self.health > _STARVATION_FLOOR:
                self.health -= 1  # starvation: health follows the empty bar

    # ---- the channel contract --------------------------------------------------
    def channels(self) -> dict[str, list[float]]:
        ahead = self._ahead()
        theta = 2.0 * math.pi * (self.time / 24000.0)
        clip = lambda v: max(-1.0, min(1.0, v))  # noqa: E731 - three uses, one line
        total = sum(self.inventory.values())
        kinds = self._kinds()
        placeable_count = sum(c for n, c in self.inventory.items() if n in _PLACEABLE)
        held_count = self.inventory.get(self.held, 0) if self.held else 0
        hand_width = 7 if self.survival else 6
        if self.held is not None and held_count > 0:
            hand = [
                1.0,
                1.0 if self.held in _PLACEABLE else 0.0,
                # the edible affordance sits beside placeability (survival)
                *([1.0 if self.held in _EDIBLE else 0.0] if self.survival else []),
                min(held_count, 64) / 64.0,
                *item_signature(self.held),
            ]
        else:
            hand = [0.0] * hand_width
        offer = self._offer()
        if offer is not None:
            offer_name, offer_count = offer
            grid = [
                len(self.grid) / 4.0,
                1.0,
                1.0 if offer_name in _PLACEABLE else 0.0,
                min(offer_count, 64) / 64.0,
                *item_signature(offer_name),
            ]
        else:
            grid = [len(self.grid) / 4.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        if self.digging is not None:
            column, progress = self.digging
            mining = [min(progress / self._dig_ticks(column), 1.0)]
        elif self.using is not None:
            # survival: the progress channel senses the HELD INTENTION's
            # progress, whatever the intention — the chew has cracks too
            # (native-survival arms amendment 1)
            mining = [min(self.using / _EAT_TICKS, 1.0)]
        else:
            mining = [0.0]
        channels = {
            "pose": [
                clip(self.x / 64.0),
                clip(self.z / 64.0),
                clip((_GROUND_Y + 1.0 - 64.0) / 64.0),
                math.sin(self.yaw),
                math.cos(self.yaw),
            ],
            "vitals": [self.health / 20.0, self.food / 20.0],
            "env": [1.0, math.sin(theta), math.cos(theta), 0.0],
            "blocks": [
                1.0 if self._feet_solid(ahead) else 0.0,
                1.0 if ahead in _EYE_SOLIDS else 0.0,
                1.0 if ahead in _PITS else 0.0,
            ],
            "mining": mining,
            "pocket": [
                min(total, 64) / 64.0,
                min(len(kinds), 9) / 9.0,
                min(placeable_count, 64) / 64.0,
                min(total - placeable_count, 64) / 64.0,
            ],
            "hand": hand,
            "grid": grid,
        }
        if self.survival:
            # the sketch has no item entities: the drops channel is
            # permanently empty here (declared); the glance is real shape
            channels["drops"] = [0.0] * 8
            channels["glance"] = self._glance()
        return channels

    def view(self) -> dict:
        """Ground truth for humans (feature 033): never sensed by the brain."""
        view = {
            "pos": [self.x, _GROUND_Y + 1.0, self.z],
            "held": self.held,
            "inventory": [
                [n, self.inventory[n]] for n in sorted(self.inventory) if self.inventory[n] > 0
            ],
        }
        if self.survival:
            view["food"] = self.food
            view["health"] = self.health
            view["eating"] = min((self.using or 0) / _EAT_TICKS, 1.0)
        return view

    # ---- the state seam ---------------------------------------------------------
    def state_dict(self) -> dict:
        state = {
            "x": self.x,
            "z": self.z,
            "yaw": self.yaw,
            "tick": self.tick,
            "time": self.time,
            "dug": sorted(self.dug),
            "placed": sorted([list(c), n] for c, n in self.placed.items()),
            "inventory": {n: c for n, c in sorted(self.inventory.items()) if c > 0},
            "held": self.held,
            "grid": list(self.grid),
            "digging": [list(self.digging[0]), self.digging[1]] if self.digging else None,
        }
        if self.survival:  # the metabolism rides the class-1 seam
            state["food"] = self.food
            state["health"] = self.health
            state["using"] = self.using
        return state

    def load_state_dict(self, state: dict) -> None:
        self.x = float(state["x"])
        self.z = float(state["z"])
        self.yaw = float(state["yaw"])
        self.tick = int(state["tick"])
        self.time = int(state["time"])
        self.dug = {tuple(c) for c in state["dug"]}
        self.placed = {tuple(c): n for c, n in state["placed"]}
        self.inventory = {n: int(c) for n, c in state["inventory"].items()}
        self.held = state["held"]
        self.grid = list(state["grid"])
        digging = state["digging"]
        self.digging = (tuple(digging[0]), int(digging[1])) if digging else None
        if self.survival:  # loud on a snapshot from the wrong mode (KeyError)
            self.food = int(state["food"])
            self.health = int(state["health"])
            self.using = int(state["using"]) if state["using"] is not None else None


class FakeBridge:
    """Serve the protocol on an ephemeral localhost port (daemon thread).

    One client at a time (the contract); a second concurrent connection
    is answered with an error and closed. ``stop()`` is idempotent.
    """

    CHANNELS = {
        "pose": 5,
        "vitals": 2,
        "env": 4,
        "blocks": 3,
        "mining": 1,
        "pocket": 4,
        "hand": 6,
        "grid": 7,
    }

    def __init__(self, survival: bool = False) -> None:
        # survival widens the hand by the edible affordance and appends the
        # distal senses (instrument mode); the instance table shadows the
        # shipped class table
        self.CHANNELS = (
            {**FakeBridge.CHANNELS, "hand": 7, "drops": 8, "glance": 32}
            if survival
            else dict(FakeBridge.CHANNELS)
        )
        self.world = _World(survival=survival)
        self._listener = socket.create_server(("127.0.0.1", 0))
        self._listener.settimeout(0.2)
        self.port = self._listener.getsockname()[1]
        self._busy = threading.Lock()
        self._stopping = threading.Event()
        self._workers: list[threading.Thread] = []
        self.requests: deque[str] = deque(maxlen=1_000_000)  # op journal (bounded)
        self._thread = threading.Thread(target=self._serve, daemon=True)
        self._thread.start()

    # ---- lifecycle -------------------------------------------------------------
    def stop(self) -> None:
        if not self._stopping.is_set():
            self._stopping.set()
            self._thread.join(timeout=5.0)
            for worker in self._workers:
                worker.join(timeout=5.0)
            self._listener.close()

    def __enter__(self) -> FakeBridge:
        return self

    def __exit__(self, *_exc) -> None:
        self.stop()

    # ---- the server loop ---------------------------------------------------------
    def _serve(self) -> None:
        # accept stays responsive while a client is being served (in its own
        # thread) so a second concurrent connection is REFUSED, not queued —
        # the contract's one-client rule, testable.
        while not self._stopping.is_set():
            try:
                conn, _addr = self._listener.accept()
            except TimeoutError:
                continue
            except OSError:
                return
            if not self._busy.acquire(blocking=False):
                try:
                    send_message(conn, {"ok": False, "error": "bridge serves one client at a time"})
                except OSError:
                    pass
                conn.close()
                continue
            worker = threading.Thread(target=self._client_thread, args=(conn,), daemon=True)
            self._workers.append(worker)
            worker.start()

    def _client_thread(self, conn: socket.socket) -> None:
        try:
            self._serve_client(conn)
        finally:
            conn.close()
            self._busy.release()

    def _serve_client(self, conn: socket.socket) -> None:
        # A manual receive buffer, NOT conn.makefile(): a buffered file object
        # on a timeout socket is left in an undefined state by a mid-read
        # timeout (found by the C1 length soak at ~367k requests). Partial
        # lines survive timeouts here by construction.
        conn.settimeout(0.2)
        buffer = bytearray()
        while not self._stopping.is_set():
            newline = buffer.find(b"\n")
            if newline < 0:
                try:
                    chunk = conn.recv(65536)
                except TimeoutError:
                    continue  # the partial line stays buffered
                except OSError:
                    return
                if not chunk:
                    return  # client closed
                buffer.extend(chunk)
                continue
            line = bytes(buffer[:newline])
            del buffer[: newline + 1]
            try:
                message = json.loads(line)
                if not isinstance(message, dict):
                    raise ValueError("message must be a JSON object")
            except ValueError:
                return  # garbage; the client side is loud
            try:
                response, goodbye = self._handle(message)
            except Exception as exc:  # a bridge-side contract violation is loud
                response, goodbye = {"ok": False, "error": str(exc)}, False
            try:
                send_message(conn, response)
            except OSError:
                return
            if goodbye:
                return

    def _handle(self, message: dict) -> tuple[dict, bool]:
        op = message.get("op")
        self.requests.append(str(op))
        if op == "hello":
            if message.get("version") != PROTOCOL_VERSION:
                return {
                    "ok": False,
                    "error": f"protocol version mismatch: bridge speaks {PROTOCOL_VERSION}, "
                    f"client sent {message.get('version')!r}",
                }, False
            return {
                "ok": True,
                "version": PROTOCOL_VERSION,
                "channels": dict(self.CHANNELS),
                "spawn": True,
            }, False
        if op == "tick":
            for command in message.get("commands", []):
                self.world.apply(command)
            self.world.advance()
            return {
                "ok": True,
                "tick": self.world.tick,
                "channels": self.world.channels(),
                "view": self.world.view(),
            }, False
        if op == "state":
            return {"ok": True, "world": self.world.state_dict()}, False
        if op == "load_state":
            self.world.load_state_dict(message.get("world", {}))
            return {"ok": True}, False
        if op == "bye":
            return {"ok": True}, True
        return {"ok": False, "error": f"unknown op {op!r}"}, False
