"""The live contract check: the pra-mc/1 adapter proven against the REAL
bridge and server (there is no fake side of this seam — the owner's
rule, 2026-08-13; this script replaced the deleted FakeBridge estate).

Run it whenever the bridge, the anatomy, or the contract changes, with
the stack up (world + bridge). It checks the wire protocol and the
channel table for WHATEVER mode the bridge is running (shipped /
survival / survival+flood, inferred from the hello table) and exits
non-zero on the first violation.

    python examples/minecraft/contract_check.py [--bridge-port 25590]
"""

from __future__ import annotations

import argparse
import json
import socket
import sys

from pra.anatomy.minecraft import PROTOCOL_VERSION, c1_anatomy


def connect(port: int) -> socket.socket:
    return socket.create_connection(("127.0.0.1", port), timeout=30)


class Session:
    def __init__(self, port: int):
        self.sock = connect(port)
        self.buf = b""

    def call(self, msg: dict) -> dict:
        self.sock.sendall((json.dumps(msg) + "\n").encode())
        while b"\n" not in self.buf:
            chunk = self.sock.recv(65536)
            if not chunk:
                raise ConnectionError("bridge closed")
            self.buf += chunk
        line, self.buf = self.buf.split(b"\n", 1)
        return json.loads(line)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bridge-port", type=int, default=25590)
    args = parser.parse_args()
    failures = 0

    def check(name: str, ok: bool, detail="") -> None:
        nonlocal failures
        print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f": {detail}" if detail else ""), flush=True)
        if not ok:
            failures += 1

    s = Session(args.bridge_port)
    hello = s.call({"op": "hello", "version": PROTOCOL_VERSION})
    check(
        "hello ok + version", hello.get("ok") is True and hello.get("version") == PROTOCOL_VERSION
    )
    check("hello waits for spawn", hello.get("spawn") is True)
    table = hello.get("channels") or {}

    # infer the bridge's mode from its own table, then hold it to the
    # anatomy declaration for that mode
    survival = table.get("hand") == 7
    flood = "flood" in table
    aim = "worth" if "aim" in table else ""
    sensors, actuators = c1_anatomy(survival=survival, flood=flood, aim=aim)
    declared = {s_.topic: s_.width for s_ in sensors}
    check(
        f"channel table matches c1_anatomy(survival={survival}, flood={flood}, aim={aim!r})",
        table == declared,
        f"bridge={table} anatomy={declared}" if table != declared else "",
    )

    second = Session(args.bridge_port)
    refused = second.call({"op": "hello", "version": PROTOCOL_VERSION})
    check("second concurrent client refused", refused.get("ok") is False)

    bad = Session(args.bridge_port)  # the refused socket closed; slot is ours
    wrong = bad.call({"op": "hello", "version": "pra-mc/999"})
    check("version mismatch is loud", wrong.get("ok") is False)
    bad.sock.close()

    r = s.call({"op": "tick", "tick_ms": 50, "commands": []})
    check("tick ok with index", r.get("ok") is True and isinstance(r.get("tick"), int))
    first_tick = r["tick"]
    channels = r.get("channels") or {}
    widths_ok = all(
        isinstance(channels.get(name), list) and len(channels[name]) == width
        for name, width in declared.items()
    )
    check("every declared channel delivered at declared width", widths_ok)
    check("view rides the tick", isinstance(r.get("view"), dict))

    r = s.call({"op": "tick", "tick_ms": 50, "commands": [{}]})
    check("tick index advances by one", r["tick"] == first_tick + 1)

    err = s.call({"op": "tick", "tick_ms": 50, "commands": [{"fly": 1.0}]})
    check("unknown command is a loud error", err.get("ok") is False and "fly" in str(err))

    known = {
        "forward",
        "back",
        "turn_left",
        "turn_right",
        "jump_forward",
        "dig_ahead",
        "place_ahead",
        "hold_next",
        "grid_put",
        "grid_take",
        "take_result",
    }
    if survival:
        known.add("use_held")
    for preset in actuators[0].presets:
        for key in preset:
            check(f"anatomy preset '{key}' is a bridge command", key in known)

    state = s.call({"op": "state"})
    check(
        "state is class 4 (live marker)",
        state.get("ok") is True and state["world"].get("live") is True,
    )
    load = s.call({"op": "load_state", "world": {"live": True, "tick": state["world"]["tick"]}})
    check("load_state accepts the live marker", load.get("ok") is True)

    bye = s.call({"op": "bye"})
    check("bye answers before closing", bye.get("ok") is True)
    s.sock.close()

    print(("CONTRACT OK" if failures == 0 else f"CONTRACT FAILED ({failures})"), flush=True)
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
