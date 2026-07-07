"""T007 — lookahead policy: argmax, tie-break, ε-gate, maturity gate, draw order."""

from __future__ import annotations

import numpy as np

from pra.action.policy import CuriosityLookaheadPolicy, PolicyContext, PolicyParams, RandomPolicy


def _ctx(values_by_action, best_frame_age=10, n_actions=4):
    predictions = {a: np.full(3, float(a)) for a in range(n_actions)}

    def predict(a):
        return predictions[a]

    def value_of(obs):
        return values_by_action[int(obs[0])]

    return PolicyContext(
        observation=np.zeros(3),
        n_actions=n_actions,
        best_frame_age=best_frame_age,
        predict_decoded=predict,
        drive_value_of=value_of,
    )


def _policy(epsilon=0.0, min_age=2):
    return CuriosityLookaheadPolicy(
        PolicyParams(exploration_epsilon=epsilon, lookahead_min_age_cycles=min_age)
    )


def test_argmax_selects_highest_valued_action():
    ctx = _ctx({0: 0.1, 1: 0.9, 2: 0.4, 3: 0.2})
    p = _policy(epsilon=0.0)
    assert p.select_action(ctx, np.random.default_rng(0)) == 1
    assert p.last_was_directed


def test_ties_break_to_lowest_action_index():
    ctx = _ctx({0: 0.5, 1: 0.9, 2: 0.9, 3: 0.9})
    p = _policy(epsilon=0.0)
    assert p.select_action(ctx, np.random.default_rng(0)) == 1  # first of the tied max


def test_epsilon_gate_takes_random_action():
    ctx = _ctx({0: 0.0, 1: 1.0, 2: 0.0, 3: 0.0})
    p = _policy(epsilon=1.0)  # always explore
    rng = np.random.default_rng(0)
    picks = {p.select_action(ctx, rng) for _ in range(30)}
    assert len(picks) > 1  # not pinned to the argmax
    assert not p.last_was_directed


def test_maturity_gate_forces_random_when_young_or_absent():
    p = _policy(epsilon=0.0, min_age=5)
    young = _ctx({a: float(a) for a in range(4)}, best_frame_age=1)
    none_ctx = _ctx({a: float(a) for a in range(4)}, best_frame_age=None)
    rng = np.random.default_rng(0)
    p.select_action(young, rng)
    assert not p.last_was_directed
    p.select_action(none_ctx, rng)
    assert not p.last_was_directed


def test_fixed_draw_order_exploit_consumes_one_uniform_only():
    # Exploit path: exactly one rng.random() (the ε-gate), no integer draw.
    ctx = _ctx({0: 0.1, 1: 0.9, 2: 0.4, 3: 0.2})
    p = _policy(epsilon=0.0)
    rng_a = np.random.default_rng(7)
    rng_b = np.random.default_rng(7)
    p.select_action(ctx, rng_a)
    rng_b.random()  # replicate the single expected draw
    assert rng_a.integers(1000) == rng_b.integers(1000)  # streams still aligned


def test_random_policy_consumes_exactly_the_baseline_draw():
    ctx = _ctx({a: 0.0 for a in range(4)})
    rng_a = np.random.default_rng(3)
    rng_b = np.random.default_rng(3)
    a = RandomPolicy().select_action(ctx, rng_a)
    b = int(rng_b.integers(4))  # the validated engine's inline draw
    assert a == b
    assert rng_a.integers(1000) == rng_b.integers(1000)  # identical stream position
