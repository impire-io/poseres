"""T019 — weighted-sum survival score + parsimony term, tie-break by frame_id."""

from __future__ import annotations

import numpy as np

from pra.config import Config
from pra.core.frame import FrameStore
from pra.core.scorer import WeightedSumScorer


def test_weighted_sum_with_parsimony():
    cfg = Config(w_explain=0.5, w_predict=0.5, w_effort=0.0, w_complexity=0.04)
    s = WeightedSumScorer(cfg)
    # 0.5*0.2 + 0.5*0.3 + 0 + 0.04*3 = 0.1 + 0.15 + 0.12 = 0.37
    val = float(s.combine(0.2, 0.3, 0.0, 3))
    assert abs(val - 0.37) < 1e-12


def test_parsimony_penalizes_higher_dim():
    s = WeightedSumScorer(Config())
    low = float(s.combine(0.3, 0.3, 0.0, 2))
    high = float(s.combine(0.3, 0.3, 0.0, 8))
    assert high > low  # same errors, higher dim scores worse


def test_combine_is_vectorized():
    s = WeightedSumScorer(Config())
    recon = np.array([0.1, 0.2, 0.3])
    out = s.combine(recon, recon, np.zeros(3), np.array([1, 2, 3]))
    assert out.shape == (3,)
    assert np.allclose(out, 0.5 * recon + 0.5 * recon + 0.04 * np.array([1, 2, 3]))


def test_best_frame_tie_break_is_lowest_frame_id():
    cfg = Config()
    rng = np.random.default_rng(0)
    store = FrameStore(cfg, rng)
    # three frames of the same dim; force identical EMAs so scores tie exactly.
    for _ in range(3):
        store.birth(dim=3, ema_init=1.0)
    g = store._groups[3]
    g.recon_err_ema[:] = 0.5
    g.pred_err_ema[:] = 0.5
    g.effort_ema[:] = 0.0
    fid, dim, score = store.best_frame(WeightedSumScorer(cfg))
    assert fid == int(g.frame_ids.min())  # ties resolved to ascending frame_id
    assert dim == 3
