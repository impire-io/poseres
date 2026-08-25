"""Compositional-frames rig v2 — the reference lives in the TRANSITION.

v1 (compose_v1_inputaug.py) put z on the observation: tier-2 read
aug_obs = [obs, z]. Pilot instruments killed it (JOURNEY 2026-08-24):
tier-2 had to reconstruct and predict the carrier block, diluting
every loss 14/6, and the kernel's lr scale rule slowed it 3.6x; at a
matched rate the population churned. The arbiter never engaged
(share <= 0.005 in every arm) — no mechanism could express itself.

v2, registered before any 24-seed run: a tier-2 frame is a PLAIN
obs-space frame (encoder/decoder/losses identical to base — same
channels, same effective lr); only its per-action transition takes
[own pose, z] — the reference is a constituent of the frame's
DYNAMICS. The one variable between arms is what z is when predicting
from obs(t):

    tower     z = best base frame's pose at obs(t) (same step) —
              adds representation, no information
    ref-pose  z = best base frame's pose at obs(t-1) (carried)
    ref-pred  z = base's predicted pose for t, made at t-1 from
              (pose(obs(t-1)), a(t-1))

Transition training at step t (sample obs(t-1) -> obs(t)) uses the z
the mode would have used predicting from obs(t-1); the z chain breaks
at episode boundaries exactly where the transition chain does. The
cached base pose is what tier-1 actually said at t-1 (post-that-
step's base learning), never recomputed.

Cross-tier arbiter: the kernel's own survival score (scorer.combine
on recon/pred/effort EMAs + complexity), both tiers' EMAs computed
by the same obs-space arithmetic — the policy's lookahead predictor
comes from the globally lowest-scoring frame, its own age gating
maturity. Task-channel (progress, pulse) EMAs are telemetry only.

Policy for every arm: stack-nc exactly (kappa=0.25, commitment off,
event head eta=0.5 on the base store; tier-2 duplicates no head).
Tier-2 draws only from its own spawn-keyed generator (spawn_key
7000); its lifecycle mirrors the engine's (on-demand birth,
per-cycle age/evict/spawn, same config).

    python compose.py calib R 4 W2 tower|ref-pose|ref-pred [c] [seeds]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

RIG = Path(__file__).parent
sys.path.insert(0, str(RIG))

from seq import ENCODINGS, M, SEEDS, EchoWorld, SeqRecordingPolicy, obs_dim_of  # noqa: E402

import pra.core.engine as engine_mod  # noqa: E402
from pra.action.policy import CompletionItchPolicy, PolicyParams  # noqa: E402
from pra.config import Config  # noqa: E402
from pra.core.contracts import FrameState  # noqa: E402
from pra.core.engine import Engine  # noqa: E402
from pra.core.frame import FrameGroup, FrameStore  # noqa: E402
from pra.core.policies import BiasedProposalPolicy, PopulationScaledDecayPolicy  # noqa: E402
from pra.core.scorer import WeightedSumScorer  # noqa: E402

Z = 8
_EPS = 1e-6

RUN = {"seed": 0, "mode": "tower", "stores": []}


class RefFrameGroup(FrameGroup):
    """FrameGroup whose per-action transition reads [pose, z] (width D+Z).

    Placement (encoder/decoder) is inherited untouched; only the transition
    tensors widen and every transition-consuming method takes z."""

    def __init__(self, dim: int, obs_dim: int, hidden: int, n_actions: int):
        super().__init__(dim, obs_dim, hidden, n_actions)
        F, A, H, D = 0, n_actions, hidden, dim
        self.T1 = np.zeros((F, A, H, D + Z))
        # identity binding (Phase B): referenced base frame id per row;
        # -1 = unbound (slot modes never read this)
        self.ref_ids = np.zeros(F, dtype=np.int64) - 1

    def remove_rows(self, rows: np.ndarray) -> None:
        keep = np.ones(self.size, dtype=bool)
        keep[rows] = False
        self.ref_ids = self.ref_ids[keep]
        super().remove_rows(rows)

    def add_frame(self, frame_id: int, ema_init: float, scale: float, rng,
                  ref_id: int = -1) -> None:
        """Same draw order as the kernel's, T1 widened to D+Z (tier-2 draws
        from its own generator, so the base stream is untouched)."""
        from pra.config import HIDDEN_REF, OBS_DIM_REF

        D, H, Od, A = self.dim, self.H, self.obs_dim, self.A
        f_obs = float(np.sqrt(OBS_DIM_REF / Od))
        f_hid = float(np.sqrt(HIDDEN_REF / H))
        W1 = rng.standard_normal((H, Od)) * (scale * f_obs)
        W2 = rng.standard_normal((D, H)) * (scale * f_hid)
        Dc1 = rng.standard_normal((H, D)) * scale
        Dc2 = rng.standard_normal((Od, H)) * (scale * f_hid)
        T1 = rng.standard_normal((A, H, D + Z)) * scale
        T2 = rng.standard_normal((A, D, H)) * (scale * f_hid)

        self.frame_ids = np.append(self.frame_ids, np.int64(frame_id))
        self.ref_ids = np.append(self.ref_ids, np.int64(ref_id))
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

    def _pin(self, pose: np.ndarray, z: np.ndarray) -> np.ndarray:
        """z: (Z,) shared across the group (slot modes) or (F, Z) per-frame
        (identity-bound modes)."""
        if z.ndim == 2:
            return np.concatenate([pose, z], axis=1)
        return np.concatenate([pose, np.broadcast_to(z, (pose.shape[0], Z))], axis=1)

    def z_rows(self, zmap: dict[int, np.ndarray]) -> np.ndarray:
        """Per-frame z from referenced ids; a dangling or unbound referent
        degrades to zeros (the registered graceful-degradation stance)."""
        out = np.zeros((self.size, Z))
        for i in range(self.size):
            v = zmap.get(int(self.ref_ids[i]))
            if v is not None:
                out[i] = v
        return out

    def predict_next_z(self, pose: np.ndarray, a: int, z: np.ndarray):
        pin = self._pin(pose, z)
        h = np.tanh(np.einsum("fhd,fd->fh", self.T1[:, a], pin) + self.tb1[:, a])
        pred = np.einsum("fdh,fh->fd", self.T2[:, a], h) + self.tb2[:, a]
        return pred, h

    def predicted_obs_z(self, prev_obs: np.ndarray, a: int, z: np.ndarray) -> np.ndarray:
        ppose, _ = self.encode(prev_obs)
        pnext, _ = self.predict_next_z(ppose, a, z)
        pobs, _ = self.reconstruct(pnext)
        return pobs

    def honest_pred_err_z(self, prev_obs, a, obs, z) -> np.ndarray:
        pobs = self.predicted_obs_z(prev_obs, a, z)
        return np.linalg.norm(pobs - obs, axis=1) / (np.linalg.norm(obs) + _EPS)

    def effort_z(self, prev_obs, a, z) -> np.ndarray:
        ppose, _ = self.encode(prev_obs)
        pnext, _ = self.predict_next_z(ppose, a, z)
        return np.linalg.norm(pnext - ppose, axis=1)

    def learn_transition_z(self, prev_obs, a, next_obs, elect, lr, clip, z) -> None:
        m = elect.astype(np.float64)
        m1 = m[:, None]
        m2 = m[:, None, None]
        p, _ = self.encode(prev_obs)
        nxt, _ = self.encode(next_obs)
        pin = self._pin(p, z)
        pred, h = self.predict_next_z(p, a, z)
        e = pred - nxt
        gT2 = np.clip(np.einsum("fd,fh->fdh", e, h), -clip, clip)
        gh = np.einsum("fdh,fd->fh", self.T2[:, a], e) * (1.0 - h**2)
        gT1 = np.clip(np.einsum("fh,fd->fhd", gh, pin), -clip, clip)
        self.T2[:, a] -= lr * gT2 * m2
        self.tb2[:, a] -= lr * np.clip(e, -clip, clip) * m1
        self.T1[:, a] -= lr * gT1 * m2
        self.tb1[:, a] -= lr * np.clip(gh, -clip, clip) * m1


class Tier2Store:
    """Minimal mirror of the FrameStore lifecycle for RefFrameGroups: same
    on-demand birth rule, same per-cycle age/evict/spawn, same EMAs by the
    same arithmetic — its own rng (spawn_key 7000), no event head."""

    def __init__(self, cfg: Config, seed: int):
        self.cfg = cfg
        self.rng = np.random.default_rng(np.random.SeedSequence(entropy=seed, spawn_key=(7000,)))
        self.scorer = WeightedSumScorer(cfg)
        self.decay_policy = PopulationScaledDecayPolicy(cfg)
        self.proposal = BiasedProposalPolicy(cfg)
        self._groups: dict[int, RefFrameGroup] = {}
        self._next_id = 1_000_000  # disjoint from base ids (telemetry clarity)
        self._fit_gate = float(cfg.fit_gate)
        self._lr = float(cfg.effective_learning_rate)
        self._clip = float(cfg.gradient_clip)
        self._decay = float(cfg.ema_decay)
        self._scale = float(cfg.init_weight_scale)
        self.task_ema: dict[int, float] = {}  # telemetry only
        self.mapped_steps = 0
        self.total_steps = 0

    @property
    def population_size(self) -> int:
        return sum(g.size for g in self._groups.values())

    def dims_alive(self) -> list[int]:
        dims: list[int] = []
        for d, g in self._groups.items():
            dims.extend([d] * g.size)
        return sorted(dims)

    def _group_for(self, dim: int) -> RefFrameGroup:
        g = self._groups.get(dim)
        if g is None:
            g = RefFrameGroup(dim, self.cfg.obs_dim, self.cfg.hidden_size, self.cfg.n_actions)
            self._groups[dim] = g
        return g

    def birth(self, dim: int, ema_init: float, ref_id: int = -1) -> int:
        fid = self._next_id
        self._next_id += 1
        self._group_for(dim).add_frame(fid, ema_init, self._scale, self.rng, ref_id)
        return fid

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
        for fid in frame_ids:
            self.task_ema.pop(fid, None)

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

    def best(self):
        """(group, row, frame_id, dim, age, score) of the lowest-score frame."""
        out = None
        for d, g in self._groups.items():
            if g.size == 0:
                continue
            scores = self.scorer.combine(g.recon_err_ema, g.pred_err_ema, g.effort_ema, d)
            for i in range(g.size):
                cand = (float(scores[i]), int(g.frame_ids[i]), d, g, i)
                if out is None or cand[:2] < out[:2]:
                    out = cand
        if out is None:
            return None
        score, fid, d, g, i = out
        return g, i, fid, d, int(g.age_cycles[i]), score

    def online_step(self, obs, prev_obs, prev_a, z_train, z_now, bind_ref: int = -1) -> None:
        """One step: placement learning on obs (kernel arithmetic inherited),
        transition learning on (prev_obs, prev_a, obs) with z_train, EMAs by
        the kernel's own update, on-demand birth when nothing maps. z_train
        is a shared (Z,) vector (slot modes) or a {base_fid: z} dict
        (identity-bound modes); newborns bind to bind_ref."""
        self.total_steps += 1
        mapped = 0
        for g in self._groups.values():
            if g.size == 0:
                continue
            zt = g.z_rows(z_train) if isinstance(z_train, dict) else z_train
            fit, pose, h, recon, hd = g.fit_quality(obs)
            elect = fit < self._fit_gate
            mapped += int(elect.sum())
            if elect.any():
                g.learn_placement(obs, pose, h, recon, hd, elect, self._lr, self._clip)
                if prev_obs is not None:
                    g.learn_transition_z(
                        prev_obs, prev_a, obs, elect, self._lr, self._clip, zt
                    )
            g.recon_err_ema = self._decay * g.recon_err_ema + (1.0 - self._decay) * fit
            if prev_obs is not None:
                honest = g.honest_pred_err_z(prev_obs, prev_a, obs, zt)
                g.pred_err_ema = self._decay * g.pred_err_ema + (1.0 - self._decay) * honest
                pobs = g.predicted_obs_z(prev_obs, prev_a, zt)
                terr = np.linalg.norm(pobs[:, -2:] - obs[-2:], axis=1)
                for i in range(g.size):
                    fid = int(g.frame_ids[i])
                    prev = self.task_ema.get(fid, 1.0)
                    self.task_ema[fid] = (
                        self._decay * prev + (1.0 - self._decay) * float(terr[i])
                    )
        if mapped > 0:
            self.mapped_steps += 1
        else:
            b = self.best()
            if b is not None:
                d = max(1, b[3] + int(self.rng.choice([-1, 0, 1])))
            else:
                d = int(self.rng.integers(self.cfg.initial_dim_min, self.cfg.initial_dim_max))
            self.birth(d, ema_init=1.0, ref_id=bind_ref)

    def offline_cycle(self, bind_ref: int = -1) -> None:
        for g in self._groups.values():
            g.age_cycles += 1
            g.is_candidate = g.age_cycles < self.cfg.effective_min_age_cycles
        if self.population_size == 0:
            return
        states = self.frame_states()
        threshold = self.decay_policy.threshold(len(states))
        remove = self.decay_policy.evict(
            states,
            self.scorer,
            threshold,
            min_frames=self.cfg.min_frames,
            max_frames=self.cfg.max_frames,
            min_age_cycles=self.cfg.effective_min_age_cycles,
        )
        self.evict(remove)
        for _ in range(self.cfg.spawn_per_cycle):
            b = self.best()
            if b is None:
                break
            new_dim = self.proposal.propose_dimension(b[3], self.dims_alive(), self.rng)
            self.birth(new_dim, ema_init=0.9, ref_id=bind_ref)


_T2_FIELDS = (
    "frame_ids",
    "ref_ids",
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


def t2_state_bytes(t2: Tier2Store) -> bytes:
    """Tier-2 sidecar blob: the kernel snapshot format's discipline (npz +
    json meta, no pickle) applied to the second population. The z caches are
    NOT state — snapshots land at cycle ends, where the z chain breaks with
    the transition chain and rebuilds from zeros on the next episode."""
    import io as _io
    import json as _json

    arrays: dict[str, np.ndarray] = {}
    for dim, g in t2._groups.items():
        for name in _T2_FIELDS:
            arrays[f"g{dim}__{name}"] = getattr(g, name)
    ids = sorted(t2.task_ema)
    arrays["task_ema__ids"] = np.asarray(ids, dtype=np.int64)
    arrays["task_ema__vals"] = np.asarray([t2.task_ema[i] for i in ids], dtype=np.float64)
    meta = {
        "group_dims": [int(d) for d in t2._groups],
        "next_id": t2._next_id,
        "mapped_steps": t2.mapped_steps,
        "total_steps": t2.total_steps,
        "rng_state": t2.rng.bit_generator.state,
    }
    arrays["meta"] = np.array(_json.dumps(meta))
    buf = _io.BytesIO()
    np.savez_compressed(buf, **arrays)
    return buf.getvalue()


def t2_load_bytes(t2: Tier2Store, blob: bytes) -> None:
    import io as _io
    import json as _json

    with np.load(_io.BytesIO(blob), allow_pickle=False) as archive:
        meta = _json.loads(str(archive["meta"]))
        t2._groups.clear()
        for dim in meta["group_dims"]:
            g = RefFrameGroup(int(dim), t2.cfg.obs_dim, t2.cfg.hidden_size, t2.cfg.n_actions)
            for name in _T2_FIELDS:
                setattr(g, name, np.array(archive[f"g{int(dim)}__{name}"]))
            t2._groups[int(dim)] = g
        t2._next_id = int(meta["next_id"])
        t2.mapped_steps = int(meta["mapped_steps"])
        t2.total_steps = int(meta["total_steps"])
        t2.rng.bit_generator.state = meta["rng_state"]
        ids = archive["task_ema__ids"]
        vals = archive["task_ema__vals"]
        t2.task_ema = {int(i): float(v) for i, v in zip(ids, vals, strict=True)}


class ComposedFrameStore(FrameStore):
    """Base tier = inherited FrameStore (byte-equivalent path); tier-2 and
    the z bookkeeping live here."""

    def __init__(self, config: Config, rng: np.random.Generator):
        super().__init__(config, rng)
        self.mode = RUN["mode"]
        cfg2 = config.replace(event_head_eta=0.0)
        self.t2 = Tier2Store(cfg2, RUN["seed"])
        self._scorer = WeightedSumScorer(config)
        self._pose_cache = np.zeros(Z)  # base best pose at obs(t-1), padded
        self._z_state_prev: np.ndarray | None = None  # z_state(t-1)
        self._z_state = np.zeros(Z)  # z_state(t), for the lookahead closure
        # identity-bound modes: {base_fid: z} maps for t and t-1
        self._zmap: dict[int, np.ndarray] = {}
        self._zmap_prev: dict[int, np.ndarray] | None = None
        self.orphan_events = 0  # tier-2 frames whose referent was evicted
        self.arb_t2 = 0
        self.arb_total = 0
        RUN["stores"].append(self)

    def load_state_dict(self, state: dict) -> None:
        """Base tier restores through the untouched kernel path; the tier-2
        sidecar (RUN['t2_blob'], set by the runner beside the blob it decodes)
        restores in the same call so a resumed run continues the composed
        system, not half of it."""
        super().load_state_dict(state)
        blob = RUN.get("t2_blob")
        if blob is not None:
            t2_load_bytes(self.t2, blob)

    def _base_best(self):
        b = self.best_frame(self._scorer)
        if b is None:
            return None
        fid = b[0]
        for g in self._groups.values():
            idx = np.nonzero(g.frame_ids == fid)[0]
            if idx.size:
                return g, int(idx[0])
        return None

    def _pad(self, v: np.ndarray) -> np.ndarray:
        z = np.zeros(Z)
        n = min(v.shape[0], Z)
        z[:n] = v[:n]
        return z

    def online_step(self, obs, prev_obs, prev_a, scoring_mode, *, ema_update=True):
        if prev_obs is None:
            # episode boundary: the z chain breaks exactly where the
            # transition chain does
            self._pose_cache = np.zeros(Z)
            self._z_state_prev = None
            self._zmap = {}
            self._zmap_prev = None

        if self.mode == "bind-pred":
            # every base frame's expectation of t, made at t-1 with pre-step
            # weights (the identity-bound twin of ref-pred)
            zmap: dict[int, np.ndarray] = {}
            if prev_obs is not None and prev_a is not None:
                for g in self._groups.values():
                    if g.size == 0:
                        continue
                    pose, _ = g.encode(prev_obs)
                    pred, _ = g.predict_next(pose, prev_a)
                    for i in range(g.size):
                        zmap[int(g.frame_ids[i])] = self._pad(pred[i])
            stats = super().online_step(
                obs, prev_obs, prev_a, scoring_mode, ema_update=ema_update
            )
            bb = self._base_best()
            bind_ref = -1 if bb is None else int(bb[0].frame_ids[bb[1]])
            z_train = self._zmap_prev if self._zmap_prev is not None else {}
            self.t2.online_step(obs, prev_obs, prev_a, z_train, zmap, bind_ref)
            self._zmap_prev = zmap
            self._zmap = zmap
            return stats

        stats = super().online_step(obs, prev_obs, prev_a, scoring_mode, ema_update=ema_update)

        # z_state(t): what the mode offers a predictor standing at obs(t)
        bb = self._base_best()
        if self.mode == "tower":
            if bb is None:
                z_state = np.zeros(Z)
            else:
                g, i = bb
                pose, _ = g.encode(obs)
                z_state = self._pad(pose[i])
        elif self.mode == "ref-pose":
            z_state = self._pose_cache.copy()
        else:  # ref-pred: base's expectation of t, made at t-1
            if bb is None or prev_a is None:
                z_state = np.zeros(Z)
            else:
                g, i = bb
                dim = g.dim
                pose_prev = self._pose_cache[:dim][None, :]
                # single-frame predict through the base best's transition
                h = np.tanh(
                    np.einsum("hd,d->h", g.T1[i, prev_a], pose_prev[0]) + g.tb1[i, prev_a]
                )
                pred = np.einsum("dh,h->d", g.T2[i, prev_a], h) + g.tb2[i, prev_a]
                z_state = self._pad(pred)

        z_train = self._z_state_prev if self._z_state_prev is not None else np.zeros(Z)
        self.t2.online_step(obs, prev_obs, prev_a, z_train, z_state)

        # cache what tier-1 actually said at t (post-step weights), for the
        # carried modes' next step
        if bb is not None:
            g, i = bb
            pose, _ = g.encode(obs)
            self._pose_cache = self._pad(pose[i])
        else:
            self._pose_cache = np.zeros(Z)
        self._z_state_prev = z_state
        self._z_state = z_state
        return stats  # base-only: the engine's on-demand births mirror flat

    def age_all(self, min_age_cycles: int) -> None:
        super().age_all(min_age_cycles)
        bb = self._base_best()
        bind_ref = -1 if bb is None else int(bb[0].frame_ids[bb[1]])
        self.t2.offline_cycle(bind_ref)

    def evict(self, frame_ids: list[int]) -> None:
        # dangling-reference telemetry: count tier-2 frames whose referent
        # dies in this eviction (their z degrades to zeros from here on)
        if self.mode == "bind-pred" and frame_ids:
            dead = set(frame_ids)
            for g in self.t2._groups.values():
                for i in range(g.size):
                    if int(g.ref_ids[i]) in dead:
                        self.orphan_events += 1
        super().evict(frame_ids)

    def best_frame_predictor(self, scorer):
        self.arb_total += 1
        base = self.best_frame(scorer)
        t2b = self.t2.best()
        if t2b is None:
            return super().best_frame_predictor(scorer)
        if base is not None and base[2] <= t2b[5]:
            return super().best_frame_predictor(scorer)
        # tier-2 holds the globally lowest survival score
        self.arb_t2 += 1
        g2, i2, _fid, _dim, age2, _score = t2b
        if self.mode == "bind-pred":
            z = self._zmap.get(int(g2.ref_ids[i2]), np.zeros(Z))
        else:
            z = self._z_state

        def predict_decoded(obs_: np.ndarray, action: int, g=g2, i=i2, z=z):
            pose, _ = g.encode(obs_)
            pred, _ = g.predict_next_z(pose, action, z)
            recon, _ = g.reconstruct(pred)
            return recon[i]

        return age2, predict_decoded


def run_arm(seed: int, family: str, rung: int, encoding: str, n_cycles: int,
            frames_mode: str) -> dict:
    cfg = Config(
        obs_dim=obs_dim_of(encoding),
        n_actions=M,
        policy_mode="curiosity",
        episode_mode="continuous",
        n_cycles=n_cycles,
        event_head_eta=0.5,
    )
    worlds: list[EchoWorld] = []

    def factory(config: Config, rng: np.random.Generator) -> EchoWorld:
        w = EchoWorld(config, rng, family, rung, encoding)
        worlds.append(w)
        return w

    inner = CompletionItchPolicy(
        PolicyParams.from_config(cfg),
        kappa=0.25,
        progress_index=cfg.obs_dim - 2,
        pocket_index=cfg.obs_dim - 1,
        commit_kappa=0.0,
        explore_defers_holds=False,
    )
    rec = SeqRecordingPolicy(inner, cfg.obs_dim)

    RUN["seed"] = seed
    RUN["mode"] = frames_mode
    RUN["stores"] = []
    engine_mod.FrameStore = ComposedFrameStore if frames_mode != "flat" else FrameStore
    try:
        summary = Engine(cfg, world_factory=factory, policy=rec).run(seed)
    finally:
        engine_mod.FrameStore = FrameStore

    w = worlds[0]
    half = w.total_steps // 2
    back = sum(1 for s in w.accept_steps if s > half)
    row = {
        "seed": seed,
        "family": family,
        "rung": rung,
        "encoding": encoding,
        "policy": "stack-nc",
        "frames": frames_mode,
        "steps": w.total_steps,
        "accepts": len(w.accept_steps),
        "accepts_back": back,
        "accept_per_1k_back": round(back / max(w.total_steps - half, 1) * 1000, 3),
        "violations": w.violations,
        "pred_late": summary.pred_error_late,
        "population": summary.final_population,
        "pulse_err": round(float(rec.err_sum[-1] / max(rec.n, 1)), 6),
        "progress_err": round(float(rec.err_sum[-2] / max(rec.n, 1)), 6),
        "enc_err": round(float(rec.err_sum[:-2].mean() / max(rec.n, 1)), 6),
        "completions": inner.completions_fired,
        "false_completions": inner.false_completions,
    }
    if RUN["stores"]:
        store = RUN["stores"][0]
        t2 = store.t2
        b = t2.best()
        bb = store._base_best()
        row.update(
            {
                "base_best_pred_ema": (
                    None if bb is None else round(float(bb[0].pred_err_ema[bb[1]]), 6)
                ),
                "t2_population": t2.population_size,
                "t2_map_rate": round(t2.mapped_steps / max(t2.total_steps, 1), 4),
                "t2_best_pred_ema": (
                    None if b is None else round(float(b[0].pred_err_ema[b[1]]), 6)
                ),
                "t2_best_task_ema": (
                    None if b is None else round(t2.task_ema.get(b[2], 1.0), 6)
                ),
                "arb_t2_share": round(store.arb_t2 / max(store.arb_total, 1), 4),
            }
        )
        if frames_mode == "bind-pred":
            alive = set()
            for g in store._groups.values():
                alive.update(int(f) for f in g.frame_ids)
            dangling = sum(
                1
                for g in t2._groups.values()
                for i in range(g.size)
                if int(g.ref_ids[i]) >= 0 and int(g.ref_ids[i]) not in alive
            )
            row["orphan_events"] = store.orphan_events
            row["dangling_now"] = dangling
    return row


def calib(family: str, rung: int, encoding: str, frames_mode: str, n_cycles: int,
          n_seeds: int = SEEDS, out_tag: str | None = None) -> None:
    tag = out_tag or f"{family}{rung}-{encoding}-{frames_mode}"
    out = RIG / f"calib-{tag}-c{n_cycles}.jsonl"
    if out.exists():
        raise SystemExit(f"{out} exists — one reading per config; move it aside to re-run")
    rows = []
    with out.open("a") as f:
        for seed in range(n_seeds):
            row = run_arm(seed, family, rung, encoding, n_cycles, frames_mode)
            rows.append(row)
            f.write(json.dumps(row) + "\n")
            print(json.dumps(row), flush=True)
    rates = sorted(r["accept_per_1k_back"] for r in rows)
    summary = {
        "tag": tag,
        "seeds": n_seeds,
        "accept_per_1k_back_min": rates[0],
        "accept_per_1k_back_median": rates[len(rates) // 2],
        "accept_per_1k_back_max": rates[-1],
        "seeds_with_back_accepts": sum(1 for r in rows if r["accepts_back"] > 0),
    }
    with out.open("a") as f:
        f.write(json.dumps(summary) + "\n")
    print(f"CALIB {json.dumps(summary)}", flush=True)


def main() -> int:
    if len(sys.argv) >= 6 and sys.argv[1] == "calib":
        family = sys.argv[2]
        rung = int(sys.argv[3])
        encoding = sys.argv[4]
        frames_mode = sys.argv[5]
        n_cycles = int(sys.argv[6]) if len(sys.argv) > 6 else 18
        n_seeds = int(sys.argv[7]) if len(sys.argv) > 7 else SEEDS
        tag = None
        if n_seeds != SEEDS:
            tag = f"{family}{rung}-{encoding}-{frames_mode}-pilot{n_seeds}"
        if family not in ("R", "C") or encoding not in ENCODINGS:
            raise SystemExit("usage: compose.py calib R|C <rung> <enc> <frames_mode> [c] [seeds]")
        if frames_mode not in ("flat", "tower", "ref-pose", "ref-pred", "bind-pred"):
            raise SystemExit(f"unknown frames_mode {frames_mode}")
        calib(family, rung, encoding, frames_mode, n_cycles, n_seeds, tag)
        return 0
    raise SystemExit("usage: compose.py calib <family> <rung> <enc> <frames_mode> [c] [seeds]")


if __name__ == "__main__":
    raise SystemExit(main())
