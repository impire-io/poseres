"""Ladder world contracts — EventSource conformance and ground-truth hiding
(feature 005, contracts/ladder.md §1)."""

from __future__ import annotations

import numpy as np
import pytest

from pra.config import Config
from pra.world.event_source import EventSource
from pra.world.ladder import make_world

LADDER_CONFIGS = [
    Config(world="nonuniform", region_noise_std=0.5),
    Config(world="compositional", true_dim=6, obs_dim=18, factor_dims=(3, 3)),
    Config(world="distractor", obs_dim=14, distractor_dim=2, distractor_channels=4),
]
IDS = ["l1", "l2", "l3"]


@pytest.mark.parametrize("cfg", LADDER_CONFIGS, ids=IDS)
def test_ladder_world_satisfies_event_source(cfg):
    world = make_world(cfg, np.random.default_rng(1))
    assert isinstance(world, EventSource)
    obs = world.reset()
    assert obs.shape == (world.obs_dim,)
    assert world.step(0).shape == (world.obs_dim,)
    assert world.n_actions == cfg.n_actions
    assert world.obs_dim == cfg.obs_dim  # Config.obs_dim is the system-visible width


@pytest.mark.parametrize("cfg", LADDER_CONFIGS, ids=IDS)
def test_surface_exposes_no_ground_truth(cfg):
    """The system-visible surface is reset/step/obs_dim/n_actions; ground
    truth (regions, groups, splits, occupancy) lives only behind the
    harness-only ladder_readings() accessor (SC-005). state_dict/
    load_state_dict are the feature-008 capture protocol — persistence
    plumbing called only at snapshot boundaries, never by the learning
    system."""
    world = make_world(cfg, np.random.default_rng(1))
    public = {name for name in dir(world) if not name.startswith("_")}
    assert public == {
        "reset",
        "step",
        "obs_dim",
        "n_actions",
        "ladder_readings",
        "state_dict",
        "load_state_dict",
    }


@pytest.mark.parametrize("cfg", LADDER_CONFIGS, ids=IDS)
def test_ladder_readings_is_harness_side_ground_truth(cfg):
    world = make_world(cfg, np.random.default_rng(1))
    readings = world.ladder_readings()
    assert readings["rung"] in {"l1", "l2", "l3"}


def test_engine_never_touches_ladder_readings():
    """The engine module has no reference to the harness-only accessor —
    the seam stays observations-and-actions only."""
    import inspect

    import pra.core.engine as engine

    assert "ladder_readings" not in inspect.getsource(engine)
