"""Snapshot state + blob format (Doc 06 §2/§3, feature 003 research R2/R3/R6).

A :class:`SystemState` is the complete behavior-affecting state of a run at a
consolidation-cycle boundary: configuration in force, the frame population,
run counters and summary accumulators, drive/agency bookkeeping when present,
and the single generator's state. Encoding is a versioned ``.npz`` archive —
arrays under stable keys plus one ``meta`` JSON entry — loaded with
``allow_pickle=False`` (no pickle anywhere). The format version is checked
before any array is touched; body compatibility (``obs_dim``/``n_actions``) is
validated before any state is applied.
"""

from __future__ import annotations

import dataclasses
import io
import json
from dataclasses import dataclass

import numpy as np

from pra.config import Config

__all__ = [
    "FORMAT_VERSION",
    "SystemState",
    "SnapshotVersionError",
    "SnapshotCompatibilityError",
    "encode",
    "decode",
    "config_from_dict",
    "validate_body_compatibility",
]

FORMAT_VERSION = "1"

# Config fields that are tuples in the frozen dataclass (JSON round-trips them
# as lists); drive_weights is a tuple of (name, weight) pairs.
_TUPLE_FIELDS = ("seeds", "horizon_checkpoints")


class SnapshotVersionError(ValueError):
    """The blob's format version is not supported (Doc 06 §3.4)."""


class SnapshotCompatibilityError(ValueError):
    """The snapshot's body does not match the booting configuration (Doc 06 §5)."""


@dataclass
class SystemState:
    """Everything a resumed run needs (data-model §2)."""

    config: Config
    seed: int
    scoring_mode: str
    policy_mode: str
    cycles_done: int
    # counters
    obs_steps: int
    obs_after_warm: int
    lost_after_warm: int
    pop_sum: int
    warmed: bool
    pred_error_early: float | None  # fixed at end of warmup; must survive as-is
    # accumulators
    map_fractions: list[float]
    pred_errors: list[float]
    population_by_cycle: list[int]
    checkpoints: dict[int, tuple[int, int]]  # cycle -> (best_dim, population)
    # population
    frame_store: dict
    # agency bookkeeping (curiosity mode only)
    agency: dict | None
    # the single generator's state (research R2: it affects future behavior)
    rng_state: dict
    # reserved for Doc 06 §2's tool registry (component not yet built)
    tool_registry: list = dataclasses.field(default_factory=list)


def config_from_dict(d: dict) -> Config:
    """Rebuild the frozen Config from its JSON round-trip."""
    kwargs = dict(d)
    for name in _TUPLE_FIELDS:
        kwargs[name] = tuple(kwargs[name])
    kwargs["drive_weights"] = tuple((str(n), float(w)) for n, w in kwargs["drive_weights"])
    return Config(**kwargs)


def validate_body_compatibility(snapshot_config: Config, boot_config: Config) -> None:
    """Doc 06 §5: refuse to load state into a different body."""
    for field in ("obs_dim", "n_actions"):
        snap, boot = getattr(snapshot_config, field), getattr(boot_config, field)
        if snap != boot:
            raise SnapshotCompatibilityError(
                f"snapshot {field}={snap} is incompatible with booting {field}={boot}"
            )


def encode(state: SystemState) -> bytes:
    """Serialize to the versioned blob (research R3)."""
    arrays: dict[str, np.ndarray] = {}
    for dim, tensors in state.frame_store["groups"].items():
        for name, arr in tensors.items():
            arrays[f"g{dim}__{name}"] = arr
    arrays["acc__map_fractions"] = np.asarray(state.map_fractions, dtype=np.float64)
    arrays["acc__pred_errors"] = np.asarray(state.pred_errors, dtype=np.float64)
    arrays["acc__population_by_cycle"] = np.asarray(state.population_by_cycle, dtype=np.int64)

    agency_meta = None
    if state.agency is not None:
        a = state.agency
        arrays["agency__pred_error_history"] = np.asarray(a["pred_error_history"], dtype=np.float64)
        mem = a["observation_memory"]
        arrays["agency__observation_memory"] = (
            np.stack(mem) if len(mem) else np.zeros((0, state.config.obs_dim))
        )
        arrays["agency__values"] = np.asarray(a["values"], dtype=np.float64)
        arrays["agency__lp_terms"] = np.asarray(a["lp_terms"], dtype=np.float64)
        arrays["agency__novelty_terms"] = np.asarray(a["novelty_terms"], dtype=np.float64)
        agency_meta = {"directed_steps": a["directed_steps"], "total_steps": a["total_steps"]}

    meta = {
        "format_version": FORMAT_VERSION,
        "config": dataclasses.asdict(state.config),
        "seed": state.seed,
        "scoring_mode": state.scoring_mode,
        "policy_mode": state.policy_mode,
        "cycles_done": state.cycles_done,
        "counters": {
            "obs_steps": state.obs_steps,
            "obs_after_warm": state.obs_after_warm,
            "lost_after_warm": state.lost_after_warm,
            "pop_sum": state.pop_sum,
            "warmed": state.warmed,
            "pred_error_early": state.pred_error_early,
        },
        "checkpoints": {str(c): list(v) for c, v in state.checkpoints.items()},
        "group_dims": sorted(int(d) for d in state.frame_store["groups"]),
        "next_frame_id": state.frame_store["next_id"],
        "agency": agency_meta,
        "rng_state": state.rng_state,
        "tool_registry": state.tool_registry,
    }
    arrays["meta"] = np.array(json.dumps(meta))

    buf = io.BytesIO()
    np.savez_compressed(buf, **arrays)
    return buf.getvalue()


def decode(blob: bytes) -> SystemState:
    """Deserialize; the format version is checked before any array is read."""
    with np.load(io.BytesIO(blob), allow_pickle=False) as archive:
        meta = json.loads(str(archive["meta"]))
        version = meta.get("format_version")
        if version != FORMAT_VERSION:
            raise SnapshotVersionError(
                f"unsupported snapshot format version {version!r} (supported: {FORMAT_VERSION!r})"
            )
        from pra.core.frame import FrameStore

        groups: dict[int, dict[str, np.ndarray]] = {}
        for dim in meta["group_dims"]:
            groups[dim] = {
                name: np.array(archive[f"g{dim}__{name}"]) for name in FrameStore._GROUP_FIELDS
            }

        agency = None
        if meta["agency"] is not None:
            agency = {
                "pred_error_history": archive["agency__pred_error_history"].tolist(),
                "observation_memory": [
                    np.array(row) for row in archive["agency__observation_memory"]
                ],
                "values": archive["agency__values"].tolist(),
                "lp_terms": archive["agency__lp_terms"].tolist(),
                "novelty_terms": archive["agency__novelty_terms"].tolist(),
                "directed_steps": int(meta["agency"]["directed_steps"]),
                "total_steps": int(meta["agency"]["total_steps"]),
            }

        counters = meta["counters"]
        return SystemState(
            config=config_from_dict(meta["config"]),
            seed=int(meta["seed"]),
            scoring_mode=meta["scoring_mode"],
            policy_mode=meta["policy_mode"],
            cycles_done=int(meta["cycles_done"]),
            obs_steps=int(counters["obs_steps"]),
            obs_after_warm=int(counters["obs_after_warm"]),
            lost_after_warm=int(counters["lost_after_warm"]),
            pop_sum=int(counters["pop_sum"]),
            warmed=bool(counters["warmed"]),
            pred_error_early=counters["pred_error_early"],
            map_fractions=archive["acc__map_fractions"].tolist(),
            pred_errors=archive["acc__pred_errors"].tolist(),
            population_by_cycle=archive["acc__population_by_cycle"].tolist(),
            checkpoints={int(c): (int(v[0]), int(v[1])) for c, v in meta["checkpoints"].items()},
            frame_store={"next_id": int(meta["next_frame_id"]), "groups": groups},
            agency=agency,
            rng_state=meta["rng_state"],
            tool_registry=list(meta["tool_registry"]),
        )
