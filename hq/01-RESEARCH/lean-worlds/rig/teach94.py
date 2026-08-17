"""Teach the 94-dim peers body — the d23 recipe, verbatim, wider.

The same 45 sense-using lessons that taught worth-taught.bin (the
86-dim subject of L1), on `c1_anatomy(survival=True, flood=True,
aim="worth", peers=True)` over a PEERS=1 bridge. No peer is in the
world during any lesson — the peers channel reads zeros in every
classroom, exactly as the flood read near-zeros in sated lessons.
The palate starts from the same taught tongue the 86-dim brain is
born with (worth-palate-taught.json), removing the tongue as a
confound; arms restore it again at birth regardless.

    python teach94.py            # 45 lessons -> peers-taught.bin (+ demos)
"""

from __future__ import annotations

import dataclasses
import os
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

RIG = Path(__file__).parent
REPO = RIG.parents[3]
ARMS = REPO / "examples" / "minecraft" / "survival" / "arms"
PROBE = REPO / "examples" / "minecraft" / "survival" / "probe"
BRIDGE_JS = REPO / "examples" / "minecraft" / "bridge" / "bridge.js"
sys.path.insert(0, str(ARMS))
sys.path.insert(0, str(PROBE))
import d23_runner as D  # noqa: E402 — the teach recipe
import n23_runner as R  # noqa: E402 — engine helpers, rcon
import provision  # noqa: E402 — the probe patch builder d23's classroom uses

from pra.anatomy.minecraft import c1_anatomy  # noqa: E402

R.CONTAINER = "lw1-minecraft"
R.BRIDGE_PORT = 25592
provision.CONTAINER = R.CONTAINER
MC_PORT = 25604
R.SENSORS, R.ACTUATORS = c1_anatomy(survival=True, flood=True, aim="worth", peers=True)
R.OBS_DIM = sum(s.width for s in R.SENSORS)  # 94
R.N_ACTIONS = sum(len(a.presets) for a in R.ACTUATORS)  # 13
R.BASE = dataclasses.replace(R.BASE, obs_dim=R.OBS_DIM, n_actions=R.N_ACTIONS)
D.TAUGHT = RIG / "peers-taught.bin"
D.DEMOS = RIG / "peers-demos.json"
D.PROGRESS = RIG / "peers-taught-progress.json"
PALATE = RIG / "palate.json"


def main() -> int:
    assert R.OBS_DIM == 94, R.OBS_DIM
    shutil.copy(ARMS / "worth-palate-taught.json", PALATE)
    env = {
        **os.environ,
        "SURVIVAL": "1",
        "FLOOD": "intrusion",
        "AIM": "worth",
        "AIM_ABLATE": "",
        "PEERS": "1",
        "PALATE_FILE": str(PALATE),
        "SPAWN_ANCHOR": "0,0",
        "MC_PORT": str(MC_PORT),
        "BRIDGE_PORT": str(R.BRIDGE_PORT),
    }
    log = open(RIG / "teach94-bridge.log", "a")
    bridge = subprocess.Popen(
        ["node", str(BRIDGE_JS)], env=env, stdout=log, stderr=subprocess.STDOUT
    )
    for _ in range(120):
        try:
            socket.create_connection(("127.0.0.1", R.BRIDGE_PORT), timeout=2).close()
            break
        except OSError:
            time.sleep(0.5)
    else:
        raise SystemExit("bridge never listened — see teach94-bridge.log")
    try:
        print("world:", R.rcon("tick", "rate", "100"), flush=True)
        D.teach()
    finally:
        bridge.terminate()
        bridge.wait(timeout=10)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
