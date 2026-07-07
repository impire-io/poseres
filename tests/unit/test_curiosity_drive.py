"""T006/T018 — curiosity drive terms: LP self-limits; novelty finite from step one."""

from __future__ import annotations

import numpy as np

from pra.config import Config
from pra.motivation.context import DriveContext
from pra.motivation.drive import CuriosityDrive, CuriosityParams


def _drive(**overrides):
    cfg = Config(**overrides)
    return CuriosityDrive(CuriosityParams.from_config(cfg))


def test_learning_progress_is_zero_on_mastered_region():
    # flat-low error history: the system has mastered this region — no reward.
    d = _drive()
    history = [0.05] * 600
    assert d.learning_progress(history) < 1e-9


def test_learning_progress_is_zero_on_unlearnable_noise():
    # flat-high error history: unlearnable noise — no reward (the anti-noise-trap).
    d = _drive()
    history = [0.95] * 600
    assert d.learning_progress(history) < 1e-9


def test_learning_progress_positive_on_genuinely_improving_history():
    d = _drive()
    history = list(np.linspace(0.9, 0.2, 600))  # error falling — learning
    assert d.learning_progress(history) > 0.05


def test_learning_progress_zero_before_enough_samples():
    d = _drive()
    assert d.learning_progress([0.9, 0.2, 0.1]) == 0.0  # < lp_recent_window samples


def test_novelty_is_maximal_on_empty_memory():
    d = _drive()
    obs = np.ones(10)
    assert d.novelty(obs, []) == 1.0  # finite and defined from the very first step


def test_novelty_low_for_familiar_high_for_unfamiliar():
    d = _drive()
    rng = np.random.default_rng(0)
    memory = [rng.standard_normal(10) for _ in range(20)]
    familiar = memory[3].copy()
    unfamiliar = memory[3] + 10.0
    assert d.novelty(familiar, memory) < 0.01
    assert d.novelty(unfamiliar, memory) > d.novelty(familiar, memory)


def test_value_combines_terms_with_configured_weights():
    d = _drive(w_progress=2.0, w_novelty=0.5)
    obs = np.ones(10)
    ctx = DriveContext(
        observation=obs,
        recent_pred_errors=list(np.linspace(0.9, 0.2, 600)),
        observation_memory=[],
        step_index=0,
    )
    lp = d.learning_progress(ctx.recent_pred_errors)
    expected = 2.0 * lp + 0.5 * 1.0  # empty memory -> novelty 1.0
    assert np.isclose(d.value(ctx), expected)
    assert np.isfinite(d.value(ctx))
