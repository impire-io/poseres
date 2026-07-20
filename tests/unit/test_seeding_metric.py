"""Brain-seeding metric unit tests (feature 028): time-to-threshold with
censoring, trailing smoothing, and the paired ±1.9·SE margin form. Pure
functions — no engine, no RNG."""

from __future__ import annotations

import numpy as np

from pra.harness.seeding import (
    NONINFERIORITY_T,
    _delta_margin,
    _margin,
    _noninferior,
    _smooth,
    _superiority,
    _time_to_threshold,
)


def test_smooth_trailing_window():
    traj = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    out = _smooth(traj, 2)
    # partial at the start (window grows to w): [1, 1.5, 2.5, 3.5, 4.5]
    assert np.allclose(out, [1.0, 1.5, 2.5, 3.5, 4.5])


def test_smooth_window_one_is_identity():
    traj = np.array([0.3, 0.9, 0.1])
    assert np.allclose(_smooth(traj, 1), traj)


def test_time_to_threshold_first_crossing():
    # smoothed (w=1) crosses 0.30 first at index 3
    traj = np.array([0.9, 0.7, 0.5, 0.29, 0.2])
    tau, reached = _time_to_threshold(traj, 0.30, 1, n_censor=len(traj))
    assert reached is True
    assert tau == 3


def test_time_to_threshold_censored_when_never_reached():
    traj = np.array([0.9, 0.8, 0.85, 0.82])
    tau, reached = _time_to_threshold(traj, 0.30, 1, n_censor=len(traj))
    assert reached is False
    assert tau == len(traj)


def test_time_to_threshold_respects_censor_length():
    # crosses at index 4, but the common censor length is 3 -> censored
    traj = np.array([0.9, 0.8, 0.7, 0.6, 0.1])
    tau, reached = _time_to_threshold(traj, 0.30, 1, n_censor=3)
    assert reached is False
    assert tau == 3


def test_margin_pairs_by_seed_positive_is_seeded_faster():
    seeded = {1: 10, 2: 20, 3: 30}
    fresh = {1: 40, 2: 25, 3: 90}  # fresh slower (higher tau) => positive margin
    m = _margin("margin1", seeded, fresh)
    assert m.per_seed == [30.0, 5.0, 60.0]
    assert m.n == 3
    assert m.n_better == 3
    assert m.mean > 0


def test_margin_only_uses_common_seeds():
    m = _margin("m", {1: 10, 2: 20}, {1: 15})  # only seed 1 paired
    assert m.n == 1
    assert m.per_seed == [5.0]


def test_superiority_and_noninferiority_bounds():
    # a strongly positive, low-variance margin clears the +1.9·SE superiority bar
    seeded = {s: 0 for s in range(1, 9)}
    fresh = {s: 100 + (s % 2) for s in range(1, 9)}
    m = _margin("m", seeded, fresh)
    assert _superiority(m) is True
    assert _noninferior(m) is True

    # a margin centered on zero with spread is noninferior but not superior
    zero = _margin(
        "m", {s: 0 for s in range(1, 9)}, {s: (10 if s % 2 else -10) for s in range(1, 9)}
    )
    assert _superiority(zero) is False
    assert _noninferior(zero) is True

    # a strongly negative margin fails both
    neg = _margin("m", {s: 100 for s in range(1, 9)}, {s: 0 for s in range(1, 9)})
    assert _superiority(neg) is False
    assert _noninferior(neg) is False


def test_noninferiority_t_is_the_repo_form():
    assert NONINFERIORITY_T == 1.9


def test_delta_margin_is_paired_difference_of_margins():
    # margin1 and margin2 are paired over the same sorted seeds; delta = m2 - m1.
    seeded_b = {1: 10, 2: 20, 3: 30}
    fresh_b = {1: 40, 2: 60, 3: 50}  # margin1 = [30, 40, 20]
    seeded_c = {1: 5, 2: 10, 3: 15}
    fresh_c = {1: 45, 2: 90, 3: 45}  # margin2 = [40, 80, 30]
    m1 = _margin("margin1", seeded_b, fresh_b)
    m2 = _margin("margin2", seeded_c, fresh_c)
    d = _delta_margin(m2, m1)
    assert d.per_seed == [10.0, 40.0, 10.0]  # 40-30, 80-40, 30-20
    assert d.n == 3
    assert d.n_better == 3


def test_c1_combination_superiority_and_nonshrink():
    # C1 = margin2 superior AND delta non-shrink. A margin2 that is strongly
    # positive and a delta that does not drop below -1.9*SE both hold.
    seeded_b = {s: 100 for s in range(1, 9)}
    fresh_b = {s: 200 for s in range(1, 9)}  # margin1 = +100 each
    seeded_c = {s: 100 for s in range(1, 9)}
    fresh_c = {s: 210 + (s % 2) for s in range(1, 9)}  # margin2 ~ +110, delta ~ +10
    m1 = _margin("margin1", seeded_b, fresh_b)
    m2 = _margin("margin2", seeded_c, fresh_c)
    d = _delta_margin(m2, m1)
    assert _superiority(m2) is True
    assert _noninferior(d) is True  # non-shrink: delta not significantly negative
