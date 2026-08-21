"""Factored-actions rig — the embedded-transition machinery (declared
JOURNEY.md 2026-08-21, built rig-side, zero src changes).

`EmbeddedFrameGroup` replaces the per-action transition slices
(T1 (F,A,H,D), T2 (F,A,D,H)) with bilinear forms over an action
embedding e_a in R^E (T1 (F,H,D,E), T2 (F,D,H,E), biases likewise):
every executed act trains the shared tensors, similar acts share
gradient, parameters are O(E) in the vocabulary. The store subclass
carries the event head the same way ((E, obs, obs+1)) and the anchor
table: frozen arm = table constant, learned arm = the table takes
gradient too. With ONE-HOT anchors (E = A) every bilinear form
reduces exactly to per-action slice selection — the self-test below
proves the new math is the old math when the embedding carries no
structure.

    python embed.py selftest      # one-hot parity vs the flat kernel
"""

from __future__ import annotations

import sys

import numpy as np

import pra.core.engine as engine_mod
from pra.config import Config
from pra.core.frame import FrameGroup, FrameStore

B = 4


class Anchors:
    """The shared action-embedding table. Frozen arm: learn=False."""

    def __init__(self, table: np.ndarray, learn: bool = False, lr: float = 0.01):
        self.table = np.array(table, dtype=np.float64)
        self.learn = learn
        self.lr = float(lr)

    @property
    def E(self) -> int:
        return self.table.shape[1]


def factored_anchors(m: int) -> np.ndarray:
    """The declared anchor: [onehot_B(d); position scaled to [-1,1]]."""
    rows = []
    for d in range(B):
        for p in range(m):
            one = np.zeros(B)
            one[d] = 1.0
            rows.append(np.append(one, 2.0 * p / (m - 1) - 1.0))
    return np.array(rows)


def onehot_anchors(a: int) -> np.ndarray:
    return np.eye(a)


class EmbeddedFrameGroup(FrameGroup):
    """Transition-over-embedding variant. Tensor NAMES stay T1/tb1/T2/tb2
    (with embedded shapes) so the inherited remove_rows works untouched;
    add_frame, predict_next, and learn_transition are the overrides."""

    def __init__(self, dim: int, obs_dim: int, hidden: int, n_actions: int, anchors: Anchors):
        super().__init__(dim, obs_dim, hidden, n_actions)
        self.anchors = anchors
        F, H, D, E = 0, hidden, dim, anchors.E
        self.T1 = np.zeros((F, H, D, E))
        self.tb1 = np.zeros((F, H, E))
        self.T2 = np.zeros((F, D, H, E))
        self.tb2 = np.zeros((F, D, E))

    def add_frame(self, frame_id: int, ema_init: float, scale: float, rng) -> None:
        """Same draw sequence as the flat kernel with the transition draws
        reshaped to the embedded layout (per-seed determinism; variant arms
        are never cross-compared step-for-step with flat arms)."""
        from pra.config import HIDDEN_REF, OBS_DIM_REF

        D, H, Od, E = self.dim, self.H, self.obs_dim, self.anchors.E
        f_obs = float(np.sqrt(OBS_DIM_REF / Od))
        f_hid = float(np.sqrt(HIDDEN_REF / H))
        W1 = rng.standard_normal((H, Od)) * (scale * f_obs)
        W2 = rng.standard_normal((D, H)) * (scale * f_hid)
        Dc1 = rng.standard_normal((H, D)) * scale
        Dc2 = rng.standard_normal((Od, H)) * (scale * f_hid)
        T1 = rng.standard_normal((H, D, E)) * scale
        T2 = rng.standard_normal((D, H, E)) * (scale * f_hid)

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
        self.tb1 = np.concatenate([self.tb1, np.zeros((1, H, E))], axis=0)
        self.T2 = np.concatenate([self.T2, T2[None]], axis=0)
        self.tb2 = np.concatenate([self.tb2, np.zeros((1, D, E))], axis=0)

    def resize(self, *args, **kwargs) -> None:
        raise NotImplementedError("the factored-actions arms never resize")

    def predict_next(self, pose: np.ndarray, a: int) -> tuple[np.ndarray, np.ndarray]:
        e = self.anchors.table[a]
        pre = np.einsum("fhde,e,fd->fh", self.T1, e, pose) + np.einsum("fhe,e->fh", self.tb1, e)
        h = np.tanh(pre)
        pred = np.einsum("fdhe,e,fh->fd", self.T2, e, h) + np.einsum("fde,e->fd", self.tb2, e)
        return pred, h

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
        m = elect.astype(np.float64)
        m1 = m[:, None]
        e_vec = self.anchors.table[a]
        p, _ = self.encode(prev_obs, w)
        nxt, _ = self.encode(next_obs, w)
        pred, h = self.predict_next(p, a)
        if scoring_mode == "effort_only":
            target = np.zeros_like(nxt)
        elif scoring_mode == "identity":
            target = p
        else:
            target = nxt
        err = pred - target
        # effective-weight gradients: identical math to the flat kernel,
        # clipped at the effective level so one-hot anchors reproduce the
        # flat updates exactly
        gT2_eff = np.clip(np.einsum("fd,fh->fdh", err, h), -clip, clip)
        T2_eff = np.einsum("fdhe,e->fdh", self.T2, e_vec)  # pre-update, as flat
        gh = np.einsum("fdh,fd->fh", T2_eff, err) * (1.0 - h**2)
        gT1_eff = np.clip(np.einsum("fh,fd->fhd", gh, p), -clip, clip)
        if self.anchors.learn:
            # anchor gradient from pre-update tensors, elect-masked
            dpred_de = np.einsum("fdhe,fh->fde", self.T2, h) + self.tb2
            dpre_de = np.einsum("fhde,fd->fhe", self.T1, p) + self.tb1
            ge = np.einsum("fd,fde->e", err * m1, dpred_de) + np.einsum(
                "fh,fhe->e", gh * m1, dpre_de
            )
            self.anchors.table[a] -= self.anchors.lr * np.clip(ge, -clip, clip)
        m2e = m[:, None, None, None]
        m1e = m[:, None, None]
        self.T2 -= lr * np.einsum("fdh,e->fdhe", gT2_eff, e_vec) * m2e
        self.tb2 -= lr * np.einsum("fd,e->fde", np.clip(err, -clip, clip), e_vec) * m1e
        self.T1 -= lr * np.einsum("fhd,e->fhde", gT1_eff, e_vec) * m2e
        self.tb1 -= lr * np.einsum("fh,e->fhe", np.clip(gh, -clip, clip), e_vec) * m1e


class EmbeddedFrameStore(FrameStore):
    """FrameStore whose groups and event head run over the anchor table."""

    def __init__(self, config: Config, rng, anchors: Anchors):
        self._anchors = anchors  # before super: _eh_init runs in super().__init__
        super().__init__(config, rng)

    def _eh_init(self, obs_dim: int, n_actions: int) -> None:
        self._eh_W = np.zeros((self._anchors.E, obs_dim, obs_dim + 1))
        self._eh_updates = 0

    def event_learn(self, prev_obs: np.ndarray, action: int, obs: np.ndarray) -> None:
        e = self._anchors.table[action]
        x = np.append(prev_obs, 1.0)
        err = (obs - prev_obs) - np.einsum("k,koi->oi", e, self._eh_W) @ x
        denom = float(x @ x) * float(e @ e)
        self._eh_W += self._eh_eta * np.einsum("k,oi->koi", e, np.outer(err, x)) / denom
        self._eh_updates += 1

    def event_predict(self, obs: np.ndarray, action: int) -> np.ndarray:
        e = self._anchors.table[action]
        return np.einsum("k,koi->oi", e, self._eh_W) @ np.append(obs, 1.0)

    def _group_for(self, dim: int) -> FrameGroup:
        g = self._groups.get(dim)
        if g is None:
            g = EmbeddedFrameGroup(
                dim, self.obs_dim, self.config.hidden_size, self.n_actions, self._anchors
            )
            self._groups[dim] = g
        return g


class rebound_store:
    """Context manager: the engine builds EmbeddedFrameStore for one run."""

    def __init__(self, anchors: Anchors):
        self.anchors = anchors

    def __enter__(self):
        self._orig = engine_mod.FrameStore
        anchors = self.anchors
        engine_mod.FrameStore = lambda cfg, rng: EmbeddedFrameStore(cfg, rng, anchors)

    def __exit__(self, *exc):
        engine_mod.FrameStore = self._orig
        return False


def selftest() -> None:
    """One-hot anchors (E = A) must reproduce the flat kernel exactly:
    same weights mapped into the embedded layout, same inputs, same
    predictions and same post-update predictions, machine precision."""
    A, D, H, Od = 12, 3, 12, 12
    flat = FrameGroup(D, Od, H, A)
    emb = EmbeddedFrameGroup(D, Od, H, A, Anchors(onehot_anchors(A)))
    for fid in range(3):
        flat.add_frame(fid, 0.5, 0.1, np.random.default_rng(100 + fid))
        emb.add_frame(fid, 0.5, 0.1, np.random.default_rng(200 + fid))
    # map flat weights into the embedded layout: W[f,...,a] = T[f,a,...]
    emb.W1, emb.b1, emb.W2, emb.b2 = flat.W1, flat.b1, flat.W2, flat.b2
    emb.Dc1, emb.dc1, emb.Dc2, emb.dc2 = flat.Dc1, flat.dc1, flat.Dc2, flat.dc2
    emb.T1 = np.transpose(flat.T1, (0, 2, 3, 1)).copy()
    emb.tb1 = np.transpose(flat.tb1, (0, 2, 1)).copy()
    emb.T2 = np.transpose(flat.T2, (0, 2, 3, 1)).copy()
    emb.tb2 = np.transpose(flat.tb2, (0, 2, 1)).copy()
    step_rng = np.random.default_rng(9)
    elect = np.array([True, True, False])
    for i in range(200):
        prev = step_rng.standard_normal(Od)
        nxt = step_rng.standard_normal(Od)
        a = int(step_rng.integers(A))
        pf, _ = flat.encode(prev)
        pe, _ = emb.encode(prev)
        assert np.allclose(pf, pe)
        prf, _ = flat.predict_next(pf, a)
        pre, _ = emb.predict_next(pe, a)
        assert np.allclose(prf, pre, atol=1e-12), f"predict diverged at step {i}"
        flat.learn_transition(prev, a, nxt, "predictive", elect, 0.05, 1.0)
        emb.learn_transition(prev, a, nxt, "predictive", elect, 0.05, 1.0)
    for a in range(A):
        prf, _ = flat.predict_next(pf, a)
        pre, _ = emb.predict_next(pe, a)
        assert np.allclose(prf, pre, atol=1e-10), f"post-update action {a} diverged"
    # event head parity
    cfg = Config(obs_dim=Od, n_actions=A, event_head_eta=0.2)
    fs = FrameStore(cfg, np.random.default_rng(1))
    es = EmbeddedFrameStore(cfg, np.random.default_rng(1), Anchors(onehot_anchors(A)))
    for _i in range(300):
        prev = step_rng.standard_normal(Od)
        nxt = step_rng.standard_normal(Od)
        a = int(step_rng.integers(A))
        fs.event_learn(prev, a, nxt)
        es.event_learn(prev, a, nxt)
    for a in range(A):
        assert np.allclose(fs.event_predict(prev, a), es.event_predict(prev, a), atol=1e-10)
    print("SELFTEST PASS: one-hot embedded == flat (transition + event head)")


def main() -> int:
    phase = sys.argv[1] if len(sys.argv) > 1 else ""
    if phase == "selftest":
        selftest()
        return 0
    raise SystemExit("usage: embed.py selftest")


if __name__ == "__main__":
    raise SystemExit(main())
