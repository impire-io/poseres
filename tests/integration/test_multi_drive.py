"""T019 — US5: a counter-drive is a configuration, not a code change."""

from __future__ import annotations

import numpy as np
import pytest

from pra.config import Config
from pra.core.engine import Engine
from pra.motivation.context import DriveContext
from pra.motivation.drive import CuriosityDrive, CuriosityParams, WeightedDriveSet


class CompetenceStub:
    """A trivial fixed counter-drive (in tension with curiosity: rewards low,
    stable error). Registered purely via configuration + the drive set."""

    def id(self) -> str:
        return "competence"

    def value(self, context: DriveContext) -> float:
        if len(context.recent_pred_errors) == 0:
            return 0.0
        return max(0.0, 1.0 - float(np.mean(context.recent_pred_errors)))


def test_value_signal_is_exact_weighted_sum_of_two_drives():
    cfg = Config(drive_weights=(("curiosity", 0.6), ("competence", 0.4)))
    curiosity = CuriosityDrive(CuriosityParams.from_config(cfg))
    competence = CompetenceStub()
    ds = WeightedDriveSet((curiosity, competence), cfg.drive_weights)

    ctx = DriveContext(
        observation=np.ones(10),
        recent_pred_errors=[0.3] * 700,
        observation_memory=[np.zeros(10)],
        step_index=700,
    )
    expected = 0.6 * curiosity.value(ctx) + 0.4 * competence.value(ctx)
    assert np.isclose(ds.value(ctx), expected)


def test_engine_accepts_configured_two_drive_set_without_code_change():
    cfg = Config(
        warmup_episodes=3,
        n_cycles=2,
        episodes_per_cycle=1,
        steps_per_episode=12,
        horizon_checkpoints=(1, 2),
        drive_weights=(("curiosity", 0.5), ("competence", 0.5)),
    )
    ds = WeightedDriveSet(
        (CuriosityDrive(CuriosityParams.from_config(cfg)), CompetenceStub()),
        cfg.drive_weights,
    )
    summary = Engine(cfg, drives=ds).run(1)
    assert summary.agency is not None
    assert np.isfinite(summary.agency["value_signal_mean"])
    # deterministic with the second drive too
    summary2 = Engine(
        cfg,
        drives=WeightedDriveSet(
            (CuriosityDrive(CuriosityParams.from_config(cfg)), CompetenceStub()),
            cfg.drive_weights,
        ),
    ).run(1)
    assert summary.serialize() == summary2.serialize()


def test_base_configuration_ships_curiosity_only():
    cfg = Config()
    assert cfg.drive_weights == (("curiosity", 1.0),)
    ds = WeightedDriveSet.from_config(cfg)
    assert [d.id() for d in ds.drives] == ["curiosity"]


def test_unknown_configured_drive_is_rejected():
    cfg = Config(drive_weights=(("curiosity", 1.0), ("mystery", 1.0)))
    with pytest.raises(ValueError):
        WeightedDriveSet.from_config(cfg)
