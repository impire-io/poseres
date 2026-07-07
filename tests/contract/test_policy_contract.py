"""T009 — Policy seam: substitution, pinned-baseline byte-identity, determinism."""

from __future__ import annotations

from pra.config import Config
from pra.core.engine import Engine


class AlwaysActionZero:
    def select_action(self, context, rng) -> int:
        return 0


def test_substitute_policy_accepted_by_engine_unchanged():
    cfg = Config(
        warmup_episodes=3,
        n_cycles=2,
        episodes_per_cycle=1,
        steps_per_episode=10,
        horizon_checkpoints=(1, 2),
    )
    summary = Engine(cfg, policy=AlwaysActionZero()).run(1)
    assert summary.final_population > 0  # ran end-to-end through the seam


def test_default_policy_reproduces_the_validated_reference():
    # The pinned RandomPolicy baseline must reproduce the validated build's
    # seed-1 trajectory exactly (FR-008, SC-003).
    s = Engine(Config()).run(1)
    assert round(s.pred_error_early, 4) == 0.4465
    assert round(s.pred_error_late, 4) == 0.1574
    readings = {c: (r.best_dim, r.population_size) for c, r in s.checkpoints.items()}
    assert readings == {18: (3, 19), 30: (3, 24), 50: (4, 27)}
    assert s.agency is None
    assert "agency" not in s.serialize()


def test_curiosity_mode_is_byte_identical_on_rerun():
    cfg = Config(
        policy_mode="curiosity",
        warmup_episodes=3,
        n_cycles=2,
        episodes_per_cycle=1,
        steps_per_episode=12,
        horizon_checkpoints=(1, 2),
    )
    a = Engine(cfg).run(5)
    b = Engine(cfg).run(5)
    assert a.serialize() == b.serialize()
    assert a.agency is not None and "agency" in a.serialize()
