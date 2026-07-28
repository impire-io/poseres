"""Rover contracts (feature 006, contracts/rover.md §§1–3) — EventSource
conformance, ground-truth hiding, and tap coherence outside a run.
"""

from __future__ import annotations

import numpy as np

from pra.config import Config
from pra.core.engine import Engine
from pra.examples.rover.viewer import RoverTelemetry
from pra.examples.rover.world import RoverWorld, make_rover_body
from pra.world.event_source import EventSource

# Small budgets: these check the instrument (byte-identity, widths), never the
# science — the same shape the dash and rover suites use.
SMALL = dict(
    warmup_episodes=2,
    n_cycles=2,
    episodes_per_cycle=1,
    steps_per_episode=10,
    horizon_checkpoints=(1, 2),
)


def test_rover_body_satisfies_event_source():
    body = make_rover_body(Config(), np.random.default_rng(1))
    assert isinstance(body, EventSource)
    obs = body.reset()
    assert obs.shape == (10,) and obs.dtype == np.float64
    nxt = body.step(0)
    assert nxt.shape == (10,) and nxt.dtype == np.float64


def test_system_surface_hides_ground_truth():
    """The engine holds only the Body — nothing on it exposes pose, map, or
    layout (FR-005); the world's `layout()` accessor is harness/viewer-only."""
    body = make_rover_body(Config(), np.random.default_rng(1))
    for name in ("layout", "pose", "sense", "apply"):
        assert not hasattr(body, name)
    world = RoverWorld(Config(), np.random.default_rng(1))
    layout = world.layout()
    assert set(layout) >= {"arena_half", "obstacles", "spawns", "actions", "sensors"}


def test_tap_snapshot_is_coherent_before_any_run():
    tap = RoverTelemetry(Config())
    snap = tap.snapshot()
    assert snap == {
        "step": 0,
        "episode": 0,
        "pose": None,
        "bump": 0,
        "trail": [],
        "done": False,
        "final": None,
        "learning": None,
    }
    assert tap.snapshot() == snap  # snapshotting never mutates the tap


def test_tap_records_are_plain_value_copies():
    tap = RoverTelemetry(Config())
    tap.record_reset(0.1, 0.2, 0.3)
    tap.record_step(0.15, 0.2, 0.3, 1)
    snap = tap.snapshot()
    assert snap["episode"] == 1 and snap["step"] == 1
    assert snap["pose"] == [0.15, 0.2, 0.3] and snap["bump"] == 1
    assert snap["trail"] == [[0.1, 0.2], [0.15, 0.2]]
    tap.record_reset(0.5, 0.5, 0.0)  # a new episode clears the trail
    assert tap.snapshot()["trail"] == [[0.5, 0.5]]


def test_bus_factory_returns_the_stock_bus():
    from pra.core.bus import InMemorySyncBus
    from pra.core.frame import FrameStore

    tap = RoverTelemetry(Config())
    store = FrameStore(Config(), np.random.default_rng(1))
    bus = tap.bus_factory(store)
    assert type(bus) is InMemorySyncBus  # pass-through capture: no wrapper, no drift
    assert tap._store is store


def test_odo_flag_off_summary_is_byte_identical():
    """Constitution I: the odo flag off leaves the run's *serialized summary*
    exactly where it was. `bare` is the flag-absent world — the pinned
    baseline — and `off` carries the whole odo code path with the flag down.
    This is the feature's acceptance test, not a courtesy: the rover is used
    in measured experiments and these bytes must not move."""
    cfg = Config(**SMALL)
    bare = Engine(cfg, world_factory=make_rover_body).run(1).serialize()
    off = (
        Engine(cfg, world_factory=lambda c, r: make_rover_body(c, r, emit_odo=False))
        .run(1)
        .serialize()
    )
    assert off == bare


def test_odo_flag_off_leaves_every_observation_untouched():
    """The per-step companion to the summary check: identical summaries could
    in principle hide compensating drift, so pin the observation stream too —
    the odo branch must not perturb a single channel or consume a draw."""
    seed = 42
    cfg = Config()
    rng_a = np.random.default_rng(seed)
    body_a = make_rover_body(cfg, rng_a)
    obs_a = [body_a.reset()]
    for act in [0, 1, 2, 3, 0, 0, 3, 1]:
        obs_a.append(body_a.step(act))
    rng_b = np.random.default_rng(seed)
    body_b = make_rover_body(cfg, rng_b, emit_odo=False)
    obs_b = [body_b.reset()]
    for act in [0, 1, 2, 3, 0, 0, 3, 1]:
        obs_b.append(body_b.step(act))
    for a, b in zip(obs_a, obs_b, strict=True):
        np.testing.assert_array_equal(a, b)


def test_odo_flag_on_obs_dim():
    """emit_odo=True grows obs_dim to 12 and reports the odo group."""
    cfg = Config(obs_dim=12)
    body = make_rover_body(cfg, np.random.default_rng(1), emit_odo=True)
    assert body.obs_dim == 12
    obs = body.reset()
    assert obs.shape == (12,)
    meta = body.anatomy_meta()
    group_ids = [g["id"] for g in meta["groups"]]
    assert "odo" in group_ids
    odo_group = [g for g in meta["groups"] if g["id"] == "odo"][0]
    assert odo_group["width"] == 2
    assert odo_group["start"] == 10


def test_odo_values_match_pose_deltas():
    """Odometry channels must match hand-computed pose deltas for scripted
    actions, and reset must emit zeros (no previous pose)."""
    cfg = Config(obs_dim=12, sensor_noise_std=0.0)
    body = make_rover_body(cfg, np.random.default_rng(1), emit_odo=True)
    obs = body.reset()
    # Reset: no previous pose -> odo channels are zeros
    assert obs[10] == 0.0 and obs[11] == 0.0

    # Forward: dist/MOVE_STEP = +1, heading change = 0
    obs = body.step(0)
    assert abs(obs[10] - 1.0) < 1e-12
    assert abs(obs[11] - 0.0) < 1e-12

    # Turn left: dist = 0, heading/TURN_STEP = +1
    obs = body.step(2)
    assert abs(obs[10] - 0.0) < 1e-12
    assert abs(obs[11] - 1.0) < 1e-12

    # Turn right: dist = 0, heading/TURN_STEP = -1
    obs = body.step(3)
    assert abs(obs[10] - 0.0) < 1e-12
    assert abs(obs[11] + 1.0) < 1e-12

    # Reverse (unblocked): dist = -REVERSE_FACTOR = -0.5, heading = 0
    obs = body.step(1)
    assert abs(obs[10] + 0.5) < 1e-12
    assert abs(obs[11] - 0.0) < 1e-12


def test_odo_seed_reproducibility():
    """Odo-enabled runs must be byte-reproducible per (config, seed)."""
    cfg = Config(obs_dim=12)

    def run(seed):
        body = make_rover_body(cfg, np.random.default_rng(seed), emit_odo=True)
        results = [body.reset()]
        for a in [0, 2, 1, 3, 0, 0]:
            results.append(body.step(a))
        return results

    run_a = run(7)
    run_b = run(7)
    for a, b in zip(run_a, run_b, strict=True):
        np.testing.assert_array_equal(a, b)
