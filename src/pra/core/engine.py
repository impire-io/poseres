"""Engine: the zero-start sensorimotor lifecycle (PRA-01 §5/§6, research R3/R4).

One Engine runs one seed and produces a deterministic :class:`PerSeedRunSummary`.
It owns the five seams (EventSource, Bus, Scorer, ProposalPolicy, DecayPolicy) and
the internal batched FrameStore, and consumes a single seeded
``numpy.random.Generator`` in exactly the order the v4 oracle does — world
construction, then per-birth frame weights, online action sampling, and proposal
choices — so two runs of a seed are byte-identical (FR-010, SC-007).

The lifecycle mirrors the oracle: a warmup phase (frames born on demand by the
zero-start no-loss rule), then ``effective_n_cycles`` offline consolidation cycles
that age, evict (DecayPolicy), and spawn-and-select (ProposalPolicy). Survival
EMAs are coverage-fair (updated on every exposure); learning stays gated on
mapped events. Prediction error is scored in observation space.
"""

from __future__ import annotations

from collections.abc import Callable

import numpy as np

from pra.config import Config
from pra.core.bus import Bus, FrameProcessor, InMemorySyncBus
from pra.core.frame import FrameStore
from pra.core.policies import (
    BiasedProposalPolicy,
    DecayPolicy,
    PopulationScaledDecayPolicy,
    ProposalPolicy,
)
from pra.core.scorer import Scorer, WeightedSumScorer
from pra.telemetry.recorder import (
    EARLY_LATE_WINDOW,
    MIN_PRED_SAMPLES,
    CheckpointReading,
    PerSeedRunSummary,
    is_still_growing,
)
from pra.world.event_source import EventSource, SensorimotorWorld

__all__ = ["Engine"]


class Engine:
    """Runs one seed of the PRA system-under-test to a deterministic summary.

    The five seams (EventSource, Bus, Scorer, ProposalPolicy, DecayPolicy) are
    injectable so each can be substituted in isolation (PRA-01 §7.3); the defaults
    are the in-scope implementations. World and Bus are supplied as factories
    because they bind to the per-run seeded generator / FrameStore created inside
    :meth:`run`.
    """

    def __init__(
        self,
        config: Config,
        *,
        scoring_mode: str | None = None,
        world_factory: Callable[[Config, np.random.Generator], EventSource] | None = None,
        scorer: Scorer | None = None,
        proposal: ProposalPolicy | None = None,
        decay: DecayPolicy | None = None,
        bus_factory: Callable[[FrameProcessor], Bus] | None = None,
    ):
        self.config = config
        self.scoring_mode = scoring_mode or config.scoring_mode
        self._world_factory = world_factory or SensorimotorWorld
        self._scorer = scorer or WeightedSumScorer(config)
        self._proposal = proposal or BiasedProposalPolicy(config)
        self._decay = decay or PopulationScaledDecayPolicy(config)
        self._bus_factory = bus_factory or InMemorySyncBus

    def run(self, seed: int, *, do_offline: bool = True) -> PerSeedRunSummary:
        cfg = self.config
        rng = np.random.default_rng(seed)
        world = self._world_factory(cfg, rng)
        store = FrameStore(cfg, rng)
        scorer = self._scorer
        proposal = self._proposal
        decay = self._decay
        bus = self._bus_factory(store)
        scoring_mode = self.scoring_mode
        checkpoints = set(cfg.horizon_checkpoints)

        state = _RunState()

        def online_episode() -> None:
            obs = world.reset()
            prev_obs: np.ndarray | None = None
            prev_a: int | None = None
            for _ in range(cfg.steps_per_episode):
                if state.warmed:
                    state.obs_after_warm += 1
                state.obs_steps += 1
                stats = store.online_step(obs, prev_obs, prev_a, scoring_mode)

                if stats.mapped == 0:
                    if state.warmed:
                        state.lost_after_warm += 1
                    best = store.best_frame(scorer)
                    if best is not None:
                        d = max(1, best[1] + int(rng.choice([-1, 0, 1])))
                    else:
                        d = int(rng.integers(cfg.initial_dim_min, cfg.initial_dim_max))
                    bus.register(store.birth(d, ema_init=1.0))

                alive = store.population_size
                state.pop_sum += alive
                if alive > 0:
                    state.map_fractions.append(stats.mapped / alive)
                if stats.elect_pred_errors:
                    state.pred_errors.append(float(np.mean(stats.elect_pred_errors)))

                prev_obs = obs
                prev_a = int(rng.integers(world.n_actions))
                obs = world.step(prev_a)

        def offline_cycle() -> None:
            # effective (scale-invariant) protection window — raw at the reference
            store.age_all(cfg.effective_min_age_cycles)
            if store.population_size == 0:
                return
            states = store.frame_states()
            threshold = decay.threshold(len(states))
            remove = decay.evict(
                states,
                scorer,
                threshold,
                min_frames=cfg.min_frames,
                max_frames=cfg.max_frames,
                min_age_cycles=cfg.effective_min_age_cycles,
            )
            store.evict(remove)
            for fid in remove:
                bus.unregister(fid)
            for _ in range(cfg.spawn_per_cycle):
                best = store.best_frame(scorer)
                if best is None:
                    break
                new_dim = proposal.propose_dimension(best[1], store.dims_alive(), rng)
                bus.register(store.birth(new_dim, ema_init=0.9))

        # --- warmup -----------------------------------------------------------
        for _ in range(cfg.warmup_episodes):
            online_episode()
        early = _window_mean(state.pred_errors[:EARLY_LATE_WINDOW], require=MIN_PRED_SAMPLES)
        state.warmed = True

        # --- consolidation ----------------------------------------------------
        checkpoint_readings: dict[int, CheckpointReading] = {}
        population_by_cycle: list[int] = []
        if do_offline:
            for c in range(1, cfg.effective_n_cycles + 1):
                for _ in range(cfg.episodes_per_cycle):
                    online_episode()
                offline_cycle()
                pop = store.population_size
                population_by_cycle.append(pop)
                if c in checkpoints:
                    best = store.best_frame(scorer)
                    best_dim = best[1] if best is not None else 0
                    checkpoint_readings[c] = CheckpointReading(
                        best_dim=best_dim, population_size=pop
                    )
        else:
            # T3 effort-only ablation: equal online experience, no consolidation.
            for _ in range(cfg.effective_n_cycles * cfg.episodes_per_cycle):
                online_episode()

        late = _window_mean(state.pred_errors[-EARLY_LATE_WINDOW:], require=1)

        best = store.best_frame(scorer)
        mean_pop = state.pop_sum / state.obs_steps if state.obs_steps else 0.0
        return PerSeedRunSummary(
            seed=seed,
            scoring_mode=self.scoring_mode,
            mean_map_fraction=float(np.mean(state.map_fractions)) if state.map_fractions else 0.0,
            pred_error_early=early,
            pred_error_late=late,
            best_dim=best[1] if best is not None else None,
            best_score=best[2] if best is not None else None,
            final_population=store.population_size,
            loss_fraction=state.lost_after_warm / max(1, state.obs_after_warm),
            observation_steps=state.obs_steps,
            mean_population=mean_pop,
            checkpoints=checkpoint_readings,
            population_by_cycle=population_by_cycle,
            still_growing=is_still_growing(population_by_cycle),
        )


class _RunState:
    """Mutable accumulators threaded through the nested episode/cycle closures."""

    def __init__(self) -> None:
        self.map_fractions: list[float] = []
        self.pred_errors: list[float] = []
        self.lost_after_warm = 0
        self.obs_after_warm = 0
        self.warmed = False
        self.obs_steps = 0
        self.pop_sum = 0


def _window_mean(values: list[float], *, require: int) -> float | None:
    """Mean of ``values``; ``None`` (not available) if fewer than ``require``."""
    if len(values) < require:
        return None
    return float(np.mean(values))
