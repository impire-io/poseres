"""One-off instrument probe: z-block magnitude vs obs magnitude in a short
tower run (not part of any bar; numbers land in JOURNEY.md if load-bearing)."""

import sys
from pathlib import Path

import numpy as np

RIG = Path(__file__).parent
sys.path.insert(0, str(RIG))

import compose  # noqa: E402
from compose import RUN, ComposedFrameStore, obs_dim_of, M  # noqa: E402
from seq import EchoWorld, SeqRecordingPolicy  # noqa: E402

import pra.core.engine as engine_mod  # noqa: E402
from pra.action.policy import CompletionItchPolicy, PolicyParams  # noqa: E402
from pra.config import Config  # noqa: E402
from pra.core.engine import Engine  # noqa: E402

Z_MAGS: list[float] = []
OBS_MAGS: list[float] = []


class ProbeStore(ComposedFrameStore):
    def online_step(self, obs, prev_obs, prev_a, scoring_mode, *, ema_update=True):
        stats = super().online_step(obs, prev_obs, prev_a, scoring_mode, ema_update=ema_update)
        Z_MAGS.append(float(np.max(np.abs(self._z_now))))
        OBS_MAGS.append(float(np.max(np.abs(obs))))
        return stats


cfg = Config(
    obs_dim=obs_dim_of("W2"),
    n_actions=M,
    policy_mode="curiosity",
    episode_mode="continuous",
    n_cycles=2,
    warmup_episodes=5,
    horizon_checkpoints=(2,),
    event_head_eta=0.5,
)
worlds = []


def factory(config, rng):
    w = EchoWorld(config, rng, "R", 4, "W2")
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

RUN["seed"] = 0
RUN["mode"] = "tower"
RUN["stores"] = []
engine_mod.FrameStore = ProbeStore
try:
    Engine(cfg, world_factory=factory, policy=rec).run(0)
finally:
    engine_mod.FrameStore = engine_mod.FrameStore.__mro__[-2]  # restore FrameStore

zm = np.array(Z_MAGS)
om = np.array(OBS_MAGS)
print(f"steps={len(zm)}")
for name, v in (("z_maxabs", zm), ("obs_maxabs", om)):
    print(
        f"{name}: median={np.median(v):.3f} p90={np.percentile(v, 90):.3f} "
        f"max={v.max():.3f}"
    )
store = RUN["stores"][0]
print("t2 pop", store.t2.store.population_size, "base pop", store.population_size)
