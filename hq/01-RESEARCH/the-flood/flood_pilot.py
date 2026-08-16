"""R-form pilot: intrusion vs gain, head-to-head (the-flood README).

Each form gets its OWN taught brain (45 sense-using lessons on the
flood body, obs 77 — the lessons witness the flood swelling with the
dose and quieting as the tape eats), then 3 hungry-born 6,000-step
lives at the D3 protocol. The bridge must run the SAME form
(FLOOD=intrusion|gain); the handshake width check + contract check
hold the stack honest. The winning form runs the F bars.

    python flood_pilot.py teach intrusion|gain
    python flood_pilot.py lives intrusion|gain
"""

from __future__ import annotations

import dataclasses
import json
import sys
from pathlib import Path

OUT = Path(__file__).parent
sys.path.insert(0, str(OUT.parent.parent.parent / "examples" / "minecraft" / "survival" / "arms"))
sys.path.insert(0, str(OUT.parent / "distal-senses"))
import d23_runner as D  # noqa: E402 — the sense-using curriculum + life machinery
import n23_runner as R  # noqa: E402 — the shared engine/classroom helpers

from pra.anatomy.minecraft import c1_anatomy  # noqa: E402

# the flood body: every shared helper reads these module globals
R.SENSORS, R.ACTUATORS = c1_anatomy(survival=True, flood=True)
R.OBS_DIM = sum(s.width for s in R.SENSORS)  # 77
R.N_ACTIONS = sum(len(a.presets) for a in R.ACTUATORS)
R.BASE = dataclasses.replace(R.BASE, obs_dim=R.OBS_DIM, n_actions=R.N_ACTIONS)

PILOT_LIVES = 3
LIFE_CYCLES = 80  # 6,000 steps — the D3 protocol length


def set_form(form: str) -> None:
    assert form in ("intrusion", "gain"), form
    D.TAUGHT = OUT / f"{form}-taught.bin"
    D.DEMOS = OUT / f"{form}-demos.json"
    D.PROGRESS = OUT / f"{form}-teach-progress.json"


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
    if phase == "teach":
        D.teach()
    elif phase == "lives":
        lives(form)
    else:
        raise SystemExit("usage: flood_pilot.py teach|lives intrusion|gain")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
