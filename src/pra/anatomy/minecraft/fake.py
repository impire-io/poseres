"""FakeBridge: the deterministic in-repo bridge (feature 027, FR-005).

A voxel *sketch* — flat ground, a wall, a tall pillar, two pits — that
speaks the full pra-mc/1 protocol on a localhost socket, so the entire
adapter code path (framing, handshake, tick round-trip, delivery, the
state seam) runs in this repository's quality gate with no Minecraft,
Node, or Docker anywhere. Its physics is the *shape* of the channel
contract, not a Minecraft simulation: movement is grid steps with
feet-level collision, jump_forward additionally crosses pits, dig/place
edit the feet-level solid set, daylight advances 25/24000 per tick.
Everything is pure arithmetic — no RNG, no wall clock — so same-command
runs are byte-identical (SC-002).

``state`` returns the complete world (bot pose, tick, time, block
edits); ``load_state`` restores it exactly: fake-mode resume is class 1
(Doc 06 §5b), and the integration suite proves it byte-for-byte.
"""

from __future__ import annotations

import math
import socket
import threading

from pra.anatomy.minecraft.protocol import PROTOCOL_VERSION, recv_message, send_message

__all__ = ["FakeBridge"]

_GROUND_Y = 64.0
_TIME_STEP = 25  # ticks of the 24000-tick day per control tick

# the fixed layout: feet-level solids, eye-level solids (tall), pits, wood
_WOOD_SOLIDS = frozenset({(-2, 3), (5, -1)})  # feature 030: diggable wood columns
_FEET_SOLIDS = frozenset({(3, z) for z in range(-2, 3)} | {(-4, 0)} | _WOOD_SOLIDS)
_EYE_SOLIDS = frozenset({(-4, 0)})  # the pillar is tall; the wall is chest-high
_PITS = frozenset({(0, 4), (1, 4)})


class _World:
    """The deterministic sketch. All mutable state lives here."""

    def __init__(self) -> None:
        self.x = 0.0
        self.z = 0.0
        self.yaw = 0.0  # radians; 0 faces +z, matching the mineflayer convention
        self.tick = 0
        self.time = 0
        self.dug: set[tuple[int, int]] = set()
        self.placed: set[tuple[int, int]] = set()
        # feature 030: the pocket — world-held state, sensed per tick
        self.inventory: dict[str, int] = {"blocks": 0, "logs": 0, "planks": 0, "sticks": 0}

    # ---- geometry -------------------------------------------------------------
    def _ahead(self) -> tuple[int, int]:
        dx, dz = -math.sin(self.yaw), math.cos(self.yaw)
        return round(self.x + dx), round(self.z + dz)

    def _feet_solid(self, column: tuple[int, int]) -> bool:
        if column in self.dug:
            return False
        return column in _FEET_SOLIDS or column in self.placed

    def _step_to(self, column: tuple[int, int]) -> None:
        self.x, self.z = float(column[0]), float(column[1])

    # ---- commands (the contract's eight) --------------------------------------
    def apply(self, command: dict) -> None:
        if not command:  # idle
            return
        (name,) = command.keys()  # presets carry exactly one key by construction
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
            if self._feet_solid(ahead):
                # feature 030: digging fills the pocket — wood yields a log,
                # everything else (layout or previously placed) a block
                if ahead in self.placed:
                    self.placed.discard(ahead)
                    self.inventory["blocks"] += 1
                else:
                    self.dug.add(ahead)
                    key = "logs" if ahead in _WOOD_SOLIDS else "blocks"
                    self.inventory[key] += 1
        elif name == "place_ahead":
            ahead = self._ahead()
            # feature 030: materially honest — consumes blocks first, then
            # planks; an empty pocket no-ops (the live bridge's semantics)
            if not self._feet_solid(ahead) and (
                self.inventory["blocks"] > 0 or self.inventory["planks"] > 0
            ):
                self.dug.discard(ahead)
                self.placed.add(ahead)
                key = "blocks" if self.inventory["blocks"] > 0 else "planks"
                self.inventory[key] -= 1
        elif name == "craft_planks":
            if self.inventory["logs"] >= 1:
                self.inventory["logs"] -= 1
                self.inventory["planks"] += 4
        elif name == "craft_sticks":
            if self.inventory["planks"] >= 2:
                self.inventory["planks"] -= 2
                self.inventory["sticks"] += 4
        else:
            raise ValueError(f"unknown command {name!r}")

    def advance(self) -> None:
        self.tick += 1
        self.time = (self.time + _TIME_STEP) % 24000

    # ---- the channel contract --------------------------------------------------
    def channels(self) -> dict[str, list[float]]:
        ahead = self._ahead()
        theta = 2.0 * math.pi * (self.time / 24000.0)
        clip = lambda v: max(-1.0, min(1.0, v))  # noqa: E731 - three uses, one line
        return {
            "pose": [
                clip(self.x / 64.0),
                clip(self.z / 64.0),
                clip((_GROUND_Y + 1.0 - 64.0) / 64.0),
                math.sin(self.yaw),
                math.cos(self.yaw),
            ],
            "vitals": [1.0, 1.0],
            "env": [1.0, math.sin(theta), math.cos(theta), 0.0],
            "blocks": [
                1.0 if self._feet_solid(ahead) else 0.0,
                1.0 if ahead in _EYE_SOLIDS else 0.0,
                1.0 if ahead in _PITS else 0.0,
            ],
            "inventory": [
                min(self.inventory["blocks"], 64) / 64.0,
                min(self.inventory["logs"], 64) / 64.0,
                min(self.inventory["planks"], 64) / 64.0,
                min(self.inventory["sticks"], 64) / 64.0,
                1.0 if self.inventory["blocks"] + self.inventory["planks"] > 0 else 0.0,
            ],
        }

    # ---- the state seam ---------------------------------------------------------
    def state_dict(self) -> dict:
        return {
            "x": self.x,
            "z": self.z,
            "yaw": self.yaw,
            "tick": self.tick,
            "time": self.time,
            "dug": sorted(self.dug),
            "placed": sorted(self.placed),
            "inventory": dict(self.inventory),
        }

    def load_state_dict(self, state: dict) -> None:
        self.x = float(state["x"])
        self.z = float(state["z"])
        self.yaw = float(state["yaw"])
        self.tick = int(state["tick"])
        self.time = int(state["time"])
        self.dug = {tuple(c) for c in state["dug"]}
        self.placed = {tuple(c) for c in state["placed"]}
        self.inventory = {k: int(v) for k, v in state["inventory"].items()}


class FakeBridge:
    """Serve the protocol on an ephemeral localhost port (daemon thread).

    One client at a time (the contract); a second concurrent connection
    is answered with an error and closed. ``stop()`` is idempotent.
    """

    CHANNELS = {"pose": 5, "vitals": 2, "env": 4, "blocks": 3, "inventory": 5}

    def __init__(self) -> None:
        self.world = _World()
        self._listener = socket.create_server(("127.0.0.1", 0))
        self._listener.settimeout(0.2)
        self.port = self._listener.getsockname()[1]
        self._busy = threading.Lock()
        self._stopping = threading.Event()
        self._workers: list[threading.Thread] = []
        self.requests: list[str] = []  # op journal, a test convenience
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
        conn.settimeout(0.2)
        rfile = conn.makefile("rb")
        while not self._stopping.is_set():
            try:
                message = recv_message(rfile)
            except TimeoutError:
                continue
            except Exception:
                return  # client vanished or spoke garbage; the client side is loud
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
            return {"ok": True, "tick": self.world.tick, "channels": self.world.channels()}, False
        if op == "state":
            return {"ok": True, "world": self.world.state_dict()}, False
        if op == "load_state":
            self.world.load_state_dict(message["world"])
            return {"ok": True}, False
        if op == "bye":
            return {"ok": True}, True
        return {"ok": False, "error": f"unknown op {op!r}"}, False
