"""Factored-actions rig — the dial world and the calibration walk.

The declared world (JOURNEY.md 2026-08-21, ladder as revised): B = 4
dials, m positions each, act = "set dial d to position p" (flat index
a = d*m + p), observation = per dial [position, target, match] scaled
to [-1, 1] (obs_dim = 12 at every rung), reach = full match, on which
the target redraws — the world's only novelty, so seeking matches is
drive behavior. Implements the kernel's EventSource seam; runs the
stock engine in curiosity + continuous mode, no new machinery.

    python dial.py calib [m] [n_cycles]   # flat arm, 24 seeds, one rung
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

from pra.config import Config
from pra.core.engine import Engine

RIG = Path(__file__).parent
B = 4
SEEDS = 24


class DialWorld:
    """EventSource: B dials x m positions; target redraws on full match.

    Draw order (fixed): reset draws positions dial-by-dial then the
    target; each redraw draws the full target vector, rejecting a
    pattern equal to the current dial state (a redraw must leave
    something to do).
    """

    def __init__(self, config: Config, rng: np.random.Generator):
        self.m = config.n_actions // B
        if config.n_actions != B * self.m or config.obs_dim != 3 * B:
            raise ValueError(
                f"dial world needs n_actions = {B}*m and obs_dim = {3 * B}, "
                f"got n_actions={config.n_actions}, obs_dim={config.obs_dim}"
            )
        self._rng = rng
        self._pos = np.zeros(B, dtype=np.int64)
        self._target = np.zeros(B, dtype=np.int64)
        self.total_steps = 0
        self.reach_steps: list[int] = []

    @property
    def n_actions(self) -> int:
        return B * self.m

    @property
    def obs_dim(self) -> int:
        return 3 * B

    def _scale(self, v: np.ndarray) -> np.ndarray:
        return 2.0 * v / (self.m - 1) - 1.0

    def _obs(self) -> np.ndarray:
        match = np.where(self._pos == self._target, 1.0, -1.0)
        return np.concatenate([self._scale(self._pos), self._scale(self._target), match])

    def _redraw_target(self) -> None:
        while True:
            t = self._rng.integers(0, self.m, size=B)
            if not np.array_equal(t, self._pos):
                self._target = t
                return

    def reset(self) -> np.ndarray:
        self._pos = self._rng.integers(0, self.m, size=B)
        self._redraw_target()
        return self._obs()

    def step(self, action: int) -> np.ndarray:
        d, p = divmod(int(action), self.m)
        self._pos[d] = p
        self.total_steps += 1
        if np.array_equal(self._pos, self._target):
            self.reach_steps.append(self.total_steps)
            self._redraw_target()
        return self._obs()

    # continuous mode carries world state in snapshots (feature 008)
    def state_dict(self) -> dict:
        return {
            "pos": self._pos.tolist(),
            "target": self._target.tolist(),
            "rng": self._rng.bit_generator.state,
            "total_steps": self.total_steps,
            "reach_steps": list(self.reach_steps),
        }

    def load_state_dict(self, state: dict) -> None:
        self._pos = np.array(state["pos"], dtype=np.int64)
        self._target = np.array(state["target"], dtype=np.int64)
        self._rng.bit_generator.state = state["rng"]
        self.total_steps = int(state["total_steps"])
        self.reach_steps = list(state["reach_steps"])


class OraclePolicy:
    """The ceiling instrument (trail, never a bar): perfect world
    knowledge, no learning — at each step set the first mismatched
    dial to its target. Reads the achievable reach rate per rung so
    arm retention can be judged against the world's own ceiling."""

    def __init__(self, m: int):
        self.m = m

    def select_action(self, context, rng) -> int:
        obs = np.asarray(context.observation)
        pos = np.rint((obs[0:B] + 1.0) * (self.m - 1) / 2.0).astype(int)
        tgt = np.rint((obs[B : 2 * B] + 1.0) * (self.m - 1) / 2.0).astype(int)
        for d in range(B):
            if pos[d] != tgt[d]:
                return d * self.m + int(tgt[d])
        return int(rng.integers(B * self.m))


def run_flat(seed: int, m: int, n_cycles: int, policy_mode: str = "curiosity") -> dict:
    cfg = Config(
        obs_dim=3 * B,
        n_actions=B * m,
        policy_mode="random" if policy_mode == "oracle" else policy_mode,
        episode_mode="continuous",
        n_cycles=n_cycles,
    )
    worlds: list[DialWorld] = []

    def factory(config: Config, rng: np.random.Generator) -> DialWorld:
        w = DialWorld(config, rng)
        worlds.append(w)
        return w

    policy = OraclePolicy(m) if policy_mode == "oracle" else None
    summary = Engine(cfg, world_factory=factory, policy=policy).run(seed)
    w = worlds[0]
    half = w.total_steps // 2
    back = sum(1 for s in w.reach_steps if s > half)
    return {
        "seed": seed,
        "m": m,
        "A": B * m,
        "steps": w.total_steps,
        "reaches": len(w.reach_steps),
        "reaches_back": back,
        "reach_per_1k_back": round(back / max(w.total_steps - half, 1) * 1000, 3),
        "pred_late": summary.pred_error_late,
        "map_frac": round(summary.mean_map_fraction, 4),
        "population": summary.final_population,
    }


def calib(m: int, n_cycles: int, policy_mode: str) -> None:
    arm = "flat" if policy_mode == "curiosity" else policy_mode
    out = RIG / f"calib-{arm}-m{m}-c{n_cycles}.jsonl"
    if out.exists():
        raise SystemExit(f"{out} exists — one reading per config; move it aside to re-run")
    rows = []
    with out.open("a") as f:
        for seed in range(SEEDS):
            row = run_flat(seed, m, n_cycles, policy_mode)
            rows.append(row)
            f.write(json.dumps(row) + "\n")
            print(json.dumps(row), flush=True)
    rates = sorted(r["reach_per_1k_back"] for r in rows)
    summary = {
        "arm": arm,
        "m": m,
        "n_cycles": n_cycles,
        "seeds": SEEDS,
        "reach_per_1k_back_min": rates[0],
        "reach_per_1k_back_median": rates[SEEDS // 2],
        "reach_per_1k_back_max": rates[-1],
        "seeds_with_back_reaches": sum(1 for r in rows if r["reaches_back"] > 0),
    }
    with out.open("a") as f:
        f.write(json.dumps(summary) + "\n")
    print(f"CALIB {json.dumps(summary)}", flush=True)


def main() -> int:
    phase = sys.argv[1] if len(sys.argv) > 1 else ""
    if phase == "calib":
        m = int(sys.argv[2]) if len(sys.argv) > 2 else 3
        n_cycles = int(sys.argv[3]) if len(sys.argv) > 3 else 18
        policy_mode = sys.argv[4] if len(sys.argv) > 4 else "curiosity"
        calib(m, n_cycles, policy_mode)
        return 0
    raise SystemExit("usage: dial.py calib [m] [n_cycles] [curiosity|random]")


if __name__ == "__main__":
    raise SystemExit(main())
