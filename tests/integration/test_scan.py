"""Dimension-scan diagnostic: runs, covers every (hidden, dim) cell, deterministic."""

from __future__ import annotations

from pra.config import Config
from pra.harness.scan import run_scan


def _base():
    return Config(steps_per_episode=10)


def test_scan_covers_every_cell_with_finite_errors():
    points = run_scan(
        _base(),
        true_dim=3,
        dims=[1, 2, 3],
        hidden_sizes=[8, 12],
        seeds=[1],
        train_episodes=3,
        eval_episodes=2,
    )
    assert len(points) == 6  # 2 hidden sizes x 3 dims
    for p in points:
        assert p.pred_err_mean > 0 and p.recon_err_mean > 0
        # parsimony makes the score exceed the bare error terms.
        assert p.survival_score_mean > 0


def test_scan_is_deterministic_for_a_seed():
    kwargs = dict(
        true_dim=3,
        dims=[1, 3],
        hidden_sizes=[8],
        seeds=[7],
        train_episodes=2,
        eval_episodes=2,
    )
    a = run_scan(_base(), **kwargs)
    b = run_scan(_base(), **kwargs)
    assert [(p.dim, p.pred_err_mean, p.recon_err_mean) for p in a] == [
        (p.dim, p.pred_err_mean, p.recon_err_mean) for p in b
    ]
