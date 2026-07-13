"""Multi-stream — validation and the per-stream seeding scheme (feature 009)."""

from __future__ import annotations

import numpy as np
import pytest

from pra.config import Config


def test_n_streams_is_validated():
    with pytest.raises(ValueError, match="n_streams must be >= 1"):
        Config(n_streams=0)
    assert Config().n_streams == 1  # the pinned validated default


def test_multistream_snapshots_are_accepted_since_feature_010():
    # feature 009 rejected this pending B5; feature 010 pays the debt
    cfg = Config(n_streams=2, snapshot_every_n_cycles=2)
    assert cfg.n_streams == 2


def test_spawn_key_streams_are_distinct_and_deterministic():
    """The engine derives stream k's generator from
    SeedSequence(entropy=seed, spawn_key=(1000+k,)): distinct across k,
    reproducible per (seed, k), distinct from the brain key (0,)."""

    def draws(seed: int, key: int) -> np.ndarray:
        rng = np.random.default_rng(np.random.SeedSequence(entropy=seed, spawn_key=(key,)))
        return rng.standard_normal(8)

    assert not np.allclose(draws(1, 1000), draws(1, 1001))  # streams differ
    np.testing.assert_array_equal(draws(1, 1000), draws(1, 1000))  # reproducible
    assert not np.allclose(draws(1, 0), draws(1, 1000))  # brain != stream
    assert not np.allclose(draws(1, 1000), draws(2, 1000))  # seeds differ
