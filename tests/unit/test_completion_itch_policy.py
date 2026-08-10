"""Feature 040 — CompletionItchPolicy: the measured G3 selection semantics
(draw order, gates, candidate-skip, completion rule, ties) plus the honesty
watch, against stubbed contexts only."""

from __future__ import annotations

import numpy as np
import pytest

from pra.action.policy import (
    CompletionItchPolicy,
    CuriosityLookaheadPolicy,
    PolicyContext,
    PolicyParams,
)
from pra.anatomy.minecraft import C1_MINING_INDEX, C1_POCKET_TOTAL_INDEX, C1_SENSORS

PARAMS = PolicyParams(exploration_epsilon=0.1, lookahead_min_age_cycles=2)
NEVER_EXPLORE = PolicyParams(exploration_epsilon=0.0, lookahead_min_age_cycles=2)


def _policy(params: PolicyParams = NEVER_EXPLORE, **kw):
    defaults = dict(kappa=0.25, progress_index=2, pocket_index=3)
    defaults.update(kw)
    return CompletionItchPolicy(params, **defaults)


def _ctx(
    obs=None,
    n_actions=3,
    age=10,
    predict=None,
    drive=None,
    event=None,
):
    obs = np.zeros(6) if obs is None else obs
    kwargs = dict(
        observation=obs,
        n_actions=n_actions,
        best_frame_age=age,
        predict_decoded=predict or (lambda a: obs),
        drive_value_of=drive or (lambda o: 0.0),
    )
    if event is not None:
        kwargs["predict_event_delta"] = event
    return PolicyContext(**kwargs)


# --- draw order and gates ----------------------------------------------------


def test_draw_order_parity_with_curiosity_lookahead():
    """With the itch inert (default context: event head off), the policy must
    consume the RNG exactly as the shipped curiosity lookahead does."""
    params = PolicyParams(exploration_epsilon=0.5, lookahead_min_age_cycles=2)
    a_pol = CuriosityLookaheadPolicy(params)
    b_pol = CompletionItchPolicy(params, kappa=0.25, progress_index=2, pocket_index=3)
    rng_a = np.random.default_rng(42)
    rng_b = np.random.default_rng(42)
    drive = lambda o: float(o[0])  # noqa: E731 - one-line stub
    obs = np.arange(6, dtype=float)
    ctx = _ctx(obs=obs, drive=drive)
    actions_a = [a_pol.select_action(ctx, rng_a) for _ in range(100)]
    actions_b = [b_pol.select_action(ctx, rng_b) for _ in range(100)]
    assert actions_a == actions_b
    assert rng_a.bit_generator.state == rng_b.bit_generator.state


def test_epsilon_gate_explores():
    p = _policy(params=PolicyParams(exploration_epsilon=1.0, lookahead_min_age_cycles=2))
    picks = {p.select_action(_ctx(), np.random.default_rng(s)) for s in range(20)}
    assert p.last_was_directed is False
    assert len(picks) > 1  # uniform draws, not the argmax


def test_maturity_gate_randomizes_when_young():
    p = _policy()
    p.select_action(_ctx(age=None), np.random.default_rng(0))
    assert p.last_was_directed is False
    p.select_action(_ctx(age=1), np.random.default_rng(0))
    assert p.last_was_directed is False
    p.select_action(_ctx(age=2), np.random.default_rng(0))
    assert p.last_was_directed is True


def test_candidate_skip_and_lowest_index_ties():
    # action 0 unpredicted by the frames -> skipped even if its itch would win;
    # remaining actions tie -> lowest surviving index wins.
    p = _policy()
    ctx = _ctx(predict=lambda a: None if a == 0 else np.zeros(6))
    assert p.select_action(ctx, np.random.default_rng(0)) == 1


# --- the itch and the completion rule ---------------------------------------


def test_itch_arithmetic_and_clipping():
    obs = np.zeros(6)
    obs[2] = 0.9  # progress_now
    deltas = {
        0: np.zeros(6),  # progress_after = 0.9 -> itch 0
        1: np.array([0, 0, 0.3, 0, 0, 0.0]),  # clipped to 1.0 -> itch 0.25*(0.1)
        2: np.array([0, 0, -2.0, 0, 0, 0.0]),  # clipped to 0.0 -> itch 0.25*(-0.9)
    }
    p = _policy()
    ctx = _ctx(obs=obs, event=lambda a: deltas[a])
    assert p.select_action(ctx, np.random.default_rng(0)) == 1


def test_completion_rule_fires_strictly_above_threshold():
    obs = np.zeros(6)
    obs[2] = 0.5
    at = np.zeros(6)
    at[3] = 1.0 / 128.0  # exactly the threshold: NOT a completion
    above = np.zeros(6)
    above[3] = 1.5 / 128.0  # above: completion -> progress_after = 1.0
    p = _policy()
    ctx = _ctx(obs=obs, event=lambda a: {0: at, 1: above, 2: np.zeros(6)}[a])
    assert p.select_action(ctx, np.random.default_rng(0)) == 1
    assert p.completions_fired == 1


def test_head_off_reduces_to_drive_plus_potential():
    drive = lambda o: 0.0  # noqa: E731 - one-line stub
    p = _policy(potential_of=lambda a: {0: 0.1, 1: 0.9, 2: 0.2}[a])
    assert p.select_action(_ctx(drive=drive), np.random.default_rng(0)) == 1


# --- the honesty watch -------------------------------------------------------


def test_false_completion_is_counted_against_the_next_observation():
    obs = np.zeros(6)
    fires = np.zeros(6)
    fires[3] = 1.0  # predicted pocket gain: fires the completion rule
    p = _policy()
    ctx = _ctx(obs=obs, event=lambda a: fires)
    p.select_action(ctx, np.random.default_rng(0))
    assert p.completions_fired == 1 and p.false_completions == 0
    # next observation shows NO realized pocket gain -> false completion
    p.select_action(_ctx(obs=np.zeros(6), event=lambda a: np.zeros(6)), np.random.default_rng(0))
    assert p.false_completions == 1


def test_progress_error_ema_tracks_prediction_miss():
    obs = np.zeros(6)
    delta = np.zeros(6)
    delta[2] = 0.5  # predicts +0.5 progress
    p = _policy()
    p.select_action(_ctx(obs=obs, event=lambda a: delta), np.random.default_rng(0))
    # realized progress delta is 0 -> |0.5 - 0| enters the EMA (decay 0.99)
    p.select_action(_ctx(obs=np.zeros(6), event=lambda a: np.zeros(6)), np.random.default_rng(0))
    assert p.progress_pred_error_ema == pytest.approx(0.01 * 0.5)


def test_watch_is_bounded():
    p = _policy()
    rng = np.random.default_rng(0)
    delta = np.zeros(6)
    delta[2] = 0.1
    for _ in range(500):
        p.select_action(_ctx(event=lambda a: delta), rng)
    # no per-step lists anywhere on the policy
    assert not any(isinstance(v, list) for v in vars(p).values())


# --- construction-time honesty ----------------------------------------------


def test_out_of_range_index_raises_at_first_selection():
    p = _policy(pocket_index=99)
    with pytest.raises(ValueError, match="out of range"):
        p.select_action(_ctx(), np.random.default_rng(0))


def test_c1_channel_constants_are_derived_from_the_specs():
    # independent recomputation from the declaration order
    offset = 0
    expected = {}
    for spec in C1_SENSORS:
        for i, label in enumerate(spec.labels):
            expected[(spec.id, label)] = offset + i
        offset += spec.width
    assert C1_MINING_INDEX == expected[("mining", "progress")] == 14
    assert C1_POCKET_TOTAL_INDEX == expected[("pocket", "total")] == 15


# --- the praise label (feature 041) ------------------------------------------


def test_label_off_is_bit_exact_parity():
    a = _policy()
    b = _policy()  # label defaults off
    obs = np.zeros(6)
    fires = np.zeros(6)
    fires[3] = 1.0
    ra, rb = np.random.default_rng(9), np.random.default_rng(9)
    for _ in range(50):
        ctx = _ctx(obs=obs, event=lambda a_: fires)
        assert a.select_action(ctx, ra) == b.select_action(ctx, rb)
    assert ra.bit_generator.state == rb.bit_generator.state


def test_label_counts_fired_completions_fuller():
    # action 1 completes with applause predicted; action 0 completes without
    deltas = {0: np.zeros(6), 1: np.zeros(6), 2: np.zeros(6)}
    for k in (0, 1):
        deltas[k][3] = 1.0  # both fire the completion rule
    deltas[1][5] = 2.0  # predicted label delta (clipped to 1)
    p = _policy(label_index=5, label_beta=0.5)
    assert p.select_action(_ctx(event=lambda a: deltas[a]), np.random.default_rng(0)) == 1


def test_label_never_read_outside_completions():
    # huge label delta but NO pocket gain: the label must not influence value
    deltas = {0: np.zeros(6), 1: np.zeros(6), 2: np.zeros(6)}
    deltas[1][5] = 5.0
    p = _policy(label_index=5, label_beta=10.0)
    assert p.select_action(_ctx(event=lambda a: deltas[a]), np.random.default_rng(0)) == 0


def test_label_index_validated():
    p = _policy(label_index=99, label_beta=0.5)
    with pytest.raises(ValueError, match="out of range"):
        p.select_action(_ctx(), np.random.default_rng(0))


# --- the deficit gate (feature 042) ------------------------------------------


def test_deficit_off_is_bit_exact_parity():
    a = _policy(label_index=5, label_beta=0.5)
    b = _policy(label_index=5, label_beta=0.5, deficit_index=4, deficit_kappa=0.0)
    obs = np.zeros(6)
    fires = np.zeros(6)
    fires[3] = 1.0
    fires[5] = 1.0
    ra, rb = np.random.default_rng(9), np.random.default_rng(9)
    for _ in range(50):
        ctx = _ctx(obs=obs, event=lambda a_: fires)
        assert a.select_action(ctx, ra) == b.select_action(ctx, rb)
    assert ra.bit_generator.state == rb.bit_generator.state


def test_deficit_weight_arithmetic():
    p = _policy(label_index=5, label_beta=0.1, deficit_index=4, deficit_kappa=0.5)
    obs = np.zeros(6)
    obs[4] = 1.0
    assert p._label_weight(obs) == pytest.approx(0.1)  # sated: the gate is silent
    obs[4] = 0.6
    assert p._label_weight(obs) == pytest.approx(0.1 + 0.5 * 0.4)
    obs[4] = -0.2  # saturated meter: deficit clips to 1
    assert p._label_weight(obs) == pytest.approx(0.1 + 0.5)
    obs[4] = 1.4  # over-full meter: deficit clips to 0
    assert p._label_weight(obs) == pytest.approx(0.1)


def test_deficit_gates_the_completion_read():
    # both actions complete; only action 1 predicts the label. Sated the tie
    # breaks to 0; depleted the gated label term elects 1.
    deltas = {0: np.zeros(6), 1: np.zeros(6), 2: np.zeros(6)}
    for k in (0, 1):
        deltas[k][3] = 1.0
    deltas[1][5] = 1.0
    p = _policy(label_index=5, label_beta=0.0, deficit_index=4, deficit_kappa=0.5)
    sated = np.zeros(6)
    sated[4] = 1.0
    hungry = np.zeros(6)
    hungry[4] = 0.2
    rng = np.random.default_rng(0)
    assert p.select_action(_ctx(obs=sated, event=lambda a: deltas[a]), rng) == 0
    assert p.select_action(_ctx(obs=hungry, event=lambda a: deltas[a]), rng) == 1


def test_deficit_validation():
    with pytest.raises(ValueError, match="deficit_index requires label_index"):
        _policy(deficit_index=4, deficit_kappa=0.1)
    with pytest.raises(ValueError, match="deficit_kappa"):
        _policy(label_index=5, deficit_index=4, deficit_kappa=-0.1)
    with pytest.raises(ValueError, match="deficit_kappa"):
        _policy(label_index=5, deficit_index=4, deficit_kappa=float("nan"))
    p = _policy(label_index=5, deficit_index=99, deficit_kappa=0.1)
    with pytest.raises(ValueError, match="out of range"):
        p.select_action(_ctx(), np.random.default_rng(0))
