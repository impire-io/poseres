"""T018 — the batched dim-group path equals a straightforward per-frame loop.

This proves the PRA-01 §7.2 optimization changed no behavior: the vectorized
FrameGroup kernel must produce the same weights and outputs as a reference
implementation that applies the v4 oracle's math one frame at a time.
"""

from __future__ import annotations

import numpy as np

from pra.core.frame import FrameGroup

LR = 0.03
CLIP = 1.0


def _clip(x):
    return np.clip(x, -CLIP, CLIP)


def _extract(group: FrameGroup, i: int) -> dict:
    """Copy one frame's weights out of the batched group (per-frame layout)."""
    return {
        name: getattr(group, name)[i].copy()
        for name in ("W1", "b1", "W2", "b2", "Dc1", "dc1", "Dc2", "dc2", "T1", "tb1", "T2", "tb2")
    }


# --- reference per-frame math (a direct port of design/validate/pra_sim_v3.Frame) ---
def ref_encode(w, obs):
    h = np.tanh(w["W1"] @ obs + w["b1"])
    return w["W2"] @ h + w["b2"], h


def ref_reconstruct(w, pose):
    hd = np.tanh(w["Dc1"] @ pose + w["dc1"])
    return w["Dc2"] @ hd + w["dc2"], hd


def ref_predict(w, pose, a):
    h = np.tanh(w["T1"][a] @ pose + w["tb1"][a])
    return w["T2"][a] @ h + w["tb2"][a], h


def ref_fit(w, obs):
    pose, _ = ref_encode(w, obs)
    recon, _ = ref_reconstruct(w, pose)
    return np.linalg.norm(recon - obs) / (np.linalg.norm(obs) + 1e-6)


def ref_honest(w, prev_obs, a, obs):
    ppose, _ = ref_encode(w, prev_obs)
    pnext, _ = ref_predict(w, ppose, a)
    pobs, _ = ref_reconstruct(w, pnext)
    return np.linalg.norm(pobs - obs) / (np.linalg.norm(obs) + 1e-6)


def ref_learn_placement(w, obs):
    pose, h = ref_encode(w, obs)
    recon, hd = ref_reconstruct(w, pose)
    e = recon - obs
    gD2 = _clip(np.outer(e, hd))
    ghd = (w["Dc2"].T @ e) * (1 - hd**2)
    gD1 = _clip(np.outer(ghd, pose))
    w["Dc2"] -= LR * gD2
    w["dc2"] -= LR * _clip(e)
    w["Dc1"] -= LR * gD1
    w["dc1"] -= LR * _clip(ghd)
    gpose = w["Dc1"].T @ ghd  # uses updated Dc1
    gW2 = _clip(np.outer(gpose, h))
    ghe = (w["W2"].T @ gpose) * (1 - h**2)
    gW1 = _clip(np.outer(ghe, obs))
    w["W2"] -= LR * gW2
    w["b2"] -= LR * _clip(gpose)
    w["W1"] -= LR * gW1
    w["b1"] -= LR * _clip(ghe)


def ref_learn_transition(w, prev_obs, a, next_obs, effort_only):
    p, _ = ref_encode(w, prev_obs)
    nxt, _ = ref_encode(w, next_obs)
    pred, h = ref_predict(w, p, a)
    target = np.zeros_like(nxt) if effort_only else nxt
    e = pred - target
    gT2 = _clip(np.outer(e, h))
    gh = (w["T2"][a].T @ e) * (1 - h**2)
    gT1 = _clip(np.outer(gh, p))
    w["T2"][a] -= LR * gT2
    w["tb2"][a] -= LR * _clip(e)
    w["T1"][a] -= LR * gT1
    w["tb1"][a] -= LR * _clip(gh)


def test_batched_equals_per_frame_loop():
    rng = np.random.default_rng(7)
    dim, obs_dim, hidden, n_actions = 3, 10, 12, 4
    group = FrameGroup(dim, obs_dim, hidden, n_actions)
    n_frames = 4
    for fid in range(n_frames):
        group.add_frame(fid, ema_init=1.0, scale=0.3, rng=rng)
    refs = [_extract(group, i) for i in range(n_frames)]

    # A short obs/action stream; learn on every frame (all elect) to exercise both updates.
    for step in range(6):
        prev_obs = rng.standard_normal(obs_dim)
        obs = rng.standard_normal(obs_dim)
        a = int(rng.integers(n_actions))

        # batched: all frames elect
        elect = np.ones(group.size, dtype=bool)
        fit, pose, h, recon, hd = group.fit_quality(obs)
        group.learn_placement(obs, pose, h, recon, hd, elect, LR, CLIP)
        group.learn_transition(prev_obs, a, obs, "predictive", elect, LR, CLIP)
        honest = group.honest_pred_err(prev_obs, a, obs)

        # reference per frame
        ref_fits, ref_honests = [], []
        for w in refs:
            ref_fits.append(ref_fit(w, obs))
            ref_learn_placement(w, obs)
            ref_learn_transition(w, prev_obs, a, obs, False)
            ref_honests.append(ref_honest(w, prev_obs, a, obs))

        assert np.allclose(fit, ref_fits, atol=1e-10), f"fit mismatch @ step {step}"
        assert np.allclose(honest, ref_honests, atol=1e-10), f"honest mismatch @ step {step}"
        for i, w in enumerate(refs):
            for name in ("W1", "W2", "Dc1", "Dc2", "T1", "T2", "b1", "b2"):
                assert np.allclose(getattr(group, name)[i], w[name], atol=1e-10), (
                    f"{name}[{i}] mismatch @ step {step}"
                )


def test_effort_only_branch_matches_reference():
    rng = np.random.default_rng(11)
    dim, obs_dim, hidden, n_actions = 2, 9, 8, 4
    group = FrameGroup(dim, obs_dim, hidden, n_actions)
    for fid in range(3):
        group.add_frame(fid, ema_init=1.0, scale=0.3, rng=rng)
    refs = [_extract(group, i) for i in range(3)]

    for _ in range(4):
        prev_obs = rng.standard_normal(obs_dim)
        obs = rng.standard_normal(obs_dim)
        a = int(rng.integers(n_actions))
        elect = np.ones(group.size, dtype=bool)
        _, pose, h, recon, hd = group.fit_quality(obs)
        group.learn_placement(obs, pose, h, recon, hd, elect, LR, CLIP)
        group.learn_transition(prev_obs, a, obs, "effort_only", elect, LR, CLIP)
        for w in refs:
            ref_learn_placement(w, obs)
            ref_learn_transition(w, prev_obs, a, obs, True)
    for i, w in enumerate(refs):
        assert np.allclose(group.T2[i], w["T2"], atol=1e-10)
        assert np.allclose(group.W1[i], w["W1"], atol=1e-10)
