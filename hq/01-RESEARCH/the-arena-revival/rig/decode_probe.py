"""H0(a): the position-decode probe and the aliasing exhibit.

Reads the recorded flat-rig lives (mc/<arm>-life<N>.npz: obs 73-wide,
pos, food) and asks the registered question: does a LINEAR readout
decode the chain's lap index from the body's own observation, on the
decision span, better than chance?

Protocol, operationalized exactly as registered in ../arena.md:

- **Span:** steps at loop level (feet y < -59) on the ring perimeter
  (cell x in 0..9, z in 0..6, perimeter only) — the junction included,
  the branch/larder/exit excluded (the peek is a priced part of the
  task, not a leak).
- **Labels (amendment 4):** lap-line crossings since the last larder
  entry + 1, UNCAPPED to 4 (4 = post-third-crossing, the gate-open
  turn-in approach), reconstructed from the pos trace with the command
  blocks' exact two-zone logic (cross-checked against the world's own
  scoreboard by the life runner).
- **The verdict reads on the two aliased decision pairs** — 2v3 (the
  full-ring laps) and 3v4 (the junction approach) — each a binary
  linear readout on those labels' steps restricted to the cell support
  BOTH labels visit, so route topology cannot cheaply separate what
  geometry shares. The full multi-class probe is reported as context:
  its excess over control is the half-ring topology of label 1 (the
  exit drop lands mid-ring), explained and on record, not sensing.
- **Probe:** multinomial logistic regression (a linear readout) on
  per-channel standardized obs, trained with fixed-seed full-batch
  gradient descent; held-out accuracy via 5-fold grouped CV, groups =
  chains (never split a chain across train/test).
- **Chance band:** the same probe on 20 within-chain label
  permutations — preserves class priors and temporal blockiness,
  breaks only the true mapping. PASS = each pair's true accuracy <=
  its control mean + 2 SD. Raw numbers recorded either way.
- **Aliasing exhibit:** per-channel |mean lap-3 − mean lap-4| on the
  junction approach (cells (9,1),(9,2),(9,3)), top channels raw.

Usage: python decode_probe.py [arm]   (default: flat)
Writes decode-report.json beside itself.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
MC = HERE / "mc"

N_LAPS = 3
MAX_LABEL = 4  # 4 = post-third-crossing, the turn-in approach (amendment 4)
FOLDS = 5
CONTROL_DRAWS = 20
GD_ITERS = 400
GD_LR = 0.5
SEED = 1

CHANNEL_NAMES = (
    [f"pose.{n}" for n in ("x", "z", "y", "sin_yaw", "cos_yaw")]
    + ["vitals.health", "vitals.food"]
    + [f"env.{n}" for n in ("light", "sin_time", "cos_time", "rain")]
    + [f"blocks.{n}" for n in ("solid_ahead", "solid_eye", "drop_ahead")]
    + ["mining.progress"]
    + [f"pocket.{n}" for n in ("total", "kinds", "placeable", "other")]
    + [f"hand.{n}" for n in ("present", "placeable", "edible", "count", "sig0", "sig1", "sig2")]
    + [
        f"grid.{n}"
        for n in (
            "staged",
            "offer",
            "offer_placeable",
            "offer_count",
            "offer_sig0",
            "offer_sig1",
            "offer_sig2",
        )
    ]
    + [f"drops.{n}" for n in ("present", "sin_b", "cos_b", "dist", "count", "sig0", "sig1", "sig2")]
    + [f"glance.s{k}_{n}" for k in range(8) for n in ("dist", "sig0", "sig1", "sig2")]
)


def on_ring(x: float, z: float) -> bool:
    cx, cz = math.floor(x), math.floor(z)
    if not (0 <= cx <= 9 and 0 <= cz <= 6):
        return False
    return cx in (0, 9) or cz in (0, 6)


def label_steps(pos: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Per-step (lap_label 1..4 or 0=off-span, chain_id, span_mask) from the
    pos trace, replicating the world's own counter logic."""
    n = len(pos)
    labels = np.zeros(n, dtype=np.int64)
    chains = np.zeros(n, dtype=np.int64)
    span = np.zeros(n, dtype=bool)
    arm_a = arm_b = counted = 0
    crossings = 0
    chain_id = 0
    in_larder = False
    for i in range(n):
        x, y, z = float(pos[i][0]), float(pos[i][1]), float(pos[i][2])
        a = math.floor(x) == 0 and math.floor(z) == 3 and y < -59
        b = math.floor(x) == 0 and math.floor(z) == 2 and y < -59
        if a and not arm_b:
            arm_a = 1
        if b and arm_a and not counted:
            crossings += 1
            counted = 1
        if b and not arm_a and not counted:
            arm_b = 1
        if not a and not b:
            arm_a = arm_b = counted = 0
        larder = 12 <= x < 19 and 12 <= z < 19 and y > -58.5
        if larder and not in_larder:
            chain_id += 1
            crossings = 0
        in_larder = larder
        if y < -59 and on_ring(x, z):
            span[i] = True
            labels[i] = min(crossings + 1, MAX_LABEL)
            chains[i] = chain_id
    return labels, chains, span


def fit_softmax(x: np.ndarray, y: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Full-batch multinomial logistic regression; returns weights (d+1, k)."""
    n, d = x.shape
    xb = np.hstack([x, np.ones((n, 1))])
    k = int(y.max())
    w = rng.normal(0, 0.01, size=(d + 1, k))
    onehot = np.eye(k)[y - 1]
    for _ in range(GD_ITERS):
        logits = xb @ w
        logits -= logits.max(axis=1, keepdims=True)
        p = np.exp(logits)
        p /= p.sum(axis=1, keepdims=True)
        grad = xb.T @ (p - onehot) / n
        w -= GD_LR * grad
    return w


def accuracy(w: np.ndarray, x: np.ndarray, y: np.ndarray) -> float:
    xb = np.hstack([x, np.ones((len(x), 1))])
    return float((np.argmax(xb @ w, axis=1) + 1 == y).mean())


def grouped_cv(obs: np.ndarray, y: np.ndarray, groups: np.ndarray, seed: int) -> float:
    rng = np.random.default_rng(seed)
    uniq = np.unique(groups)
    order = rng.permutation(len(uniq))
    accs = []
    for fold in range(FOLDS):
        test_groups = set(uniq[order[fold::FOLDS]].tolist())
        test = np.isin(groups, list(test_groups))
        if test.all() or not test.any():
            continue
        mu = obs[~test].mean(axis=0)
        sd = obs[~test].std(axis=0) + 1e-9
        xtr, xte = (obs[~test] - mu) / sd, (obs[test] - mu) / sd
        w = fit_softmax(xtr, y[~test], rng)
        accs.append(accuracy(w, xte, y[test]))
    return float(np.mean(accs))


def permuted_labels(y: np.ndarray, groups: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    out = y.copy()
    values = np.unique(y)
    for g in np.unique(groups):
        perm = rng.permutation(values)
        mapping = dict(zip(values.tolist(), perm.tolist(), strict=True))
        mask = groups == g
        out[mask] = np.array([mapping[v] for v in y[mask]])
    return out


def junction_gap(obs: np.ndarray, pos: np.ndarray, y: np.ndarray, span: np.ndarray) -> list:
    window = span & np.array([math.floor(p[0]) == 9 and math.floor(p[2]) in (1, 2, 3) for p in pos])
    lap1 = obs[window & (y == 3)]
    lap3 = obs[window & (y == 4)]
    if not len(lap1) or not len(lap3):
        return []
    gap = np.abs(lap1.mean(axis=0) - lap3.mean(axis=0))
    top = np.argsort(gap)[::-1][:5]
    return [{"channel": CHANNEL_NAMES[int(i)], "gap": round(float(gap[i]), 4)} for i in top]


def cells_of(pos: np.ndarray) -> np.ndarray:
    return np.array([[math.floor(p[0]), math.floor(p[2])] for p in pos], dtype=np.int64)


def pair_read(
    pair: tuple[int, int],
    obs: np.ndarray,
    y: np.ndarray,
    groups: np.ndarray,
    cells: np.ndarray,
) -> dict:
    """The decision-pair probe (amendment 4): binary linear readout on the
    two labels' steps, restricted to the cell support BOTH labels visit —
    route topology cannot cheaply separate what geometry shares."""
    a, b = pair
    mask = (y == a) | (y == b)
    cell_keys = cells[:, 0] * 100 + cells[:, 1]
    support = set(np.unique(cell_keys[mask & (y == a)])) & set(
        np.unique(cell_keys[mask & (y == b)])
    )
    keep = mask & np.isin(cell_keys, list(support))
    yy = np.where(y[keep] == a, 1, 2)
    oo, gg = obs[keep], groups[keep]
    counts = {str(a): int((yy == 1).sum()), str(b): int((yy == 2).sum())}
    majority = max(counts.values()) / max(len(yy), 1)
    true_acc = grouped_cv(oo, yy, gg, SEED)
    rng = np.random.default_rng(SEED + 10 * a + b)
    control = [
        grouped_cv(oo, permuted_labels(yy, gg, rng), gg, SEED + 100 + i)
        for i in range(CONTROL_DRAWS)
    ]
    c_mean, c_sd = float(np.mean(control)), float(np.std(control))
    return {
        "pair": f"{a}v{b}",
        "steps": int(len(yy)),
        "support_cells": len(support),
        "label_counts": counts,
        "majority_rate": round(majority, 4),
        "true_accuracy": round(true_acc, 4),
        "control_mean": round(c_mean, 4),
        "control_sd": round(c_sd, 4),
        "pass": bool(true_acc <= c_mean + 2 * c_sd),
    }


def main() -> int:
    arm = sys.argv[1] if len(sys.argv) > 1 else "flat"
    lives = sorted(MC.glob(f"{arm}-life*.npz"))
    if not lives:
        raise SystemExit(f"no recorded lives at mc/{arm}-life*.npz — run lc_runner.py lives first")
    all_obs, all_y, all_g, all_pos, exhibits = [], [], [], [], []
    chain_base = 0
    for path in lives:
        data = np.load(path)
        obs, pos = data["obs"], data["pos"]
        n = min(len(obs), len(pos))
        obs, pos = obs[:n], pos[:n]
        labels, chains, span = label_steps(pos)
        exhibits.append(junction_gap(obs, pos, labels, span))
        keep = span
        all_obs.append(obs[keep])
        all_y.append(labels[keep])
        all_g.append(chains[keep] + chain_base)
        all_pos.append(pos[keep])
        chain_base += int(chains.max()) + 1
    obs = np.concatenate(all_obs).astype(np.float64)
    y = np.concatenate(all_y)
    groups = np.concatenate(all_g)
    cells = cells_of(np.concatenate(all_pos))
    counts = {int(k): int((y == k).sum()) for k in range(1, MAX_LABEL + 1)}
    majority = max(counts.values()) / max(len(y), 1)
    # context read: the full multi-class probe (the original registered form)
    true_acc = grouped_cv(obs, y, groups, SEED)
    rng = np.random.default_rng(SEED + 1)
    control = [
        grouped_cv(obs, permuted_labels(y, groups, rng), groups, SEED + 2 + i)
        for i in range(CONTROL_DRAWS)
    ]
    c_mean, c_sd = float(np.mean(control)), float(np.std(control))
    # the verdict: the two aliased decision pairs (amendment 4)
    pairs = [pair_read(p, obs, y, groups, cells) for p in ((2, 3), (3, 4))]
    verdict = all(p["pass"] for p in pairs)
    report = {
        "arm": arm,
        "lives": [p.name for p in lives],
        "span_steps": int(len(y)),
        "chains_in_span": int(len(np.unique(groups))),
        "label_counts": counts,
        "majority_rate": round(majority, 4),
        "context_multiclass": {
            "true_accuracy": round(true_acc, 4),
            "control_mean": round(c_mean, 4),
            "control_sd": round(c_sd, 4),
        },
        "decision_pairs": pairs,
        "rule": "PASS if each aliased pair's true accuracy <= its control mean + 2*sd",
        "h0a_pass": bool(verdict),
        "junction_gap_top5_per_life": exhibits,
    }
    (HERE / "decode-report.json").write_text(json.dumps(report, indent=1))
    print(json.dumps(report, indent=1))
    print("H0(a)", "PASS" if verdict else "FAIL", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
