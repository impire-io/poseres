"""T008 — frame I/O resize (Doc 03 §7): preservation, fresh slices, determinism."""

from __future__ import annotations

import numpy as np

from pra.config import Config
from pra.core.frame import FrameStore


def _store(seed=3):
    store = FrameStore(Config(), np.random.default_rng(seed))
    for d in (2, 3, 3):
        store.birth(dim=d, ema_init=1.0)
    return store


def _tensors(store):
    return {
        (dim, name): np.array(getattr(g, name), copy=True)
        for dim, g in store._groups.items()
        for name in ("W1", "b1", "W2", "b2", "Dc1", "dc1", "Dc2", "dc2", "T1", "tb1", "T2", "tb2")
    }


def test_obs_growth_preserves_learned_entries_bitwise():
    store = _store()
    before = _tensors(store)
    store.resize(13, 4, np.random.default_rng(99))  # obs 10 -> 13
    for dim, g in store._groups.items():
        assert g.W1.shape[2] == 13 and g.Dc2.shape[1] == 13 and g.dc2.shape[1] == 13
        assert np.array_equal(g.W1[:, :, :10], before[(dim, "W1")])  # bit-preserved
        assert np.array_equal(g.Dc2[:, :10, :], before[(dim, "Dc2")])
        assert np.array_equal(g.dc2[:, :10], before[(dim, "dc2")])
        assert np.any(g.W1[:, :, 10:] != 0)  # fresh slices drawn, not zeros
        assert np.all(g.dc2[:, 10:] == 0)  # new biases zero
        # untouched tensors identical
        for name in ("W2", "b2", "Dc1", "dc1", "T1", "tb1", "T2", "tb2", "b1"):
            assert np.array_equal(getattr(g, name), before[(dim, name)]), name
    assert store.obs_dim == 13


def test_action_growth_and_shrink():
    store = _store()
    before = _tensors(store)
    store.resize(10, 6, np.random.default_rng(5))  # actions 4 -> 6
    for dim, g in store._groups.items():
        assert g.T1.shape[1] == 6 and g.T2.shape[1] == 6
        assert np.array_equal(g.T1[:, :4], before[(dim, "T1")])
        assert np.any(g.T1[:, 4:] != 0)
        assert np.all(g.tb1[:, 4:] == 0)
    store.resize(10, 3, np.random.default_rng(5))  # shrink 6 -> 3: trailing discarded
    for dim, g in store._groups.items():
        assert g.T1.shape[1] == 3
        assert np.array_equal(g.T1, before[(dim, "T1")][:, :3])
    assert store.n_actions == 3


def test_obs_shrink_discards_trailing():
    store = _store()
    before = _tensors(store)
    store.resize(7, 4, np.random.default_rng(0))
    for dim, g in store._groups.items():
        assert g.W1.shape[2] == 7
        assert np.array_equal(g.W1, before[(dim, "W1")][:, :, :7])


def test_resize_draws_are_deterministic():
    a, b = _store(), _store()
    a.resize(14, 6, np.random.default_rng(42))
    b.resize(14, 6, np.random.default_rng(42))
    for dim in a._groups:
        assert np.array_equal(a._groups[dim].W1, b._groups[dim].W1)
        assert np.array_equal(a._groups[dim].T2, b._groups[dim].T2)


def test_births_after_resize_use_current_dims_and_lr_tracks():
    store = _store()
    lr_before = store._lr
    store.resize(20, 5, np.random.default_rng(1))
    fid = store.birth(dim=4, ema_init=1.0)
    g = store._groups[4]
    assert g.W1.shape[2] == 20 and g.T1.shape[1] == 5
    assert store._lr < lr_before  # effective lr re-derived at the wider obs (§8.8)
    assert fid == 3
