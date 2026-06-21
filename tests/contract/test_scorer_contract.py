"""T014 — Scorer seam: a substitute scorer changes which frame is "best"."""

from __future__ import annotations

import numpy as np

from pra.config import Config
from pra.core.frame import FrameStore
from pra.core.scorer import WeightedSumScorer


class ErrorOnlyScorer:
    """A substitute with no parsimony term (w_complexity = 0)."""

    def combine(self, recon_err_ema, pred_err_ema, effort_ema, dim):
        recon = np.asarray(recon_err_ema, dtype=np.float64)
        pred = np.asarray(pred_err_ema, dtype=np.float64)
        return 0.5 * recon + 0.5 * pred


def test_substitute_scorer_changes_the_winner_with_no_other_edit():
    store = FrameStore(Config(), np.random.default_rng(0))
    # frame A: low dim (2), slightly higher error; frame B: high dim (9), lower error.
    fid_a = store.birth(dim=2, ema_init=1.0)
    fid_b = store.birth(dim=9, ema_init=1.0)
    ga = store._groups[2]
    gb = store._groups[9]
    ga.recon_err_ema[:] = 0.30
    ga.pred_err_ema[:] = 0.30
    gb.recon_err_ema[:] = 0.20
    gb.pred_err_ema[:] = 0.20

    # With parsimony (w_complexity=0.04): A = 0.30 + 0.08 = 0.38; B = 0.20 + 0.36 = 0.56
    # -> A wins. Without parsimony: A = 0.30, B = 0.20 -> B wins.
    parsimony_winner = store.best_frame(WeightedSumScorer(Config()))
    error_only_winner = store.best_frame(ErrorOnlyScorer())

    assert parsimony_winner[0] == fid_a
    assert error_only_winner[0] == fid_b
