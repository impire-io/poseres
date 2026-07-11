"""T017 — frame kernel forward maps + per-element gradient clipping."""

from __future__ import annotations

import numpy as np

from pra.core.frame import FrameGroup

LR = 0.03
CLIP = 1.0


def _group(dim=3, obs_dim=10, hidden=12, n_actions=4, n=2, seed=0):
    rng = np.random.default_rng(seed)
    g = FrameGroup(dim, obs_dim, hidden, n_actions)
    for fid in range(n):
        g.add_frame(fid, ema_init=1.0, scale=0.3, rng=rng)
    return g


def test_encode_decode_transition_shapes_and_nonlinearity():
    g = _group()
    obs = np.random.default_rng(1).standard_normal(g.obs_dim)
    pose, h = g.encode(obs)
    assert pose.shape == (g.size, g.dim)
    assert h.shape == (g.size, g.H)
    # hidden passed through tanh -> bounded in (-1, 1)
    assert np.all(np.abs(h) < 1.0)
    recon, hd = g.reconstruct(pose)
    assert recon.shape == (g.size, g.obs_dim)
    assert np.all(np.abs(hd) < 1.0)
    pred, ht = g.predict_next(pose, 1)
    assert pred.shape == (g.size, g.dim)
    assert np.all(np.abs(ht) < 1.0)


def test_encode_matches_manual_single_frame():
    g = _group(n=1, seed=3)
    obs = np.random.default_rng(2).standard_normal(g.obs_dim)
    pose, h = g.encode(obs)
    manual_h = np.tanh(g.W1[0] @ obs + g.b1[0])
    manual_pose = g.W2[0] @ manual_h + g.b2[0]
    assert np.allclose(h[0], manual_h)
    assert np.allclose(pose[0], manual_pose)


def test_gradient_clipping_bounds_each_weight_update():
    g = _group(n=1, seed=5)
    before = g.W1[0].copy()
    # An adversarially large observation drives a big error; per-element clip must
    # still bound every weight delta by lr * clip.
    obs = np.full(g.obs_dim, 50.0)
    fit, pose, h, recon, hd = g.fit_quality(obs)
    g.learn_placement(obs, pose, h, recon, hd, np.array([True]), LR, CLIP)
    delta = np.abs(g.W1[0] - before)
    assert np.all(delta <= LR * CLIP + 1e-12)
    assert np.any(delta > 0)  # it did update


def test_unmapped_frame_is_not_updated():
    g = _group(n=2, seed=8)
    obs = np.random.default_rng(4).standard_normal(g.obs_dim)
    w_before = g.W1.copy()
    fit, pose, h, recon, hd = g.fit_quality(obs)
    elect = np.array([True, False])  # only frame 0 maps
    g.learn_placement(obs, pose, h, recon, hd, elect, LR, CLIP)
    assert np.any(g.W1[0] != w_before[0])  # frame 0 changed
    assert np.array_equal(g.W1[1], w_before[1])  # frame 1 untouched


def test_weight_norm_cap_projects_only_runaway_tensors():
    # LONGEVITY-DIAGNOSIS: per-tensor max-norm control. Healthy tensors are
    # untouched (init norms sit at ~1x the expected value, under a 1.2 cap);
    # an inflated tensor is projected back to exactly the cap; biases never.
    import numpy as np

    from pra.config import Config
    from pra.core.frame import FrameGroup

    cfg = Config()
    rng = np.random.default_rng(5)
    g = FrameGroup(3, cfg.obs_dim, cfg.hidden_size, cfg.n_actions)
    g.add_frame(0, ema_init=1.0, scale=cfg.init_weight_scale, rng=rng)

    before = {n: np.array(getattr(g, n), copy=True) for n in ("W1", "T1", "b1")}
    g.project_norms(1.2, cfg.init_weight_scale)
    for n, w in before.items():
        assert np.array_equal(getattr(g, n), w), f"{n} changed while healthy"

    g.W1 = g.W1 * 10.0  # simulate runaway
    g.b1 = g.b1 + 7.0  # biases are exempt from the cap
    g.project_norms(1.2, cfg.init_weight_scale)
    cap = 1.2 * cfg.init_weight_scale * (cfg.hidden_size * 10) ** 0.5
    assert np.isclose(float(np.linalg.norm(g.W1[0])), cap)
    assert float(g.b1[0][0]) == 7.0
