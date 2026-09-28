"""Bar R1 — the reading, from the rows and the traces (topic the-arena-revival).

Per arm and life: crossings, gate passages (counted from the trace: a
step in the gate cell (15, 9) at loop level while the counter stood at 3,
followed by a larder entry), larder entries, eats, peeks, the rungs'
watch counters, and where the life was spent. Then the paired (by round)
sib − flat differences with their standard error on the registered
primary meter (full-chain eats) and on 0120's chains meter (gate passages).

Usage: python r1_verdict.py [--json out.json]
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
MC = HERE / "mc"


def trace_metrics(npz: Path) -> dict:
    d = np.load(npz)
    obs, pos = d["obs"], d["pos"]
    n = min(len(obs), len(pos))
    pos = pos[:n]
    arm_a = arm_b = counted = 0
    laps = 0
    cross: list[int] = []
    passages: list[int] = []
    entries: list[int] = []
    in_larder = False
    in_gate = False
    for i, p in enumerate(pos):
        loop = p[1] < -59
        a = loop and int(np.floor(p[0])) == 0 and int(np.floor(p[2])) == 3
        b = loop and int(np.floor(p[0])) == 0 and int(np.floor(p[2])) == 2
        if a and not arm_b:
            arm_a = 1
        if b and arm_a and not counted:
            cross.append(i)
            laps += 1
            counted = 1
        if b and not arm_a and not counted:
            arm_b = 1
        if not a and not b:
            arm_a = arm_b = counted = 0
        gate = loop and int(np.floor(p[0])) == 15 and int(np.floor(p[2])) == 9
        if gate and not in_gate and laps >= 3:
            passages.append(i)
        in_gate = gate
        larder = 12 <= p[0] < 19 and 12 <= p[2] < 19 and p[1] > -58.5
        if larder and not in_larder:
            entries.append(i)
            laps = 0  # the world's reset
        in_larder = larder
    cells = Counter((int(np.floor(p[0])), int(np.floor(p[2]))) for p in pos)
    top = cells.most_common(1)[0]
    return {
        "crossings": len(cross),
        "gate_passages": len(passages),
        "larder_entries": len({e // 50 for e in entries}),  # merge boundary toggles within 50 steps
        "first_crossing_step": cross[0] if cross else None,
        "top_cell": {"cell": list(top[0]), "steps": top[1]},
    }


def main() -> int:
    out = {}
    rows = {}
    for arm in ("flat", "sib", "sap"):
        rows[arm] = {}
        lp = HERE / f"{arm}-lives.jsonl"
        if not lp.exists():
            continue
        for line in lp.read_text().splitlines():
            r = json.loads(line)
            t = trace_metrics(MC / f"{arm}-life{r['life']}.npz")
            rows[arm][r["life"]] = {**r, **t}
    rounds = sorted(set(rows["flat"]) & set(rows["sib"]))
    print(f"paired rounds on record (sib vs flat): {len(rounds)}  ({rounds})")
    rounds_sap = sorted(set(rows["sap"]) & set(rows["sib"]))
    print(f"paired rounds on record (sap vs sib): {len(rounds_sap)}  ({rounds_sap})\n")
    cols = (
        "arm",
        "life",
        "cross",
        "gate",
        "entries",
        "eats",
        "peeks",
        "fatigue",
        "revive",
        "stage_filt",
        "ooc",
        "top_cell(steps)",
    )
    print("  ".join(f"{c:>7}" for c in cols))
    for arm in ("flat", "sib", "sap"):
        for life in sorted(rows[arm]):
            r = rows[arm][life]
            top = f"{tuple(r['top_cell']['cell'])}({r['top_cell']['steps']})"
            vals = (
                arm,
                life,
                r["crossings"],
                r["gate_passages"],
                r["larder_entries"],
                r["eats"],
                r["wasted_peeks"],
                r["fatigue_events"],
                r["revive_events"],
                r["stage_filtered_events"],
                r["out_of_context"],
                top,
            )
            print("  ".join(f"{str(v):>7}" for v in vals))
        print()

    def paired(key):
        d = np.array([rows["sib"][k][key] - rows["flat"][k][key] for k in rounds], dtype=float)
        se = d.std(ddof=1) / np.sqrt(len(d)) if len(d) > 1 else float("nan")
        return {
            "sib": [rows["sib"][k][key] for k in rounds],
            "flat": [rows["flat"][k][key] for k in rounds],
            "mean_diff": float(d.mean()) if len(d) else None,
            "se": float(se) if len(d) > 1 else None,
        }

    summary = {}
    for key, label in (
        ("eats", "full-chain eats (registered primary)"),
        ("gate_passages", "gate passages (0120 chains meter)"),
        ("crossings", "lap crossings"),
        ("wasted_peeks", "wasted peeks"),
        ("fatigue_events", "poisons created"),
        ("out_of_context", "out-of-context steps"),
    ):
        p = paired(key)
        summary[key] = p
        se = f"{p['se']:.2f}" if p["se"] is not None else "n/a"
        md = f"{p['mean_diff']:+.2f}" if p["mean_diff"] is not None else "n/a"
        print(f"{label:<38} sib {p['sib']}  flat {p['flat']}")
        print(f"{'':<38} sib−flat {md} ± {se} SE")
    sib_eats = sum(rows["sib"][k]["eats"] for k in rounds)
    print()
    print(
        "R1 as registered (sibling chains beyond spread above the 0120 sibling baseline of zero):",
        "PASS"
        if sib_eats > 0
        and summary["eats"]["mean_diff"]
        and summary["eats"]["se"]
        and abs(summary["eats"]["mean_diff"]) > summary["eats"]["se"]
        else "FAIL (as measured)",
    )
    out = {"rounds": rounds, "rows": rows, "paired": summary}
    if "--json" in sys.argv:
        Path(sys.argv[sys.argv.index("--json") + 1]).write_text(
            json.dumps(out, indent=1, default=int)
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
