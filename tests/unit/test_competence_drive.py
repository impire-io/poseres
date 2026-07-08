"""Competence drive (AGENCY-DIAGNOSIS remedy): mastery + familiarity terms."""

from __future__ import annotations

import numpy as np

from pra.config import Config
from pra.motivation.context import DriveContext
from pra.motivation.drive import CompetenceDrive, CuriosityParams, WeightedDriveSet


def _drive():
    return CompetenceDrive(CuriosityParams.from_config(Config()))


def test_mastery_high_when_error_low_and_stable():
    from collections import deque

    d = _drive()
    assert d.mastery([0.1] * 600) > 0.85
    assert d.mastery([0.9] * 600) < 0.15  # unmastered region scores low
    assert d.mastery([0.1] * 5) == 0.0  # silent before enough samples
    # the engine hands the drive a deque — must not rely on slicing
    assert d.mastery(deque([0.1] * 600)) > 0.85


def test_familiarity_prefers_known_territory():
    d = _drive()
    rng = np.random.default_rng(0)
    memory = [rng.standard_normal(10) for _ in range(20)]
    known = memory[4].copy()
    alien = memory[4] + 10.0
    assert d.familiarity(known, memory) > 0.99
    assert d.familiarity(alien, memory) < d.familiarity(known, memory)
    assert d.familiarity(known, []) == 0.0  # silent at cold start (novelty leads)


def test_value_is_finite_from_the_first_step():
    d = _drive()
    ctx = DriveContext(
        observation=np.ones(10),
        recent_pred_errors=[],
        observation_memory=[],
        step_index=0,
    )
    assert np.isfinite(d.value(ctx))


def test_competence_registers_by_configuration_only():
    cfg = Config(drive_weights=(("curiosity", 0.5), ("competence", 0.5)))
    ds = WeightedDriveSet.from_config(cfg)
    assert sorted(d.id() for d in ds.drives) == ["competence", "curiosity"]
    # competence-only configuration works too (the scaled recommendation)
    only = WeightedDriveSet.from_config(Config(drive_weights=(("competence", 1.0),)))
    assert [d.id() for d in only.drives] == ["competence"]


def test_base_configuration_is_unchanged():
    assert Config().drive_weights == (("curiosity", 1.0),)
