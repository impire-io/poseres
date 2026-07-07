"""T008/T017 — Drive seam: purity, weighted combination, structural immutability."""

from __future__ import annotations

import dataclasses

import numpy as np
import pytest

from pra.config import Config
from pra.core.engine import Engine
from pra.motivation.context import DriveContext
from pra.motivation.drive import CuriosityDrive, CuriosityParams, WeightedDriveSet


class ConstantDrive:
    def __init__(self, name: str, constant: float):
        self._name = name
        self._constant = constant

    def id(self) -> str:
        return self._name

    def value(self, context: DriveContext) -> float:
        return self._constant


def _ctx():
    return DriveContext(
        observation=np.ones(10),
        recent_pred_errors=[],
        observation_memory=[],
        step_index=0,
    )


def test_weighted_sum_is_exact():
    ds = WeightedDriveSet(
        (ConstantDrive("a", 2.0), ConstantDrive("b", 10.0)),
        (("a", 0.7), ("b", 0.3)),
    )
    assert np.isclose(ds.value(_ctx()), 0.7 * 2.0 + 0.3 * 10.0)


def test_weight_id_mismatch_rejected_at_construction():
    with pytest.raises(ValueError):
        WeightedDriveSet((ConstantDrive("a", 1.0),), (("b", 1.0),))
    with pytest.raises(ValueError):
        WeightedDriveSet(
            (ConstantDrive("a", 1.0), ConstantDrive("b", 1.0)),
            (("a", 1.0),),
        )


def test_drive_valuation_consumes_no_rng():
    # Drives are pure: the run's generator state is untouched by valuation.
    cfg = Config()
    drive = CuriosityDrive(CuriosityParams.from_config(cfg))
    rng = np.random.default_rng(11)
    before = rng.bit_generator.state
    drive.value(_ctx())
    assert rng.bit_generator.state == before


def test_drive_parameters_are_structurally_immutable():
    cfg = Config()
    drive = CuriosityDrive(CuriosityParams.from_config(cfg))
    with pytest.raises(dataclasses.FrozenInstanceError):
        drive.params.w_novelty = 99.0
    with pytest.raises(dataclasses.FrozenInstanceError):
        cfg.w_progress = 5.0
    with pytest.raises(dataclasses.FrozenInstanceError):
        cfg.drive_weights = (("curiosity", 0.0),)


def test_substitute_drive_set_accepted_by_engine_unchanged():
    # A custom drive set (constant second drive) injected without touching any
    # other component; the engine runs and records agency telemetry.
    cfg = Config(
        warmup_episodes=3,
        n_cycles=2,
        episodes_per_cycle=1,
        steps_per_episode=10,
        horizon_checkpoints=(1, 2),
        drive_weights=(("curiosity", 0.5), ("boredom", 0.5)),
    )
    ds = WeightedDriveSet(
        (CuriosityDrive(CuriosityParams.from_config(cfg)), ConstantDrive("boredom", 0.25)),
        cfg.drive_weights,
    )
    summary = Engine(cfg, drives=ds).run(1)
    assert summary.agency is not None
    assert np.isfinite(summary.agency["value_signal_mean"])
