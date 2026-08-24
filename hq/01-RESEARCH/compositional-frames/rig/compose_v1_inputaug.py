"""Compositional-frames rig — the tower and the reference arms.

Shared scaffolding (JOURNEY.md 2026-08-24, registered before any run):
the kernel FrameStore untouched as the base tier; a second frame
population (tier-2) reads aug_obs = [obs, z] where z (width Z=8) is
the composition carrier — the ONE variable between arms:

    tower     z = best base frame's pose at the CURRENT obs (same-step,
              post-base-step weights) — hierarchy-as-built, adds
              representation and no information
    ref-pose  z = best base frame's pose at obs(t-1) (pre-step weights)
              — carried state, slot semantics
    ref-pred  z = best base frame's predicted next pose from
              (obs(t-1), a(t-1)) (pre-step weights)

Tier-2 draws from its own spawn-keyed generator (spawn_key 7000); its
lifecycle mirrors the engine's exactly (on-demand birth, per-cycle
age/evict/spawn, same config through the kernel's own scale rules,
event head NOT duplicated). The policy's lookahead predictor comes
from the tier whose best frame carries the lower honest obs-space
one-step prediction-error EMA (tier-2's trimmed to the first obs_dim
channels over ||obs||, decay = ema_decay). Tier-2 decoded predictions
are trimmed to obs space; progress/pulse indices unchanged.

Policy for every arm: stack-nc exactly (kappa=0.25, commitment off,
event head eta=0.5 on the base store). Protocol: the frozen echo
world, W2/DK, 13,000 steps, 24 seeds, continuous mode.

    python compose.py calib R 4 W2 tower|ref-pose|ref-pred [n_cycles]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

RIG = Path(__file__).parent
sys.path.insert(0, str(RIG))

from seq import ENCODINGS, M, SEEDS, EchoWorld, SeqRecordingPolicy, obs_dim_of  # noqa: E402

import pra.core.engine as engine_mod  # noqa: E402
from pra.action.policy import CompletionItchPolicy, PolicyParams  # noqa: E402
from pra.config import Config  # noqa: E402
from pra.core.engine import Engine  # noqa: E402
from pra.core.frame import FrameStore  # noqa: E402
from pra.core.policies import BiasedProposalPolicy, PopulationScaledDecayPolicy  # noqa: E402
from pra.core.scorer import WeightedSumScorer  # noqa: E402

Z = 8
_EPS = 1e-6

# rig globals threaded into ComposedFrameStore (the engine constructs the
# store internally and passes no seed/mode)
RUN = {"seed": 0, "mode": "tower", "stores": []}


class Tier2:
    """The second population: a kernel FrameStore on aug_obs, own rng,
    mirrored lifecycle, per-frame trimmed obs-space pred-error EMA."""

    def __init__(self, cfg: Config, seed: int):
        self.obs_dim = int(cfg.obs_dim)
        # Amended (JOURNEY 2026-08-24, pilot numbers recorded): the kernel's
        # lr scale rule treats the z block as more world and slowed tier-2
        # 3.6x vs base; the block is a carrier, so tier-2 learns at the BASE
        # tier's effective rate (raw lr rescaled to cancel the rule).
        lr2 = cfg.learning_rate * ((cfg.obs_dim + Z) / cfg.obs_dim) ** 1.5
        self.cfg2 = cfg.replace(
            obs_dim=cfg.obs_dim + Z, event_head_eta=0.0, learning_rate=lr2
        )
        self.rng = np.random.default_rng(np.random.SeedSequence(entropy=seed, spawn_key=(7000,)))
        self.store = FrameStore(self.cfg2, self.rng)
        self.scorer = WeightedSumScorer(self.cfg2)
        self.decay_policy = PopulationScaledDecayPolicy(self.cfg2)
        self.proposal = BiasedProposalPolicy(self.cfg2)
        # frame_id -> EMA of ABSOLUTE L2 pred error on the task channels
        # (progress, pulse — the last two obs channels), amended arbiter
        # metric (JOURNEY 2026-08-24: the whole-obs norm is dominated by the
        # easy encoding channels and never let tier-2 engage)
        self.task_ema: dict[int, float] = {}
        self._d = float(self.cfg2.ema_decay)
        # instrument telemetry
        self.mapped_steps = 0
        self.total_steps = 0

    def step(self, aug: np.ndarray, prev_aug: np.ndarray | None, prev_a: int | None,
             scoring_mode: str) -> None:
        stats = self.store.online_step(aug, prev_aug, prev_a, scoring_mode)
        self.total_steps += 1
        if stats.mapped > 0:
            self.mapped_steps += 1
        if prev_aug is not None:
            od = self.obs_dim
            for g in self.store._groups.values():
                if g.size == 0:
                    continue
                pobs = g.predicted_obs(prev_aug, prev_a)
                errs = np.linalg.norm(pobs[:, od - 2 : od] - aug[od - 2 : od], axis=1)
                for i in range(g.size):
                    fid = int(g.frame_ids[i])
                    prev = self.task_ema.get(fid, 1.0)
                    self.task_ema[fid] = self._d * prev + (1.0 - self._d) * float(errs[i])
        if stats.mapped == 0:
            best = self.store.best_frame(self.scorer)
            if best is not None:
                d = max(1, best[1] + int(self.rng.choice([-1, 0, 1])))
            else:
                d = int(self.rng.integers(self.cfg2.initial_dim_min, self.cfg2.initial_dim_max))
            self.store.birth(d, ema_init=1.0)

    def offline_cycle(self) -> None:
        self.store.age_all(self.cfg2.effective_min_age_cycles)
        if self.store.population_size == 0:
            return
        states = self.store.frame_states()
        threshold = self.decay_policy.threshold(len(states))
        remove = self.decay_policy.evict(
            states,
            self.scorer,
            threshold,
            min_frames=self.cfg2.min_frames,
            max_frames=self.cfg2.max_frames,
            min_age_cycles=self.cfg2.effective_min_age_cycles,
        )
        self.store.evict(remove)
        for fid in remove:
            self.task_ema.pop(fid, None)
        for _ in range(self.cfg2.spawn_per_cycle):
            best = self.store.best_frame(self.scorer)
            if best is None:
                break
            new_dim = self.proposal.propose_dimension(
                best[1], self.store.dims_alive(), self.rng
            )
            self.store.birth(new_dim, ema_init=0.9)

    def best(self):
        """(group, row, age, task_ema) of tier-2's best by the standard scorer."""
        b = self.store.best_frame(self.scorer)
        if b is None:
            return None
        fid = b[0]
        for g in self.store._groups.values():
            idx = np.nonzero(g.frame_ids == fid)[0]
            if idx.size:
                i = int(idx[0])
                return g, i, int(g.age_cycles[i]), self.task_ema.get(fid, 1.0)
        return None


class ComposedFrameStore(FrameStore):
    """Base tier = inherited FrameStore behavior, byte-equivalent path;
    tier-2 and the cross-tier arbiter live here."""

    def __init__(self, config: Config, rng: np.random.Generator):
        super().__init__(config, rng)
        self.mode = RUN["mode"]
        self.t2 = Tier2(config, RUN["seed"])
        self._scorer = WeightedSumScorer(config)  # the engine's default scorer
        self._prev_aug: np.ndarray | None = None
        self._z_now = np.zeros(Z)
        # mirrored task-channel EMA for the base tier (same metric, same decay
        # — the arbiter never compares two different norms)
        self.task_ema_base: dict[int, float] = {}
        # arbiter telemetry
        self.arb_t2 = 0
        self.arb_total = 0
        RUN["stores"].append(self)

    # -- helpers -------------------------------------------------------------
    def _base_best(self):
        """(group, row) of the base tier's best frame, or None."""
        b = self.best_frame(self._scorer)
        if b is None:
            return None
        fid = b[0]
        for g in self._groups.values():
            idx = np.nonzero(g.frame_ids == fid)[0]
            if idx.size:
                return g, int(idx[0])
        return None

    def _pad(self, v: np.ndarray) -> np.ndarray:
        z = np.zeros(Z)
        n = min(v.shape[0], Z)
        z[:n] = v[:n]
        return z

    def _z_ref(self, prev_obs: np.ndarray | None, prev_a: int | None) -> np.ndarray:
        """Carried z (pre-step weights): pose at obs(t-1), or the predicted
        next pose from (obs(t-1), a(t-1))."""
        if prev_obs is None:
            return np.zeros(Z)
        bb = self._base_best()
        if bb is None:
            return np.zeros(Z)
        g, i = bb
        pose, _ = g.encode(prev_obs)
        if self.mode == "ref-pose":
            return self._pad(pose[i])
        pred, _ = g.predict_next(pose, prev_a)
        return self._pad(pred[i])

    def _z_tower(self, obs: np.ndarray) -> np.ndarray:
        """Same-step z (post-step weights): pose at the current obs."""
        bb = self._base_best()
        if bb is None:
            return np.zeros(Z)
        g, i = bb
        pose, _ = g.encode(obs)
        return self._pad(pose[i])

    # -- the composed step ----------------------------------------------------
    def online_step(self, obs, prev_obs, prev_a, scoring_mode, *, ema_update=True):
        if prev_obs is None:
            # episode boundary: tier-2's transition chain breaks exactly where
            # the base tier's does (the kernel's episode-keyed semantics)
            self._prev_aug = None
        if self.mode in ("ref-pose", "ref-pred"):
            z_now = self._z_ref(prev_obs, prev_a)
        else:
            z_now = None
        stats = super().online_step(obs, prev_obs, prev_a, scoring_mode, ema_update=ema_update)
        if prev_obs is not None:
            d = float(self.config.ema_decay)
            for g in self._groups.values():
                if g.size == 0:
                    continue
                pobs = g.predicted_obs(prev_obs, prev_a)
                errs = np.linalg.norm(pobs[:, -2:] - obs[-2:], axis=1)
                for i in range(g.size):
                    fid = int(g.frame_ids[i])
                    prev = self.task_ema_base.get(fid, 1.0)
                    self.task_ema_base[fid] = d * prev + (1.0 - d) * float(errs[i])
        if z_now is None:
            z_now = self._z_tower(obs)
        aug = np.concatenate([obs, z_now])
        self.t2.step(aug, self._prev_aug, prev_a, scoring_mode)
        self._prev_aug = aug
        self._z_now = z_now
        return stats  # base-only: the engine's on-demand births mirror flat

    def age_all(self, min_age_cycles: int) -> None:
        super().age_all(min_age_cycles)
        self.t2.offline_cycle()

    def evict(self, frame_ids: list[int]) -> None:
        super().evict(frame_ids)
        for fid in frame_ids:
            self.task_ema_base.pop(fid, None)

    # -- the cross-tier arbiter ------------------------------------------------
    def best_frame_predictor(self, scorer):
        self.arb_total += 1
        base_age, base_pred = super().best_frame_predictor(scorer)
        t2b = self.t2.best()
        if t2b is None:
            return base_age, base_pred
        g2, i2, age2, ema2 = t2b
        base_ema = None
        bb = self._base_best()
        if bb is not None:
            g, i = bb
            base_ema = self.task_ema_base.get(int(g.frame_ids[i]), 1.0)
        if base_ema is not None and base_ema <= ema2:
            return base_age, base_pred
        # tier-2 wins the arbiter
        self.arb_t2 += 1
        od = self.t2.obs_dim
        z = self._z_now

        def predict_decoded(obs_: np.ndarray, action: int, g=g2, i=i2, z=z, od=od):
            aug_ = np.concatenate([obs_, z])
            pose, _ = g.encode(aug_)
            pred, _ = g.predict_next(pose, action)
            recon, _ = g.reconstruct(pred)
            return recon[i][:od]

        return age2, predict_decoded


def run_arm(seed: int, family: str, rung: int, encoding: str, n_cycles: int,
            frames_mode: str) -> dict:
    cfg = Config(
        obs_dim=obs_dim_of(encoding),
        n_actions=M,
        policy_mode="curiosity",
        episode_mode="continuous",
        n_cycles=n_cycles,
        event_head_eta=0.5,
    )
    worlds: list[EchoWorld] = []

    def factory(config: Config, rng: np.random.Generator) -> EchoWorld:
        w = EchoWorld(config, rng, family, rung, encoding)
        worlds.append(w)
        return w

    inner = CompletionItchPolicy(
        PolicyParams.from_config(cfg),
        kappa=0.25,
        progress_index=cfg.obs_dim - 2,
        pocket_index=cfg.obs_dim - 1,
        commit_kappa=0.0,
        explore_defers_holds=False,
    )
    rec = SeqRecordingPolicy(inner, cfg.obs_dim)

    RUN["seed"] = seed
    RUN["mode"] = frames_mode
    RUN["stores"] = []
    engine_mod.FrameStore = ComposedFrameStore if frames_mode != "flat" else FrameStore
    try:
        summary = Engine(cfg, world_factory=factory, policy=rec).run(seed)
    finally:
        engine_mod.FrameStore = FrameStore

    w = worlds[0]
    half = w.total_steps // 2
    back = sum(1 for s in w.accept_steps if s > half)
    row = {
        "seed": seed,
        "family": family,
        "rung": rung,
        "encoding": encoding,
        "policy": "stack-nc",
        "frames": frames_mode,
        "steps": w.total_steps,
        "accepts": len(w.accept_steps),
        "accepts_back": back,
        "accept_per_1k_back": round(back / max(w.total_steps - half, 1) * 1000, 3),
        "violations": w.violations,
        "pred_late": summary.pred_error_late,
        "population": summary.final_population,
        "pulse_err": round(float(rec.err_sum[-1] / max(rec.n, 1)), 6),
        "progress_err": round(float(rec.err_sum[-2] / max(rec.n, 1)), 6),
        "enc_err": round(float(rec.err_sum[:-2].mean() / max(rec.n, 1)), 6),
        "completions": inner.completions_fired,
        "false_completions": inner.false_completions,
    }
    if RUN["stores"]:
        store = RUN["stores"][0]
        t2 = store.t2
        b = t2.best()
        bb = store._base_best()
        base_ema = (
            None
            if bb is None
            else round(store.task_ema_base.get(int(bb[0].frame_ids[bb[1]]), 1.0), 6)
        )
        row.update(
            {
                "base_best_task_ema": base_ema,
                "t2_population": t2.store.population_size,
                "t2_map_rate": round(t2.mapped_steps / max(t2.total_steps, 1), 4),
                "t2_best_task_ema": None if b is None else round(b[3], 6),
                "arb_t2_share": round(store.arb_t2 / max(store.arb_total, 1), 4),
            }
        )
    return row


def calib(family: str, rung: int, encoding: str, frames_mode: str, n_cycles: int,
          n_seeds: int = SEEDS, out_tag: str | None = None) -> None:
    tag = out_tag or f"{family}{rung}-{encoding}-{frames_mode}"
    out = RIG / f"calib-{tag}-c{n_cycles}.jsonl"
    if out.exists():
        raise SystemExit(f"{out} exists — one reading per config; move it aside to re-run")
    rows = []
    with out.open("a") as f:
        for seed in range(n_seeds):
            row = run_arm(seed, family, rung, encoding, n_cycles, frames_mode)
            rows.append(row)
            f.write(json.dumps(row) + "\n")
            print(json.dumps(row), flush=True)
    rates = sorted(r["accept_per_1k_back"] for r in rows)
    summary = {
        "tag": tag,
        "seeds": n_seeds,
        "accept_per_1k_back_min": rates[0],
        "accept_per_1k_back_median": rates[len(rates) // 2],
        "accept_per_1k_back_max": rates[-1],
        "seeds_with_back_accepts": sum(1 for r in rows if r["accepts_back"] > 0),
    }
    with out.open("a") as f:
        f.write(json.dumps(summary) + "\n")
    print(f"CALIB {json.dumps(summary)}", flush=True)


def main() -> int:
    if len(sys.argv) >= 6 and sys.argv[1] == "calib":
        family = sys.argv[2]
        rung = int(sys.argv[3])
        encoding = sys.argv[4]
        frames_mode = sys.argv[5]
        n_cycles = int(sys.argv[6]) if len(sys.argv) > 6 else 18
        n_seeds = int(sys.argv[7]) if len(sys.argv) > 7 else SEEDS
        tag = None
        if n_seeds != SEEDS:
            tag = f"{family}{rung}-{encoding}-{frames_mode}-pilot{n_seeds}"
        if family not in ("R", "C") or encoding not in ENCODINGS:
            raise SystemExit("usage: compose.py calib R|C <rung> <enc> <frames_mode> [c] [seeds]")
        if frames_mode not in ("flat", "tower", "ref-pose", "ref-pred"):
            raise SystemExit(f"unknown frames_mode {frames_mode}")
        calib(family, rung, encoding, frames_mode, n_cycles, n_seeds, tag)
        return 0
    raise SystemExit("usage: compose.py calib <family> <rung> <enc> <frames_mode> [c] [seeds]")


if __name__ == "__main__":
    raise SystemExit(main())
