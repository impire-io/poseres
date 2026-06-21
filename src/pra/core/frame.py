"""Homogeneous batched frame kernel (PRA-01 §5/§7.2, data-model §3, research R1/R2).

A *FrameGroup* stacks every frame of one ``dim`` along a leading frame axis and
runs encode/decode/transition/learn as batched ``np.einsum`` ops over that axis —
there is **no per-frame branching**; a frame that does not elect to map simply has
its weight updates masked to zero. Frames of different ``dim`` live in different
groups because their tensor shapes differ. The *FrameStore* owns the groups,
births frames (drawing weights in the v4 oracle's exact order so the single seeded
generator is consumed identically), evicts them, and runs one online step batched
across all groups.

The math is a faithful, vectorized port of ``design/validate/pra_sim_v3.Frame``
(the behavioral oracle): a single-hidden-layer encoder, decoder, and per-action
transition, trained with clipped one-layer backprop. ``tests/unit/
test_batched_equivalence.py`` proves the batched path matches a straightforward
per-frame reference.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from pra.config import Config
from pra.core.contracts import FrameResult, FrameState, SensorimotorEvent

__all__ = ["FrameGroup", "FrameStore", "StepStats"]

_EPS = 1e-6


@dataclass
class StepStats:
    """Aggregates produced by one batched online step."""

    mapped: int
    alive: int
    elect_pred_errors: list[float]  # honest obs-space pred error of electing frames


class FrameGroup:
    """All frames of a single dimension ``D``, weights stacked on a leading axis."""

    def __init__(self, dim: int, obs_dim: int, hidden: int, n_actions: int):
        self.dim = dim
        self.obs_dim = obs_dim
        self.H = hidden
        self.A = n_actions
        F = 0
        D, H, Od, A = dim, hidden, obs_dim, n_actions
        # identity / survival records
        self.frame_ids = np.zeros(F, dtype=np.int64)
        self.is_candidate = np.zeros(F, dtype=bool)
        self.age_cycles = np.zeros(F, dtype=np.int64)
        self.recon_err_ema = np.zeros(F, dtype=np.float64)
        self.pred_err_ema = np.zeros(F, dtype=np.float64)
        self.effort_ema = np.zeros(F, dtype=np.float64)
        # encoder
        self.W1 = np.zeros((F, H, Od))
        self.b1 = np.zeros((F, H))
        self.W2 = np.zeros((F, D, H))
        self.b2 = np.zeros((F, D))
        # decoder
        self.Dc1 = np.zeros((F, H, D))
        self.dc1 = np.zeros((F, H))
        self.Dc2 = np.zeros((F, Od, H))
        self.dc2 = np.zeros((F, Od))
        # transition (per action)
        self.T1 = np.zeros((F, A, H, D))
        self.tb1 = np.zeros((F, A, H))
        self.T2 = np.zeros((F, A, D, H))
        self.tb2 = np.zeros((F, A, D))

    @property
    def size(self) -> int:
        return int(self.frame_ids.shape[0])

    # ---- membership ----------------------------------------------------------
    def add_frame(
        self, frame_id: int, ema_init: float, scale: float, rng: np.random.Generator
    ) -> None:
        """Append one frame, drawing its weights in the v4 Frame.__init__ order."""
        D, H, Od, A = self.dim, self.H, self.obs_dim, self.A
        # Draw order is load-bearing for determinism (PRA-01 §7.1).
        W1 = rng.standard_normal((H, Od)) * scale
        W2 = rng.standard_normal((D, H)) * scale
        Dc1 = rng.standard_normal((H, D)) * scale
        Dc2 = rng.standard_normal((Od, H)) * scale
        T1 = rng.standard_normal((A, H, D)) * scale
        T2 = rng.standard_normal((A, D, H)) * scale

        self.frame_ids = np.append(self.frame_ids, np.int64(frame_id))
        self.is_candidate = np.append(self.is_candidate, True)
        self.age_cycles = np.append(self.age_cycles, np.int64(0))
        self.recon_err_ema = np.append(self.recon_err_ema, float(ema_init))
        self.pred_err_ema = np.append(self.pred_err_ema, float(ema_init))
        self.effort_ema = np.append(self.effort_ema, 0.0)
        self.W1 = np.concatenate([self.W1, W1[None]], axis=0)
        self.b1 = np.concatenate([self.b1, np.zeros((1, H))], axis=0)
        self.W2 = np.concatenate([self.W2, W2[None]], axis=0)
        self.b2 = np.concatenate([self.b2, np.zeros((1, D))], axis=0)
        self.Dc1 = np.concatenate([self.Dc1, Dc1[None]], axis=0)
        self.dc1 = np.concatenate([self.dc1, np.zeros((1, H))], axis=0)
        self.Dc2 = np.concatenate([self.Dc2, Dc2[None]], axis=0)
        self.dc2 = np.concatenate([self.dc2, np.zeros((1, Od))], axis=0)
        self.T1 = np.concatenate([self.T1, T1[None]], axis=0)
        self.tb1 = np.concatenate([self.tb1, np.zeros((1, A, H))], axis=0)
        self.T2 = np.concatenate([self.T2, T2[None]], axis=0)
        self.tb2 = np.concatenate([self.tb2, np.zeros((1, A, D))], axis=0)

    def remove_rows(self, rows: np.ndarray) -> None:
        keep = np.ones(self.size, dtype=bool)
        keep[rows] = False
        for name in (
            "frame_ids",
            "is_candidate",
            "age_cycles",
            "recon_err_ema",
            "pred_err_ema",
            "effort_ema",
            "W1",
            "b1",
            "W2",
            "b2",
            "Dc1",
            "dc1",
            "Dc2",
            "dc2",
            "T1",
            "tb1",
            "T2",
            "tb2",
        ):
            setattr(self, name, getattr(self, name)[keep])

    # ---- forward maps (batched over the frame axis) --------------------------
    def encode(self, obs: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        h = np.tanh(np.einsum("fho,o->fh", self.W1, obs) + self.b1)
        pose = np.einsum("fdh,fh->fd", self.W2, h) + self.b2
        return pose, h

    def reconstruct(self, pose: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        hd = np.tanh(np.einsum("fhd,fd->fh", self.Dc1, pose) + self.dc1)
        recon = np.einsum("foh,fh->fo", self.Dc2, hd) + self.dc2
        return recon, hd

    def predict_next(self, pose: np.ndarray, a: int) -> tuple[np.ndarray, np.ndarray]:
        h = np.tanh(np.einsum("fhd,fd->fh", self.T1[:, a], pose) + self.tb1[:, a])
        pred = np.einsum("fdh,fh->fd", self.T2[:, a], h) + self.tb2[:, a]
        return pred, h

    def fit_quality(
        self, obs: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        pose, h = self.encode(obs)
        recon, hd = self.reconstruct(pose)
        fit = np.linalg.norm(recon - obs, axis=1) / (np.linalg.norm(obs) + _EPS)
        return fit, pose, h, recon, hd

    def honest_pred_err(self, prev_obs: np.ndarray, a: int, obs: np.ndarray) -> np.ndarray:
        """Obs-space prediction error with current weights (PRA-01 §5.2)."""
        ppose, _ = self.encode(prev_obs)
        pnext, _ = self.predict_next(ppose, a)
        pobs, _ = self.reconstruct(pnext)
        return np.linalg.norm(pobs - obs, axis=1) / (np.linalg.norm(obs) + _EPS)

    def effort(self, prev_obs: np.ndarray, a: int) -> np.ndarray:
        ppose, _ = self.encode(prev_obs)
        pnext, _ = self.predict_next(ppose, a)
        return np.linalg.norm(pnext - ppose, axis=1)

    # ---- learning (clipped one-layer backprop, masked by ``elect``) ----------
    def learn_placement(
        self,
        obs: np.ndarray,
        pose: np.ndarray,
        h: np.ndarray,
        recon: np.ndarray,
        hd: np.ndarray,
        elect: np.ndarray,
        lr: float,
        clip: float,
    ) -> None:
        m = elect.astype(np.float64)
        m1 = m[:, None]
        m2 = m[:, None, None]
        e = recon - obs
        gD2 = np.clip(np.einsum("fo,fh->foh", e, hd), -clip, clip)
        ghd = np.einsum("foh,fo->fh", self.Dc2, e) * (1.0 - hd**2)
        gD1 = np.clip(np.einsum("fh,fd->fhd", ghd, pose), -clip, clip)
        self.Dc2 -= lr * gD2 * m2
        self.dc2 -= lr * np.clip(e, -clip, clip) * m1
        self.Dc1 -= lr * gD1 * m2
        self.dc1 -= lr * np.clip(ghd, -clip, clip) * m1
        gpose = np.einsum("fhd,fh->fd", self.Dc1, ghd)  # uses updated Dc1 (matches v4)
        gW2 = np.clip(np.einsum("fd,fh->fdh", gpose, h), -clip, clip)
        ghe = np.einsum("fdh,fd->fh", self.W2, gpose) * (1.0 - h**2)  # uses current W2
        gW1 = np.clip(np.einsum("fh,o->fho", ghe, obs), -clip, clip)
        self.W2 -= lr * gW2 * m2
        self.b2 -= lr * np.clip(gpose, -clip, clip) * m1
        self.W1 -= lr * gW1 * m2
        self.b1 -= lr * np.clip(ghe, -clip, clip) * m1

    def learn_transition(
        self,
        prev_obs: np.ndarray,
        a: int,
        next_obs: np.ndarray,
        effort_only: bool,
        elect: np.ndarray,
        lr: float,
        clip: float,
    ) -> None:
        m = elect.astype(np.float64)
        m1 = m[:, None]
        m2 = m[:, None, None]
        p, _ = self.encode(prev_obs)
        nxt, _ = self.encode(next_obs)
        pred, h = self.predict_next(p, a)
        target = np.zeros_like(nxt) if effort_only else nxt
        e = pred - target
        gT2 = np.clip(np.einsum("fd,fh->fdh", e, h), -clip, clip)
        gh = np.einsum("fdh,fd->fh", self.T2[:, a], e) * (1.0 - h**2)
        gT1 = np.clip(np.einsum("fh,fd->fhd", gh, p), -clip, clip)
        self.T2[:, a] -= lr * gT2 * m2
        self.tb2[:, a] -= lr * np.clip(e, -clip, clip) * m1
        self.T1[:, a] -= lr * gT1 * m2
        self.tb1[:, a] -= lr * np.clip(gh, -clip, clip) * m1


class FrameStore:
    """Owns the ``dim``-grouped FrameGroups; the Engine drives it.

    Implements the Bus's ``FrameProcessor`` protocol (``results_for``) so the
    delivery seam can return per-frame results without the Engine allocating a
    FrameResult per frame in its hot loop.
    """

    def __init__(self, config: Config, rng: np.random.Generator):
        self.config = config
        self.rng = rng
        self._groups: dict[int, FrameGroup] = {}
        self._next_id = 0
        self._fit_gate = float(config.fit_gate)
        self._lr = float(config.learning_rate)
        self._clip = float(config.gradient_clip)
        self._decay = float(config.ema_decay)
        self._scale = float(config.init_weight_scale)

    # ---- population ----------------------------------------------------------
    @property
    def population_size(self) -> int:
        return sum(g.size for g in self._groups.values())

    def dims_alive(self) -> list[int]:
        dims: list[int] = []
        for d, g in self._groups.items():
            dims.extend([d] * g.size)
        return sorted(dims)

    def _group_for(self, dim: int) -> FrameGroup:
        g = self._groups.get(dim)
        if g is None:
            g = FrameGroup(dim, self.config.obs_dim, self.config.hidden_size, self.config.n_actions)
            self._groups[dim] = g
        return g

    def birth(self, dim: int, ema_init: float) -> int:
        frame_id = self._next_id
        self._next_id += 1
        self._group_for(dim).add_frame(frame_id, ema_init, self._scale, self.rng)
        return frame_id

    def evict(self, frame_ids: list[int]) -> None:
        targets = set(frame_ids)
        if not targets:
            return
        for dim in list(self._groups):
            g = self._groups[dim]
            mask = np.isin(g.frame_ids, list(targets))
            if mask.any():
                g.remove_rows(np.nonzero(mask)[0])
                if g.size == 0:
                    del self._groups[dim]

    def age_all(self, min_age_cycles: int) -> None:
        for g in self._groups.values():
            g.age_cycles += 1
            g.is_candidate = g.age_cycles < min_age_cycles

    # ---- scoring helpers -----------------------------------------------------
    def frame_states(self) -> list[FrameState]:
        states: list[FrameState] = []
        for d, g in self._groups.items():
            for i in range(g.size):
                states.append(
                    FrameState(
                        frame_id=int(g.frame_ids[i]),
                        dim=d,
                        is_candidate=bool(g.is_candidate[i]),
                        age_cycles=int(g.age_cycles[i]),
                        recon_err_ema=float(g.recon_err_ema[i]),
                        pred_err_ema=float(g.pred_err_ema[i]),
                        effort_ema=float(g.effort_ema[i]),
                    )
                )
        states.sort(key=lambda s: s.frame_id)
        return states

    def best_frame(self, scorer) -> tuple[int, int, float] | None:
        """Return ``(frame_id, dim, score)`` of the lowest-score frame; ties by
        ascending ``frame_id`` (PRA-01 §7.1)."""
        best: tuple[float, int, int] | None = None  # (score, frame_id, dim)
        for d, g in self._groups.items():
            if g.size == 0:
                continue
            scores = scorer.combine(g.recon_err_ema, g.pred_err_ema, g.effort_ema, d)
            for i in range(g.size):
                cand = (float(scores[i]), int(g.frame_ids[i]), d)
                if best is None or cand < best:
                    best = cand
        if best is None:
            return None
        return best[1], best[2], best[0]

    # ---- the batched online step --------------------------------------------
    def online_step(
        self, obs: np.ndarray, prev_obs: np.ndarray | None, prev_a: int | None, effort_only: bool
    ) -> StepStats:
        mapped = 0
        alive = 0
        elect_errs: list[float] = []
        decay = self._decay
        for g in self._groups.values():
            if g.size == 0:
                continue
            alive += g.size
            fit, pose, h, recon, hd = g.fit_quality(obs)  # pre-learning forward
            elect = fit < self._fit_gate
            mapped += int(elect.sum())
            if elect.any():
                g.learn_placement(obs, pose, h, recon, hd, elect, self._lr, self._clip)
                if prev_obs is not None:
                    g.learn_transition(
                        prev_obs, prev_a, obs, effort_only, elect, self._lr, self._clip
                    )
            # coverage-fair recon EMA over every exposure, using the pre-learning fit
            g.recon_err_ema = decay * g.recon_err_ema + (1.0 - decay) * fit
            if prev_obs is not None:
                honest = g.honest_pred_err(prev_obs, prev_a, obs)  # post-learning weights
                g.pred_err_ema = decay * g.pred_err_ema + (1.0 - decay) * honest
                if elect.any():
                    elect_errs.extend(honest[elect].tolist())
        return StepStats(mapped=mapped, alive=alive, elect_pred_errors=elect_errs)

    # ---- per-frame delivery (Bus FrameProcessor) -----------------------------
    def results_for(self, event: SensorimotorEvent, frame_ids: list[int]) -> dict[int, FrameResult]:
        wanted = set(frame_ids)
        out: dict[int, FrameResult] = {}
        obs = event.observation
        for g in self._groups.values():
            if g.size == 0:
                continue
            fit, pose, _, _, _ = g.fit_quality(obs)
            elect = fit < self._fit_gate
            if event.has_previous:
                honest = g.honest_pred_err(event.previous_observation, event.action, obs)
                effort = g.effort(event.previous_observation, event.action)
            for i in range(g.size):
                fid = int(g.frame_ids[i])
                if fid not in wanted:
                    continue
                mapped = bool(elect[i])
                out[fid] = FrameResult(
                    frame_id=fid,
                    mapped=mapped,
                    local_pose=pose[i].copy() if mapped else None,
                    recon_error=float(fit[i]) if mapped else None,
                    pred_error=float(honest[i]) if event.has_previous else None,
                    effort=float(effort[i]) if event.has_previous else None,
                )
        return out
