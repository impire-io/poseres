"""Head-to-head pilot: salience vs worth (the-aim README).

Each form gets its OWN taught brain AND its own taught tongue (45
sense-using lessons on the flood body, tongue born naive — the
demonstrations bootstrap the palate exactly as they bootstrap the
head), then 3 hungry-born 6,000-step lives at the D3 protocol. The
bridge runs FLOOD=intrusion beside AIM=<form>: the flood supplies the
urgency, the aim is what's on trial. Measured floors this pilot reads
against: no-flood 1/6, flooded pilot 3/3 with first-eats 3.8-5.2k.
The winning form proceeds to the A2/A3 arms.

    python aim_pilot.py teach salience|worth
    python aim_pilot.py lives salience|worth
"""

from __future__ import annotations

import dataclasses
import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

OUT = Path(__file__).parent
sys.path.insert(0, str(OUT.parent / "native-survival" / "arms"))
sys.path.insert(0, str(OUT.parent / "distal-senses"))
import d23_runner as D  # noqa: E402 — the sense-using curriculum + life machinery
import n23_runner as R  # noqa: E402 — the shared engine/classroom helpers

from pra.anatomy.minecraft import c1_anatomy  # noqa: E402

BRIDGE_JS = OUT.parent.parent.parent / "examples" / "minecraft" / "bridge" / "bridge.js"
PILOT_LIVES = 3
LIFE_CYCLES = 80  # 6,000 steps — the D3 protocol length


def set_form(form: str) -> None:
    assert form in ("salience", "worth"), form
    R.SENSORS, R.ACTUATORS = c1_anatomy(survival=True, flood=True, aim=form)
    R.OBS_DIM = sum(s.width for s in R.SENSORS)  # salience 77, worth 86
    R.N_ACTIONS = sum(len(a.presets) for a in R.ACTUATORS)
    R.BASE = dataclasses.replace(R.BASE, obs_dim=R.OBS_DIM, n_actions=R.N_ACTIONS)
    D.TAUGHT = OUT / f"{form}-taught.bin"
    D.DEMOS = OUT / f"{form}-demos.json"
    D.PROGRESS = OUT / f"{form}-teach-progress.json"


def start_bridge(form: str) -> subprocess.Popen:
    env = {
        **os.environ,
        "SURVIVAL": "1",
        "FLOOD": "intrusion",
        "AIM": form,
        "PALATE_FILE": str(OUT / f"{form}-palate.json"),
        "SPAWN_ANCHOR": "0,0",
        "MC_PORT": "25602",
        "BRIDGE_PORT": str(R.BRIDGE_PORT),
    }
    log = open(OUT / f"{form}-bridge.log", "a")
    proc = subprocess.Popen(["node", str(BRIDGE_JS)], env=env, stdout=log, stderr=subprocess.STDOUT)
    for _ in range(120):
        try:
            socket.create_connection(("127.0.0.1", R.BRIDGE_PORT), timeout=2).close()
            return proc
        except OSError:
            time.sleep(0.5)
    raise SystemExit(f"bridge (AIM={form}) never listened — see {form}-bridge.log")


def teach(form: str) -> None:
    if not D.PROGRESS.exists():
        # a fresh teach is born tongue-naive; a resume keeps its book
        (OUT / f"{form}-palate.json").unlink(missing_ok=True)
    D.teach()


def lives(form: str) -> None:
    from pra.persistence.snapshot import decode

    rows = []
    for life in range(1, PILOT_LIVES + 1):
        D.hungry_newborn()
        state = decode(D.TAUGHT.read_bytes())
        state, views, policy = D.run_life_segment(state, LIFE_CYCLES, kd=R.KD)
        row = {
            "form": form,
            "life": life,
            **D.chains_of(views),
            "completions": policy.completions_fired,
            "false_completions": policy.false_completions,
            "food_min": min((v.get("food", 0) for v in views), default=None),
            "food_max": max((v.get("food", 0) for v in views), default=None),
            "palate": views[-1].get("palate", {}) if views else {},
        }
        rows.append(row)
        print(f"LIFE {json.dumps(row)}", flush=True)
    (OUT / f"{form}-lives.json").write_text(json.dumps(rows, indent=1))
    expressed = sum(1 for r in rows if r["eats"] > 0)
    print(f"{form.upper()}_PILOT_COMPLETE expressed={expressed}/{PILOT_LIVES}", flush=True)


def main() -> int:
    phase = sys.argv[1] if len(sys.argv) > 1 else ""
    form = sys.argv[2] if len(sys.argv) > 2 else ""
    set_form(form)
    print("world:", R.rcon("tick", "rate", "100"), flush=True)
    bridge = start_bridge(form)
    try:
        if phase == "teach":
            teach(form)
        elif phase == "lives":
            lives(form)
        else:
            raise SystemExit("usage: aim_pilot.py teach|lives salience|worth")
    finally:
        bridge.terminate()
        bridge.wait(timeout=10)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
