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

import time
from collections import deque
from collections.abc import Callable

import numpy as np

from pra.action.policy import (
    CuriosityLookaheadPolicy,
    Policy,
    PolicyContext,
    PolicyParams,
    RandomPolicy,
)
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
from pra.motivation.context import DriveContext
from pra.motivation.drive import CuriosityDrive, WeightedDriveSet
from pra.persistence.snapshot import (
    FORMAT_VERSION,
    SystemState,
    decode,
    encode,
    validate_body_compatibility,
)
from pra.telemetry.recorder import (
    EARLY_LATE_WINDOW,
    MIN_PRED_SAMPLES,
    CheckpointReading,
    PerSeedRunSummary,
    is_still_growing,
)
from pra.world.event_source import EventSource, SensorimotorWorld

__all__ = ["Engine"]

# Lightweight context pieces for the pinned random baseline: RandomPolicy reads
# only n_actions, so the baseline path never scans frames or evaluates drives —
# zero added work, zero added RNG, byte-identical behavior (research R1).


def _no_prediction(action: int) -> None:
    return None


def _zero_value(obs: np.ndarray) -> float:
    return 0.0


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
        policy: Policy | None = None,
        drives: WeightedDriveSet | None = None,
        snapshot_store=None,
    ):
        self.config = config
        self.scoring_mode = scoring_mode or config.scoring_mode
        self._world_factory = world_factory or SensorimotorWorld
        self._scorer = scorer or WeightedSumScorer(config)
        self._proposal = proposal or BiasedProposalPolicy(config)
        self._decay = decay or PopulationScaledDecayPolicy(config)
        self._bus_factory = bus_factory or InMemorySyncBus
        # persistence (Doc 06): snapshots only when a store is injected AND the
        # config cadence is > 0; the default writes nothing (feature 003 FR-009)
        self._snapshot_store = snapshot_store
        # raw injections, so a resumed run can rebuild default seams from the
        # snapshot's config-in-force without discarding custom substitutes
        self._injected = {
            "scorer": scorer,
            "proposal": proposal,
            "decay": decay,
            "policy": policy,
            "drives": drives,
        }
        # Agency (Doc 05): the drive set exists iff the run is in curiosity mode
        # (or a set is injected); the policy default depends on the mode.
        # policy_mode="random" is the pinned validation baseline (FR-008).
        curiosity_mode = config.policy_mode == "curiosity" or drives is not None
        self._drives = drives or (WeightedDriveSet.from_config(config) if curiosity_mode else None)
        if policy is not None:
            self._policy: Policy = policy
        elif curiosity_mode:
            self._policy = CuriosityLookaheadPolicy(PolicyParams.from_config(config))
        else:
            self._policy = RandomPolicy()

    def run(
        self, seed: int, *, do_offline: bool = True, resume_from: bytes | SystemState | None = None
    ) -> PerSeedRunSummary:
        resumed: SystemState | None = None
        if resume_from is not None:
            resumed = decode(resume_from) if isinstance(resume_from, bytes) else resume_from
            validate_body_compatibility(resumed.config, self.config)
            if seed != resumed.seed:
                raise ValueError(f"resume seed {resumed.seed} does not match requested {seed}")
            # the configuration in force is part of the snapshot (Doc 06 §2);
            # default seams are rebuilt from it, custom injections are kept
            cfg = resumed.config
            scoring_mode = resumed.scoring_mode
            curiosity = resumed.policy_mode == "curiosity"
            inj = self._injected
            scorer = inj["scorer"] or WeightedSumScorer(cfg)
            proposal = inj["proposal"] or BiasedProposalPolicy(cfg)
            decay = inj["decay"] or PopulationScaledDecayPolicy(cfg)
            drives = inj["drives"] or (WeightedDriveSet.from_config(cfg) if curiosity else None)
            if inj["policy"] is not None:
                policy: Policy = inj["policy"]
            elif curiosity:
                policy = CuriosityLookaheadPolicy(PolicyParams.from_config(cfg))
            else:
                policy = RandomPolicy()
        else:
            cfg = self.config
            scoring_mode = self.scoring_mode
            scorer = self._scorer
            proposal = self._proposal
            decay = self._decay
            policy = self._policy
            drives = self._drives

        rng = np.random.default_rng(seed)
        world = self._world_factory(cfg, rng)
        store = FrameStore(cfg, rng)
        if resumed is not None:
            # the world's fixed structure is a pure function of the seed prefix
            # just consumed; overwriting the generator state resumes the exact
            # stream of the uninterrupted run (research R4)
            rng.bit_generator.state = resumed.rng_state
            store.load_state_dict(resumed.frame_store)
        bus = self._bus_factory(store)
        if resumed is not None:
            for s in store.frame_states():  # re-register the population (Doc 06 §3.3)
                bus.register(s.frame_id)
        checkpoints = set(cfg.horizon_checkpoints)

        state = _RunState()
        agency = _AgencyState(cfg) if drives is not None else None
        if resumed is not None:
            state.map_fractions = list(resumed.map_fractions)
            state.pred_errors = list(resumed.pred_errors)
            state.lost_after_warm = resumed.lost_after_warm
            state.obs_after_warm = resumed.obs_after_warm
            state.warmed = resumed.warmed
            state.obs_steps = resumed.obs_steps
            state.pop_sum = resumed.pop_sum
            if agency is not None and resumed.agency is not None:
                agency.load(resumed.agency)

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
                mean_pred = (
                    float(np.mean(stats.elect_pred_errors)) if stats.elect_pred_errors else None
                )
                if mean_pred is not None:
                    state.pred_errors.append(mean_pred)

                if agency is None:
                    # pinned baseline: RandomPolicy reads only n_actions — the
                    # context is inert and no drive work happens (research R1).
                    ctx = PolicyContext(
                        observation=obs,
                        n_actions=world.n_actions,
                        best_frame_age=None,
                        predict_decoded=_no_prediction,
                        drive_value_of=_zero_value,
                    )
                else:
                    # value the CURRENT observation first (memory through t−1:
                    # the very first step sees an empty memory, novelty = 1.0)
                    drive_ctx = DriveContext(
                        observation=obs,
                        recent_pred_errors=agency.pred_error_history,
                        observation_memory=agency.observation_memory,
                        step_index=state.obs_steps,
                    )
                    agency.record_value(drives, drive_ctx, obs)
                    age, predictor = store.best_frame_predictor(scorer)

                    def _value_of(
                        hypothetical: np.ndarray,
                        _hist=agency.pred_error_history,
                        _mem=agency.observation_memory,
                        _step=state.obs_steps,
                    ) -> float:
                        return drives.value(
                            DriveContext(
                                observation=hypothetical,
                                recent_pred_errors=_hist,
                                observation_memory=_mem,
                                step_index=_step,
                            )
                        )

                    def _predict(action: int, _p=predictor, _obs=obs):
                        return None if _p is None else _p(_obs, action)

                    ctx = PolicyContext(
                        observation=obs,
                        n_actions=world.n_actions,
                        best_frame_age=age,
                        predict_decoded=_predict,
                        drive_value_of=_value_of,
                    )

                prev_obs = obs
                prev_a = policy.select_action(ctx, rng)
                if agency is not None:
                    agency.record_step(policy, obs, mean_pred)
                obs = world.step(prev_a)

        def offline_cycle() -> None:
            # Anatomy hook (Doc 02 §5, feature 004): tool registrations queued on
            # a Body take effect here — the C4 safe point, before any aging,
            # eviction, spawning, or snapshot. Plain worlds lack the attribute:
            # one getattr, no RNG, no float work — the baseline stays byte-frozen.
            apply_tools = getattr(world, "apply_pending_tools", None)
            if apply_tools is not None:
                changed = apply_tools()
                if changed is not None:
                    store.resize(changed[0], changed[1], rng)
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

        # --- warmup (skipped on resume: the snapshot post-dates it) ------------
        if resumed is None:
            for _ in range(cfg.warmup_episodes):
                online_episode()
            early = _window_mean(state.pred_errors[:EARLY_LATE_WINDOW], require=MIN_PRED_SAMPLES)
            state.warmed = True
            first_cycle = 1
        else:
            # `early` was fixed at end of warmup; recomputing after more episodes
            # would silently change it — it travels in the snapshot (research R2)
            early = resumed.pred_error_early
            first_cycle = resumed.cycles_done + 1

        # --- consolidation ----------------------------------------------------
        checkpoint_readings: dict[int, CheckpointReading] = {}
        population_by_cycle: list[int] = []
        if resumed is not None:
            population_by_cycle = list(resumed.population_by_cycle)
            checkpoint_readings = {
                c: CheckpointReading(best_dim=bd, population_size=p)
                for c, (bd, p) in resumed.checkpoints.items()
            }
        if do_offline:
            for c in range(first_cycle, cfg.effective_n_cycles + 1):
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
                if (
                    self._snapshot_store is not None
                    and cfg.snapshot_every_n_cycles > 0
                    and c % cfg.snapshot_every_n_cycles == 0
                ):
                    # C4 safe point: end of an offline cycle. Capture consumes no
                    # RNG and mutates nothing (feature 003 FR-002).
                    self._take_snapshot(
                        cfg,
                        seed,
                        scoring_mode,
                        store,
                        state,
                        agency,
                        rng,
                        c,
                        early,
                        checkpoint_readings,
                        population_by_cycle,
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
            agency=agency.summary() if agency is not None else None,
        )

    def _take_snapshot(
        self,
        cfg: Config,
        seed: int,
        scoring_mode: str,
        store: FrameStore,
        state: _RunState,
        agency: _AgencyState | None,
        rng: np.random.Generator,
        cycle: int,
        early: float | None,
        checkpoint_readings: dict,
        population_by_cycle: list[int],
    ) -> None:
        snapshot = SystemState(
            config=cfg,
            seed=seed,
            scoring_mode=scoring_mode,
            policy_mode="curiosity" if agency is not None else "random",
            cycles_done=cycle,
            obs_steps=state.obs_steps,
            obs_after_warm=state.obs_after_warm,
            lost_after_warm=state.lost_after_warm,
            pop_sum=state.pop_sum,
            warmed=state.warmed,
            pred_error_early=early,
            map_fractions=list(state.map_fractions),
            pred_errors=list(state.pred_errors),
            population_by_cycle=list(population_by_cycle),
            checkpoints={
                c: (r.best_dim, r.population_size) for c, r in checkpoint_readings.items()
            },
            frame_store=store.state_dict(),
            agency=agency.state_dict() if agency is not None else None,
            rng_state=rng.bit_generator.state,
        )
        metadata = {
            "timestamp": time.time(),
            "step": state.obs_steps,
            "cycle": cycle,
            "population": store.population_size,
            "format_version": FORMAT_VERSION,
        }
        self._snapshot_store.write(encode(snapshot), metadata)


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


class _AgencyState:
    """Per-run agency bookkeeping (Doc 05 §3.3): the drive-context FIFOs the
    Engine owns on the drives' behalf, plus value-signal telemetry accumulators.
    State, not policy — never persisted; exists only in curiosity mode."""

    def __init__(self, config: Config) -> None:
        self.pred_error_history: deque[float] = deque(maxlen=config.lp_baseline_window)
        self.observation_memory: deque[np.ndarray] = deque(maxlen=config.novelty_memory_size)
        self.values: list[float] = []
        self.lp_terms: list[float] = []
        self.novelty_terms: list[float] = []
        self.directed_steps = 0
        self.total_steps = 0

    def record_value(self, drives: WeightedDriveSet, ctx: DriveContext, obs: np.ndarray) -> None:
        self.values.append(drives.value(ctx))
        for d in drives.drives:
            if isinstance(d, CuriosityDrive):
                self.lp_terms.append(d.learning_progress(ctx.recent_pred_errors))
                self.novelty_terms.append(d.novelty(obs, ctx.observation_memory))
                break

    def record_step(self, policy: Policy, obs: np.ndarray, mean_pred: float | None) -> None:
        self.total_steps += 1
        if getattr(policy, "last_was_directed", False):
            self.directed_steps += 1
        # bookkeeping updates AFTER valuation (value at t sees memory through t−1)
        if mean_pred is not None:
            self.pred_error_history.append(mean_pred)
        self.observation_memory.append(np.array(obs, copy=True))

    def summary(self) -> dict:
        return {
            "value_signal_mean": float(np.mean(self.values)) if self.values else 0.0,
            "value_signal_final": float(self.values[-1]) if self.values else 0.0,
            "learning_progress_mean": float(np.mean(self.lp_terms)) if self.lp_terms else 0.0,
            "novelty_mean": float(np.mean(self.novelty_terms)) if self.novelty_terms else 0.0,
            "directed_fraction": self.directed_steps / self.total_steps
            if self.total_steps
            else 0.0,
        }

    # ---- persistence (Doc 06 §2: drive bookkeeping is system state) ----------
    def state_dict(self) -> dict:
        return {
            "pred_error_history": list(self.pred_error_history),
            "observation_memory": [np.array(o, copy=True) for o in self.observation_memory],
            "values": list(self.values),
            "lp_terms": list(self.lp_terms),
            "novelty_terms": list(self.novelty_terms),
            "directed_steps": self.directed_steps,
            "total_steps": self.total_steps,
        }

    def load(self, state: dict) -> None:
        self.pred_error_history.extend(state["pred_error_history"])
        self.observation_memory.extend(state["observation_memory"])
        self.values = list(state["values"])
        self.lp_terms = list(state["lp_terms"])
        self.novelty_terms = list(state["novelty_terms"])
        self.directed_steps = int(state["directed_steps"])
        self.total_steps = int(state["total_steps"])


def _window_mean(values: list[float], *, require: int) -> float | None:
    """Mean of ``values``; ``None`` (not available) if fewer than ``require``."""
    if len(values) < require:
        return None
    return float(np.mean(values))
