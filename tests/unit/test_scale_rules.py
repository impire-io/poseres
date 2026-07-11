"""Scale-invariant parameter rules: exactly the raw constants at the reference.

The four rules (world emission normalization, effective learning rate, fan-in
init factors, effective parsimony) must all reduce to factor 1.0 at the validated
reference scale (obs_dim=10, hidden=12, true_dim=3) — the reference behavior is
byte-identical — and must move in the documented direction at scale.
"""

from __future__ import annotations

import numpy as np

from pra.config import HIDDEN_REF, OBS_DIM_REF, TRUE_DIM_REF, Config
from pra.core.frame import FrameGroup
from pra.core.scorer import WeightedSumScorer
from pra.world.event_source import SensorimotorWorld


def test_reference_constants_match_spec_defaults():
    cfg = Config()
    assert (cfg.obs_dim, cfg.hidden_size, cfg.true_dim) == (OBS_DIM_REF, HIDDEN_REF, TRUE_DIM_REF)


def test_effective_params_are_raw_at_reference():
    cfg = Config()
    assert cfg.effective_learning_rate == cfg.learning_rate == 0.03
    assert cfg.effective_w_complexity == cfg.w_complexity == 0.04
    assert cfg.effective_min_age_cycles == cfg.min_age_cycles == 2


def test_effective_params_shrink_at_scale():
    cfg = Config(true_dim=20, obs_dim=60)
    assert np.isclose(cfg.effective_learning_rate, 0.03 * (10 / 60) ** 1.5)
    assert np.isclose(cfg.effective_w_complexity, 0.04 * 10 / 60)
    assert cfg.effective_learning_rate < cfg.learning_rate
    assert cfg.effective_w_complexity < cfg.w_complexity
    # patience GROWS with scale by the inverse of the lr factor: 2·6^1.5 ≈ 29
    assert cfg.effective_min_age_cycles == 29


def test_world_emission_regime_is_scale_invariant():
    # The property the sqrt(true_dim/TRUE_DIM_REF) normalization guarantees: the
    # emission pre-activation distribution over an episode (40 steps, like the
    # live schedule) is the SAME at every true_dim as at the validated reference.
    # Unnormalized, saturation grows with sqrt(true_dim) instead.
    def saturation(true_dim: int) -> float:
        cfg = Config(true_dim=true_dim, obs_dim=3 * true_dim, sensor_noise_std=0.0)
        rng = np.random.default_rng(0)
        w = SensorimotorWorld(cfg, rng)
        vals = []
        for _ in range(50):  # 50 episodes x 40 steps, resets included
            vals.append(w.reset())
            for _ in range(40):
                vals.append(w.step(int(rng.integers(w.n_actions))))
        arr = np.abs(np.concatenate(vals))
        return float(np.mean(arr > np.tanh(2.0)))

    # Measured: 0.77 / 0.70 / 0.75 at true_dim 3 / 20 / 50 — equal up to
    # world-draw sampling noise (each config draws its own emission matrices).
    # Unnormalized, true_dim=20 sits near 0.9 and grows with sqrt(true_dim).
    ref = saturation(TRUE_DIM_REF)
    assert abs(saturation(20) - ref) < 0.10
    assert abs(saturation(50) - ref) < 0.10


def test_init_factors_are_one_at_reference_and_shrink_at_scale():
    def w1_std(obs_dim: int, hidden: int) -> float:
        g = FrameGroup(3, obs_dim, hidden, 4)
        g.add_frame(0, 1.0, 0.3, np.random.default_rng(0))
        return float(g.W1[0].std())

    # reference: raw scale 0.3
    assert np.isclose(w1_std(OBS_DIM_REF, HIDDEN_REF), 0.3, atol=0.05)
    # at obs_dim=60 the encoder init shrinks by sqrt(10/60)
    assert np.isclose(w1_std(60, HIDDEN_REF), 0.3 * np.sqrt(10 / 60), atol=0.02)


def test_scorer_uses_effective_parsimony():
    scaled = WeightedSumScorer(Config(true_dim=20, obs_dim=60))
    # score difference between dim 20 and dim 2 = w_eff * 18
    diff = float(scaled.combine(0.5, 0.5, 0.0, 20) - scaled.combine(0.5, 0.5, 0.0, 2))
    assert np.isclose(diff, (0.04 * 10 / 60) * 18)


def test_conveyor_correction_is_conditional_on_the_fair_judge():
    # THRESHOLD-DIAGNOSIS: the seventh rule is the conveyor correction — the
    # youth-protected stock (spawn_per_cycle x patience) does not tighten the
    # bar. Raw baseline at the reference (either judge: patience is raw there),
    # raw at scale under all-step scoring (the reopened niche is colonized by
    # tracking-flattered low dims), corrected only with the fair judge on.
    assert Config().effective_survive_threshold_pop_baseline == 4
    assert Config(score_window_steps=5).effective_survive_threshold_pop_baseline == 4
    scaled_raw = Config(true_dim=20, obs_dim=60, hidden_size=40)
    assert scaled_raw.effective_survive_threshold_pop_baseline == 4
    scaled_fair = scaled_raw.replace(score_window_steps=5)
    # patience 29 at obs=60: baseline 4 + 1*(29 - 2) = 31
    assert scaled_fair.effective_survive_threshold_pop_baseline == 31


def test_score_window_gates_ema_updates_only():
    # ema_update=False: the step still learns and reports, but survival EMAs
    # do not advance — the fair judge ignores within-episode tracking.
    from pra.core.frame import FrameStore

    cfg = Config()
    rng = np.random.default_rng(3)
    store = FrameStore(cfg, rng)
    store.birth(3, ema_init=0.9)
    obs1 = rng.normal(size=cfg.obs_dim)
    obs2 = rng.normal(size=cfg.obs_dim)

    store.online_step(obs1, None, None, "predictive", ema_update=False)
    stats = store.online_step(obs2, obs1, 0, "predictive", ema_update=False)
    g = next(iter(store._groups.values()))
    assert float(g.recon_err_ema[0]) == 0.9  # untouched
    assert float(g.pred_err_ema[0]) == 0.9
    assert stats.alive == 1  # the step itself ran (telemetry intact)

    store.online_step(obs2, obs1, 0, "predictive", ema_update=True)
    assert float(g.recon_err_ema[0]) != 0.9  # now they advance
    assert float(g.pred_err_ema[0]) != 0.9
