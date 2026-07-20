"""Homogeneous batched frame kernel (PRA-01 §5/§7.2, data-model §3, research R1/R2).

A *FrameGroup* stacks every frame of one ``dim`` along a leading frame axis and
runs encode/decode/transition/learn as batched ``np.einsum`` ops over that axis —
there is **no per-frame branching**; a frame that does not elect to map simply has
its weight updates masked to zero. Frames of different ``dim`` live in different
groups because their tensor shapes differ. The *FrameStore* owns the groups,
births frames (drawing weights in the v4 oracle's exact order so the single seeded
generator is consumed identically), evicts them, and runs one online step batched
across all groups.

The math is a faithful, vectorized port of ``hq/02-DESIGN/validate/pra_sim_v3.Frame``
(the behavioral oracle): a single-hidden-layer encoder, decoder, and per-action
transition, trained with clipped one-layer backprop. ``tests/unit/
test_batched_equivalence.py`` proves the batched path matches a straightforward
per-frame reference.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from pra.config import HIDDEN_REF, OBS_DIM_REF, Config
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
        """Append one frame, drawing its weights in the v4 Frame.__init__ order.

        Scale-invariant init [D] (SCALE-DIAGNOSIS layer 3): tensors whose fan-in
        grows with ``obs_dim``/``hidden`` are rescaled by ``sqrt(fan_in_ref /
        fan_in)`` so pre-activation magnitudes stay in the regime validated at
        the reference scale, where both factors are exactly 1.0 (the reference
        weights are byte-identical). Pose-dim fan-ins (``Dc1``/``T1``) are left
        at the raw scale — rescaling them would alter validated reference frames.
        """
        D, H, Od, A = self.dim, self.H, self.obs_dim, self.A
        f_obs = float(np.sqrt(OBS_DIM_REF / Od))
        f_hid = float(np.sqrt(HIDDEN_REF / H))
        # Draw order is load-bearing for determinism (PRA-01 §7.1).
        W1 = rng.standard_normal((H, Od)) * (scale * f_obs)
        W2 = rng.standard_normal((D, H)) * (scale * f_hid)
        Dc1 = rng.standard_normal((H, D)) * scale
        Dc2 = rng.standard_normal((Od, H)) * (scale * f_hid)
        T1 = rng.standard_normal((A, H, D)) * scale
        T2 = rng.standard_normal((A, D, H)) * (scale * f_hid)

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

    def project_norms(self, cap_factor: float, init_scale: float) -> None:
        """Per-tensor max-norm control (LONGEVITY-DIAGNOSIS, the lifetime-
        stability mechanism): project each frame's weight tensors back to
        ``‖W‖_F ≤ cap_factor · E‖W_init‖_F``. The expected init norm has a
        closed form (Gaussian init: ``s_eff·sqrt(n)``; the §8.8 fan-in factors
        cancel one dimension), so the cap needs no stored state. Biases (init
        0) are never projected. Constrains magnitude only — direction and
        ongoing adaptation stay free."""
        if self.size == 0:
            return
        D, H, Od, A = self.dim, self.H, self.obs_dim, self.A
        roots = {
            "W1": (H * OBS_DIM_REF) ** 0.5,
            "W2": (D * HIDDEN_REF) ** 0.5,
            "Dc1": (H * D) ** 0.5,
            "Dc2": (HIDDEN_REF * Od) ** 0.5,
            "T1": (A * H * D) ** 0.5,
            "T2": (HIDDEN_REF * A * D) ** 0.5,
        }
        for name, root in roots.items():
            w = getattr(self, name)
            cap = cap_factor * init_scale * root
            norms = np.sqrt((w * w).reshape(w.shape[0], -1).sum(axis=1))
            over = norms > cap
            if over.any():
                factors = np.ones_like(norms)
                factors[over] = cap / norms[over]
                setattr(self, name, w * factors.reshape((-1,) + (1,) * (w.ndim - 1)))

    def resize(self, new_obs_dim: int, new_n_actions: int, scale: float, rng) -> None:
        """Frame I/O resize (Doc 03 §7, feature 004 research R3).

        Existing weight entries are preserved bit-for-bit. Growth appends
        trailing slices drawn at the §8.8 effective scale for each tensor's
        fan-in at the NEW widths (biases zero); shrink discards trailing
        slices. Draw order within a group is fixed: W1, Dc2 (observation),
        then T1, T2 (actions) — single tensor draws, row-major.
        """
        from pra.config import HIDDEN_REF, OBS_DIM_REF

        F, H = self.size, self.H
        d_obs = new_obs_dim - self.obs_dim
        if d_obs > 0:
            f_obs = float(np.sqrt(OBS_DIM_REF / new_obs_dim))
            f_hid = float(np.sqrt(HIDDEN_REF / H))
            self.W1 = np.concatenate(
                [self.W1, rng.standard_normal((F, H, d_obs)) * (scale * f_obs)], axis=2
            )
            self.Dc2 = np.concatenate(
                [self.Dc2, rng.standard_normal((F, d_obs, H)) * (scale * f_hid)], axis=1
            )
            self.dc2 = np.concatenate([self.dc2, np.zeros((F, d_obs))], axis=1)
        elif d_obs < 0:
            self.W1 = self.W1[:, :, :new_obs_dim]
            self.Dc2 = self.Dc2[:, :new_obs_dim, :]
            self.dc2 = self.dc2[:, :new_obs_dim]
        self.obs_dim = new_obs_dim

        d_act = new_n_actions - self.A
        if d_act > 0:
            f_hid = float(np.sqrt(HIDDEN_REF / H))
            D = self.dim
            self.T1 = np.concatenate(
                [self.T1, rng.standard_normal((F, d_act, H, D)) * scale], axis=1
            )
            self.tb1 = np.concatenate([self.tb1, np.zeros((F, d_act, H))], axis=1)
            self.T2 = np.concatenate(
                [self.T2, rng.standard_normal((F, d_act, D, H)) * (scale * f_hid)], axis=1
            )
            self.tb2 = np.concatenate([self.tb2, np.zeros((F, d_act, D))], axis=1)
        elif d_act < 0:
            self.T1 = self.T1[:, :new_n_actions]
            self.tb1 = self.tb1[:, :new_n_actions]
            self.T2 = self.T2[:, :new_n_actions]
            self.tb2 = self.tb2[:, :new_n_actions]
        self.A = new_n_actions

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
    # Every observation-facing method takes ``w`` (learned channel weighting,
    # CHANNELWEIGHT-DIAGNOSIS): ``None`` is the pinned validated path — the
    # textually-current expressions, no extra float work. A weight vector
    # applies ONE consistent treatment to both legs: the survival norms
    # (weighted numerator AND denominator) and the learning path (the encoder
    # consumes w*obs; the placement error and its encoder outer product are
    # weighted) — judging and learning never disagree about a channel's worth.
    def encode(self, obs: np.ndarray, w: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray]:
        x = obs if w is None else obs * w
        h = np.tanh(np.einsum("fho,o->fh", self.W1, x) + self.b1)
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
        self, obs: np.ndarray, w: np.ndarray | None = None
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        pose, h = self.encode(obs, w)
        recon, hd = self.reconstruct(pose)
        if w is None:
            fit = np.linalg.norm(recon - obs, axis=1) / (np.linalg.norm(obs) + _EPS)
        else:
            fit = np.linalg.norm((recon - obs) * w, axis=1) / (np.linalg.norm(obs * w) + _EPS)
        return fit, pose, h, recon, hd

    def predicted_obs(
        self, prev_obs: np.ndarray, a: int, w: np.ndarray | None = None
    ) -> np.ndarray:
        """The decoded one-step prediction (the forward half of
        :meth:`honest_pred_err`, exposed so a caller can norm it more than
        one way without a second forward pass)."""
        ppose, _ = self.encode(prev_obs, w)
        pnext, _ = self.predict_next(ppose, a)
        pobs, _ = self.reconstruct(pnext)
        return pobs

    def honest_pred_err(
        self, prev_obs: np.ndarray, a: int, obs: np.ndarray, w: np.ndarray | None = None
    ) -> np.ndarray:
        """Obs-space prediction error with current weights (PRA-01 §5.2)."""
        pobs = self.predicted_obs(prev_obs, a, w)
        if w is None:
            return np.linalg.norm(pobs - obs, axis=1) / (np.linalg.norm(obs) + _EPS)
        return np.linalg.norm((pobs - obs) * w, axis=1) / (np.linalg.norm(obs * w) + _EPS)

    def effort(self, prev_obs: np.ndarray, a: int, w: np.ndarray | None = None) -> np.ndarray:
        ppose, _ = self.encode(prev_obs, w)
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
        w: np.ndarray | None = None,
    ) -> None:
        m = elect.astype(np.float64)
        m1 = m[:, None]
        m2 = m[:, None, None]
        # Weighted (w is not None): the error is weighted — silencing the
        # static-target decoder rows AND the static leak back through Dc2 into
        # the shared layers — and the encoder outer product uses the weighted
        # input the forward pass actually saw (gradient correctness + the
        # third contamination point, CHANNELWEIGHT-DIAGNOSIS).
        e = recon - obs if w is None else (recon - obs) * w
        x = obs if w is None else obs * w
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
        gW1 = np.clip(np.einsum("fh,o->fho", ghe, x), -clip, clip)
        self.W2 -= lr * gW2 * m2
        self.b2 -= lr * np.clip(gpose, -clip, clip) * m1
        self.W1 -= lr * gW1 * m2
        self.b1 -= lr * np.clip(ghe, -clip, clip) * m1

    def learn_transition(
        self,
        prev_obs: np.ndarray,
        a: int,
        next_obs: np.ndarray,
        scoring_mode: str,
        elect: np.ndarray,
        lr: float,
        clip: float,
        w: np.ndarray | None = None,
    ) -> None:
        """Train the per-action transition toward the mode's target (PRA-01 §5.6):
        ``predictive`` → the next pose (the real dynamics), ``effort_only`` → the
        zero pose (the T3 zero-pull ablation), ``identity`` → the current pose
        (the learned-persistence ablation: "predict that nothing changes")."""
        m = elect.astype(np.float64)
        m1 = m[:, None]
        m2 = m[:, None, None]
        p, _ = self.encode(prev_obs, w)
        nxt, _ = self.encode(next_obs, w)
        pred, h = self.predict_next(p, a)
        if scoring_mode == "effort_only":
            target = np.zeros_like(nxt)
        elif scoring_mode == "identity":
            target = p
        else:
            target = nxt
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
        self._lr = float(config.effective_learning_rate)
        self._clip = float(config.gradient_clip)
        self._decay = float(config.ema_decay)
        self._scale = float(config.init_weight_scale)
        self._norm_cap = float(config.weight_norm_cap)
        # Current anatomy dims: equal to config at boot; tool registration
        # (Doc 02 §5) changes them via resize() at the slow loop. Births and
        # per-event results always use the current dims.
        self.obs_dim = int(config.obs_dim)
        self.n_actions = int(config.n_actions)
        # Learned channel weighting (CHANNELWEIGHT-DIAGNOSIS, feature 016).
        # Off (floor == 0, the default): no state, no float work, no RNG —
        # every group call receives w=None, the pinned validated path.
        self._cw_floor = float(config.channel_weight_floor)
        self._cw_on = self._cw_floor > 0.0
        if self._cw_on:
            self._cw_beta = float(config.channel_stats_decay)
            self._cw_ready_at = math.ceil(1.0 / (1.0 - self._cw_beta))
            self._cw_init_stats(self.obs_dim)

    # ---- learned channel weighting (store-level: channel quality is a world
    # property, not a frame property; one estimator, one weight vector) -------
    def _cw_init_stats(self, obs_dim: int) -> None:
        self._cw_m = np.zeros(obs_dim)
        self._cw_v = np.zeros(obs_dim)
        self._cw_cov = np.zeros(obs_dim)
        self._cw_n = np.zeros(obs_dim)
        self._cw_w = np.ones(obs_dim)

    def _cw_update(self, obs: np.ndarray, prev_obs: np.ndarray | None) -> None:
        """The registered EMA arithmetic — every online step, before forwards."""
        b = self._cw_beta
        self._cw_m = b * self._cw_m + (1.0 - b) * obs
        d = obs - self._cw_m  # post-update mean, as registered
        self._cw_v = b * self._cw_v + (1.0 - b) * d * d
        if prev_obs is not None:
            self._cw_cov = b * self._cw_cov + (1.0 - b) * d * (prev_obs - self._cw_m)
        self._cw_n += 1.0

    def _cw_recompute(self) -> None:
        """Weights from the whiteness statistic — episode starts only, so every
        within-episode judgment happens in one norm (the fair-judge window
        must not drift mid-window). Max-normalized shaping, P1-pinned."""
        ready = self._cw_n >= self._cw_ready_at
        if not ready.any():
            return
        rho = np.clip(self._cw_cov / (self._cw_v + _EPS), 0.0, 1.0)
        w = np.clip(rho / (rho[ready].max() + _EPS), self._cw_floor, 1.0)
        w[~ready] = 1.0
        self._cw_w = w

    @property
    def channel_weights(self) -> np.ndarray | None:
        """The current weight vector (copy) when on; ``None`` when off."""
        return np.array(self._cw_w, copy=True) if self._cw_on else None

    def channel_weighting_summary(self) -> dict | None:
        """The ON-only summary block (agency-fields pattern): ``None`` when
        off, so every existing mode's serialization stays byte-identical."""
        if not self._cw_on:
            return None
        return {
            "floor": self._cw_floor,
            "decay": self._cw_beta,
            "ready_channels": int((self._cw_n >= self._cw_ready_at).sum()),
            "final_weights": [round(float(x), 4) for x in self._cw_w],
        }

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
            g = FrameGroup(dim, self.obs_dim, self.config.hidden_size, self.n_actions)
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

    def resize(self, new_obs_dim: int, new_n_actions: int, rng) -> None:
        """Apply an anatomy change to every frame (Doc 03 §7; slow loop only).

        Groups are resized in ascending ``dim`` order (fixed draw order,
        feature 004 FR-006); the store's current dims and the scale-dependent
        effective learning rate (PRA-01 §8.8) track the new observation width.
        """
        from pra.config import OBS_DIM_REF

        for dim in sorted(self._groups):
            self._groups[dim].resize(new_obs_dim, new_n_actions, self._scale, rng)
        if self._cw_on:
            d_obs = int(new_obs_dim) - self.obs_dim
            if d_obs > 0:
                # new channels: zero stats, FULL weight until ready — the same
                # optimistic-until-evidence stance the ready gate gives young runs
                zeros = np.zeros(d_obs)
                self._cw_m = np.concatenate([self._cw_m, zeros])
                self._cw_v = np.concatenate([self._cw_v, zeros])
                self._cw_cov = np.concatenate([self._cw_cov, zeros])
                self._cw_n = np.concatenate([self._cw_n, zeros])
                self._cw_w = np.concatenate([self._cw_w, np.ones(d_obs)])
            elif d_obs < 0:
                for name in ("_cw_m", "_cw_v", "_cw_cov", "_cw_n", "_cw_w"):
                    setattr(self, name, getattr(self, name)[: int(new_obs_dim)])
        self.obs_dim = int(new_obs_dim)
        self.n_actions = int(new_n_actions)
        self._lr = float(self.config.learning_rate * (OBS_DIM_REF / new_obs_dim) ** 1.5)

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

    # ---- persistence (Doc 06 §2: the frame population is system state) -------
    _GROUP_FIELDS = (
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
    )

    def state_dict(self) -> dict:
        """The full population state: per-dim identity records + weight tensors
        + the next frame id, plus the current anatomy dims (feature 010 —
        differ from the boot config after a mid-run resize). Arrays are copies
        (a snapshot is point-in-time)."""
        state = {
            "next_id": self._next_id,
            "obs_dim": self.obs_dim,
            "n_actions": self.n_actions,
            "groups": {
                dim: {name: np.array(getattr(g, name), copy=True) for name in self._GROUP_FIELDS}
                for dim, g in self._groups.items()
                if g.size > 0
            },
        }
        if self._cw_on:
            # estimator state is behavior-affecting → snapshot state (Doc 06
            # §2); written only when on, so feature-off snapshots stay
            # bit-identical to the pre-016 format.
            state["channel_stats"] = {
                "m": np.array(self._cw_m, copy=True),
                "v": np.array(self._cw_v, copy=True),
                "cov": np.array(self._cw_cov, copy=True),
                "n": np.array(self._cw_n, copy=True),
                "w": np.array(self._cw_w, copy=True),
            }
        return state

    def load_state_dict(self, state: dict) -> None:
        """Reconstruct the population exactly from :meth:`state_dict` output.

        Anatomy-resized runs (feature 010): the state carries the *current*
        dims when the run grew mid-run; groups rebuild at those dims and the
        store's current dims + effective learning rate are restored (the
        feature-004 resize bookkeeping). Pre-010 blobs carry no dims and fall
        back to the boot config — exactly what they were written with."""
        from pra.config import OBS_DIM_REF

        self._groups.clear()
        self._next_id = int(state["next_id"])
        self.obs_dim = int(state.get("obs_dim", self.config.obs_dim))
        self.n_actions = int(state.get("n_actions", self.config.n_actions))
        self._lr = float(self.config.learning_rate * (OBS_DIM_REF / self.obs_dim) ** 1.5)
        for dim, tensors in state["groups"].items():
            g = FrameGroup(int(dim), self.obs_dim, self.config.hidden_size, self.n_actions)
            for name in self._GROUP_FIELDS:
                setattr(g, name, np.array(tensors[name], copy=True))
            self._groups[int(dim)] = g
        if self._cw_on:
            cs = state.get("channel_stats")
            if cs is not None:
                self._cw_m = np.array(cs["m"], copy=True)
                self._cw_v = np.array(cs["v"], copy=True)
                self._cw_cov = np.array(cs["cov"], copy=True)
                self._cw_n = np.array(cs["n"], copy=True)
                self._cw_w = np.array(cs["w"], copy=True)
            else:
                # pre-016 blob (or one written with the feature off) resumed
                # with the feature newly enabled: the estimator starts fresh
                # from new data — stated openly (spec US3 scenario 2).
                self._cw_init_stats(self.obs_dim)

    def best_frame_predictor(self, scorer):
        """The current best frame's ``(age_cycles, predict_decoded)`` for the
        policy's one-step lookahead (Doc 05 §4.2): ``predict_decoded(obs, a)``
        encodes ``obs`` with the best frame, applies its transition for ``a``,
        and decodes the predicted pose back to observation space. Returns
        ``(None, None)`` when no frame exists. Read-only: never mutates weights
        or consumes RNG."""
        best = self.best_frame(scorer)
        if best is None:
            return None, None
        fid = best[0]
        for g in self._groups.values():
            idx = np.nonzero(g.frame_ids == fid)[0]
            if idx.size == 0:
                continue
            i = int(idx[0])

            wv = self._cw_w if self._cw_on else None

            def predict_decoded(obs: np.ndarray, action: int, g=g, i=i, w=wv) -> np.ndarray:
                pose, _ = g.encode(obs, w)
                pred, _ = g.predict_next(pose, action)
                recon, _ = g.reconstruct(pred)
                return recon[i]

            return int(g.age_cycles[i]), predict_decoded
        return None, None

    # ---- the batched online step --------------------------------------------
    def online_step(
        self,
        obs: np.ndarray,
        prev_obs: np.ndarray | None,
        prev_a: int | None,
        scoring_mode: str,
        *,
        ema_update: bool = True,
    ) -> StepStats:
        mapped = 0
        alive = 0
        elect_errs: list[float] = []
        decay = self._decay
        # learned channel weighting (opt-in): recompute weights at episode
        # starts (from the stats accumulated so far), then fold this step's
        # observation into the stats — both before any forward pass. No RNG.
        if self._cw_on:
            if prev_obs is None:
                self._cw_recompute()
            self._cw_update(obs, prev_obs)
        wv = self._cw_w if self._cw_on else None
        # lifetime stability (weight_norm_cap > 0, opt-in): project weight
        # norms at each episode start, before any processing of the episode.
        if prev_obs is None and self._norm_cap > 0.0:
            for g in self._groups.values():
                g.project_norms(self._norm_cap, self._scale)
        for g in self._groups.values():
            if g.size == 0:
                continue
            alive += g.size
            fit, pose, h, recon, hd = g.fit_quality(obs, wv)  # pre-learning forward
            elect = fit < self._fit_gate
            mapped += int(elect.sum())
            if elect.any():
                g.learn_placement(obs, pose, h, recon, hd, elect, self._lr, self._clip, wv)
                if prev_obs is not None:
                    g.learn_transition(
                        prev_obs, prev_a, obs, scoring_mode, elect, self._lr, self._clip, wv
                    )
            # coverage-fair recon EMA over every exposure, using the pre-learning fit.
            # ema_update=False (score_window_steps, THRESHOLD-DIAGNOSIS): the step
            # still learns and reports telemetry, but the survival EMAs advance only
            # on episode-start steps — the fair judge scores structural transfer,
            # not within-episode tracking.
            if ema_update:
                g.recon_err_ema = decay * g.recon_err_ema + (1.0 - decay) * fit
            if prev_obs is not None:
                if wv is None:
                    honest = g.honest_pred_err(prev_obs, prev_a, obs)  # post-learning weights
                    honest_tele = honest
                else:
                    # one forward pass, two norms: the WEIGHTED error feeds the
                    # survival EMAs (what the ecology judges); the UNWEIGHTED
                    # all-channel error feeds telemetry, keeping pred_error_
                    # early/late/improvement comparable across the dose record
                    # (CHANNELWEIGHT-DIAGNOSIS constraint C2).
                    pobs = g.predicted_obs(prev_obs, prev_a, wv)
                    honest = np.linalg.norm((pobs - obs) * wv, axis=1) / (
                        np.linalg.norm(obs * wv) + _EPS
                    )
                    honest_tele = np.linalg.norm(pobs - obs, axis=1) / (np.linalg.norm(obs) + _EPS)
                if ema_update:
                    g.pred_err_ema = decay * g.pred_err_ema + (1.0 - decay) * honest
                if elect.any():
                    elect_errs.extend(honest_tele[elect].tolist())
        return StepStats(mapped=mapped, alive=alive, elect_pred_errors=elect_errs)

    # ---- per-frame delivery (Bus FrameProcessor) -----------------------------
    def results_for(self, event: SensorimotorEvent, frame_ids: list[int]) -> dict[int, FrameResult]:
        wanted = set(frame_ids)
        out: dict[int, FrameResult] = {}
        obs = event.observation
        # channel weighting on → delivered per-frame results are the judged
        # (weighted) quantities, consistent with the survival EMAs they mirror.
        wv = self._cw_w if self._cw_on else None
        for g in self._groups.values():
            if g.size == 0:
                continue
            fit, pose, _, _, _ = g.fit_quality(obs, wv)
            elect = fit < self._fit_gate
            if event.has_previous:
                honest = g.honest_pred_err(event.previous_observation, event.action, obs, wv)
                effort = g.effort(event.previous_observation, event.action, wv)
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
