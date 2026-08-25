"""M0(c) on the cheap world first: the composed system (base blob +
tier-2 sidecar) must resume byte-exactly. Run A goes 50 cycles straight,
snapshotting at 25; run B resumes from the 25-cycle pair. PASS = final
base tensors and final tier-2 sidecar bytes identical, and the sidecar
round-trips byte-identically. Runs per mode (tower, bind-pred)."""

import io
import json
import sys
from pathlib import Path

import numpy as np

RIG = Path(__file__).parent
sys.path.insert(0, str(RIG))

import compose  # noqa: E402
from compose import RUN, ComposedFrameStore, t2_load_bytes, t2_state_bytes  # noqa: E402
from seq import EchoWorld, SeqRecordingPolicy, obs_dim_of  # noqa: E402

import pra.core.engine as engine_mod  # noqa: E402
from pra.action.policy import CompletionItchPolicy, PolicyParams  # noqa: E402
from pra.config import Config  # noqa: E402
from pra.core.engine import Engine  # noqa: E402
from pra.persistence.store import InMemorySnapshotStore  # noqa: E402


class SidecarStore(InMemorySnapshotStore):
    """Captures the tier-2 sidecar at the exact moment the engine writes
    the base blob (the C4 safe point) — the pair is the composed state."""

    def __init__(self):
        super().__init__()
        self.sidecars: dict[int, bytes] = {}  # cycle -> sidecar

    def write(self, blob: bytes, metadata: dict) -> str:
        sid = super().write(blob, metadata)
        self.sidecars[int(metadata["cycle"])] = t2_state_bytes(RUN["stores"][-1].t2)
        return sid


def base_bytes(store) -> bytes:
    arrays = {}
    for dim, g in store._groups.items():
        for name in store._GROUP_FIELDS:
            arrays[f"g{dim}__{name}"] = getattr(g, name)
    arrays["meta"] = np.array(json.dumps({"next_id": store._next_id}))
    buf = io.BytesIO()
    np.savez_compressed(buf, **arrays)
    return buf.getvalue()


def build(mode: str, seed: int):
    cfg = Config(
        obs_dim=obs_dim_of("W2"),
        n_actions=4,
        policy_mode="curiosity",
        episode_mode="continuous",
        n_cycles=50,
        horizon_checkpoints=(50,),
        snapshot_every_n_cycles=25,
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
    policy = SeqRecordingPolicy(inner, cfg.obs_dim)
    store = SidecarStore()
    return cfg, factory, policy, store


def run_mode(mode: str) -> None:
    seed = 0
    engine_mod.FrameStore = ComposedFrameStore
    try:
        # Run A: straight through, snapshots at 25 and 50
        RUN.update({"seed": seed, "mode": mode, "stores": [], "t2_blob": None})
        cfg, factory, policy, store_a = build(mode, seed)
        Engine(cfg, world_factory=factory, policy=policy, snapshot_store=store_a).run(seed)
        a_store = RUN["stores"][-1]
        a_base, a_t2 = base_bytes(a_store), t2_state_bytes(a_store.t2)

        # the 25-cycle pair
        blob25 = None
        for sid, meta in store_a.list():
            if int(meta["cycle"]) == 25:
                blob25 = store_a.read(sid)
        assert blob25 is not None, "no cycle-25 snapshot"
        side25 = store_a.sidecars[25]

        # sidecar round-trip byte-exactness
        RUN.update({"seed": seed, "mode": mode, "stores": [], "t2_blob": None})
        cfg2, factory2, policy2, _ = build(mode, seed)
        probe = ComposedFrameStore(
            cfg2.replace(event_head_eta=0.5), np.random.default_rng(seed)
        )
        t2_load_bytes(probe.t2, side25)
        assert t2_state_bytes(probe.t2) == side25, "sidecar round-trip differs"

        # Run B: resume from the pair, run to 50
        RUN.update({"seed": seed, "mode": mode, "stores": [], "t2_blob": side25})
        cfgb, factoryb, policyb, store_b = build(mode, seed)
        Engine(cfgb, world_factory=factoryb, policy=policyb, snapshot_store=store_b).run(
            seed, resume_from=blob25
        )
        b_store = RUN["stores"][-1]
        b_base, b_t2 = base_bytes(b_store), t2_state_bytes(b_store.t2)

        print(
            f"{mode}: base_equal={a_base == b_base} t2_equal={a_t2 == b_t2} "
            f"t2_pop={b_store.t2.population_size} roundtrip=ok"
        )
        assert a_base == b_base, f"{mode}: base tensors diverge on resume"
        assert a_t2 == b_t2, f"{mode}: tier-2 diverges on resume"
    finally:
        engine_mod.FrameStore = compose.FrameStore
        RUN["t2_blob"] = None


for mode in ("tower", "bind-pred"):
    run_mode(mode)
print("M0(c) echo-world reading: PASS")
