"""Sequence-encoding rig — the echo-teacher world and the encoding arms.

The declared world (JOURNEY.md 2026-08-23): the subject emits one of
m=4 tokens per step; a scripted teacher holds a target structure —
R(P): a seeded repeating template with phase, acceptance after
T = 2P conforming tokens, reset-on-violation; C(n): AⁿBⁿ with seeded
roles — and answers only through the observation (a progress channel
and a pulse channel). The sequence-so-far reaches the body through a
declared encoding: W-K (last K own emissions), DK (recency sum,
λ = 0.5), or WD (window-4 + decay). Kernel untouched; flat actions.

    python seq.py calib R 2 W2 [curiosity|random|oracle] [n_cycles]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

from pra.config import Config
from pra.core.engine import Engine

RIG = Path(__file__).parent
M = 4
SEEDS = 24
LAMBDA = 0.5

ENCODINGS = {"W1": 1, "W2": 2, "W4": 4, "W8": 8, "DK": 0, "WD": 4}


def obs_dim_of(encoding: str) -> int:
    k = ENCODINGS[encoding]
    d = M if encoding in ("DK", "WD") else 0
    return k + d + 2


class EchoWorld:
    """EventSource: emit-token world with a scripted teacher's voice."""

    def __init__(
        self,
        config: Config,
        rng: np.random.Generator,
        family: str,
        rung: int,
        encoding: str,
    ):
        if config.n_actions != M or config.obs_dim != obs_dim_of(encoding):
            raise ValueError(
                f"echo world needs n_actions={M}, obs_dim={obs_dim_of(encoding)} "
                f"for {encoding}, got {config.n_actions}/{config.obs_dim}"
            )
        self._rng = rng
        self.family = family
        self.rung = int(rung)
        self.encoding = encoding
        self.K = ENCODINGS[encoding]
        self.has_decay = encoding in ("DK", "WD")
        self.T = 2 * self.rung
        self._template = np.zeros(self.rung, dtype=np.int64)
        self._roles = (0, 1)
        self._j = 0
        self._pulse = 0.0
        self._window = np.zeros(max(self.K, 1), dtype=np.int64) - 1  # -1 = empty
        self._decay = np.zeros(M)
        self.total_steps = 0
        self.accept_steps: list[int] = []
        self.violations = 0

    @property
    def n_actions(self) -> int:
        return M

    @property
    def obs_dim(self) -> int:
        return obs_dim_of(self.encoding)

    def _reseed(self) -> None:
        if self.family == "R":
            self._template = self._rng.integers(0, M, size=self.rung)
        else:  # C: draw two distinct role tokens
            a = int(self._rng.integers(M))
            b = int(self._rng.integers(M - 1))
            self._roles = (a, b if b < a else b + 1)
        self._j = 0

    def expected(self) -> int:
        if self.family == "R":
            return int(self._template[self._j % self.rung])
        return self._roles[0] if self._j < self.rung else self._roles[1]

    def _obs(self) -> np.ndarray:
        parts = []
        if self.K > 0:
            w = np.where(self._window < 0, 0.0, 2.0 * self._window / (M - 1) - 1.0)
            parts.append(w[-self.K :] if self.K > 0 else w[:0])
        if self.has_decay:
            parts.append(self._decay * (1.0 - LAMBDA))
        progress = 2.0 * (self._j / self.T) - 1.0
        parts.append(np.array([progress, self._pulse]))
        return np.concatenate(parts)

    def reset(self) -> np.ndarray:
        self._reseed()
        self._pulse = 0.0
        self._window[:] = -1
        self._decay[:] = 0.0
        return self._obs()

    def step(self, action: int) -> np.ndarray:
        token = int(action)
        self.total_steps += 1
        if token == self.expected():
            self._j += 1
            self._pulse = 0.0
            if self._j >= self.T:
                self.accept_steps.append(self.total_steps)
                self._pulse = 1.0
                self._reseed()
        else:
            self._j = 0
            self._pulse = -1.0
            self.violations += 1
        if self.K > 0:
            self._window = np.roll(self._window, -1)
            self._window[-1] = token
        if self.has_decay:
            self._decay = LAMBDA * self._decay
            self._decay[token] += 1.0
        return self._obs()

    def state_dict(self) -> dict:
        return {
            "template": self._template.tolist(),
            "roles": list(self._roles),
            "j": self._j,
            "pulse": self._pulse,
            "window": self._window.tolist(),
            "decay": self._decay.tolist(),
            "rng": self._rng.bit_generator.state,
            "total_steps": self.total_steps,
            "accept_steps": list(self.accept_steps),
            "violations": self.violations,
        }

    def load_state_dict(self, state: dict) -> None:
        self._template = np.array(state["template"], dtype=np.int64)
        self._roles = tuple(state["roles"])
        self._j = int(state["j"])
        self._pulse = float(state["pulse"])
        self._window = np.array(state["window"], dtype=np.int64)
        self._decay = np.array(state["decay"])
        self._rng.bit_generator.state = state["rng"]
        self.total_steps = int(state["total_steps"])
        self.accept_steps = list(state["accept_steps"])
        self.violations = int(state["violations"])


class SeqRecordingPolicy:
    """The pulse instrument (Amendment 1): wraps the curiosity policy
    and records the frames' per-channel one-step prediction error —
    the PULSE channel's error is the encoding-information probe,
    independent of task completion. Read-only; the inner policy's
    draw order is untouched."""

    def __init__(self, inner, obs_dim: int):
        self.inner = inner
        self._pred: np.ndarray | None = None
        self.err_sum = np.zeros(obs_dim)
        self.n = 0
        self.n_missing = 0

    def select_action(self, context, rng) -> int:
        obs = np.asarray(context.observation, dtype=float)
        if self._pred is not None:
            self.err_sum += np.abs(self._pred - obs)
            self.n += 1
        a = self.inner.select_action(context, rng)
        pred = context.predict_decoded(a)
        if pred is None:
            self._pred = None
            self.n_missing += 1
        else:
            self._pred = np.array(pred, dtype=float, copy=True)
        return a


class OracleProducer:
    """The ceiling instrument: emits the phase-correct token, reading
    the target from the world instance itself (never from the subject's
    observation — the oracle is an instrument, not a contestant)."""

    def __init__(self, world_ref: list):
        self.world_ref = world_ref

    def select_action(self, context, rng) -> int:
        return self.world_ref[0].expected()


def run_arm(
    seed: int,
    family: str,
    rung: int,
    encoding: str,
    n_cycles: int,
    policy_mode: str = "curiosity",
) -> dict:
    cfg = Config(
        obs_dim=obs_dim_of(encoding),
        n_actions=M,
        policy_mode="curiosity"
        if policy_mode in ("record", "stack", "stack-lo", "stack-nc")
        else ("random" if policy_mode in ("oracle", "random") else policy_mode),
        episode_mode="continuous",
        n_cycles=n_cycles,
        event_head_eta=0.5 if policy_mode.startswith("stack") else 0.0,
    )
    worlds: list[EchoWorld] = []

    def factory(config: Config, rng: np.random.Generator) -> EchoWorld:
        w = EchoWorld(config, rng, family, rung, encoding)
        worlds.append(w)
        return w

    policy = OracleProducer(worlds) if policy_mode == "oracle" else None
    rec = None
    inner = None
    if policy_mode == "record":
        from pra.action.policy import CuriosityLookaheadPolicy, PolicyParams

        rec = SeqRecordingPolicy(
            CuriosityLookaheadPolicy(PolicyParams.from_config(cfg)), cfg.obs_dim
        )
        policy = rec
    if policy_mode.startswith("stack"):
        from pra.action.policy import CompletionItchPolicy, PolicyParams

        kappa = 0.05 if policy_mode == "stack-lo" else 0.25
        kc = 0.0 if policy_mode == "stack-nc" else 0.1
        inner = CompletionItchPolicy(
            PolicyParams.from_config(cfg),
            kappa=kappa,
            progress_index=cfg.obs_dim - 2,
            pocket_index=cfg.obs_dim - 1,
            commit_kappa=kc,
            explore_defers_holds=kc > 0.0,
        )
        rec = SeqRecordingPolicy(inner, cfg.obs_dim)
        policy = rec
    summary = Engine(cfg, world_factory=factory, policy=policy).run(seed)
    w = worlds[0]
    half = w.total_steps // 2
    back = sum(1 for s in w.accept_steps if s > half)
    return {
        "seed": seed,
        "family": family,
        "rung": rung,
        "encoding": encoding,
        "policy": policy_mode,
        "steps": w.total_steps,
        "accepts": len(w.accept_steps),
        "accepts_back": back,
        "accept_per_1k_back": round(back / max(w.total_steps - half, 1) * 1000, 3),
        "violations": w.violations,
        "pred_late": summary.pred_error_late,
        "population": summary.final_population,
        **(
            {
                "pulse_err": round(float(rec.err_sum[-1] / max(rec.n, 1)), 6),
                "progress_err": round(float(rec.err_sum[-2] / max(rec.n, 1)), 6),
                "enc_err": round(float(rec.err_sum[:-2].mean() / max(rec.n, 1)), 6),
                "rec_n": rec.n,
            }
            if rec is not None
            else {}
        ),
        **(
            {
                "completions": inner.completions_fired,
                "false_completions": inner.false_completions,
                "progress_pred_ema": round(float(inner.progress_pred_error_ema), 6),
            }
            if inner is not None
            else {}
        ),
    }


def calib(family: str, rung: int, encoding: str, policy_mode: str, n_cycles: int) -> None:
    tag = f"{family}{rung}-{encoding}-{policy_mode}"
    out = RIG / f"calib-{tag}-c{n_cycles}.jsonl"
    if out.exists():
        raise SystemExit(f"{out} exists — one reading per config; move it aside to re-run")
    rows = []
    with out.open("a") as f:
        for seed in range(SEEDS):
            row = run_arm(seed, family, rung, encoding, n_cycles, policy_mode)
            rows.append(row)
            f.write(json.dumps(row) + "\n")
            print(json.dumps(row), flush=True)
    rates = sorted(r["accept_per_1k_back"] for r in rows)
    summary = {
        "tag": tag,
        "seeds": SEEDS,
        "accept_per_1k_back_min": rates[0],
        "accept_per_1k_back_median": rates[SEEDS // 2],
        "accept_per_1k_back_max": rates[-1],
        "seeds_with_back_accepts": sum(1 for r in rows if r["accepts_back"] > 0),
    }
    with out.open("a") as f:
        f.write(json.dumps(summary) + "\n")
    print(f"CALIB {json.dumps(summary)}", flush=True)


def main() -> int:
    phase = sys.argv[1] if len(sys.argv) > 1 else ""
    if phase == "calib":
        family = sys.argv[2]
        rung = int(sys.argv[3])
        encoding = sys.argv[4]
        policy_mode = sys.argv[5] if len(sys.argv) > 5 else "curiosity"
        n_cycles = int(sys.argv[6]) if len(sys.argv) > 6 else 18
        if family not in ("R", "C") or encoding not in ENCODINGS:
            raise SystemExit(f"usage: seq.py calib R|C <rung> {'|'.join(ENCODINGS)} [policy] [c]")
        calib(family, rung, encoding, policy_mode, n_cycles)
        return 0
    raise SystemExit("usage: seq.py calib <family> <rung> <encoding> [policy] [n_cycles]")


if __name__ == "__main__":
    raise SystemExit(main())
