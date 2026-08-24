"""Meter table over calib jsonl rows: acceptance (back half), seeds
accepting, conformity (violations/step), and the tier-2 instruments.

    python summarize.py <file.jsonl> [...]
"""

import json
import sys

import numpy as np


def load(path):
    rows = []
    with open(path) as f:
        for line in f:
            r = json.loads(line)
            if "seed" in r:
                rows.append(r)
    return rows


def med(xs):
    return float(np.median(xs)) if xs else float("nan")


for path in sys.argv[1:]:
    rows = load(path)
    if not rows:
        continue
    acc = [r["accept_per_1k_back"] for r in rows]
    conf = [r["violations"] / r["steps"] for r in rows]
    n_acc = sum(1 for r in rows if r["accepts_back"] > 0)
    out = {
        "file": path.split("/")[-1],
        "n": len(rows),
        "acc_med": round(med(acc), 3),
        "acc_min": round(min(acc), 3),
        "acc_max": round(max(acc), 3),
        "seeds_acc": n_acc,
        "conf_med": round(med(conf), 4),
    }
    if "arb_t2_share" in rows[0]:
        out["arb_med"] = round(med([r["arb_t2_share"] for r in rows]), 4)
        out["t2_pop_med"] = med([r["t2_population"] for r in rows])
        out["t2_map_med"] = round(med([r["t2_map_rate"] for r in rows]), 4)
    print(json.dumps(out))
