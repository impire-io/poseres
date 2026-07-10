"""T015 — Proposal/Decay seams: scaling, young protection, substitutability."""

from __future__ import annotations

import numpy as np

from pra.config import Config
from pra.core.contracts import FrameState
from pra.core.engine import Engine
from pra.core.policies import ClimbingProposalPolicy, PopulationScaledDecayPolicy
from pra.core.scorer import WeightedSumScorer


def test_threshold_decreases_as_population_grows():
    decay = PopulationScaledDecayPolicy(Config())
    t_small = decay.threshold(4)
    t_big = decay.threshold(40)
    assert t_big < t_small  # crowding tightens the bar (it DIVIDES by the pop factor)


def test_young_frames_are_never_evicted():
    cfg = Config(min_age_cycles=2, min_frames=1, max_frames=200)
    decay = PopulationScaledDecayPolicy(cfg)
    scorer = WeightedSumScorer(cfg)
    # all frames score far above threshold, but the young one is protected.
    frames = [
        FrameState(frame_id=0, dim=8, age_cycles=5, recon_err_ema=2.0, pred_err_ema=2.0),
        FrameState(frame_id=1, dim=8, age_cycles=0, recon_err_ema=2.0, pred_err_ema=2.0),
    ]
    removed = decay.evict(
        frames,
        scorer,
        decay.threshold(len(frames)),
        min_frames=1,
        max_frames=200,
        min_age_cycles=2,
    )
    assert 1 not in removed  # young frame survives
    assert 0 in removed  # old, over-threshold frame is evicted


def test_min_frames_floor_is_respected():
    cfg = Config()
    decay = PopulationScaledDecayPolicy(cfg)
    scorer = WeightedSumScorer(cfg)
    frames = [
        FrameState(frame_id=0, dim=9, age_cycles=5, recon_err_ema=3.0, pred_err_ema=3.0),
    ]
    removed = decay.evict(
        frames, scorer, decay.threshold(1), min_frames=1, max_frames=200, min_age_cycles=2
    )
    assert removed == []  # never drop below min_frames even if over threshold


def test_climbing_proposal_stays_in_the_upward_band():
    # PROPOSAL-DIAGNOSIS: every proposal lands in (best, best + offset] — no mass
    # at or below the incumbent (re-tread), none beyond the band (overreach).
    cfg = Config()  # explore_dim_max_offset = 4
    policy = ClimbingProposalPolicy(cfg)
    rng = np.random.default_rng(7)
    for best in (1, 5, 20):
        draws = {policy.propose_dimension(best, [best], rng) for _ in range(500)}
        assert min(draws) >= best + 1
        assert max(draws) <= best + 4


def test_climbing_proposal_is_deterministic_per_seed():
    cfg = Config()

    def draws() -> list[int]:
        policy = ClimbingProposalPolicy(cfg)
        rng = np.random.default_rng(3)
        return [policy.propose_dimension(6, [6], rng) for _ in range(50)]

    assert draws() == draws()


def test_climbing_proposal_is_accepted_by_engine():
    cfg = Config(
        warmup_episodes=3,
        n_cycles=3,
        episodes_per_cycle=1,
        steps_per_episode=8,
        horizon_checkpoints=(1, 2, 3),
    )
    summary = Engine(cfg, proposal=ClimbingProposalPolicy(cfg)).run(1)
    assert summary.final_population > 0
    assert summary.best_dim is not None


def test_high_dim_proposal_substitute_is_accepted_by_engine():
    class HighDimProposal:
        def propose_dimension(self, best_dim, population_dims, rng):
            # ignore the bias; always explore upward (the open research-question seam).
            return best_dim + 10

    cfg = Config(
        warmup_episodes=3,
        n_cycles=3,
        episodes_per_cycle=1,
        steps_per_episode=8,
        horizon_checkpoints=(1, 2, 3),
    )
    engine = Engine(cfg, proposal=HighDimProposal())
    summary = engine.run(1)
    assert summary.final_population > 0
    # the upward-only policy drives dims well above the default range.
    assert summary.best_dim is not None
