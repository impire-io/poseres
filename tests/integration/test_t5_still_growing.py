"""T038 — T5 self-limiting, not merely capped (US4).

A population that keeps growing at the spawn rate up to (but not reaching) the cap
must FAIL T5 despite a finite final count — eviction is not pacing spawn.
"""

from __future__ import annotations

from pra.config import Config
from pra.core.engine import Engine
from pra.harness.acceptance import FAIL, _t5


def test_below_cap_but_still_growing_fails_t5():
    # Disable soft eviction (an unreachable survival threshold) and keep spawning
    # one frame per cycle, far below a large cap: the population strictly increases
    # over its final third -> still growing -> FAIL.
    cfg = Config(
        seeds=(1,),
        warmup_episodes=5,
        n_cycles=16,
        episodes_per_cycle=1,
        steps_per_episode=15,
        horizon_checkpoints=(1, 8, 16),
        survive_threshold_base=1000.0,  # nothing ever exceeds threshold -> no eviction
        min_age_cycles=1,
        spawn_per_cycle=1,
        max_frames=100000,  # cap is never reached
    )
    summary = Engine(cfg).run(1)
    assert summary.final_population < cfg.max_frames  # genuinely below the cap
    assert summary.still_growing  # strictly increasing over its final third

    verdict = _t5([summary], cfg.max_frames, 1)
    assert verdict.verdict == FAIL
    assert verdict.t5_detail.still_growing_per_seed == [True]
    assert verdict.t5_detail.capped is False  # not a cap artifact — genuine growth
