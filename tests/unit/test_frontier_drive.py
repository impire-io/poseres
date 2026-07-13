"""FrontierDrive — realized local progress per candidate (PREDLP-DIAGNOSIS)."""

from __future__ import annotations

import numpy as np
import pytest

from pra.config import Config
from pra.motivation.drive import CuriosityParams, FrontierDrive, WeightedDriveSet


def _drive(k: int = 3) -> FrontierDrive:
    return FrontierDrive(CuriosityParams.from_config(Config()), neighbors=k)


def _memory(errs: list[float], base: float = 0.0) -> tuple[list[np.ndarray], list[float]]:
    # observations clustered around `base` so all are neighbors of the probe
    obs = [np.full(10, base) + 0.01 * i for i in range(len(errs))]
    return obs, errs


def test_falling_local_error_is_sought():
    obs, errs = _memory([1.0, 1.0, 1.0, 0.2, 0.2, 0.2])  # older high, newer low
    signal = _drive(k=3).local_progress(np.full(10, 0.0), obs, errs)
    assert signal == pytest.approx(0.8)


def test_flat_error_is_silent_high_and_low():
    for level in (1.0, 0.05):
        obs, errs = _memory([level] * 6)
        assert _drive(k=3).local_progress(np.full(10, 0.0), obs, errs) == 0.0


def test_rising_error_clamps_to_zero():
    obs, errs = _memory([0.2, 0.2, 0.2, 1.0, 1.0, 1.0])
    assert _drive(k=3).local_progress(np.full(10, 0.0), obs, errs) == 0.0


def test_silent_until_enough_finite_samples():
    obs, errs = _memory([1.0, np.nan, 1.0, 0.2, np.nan, 0.2])
    # only 4 finite entries < 2k = 6
    assert _drive(k=3).local_progress(np.full(10, 0.0), obs, errs) == 0.0
    obs, errs = _memory([1.0, 1.0])
    assert _drive(k=3).local_progress(np.full(10, 0.0), obs, errs) == 0.0


def test_locality_prefers_the_frontier_region():
    """Two regions: one mastered-flat, one improving. A candidate near the
    improving region scores higher than one near the flat region."""
    drive = _drive(k=3)
    flat_obs = [np.full(10, 0.0) + 0.01 * i for i in range(6)]
    flat_errs = [0.1] * 6
    frontier_obs = [np.full(10, 5.0) + 0.01 * i for i in range(6)]
    frontier_errs = [1.0, 1.0, 1.0, 0.3, 0.3, 0.3]
    # interleave region visits to keep recency comparable
    memory, errors = [], []
    for a, b, ea, eb in zip(flat_obs, frontier_obs, flat_errs, frontier_errs, strict=True):
        memory += [a, b]
        errors += [ea, eb]
    near_frontier = drive.local_progress(np.full(10, 5.0), memory, errors)
    near_flat = drive.local_progress(np.full(10, 0.0), memory, errors)
    assert near_frontier > near_flat
    assert near_flat == 0.0


def test_registry_builds_frontier_and_blends():
    ds = WeightedDriveSet.from_config(Config(drive_weights=(("frontier", 1.0),)))
    assert [d.id() for d in ds.drives] == ["frontier"]
    blend = WeightedDriveSet.from_config(
        Config(drive_weights=(("frontier", 0.5), ("competence", 0.5)))
    )
    assert sorted(d.id() for d in blend.drives) == ["competence", "frontier"]
    with pytest.raises(ValueError, match="unknown drive"):
        WeightedDriveSet.from_config(Config(drive_weights=(("boredom", 1.0),)))


def test_frontier_neighbors_validated():
    with pytest.raises(ValueError, match="frontier_neighbors"):
        Config(frontier_neighbors=0)
