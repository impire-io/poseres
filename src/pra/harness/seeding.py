"""Brain-seeding experiment (feature 028, ROADMAP compounding-intelligence
horizon; SEEDING-DIAGNOSIS).

Measures whether a snapshotted brain used as a *seed* reaches competence on a
new rover map in less experience than a blank brain (transfer) and than an
equally-experienced brain from an unrelated world (transfer, not maturity), and
whether that head start survives a body-growing hop (compounding). All
orchestration over the unchanged engine: pre-train → capture snapshot → resume
on a new map, reading the per-step prediction-error trajectory back out of the
captured :class:`SystemState` (``pred_errors``). No engine/core edits.

**The three arms** on a probe map, per seed:
- ``seeded`` — the brain pre-trained on map A.
- ``fresh`` — a blank brain (warms up on the probe map, then learns it).
- ``maturity`` — a brain that spent the *identical* pre-train budget on the
  permuted rover (learnable but unrelated), then dropped onto the probe map.

**Time-to-competence** ``tau`` is the first prediction-step on the probe map at
which the ``W_smooth``-smoothed prediction error crosses ``theta`` (lower is
better). Experience is counted in prediction-steps on the probe map from each
arm's first probe step; the fresh arm's warmup is part of its cost (a seeded
brain genuinely skips it — that is the head start). To keep the warmup-length
difference from faking a margin, all three arms at a seed are censored at a
common length (the shortest arm's probe trajectory). Positive margin = seeded
faster.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field

import numpy as np

from pra.config import Config
from pra.core.engine import Engine
from pra.examples.rover.world import make_rover_body
from pra.persistence.snapshot import SystemState, decode
from pra.persistence.store import InMemorySnapshotStore

__all__ = [
    "SeedingParams",
    "ArmReading",
    "Margin",
    "Bar",
    "SeedingResult",
    "run_seeding",
    "params_from_dict",
    "render_text",
    "to_json",
]

# The one-sided paired test the acceptance suite uses (T7 / A4 precedent): a
# claim of "faster" (superiority) PASSes iff the paired mean margin clears
# +T·SE; "no worse" (non-shrink) PASSes iff it clears −T·SE.
NONINFERIORITY_T = 1.9

# Layout-seed combiner: map X for experiment seed s draws its obstacle layout
# from a harness-owned generator, independent of the brain's run seed, so all
# three arms at a seed face the identical new map (SEEDING-DIAGNOSIS R4).
_MAP_OFFSET = {"A": 11, "B": 22, "C": 33}
_PERM_OFFSET = 44


def _layout_seed(seed: int, label: str) -> int:
    return (seed * 1_000_003 + _MAP_OFFSET[label]) % (2**31)


def _permute_seed(seed: int) -> int:
    return (seed * 1_000_003 + _PERM_OFFSET) % (2**31)


@dataclass(frozen=True)
class SeedingParams:
    """The frozen calibration table (pilot-set, then committed before the
    confirmatory run — SEEDING-DIAGNOSIS §calibration)."""

    n_pretrain: int = 24
    n_probe: int = 30
    theta_b: float = 0.30
    theta_c: float = 0.30
    w_smooth: int = 200
    # Base rover config (schedule dials); anatomy fixed at the reference widths.
    base_config: Config = field(default_factory=Config)


@dataclass
class ArmReading:
    arm: str  # "seeded" | "fresh" | "maturity"
    seed: int
    map_label: str  # "B" | "C"
    theta: float
    tau: int
    reached: bool
    final_error: float
    n_censor: int


@dataclass
class Margin:
    name: str
    per_seed: list[float]
    mean: float
    std: float
    se: float
    n_better: int
    n: int

    @property
    def bound_superiority(self) -> float:
        return NONINFERIORITY_T * self.se

    @property
    def bound_noninferiority(self) -> float:
        return -NONINFERIORITY_T * self.se


@dataclass
class Bar:
    name: str
    description: str
    verdict: str  # "PASS" | "FAIL"
    detail: str


@dataclass
class SeedingResult:
    mode: str
    seeds: list[int]
    params: SeedingParams
    readings: list[ArmReading]
    margins: dict[str, Margin]
    reach_rates: dict[str, float]
    bars: list[Bar]
    overall: str | None
    # pilot-only calibration read (median fresh curve), else None
    calibration: dict | None = None


# --- run capture ---------------------------------------------------------------


def _rover_factory(layout_seed, permute=False, permute_seed=None):
    def factory(cfg: Config, rng):
        return make_rover_body(
            cfg, rng, layout_seed=layout_seed, permute=permute, permute_seed=permute_seed
        )

    return factory


def _capture(cfg: Config, factory, seed: int, resume_from=None) -> SystemState:
    """Run one engine to completion and return the captured final SystemState.

    The run length is ``cfg`` (or, on resume, the resumed config): a single
    end-of-run snapshot is taken by pinning ``snapshot_every_n_cycles`` and
    ``horizon_checkpoints`` to the total cycle count.
    """
    store = InMemorySnapshotStore()
    Engine(cfg, world_factory=factory, snapshot_store=store).run(seed, resume_from=resume_from)
    listing = store.list()
    if not listing:
        raise RuntimeError(
            "seeding: no snapshot captured — check n_cycles/horizon_checkpoints/"
            "snapshot cadence line up on the final cycle"
        )
    return decode(store.read(listing[0][0]))


def _fixed_length_config(total_cycles: int, base: Config) -> Config:
    """A config whose run length is exactly ``total_cycles`` with one end
    snapshot: horizon checkpoints and snapshot cadence pinned to the total so
    ``effective_n_cycles`` does not silently stretch to the default 50."""
    return base.replace(
        n_cycles=total_cycles,
        horizon_checkpoints=(total_cycles,),
        snapshot_every_n_cycles=total_cycles,
    )


def _pretrain(seed: int, params: SeedingParams, *, permute: bool) -> SystemState:
    """Pre-train a brain to the plateau budget on map A (or, for the maturity
    control, the permuted rover — identical budget), returning the seed state."""
    cfg = _fixed_length_config(params.n_pretrain, params.base_config)
    layout = _layout_seed(seed, "A")
    factory = _rover_factory(
        layout, permute=permute, permute_seed=_permute_seed(seed) if permute else None
    )
    return _capture(cfg, factory, seed)


def _probe_trajectory(
    seed: int, seed_state: SystemState | None, params: SeedingParams, map_label: str
) -> np.ndarray:
    """Run the probe phase on ``map_label`` and return the per-step prediction
    error trajectory *on the probe map only* (the prior-map prefix sliced off
    for resumed arms)."""
    layout = _layout_seed(seed, map_label)
    factory = _rover_factory(layout)
    if seed_state is None:  # fresh: whole trajectory (warmup + probe cycles)
        cfg = _fixed_length_config(params.n_probe, params.base_config)
        final = _capture(cfg, factory, seed)
        return np.asarray(final.pred_errors, dtype=np.float64)
    # seeded / maturity: extend the resumed run by n_probe cycles, slice the prefix
    prior_len = len(seed_state.pred_errors)
    total = seed_state.cycles_done + params.n_probe
    probe_cfg = _fixed_length_config(total, seed_state.config)
    probe_state = dataclasses.replace(seed_state, config=probe_cfg)
    final = _capture(probe_cfg, factory, seed, resume_from=probe_state)
    return np.asarray(final.pred_errors[prior_len:], dtype=np.float64)


# --- metric --------------------------------------------------------------------


def _smooth(traj: np.ndarray, w: int) -> np.ndarray:
    """Trailing moving average of window ``w`` (partial at the start)."""
    if traj.size == 0:
        return traj
    w = max(1, min(w, traj.size))
    csum = np.cumsum(np.insert(traj, 0, 0.0))
    out = np.empty(traj.size, dtype=np.float64)
    for i in range(traj.size):
        lo = max(0, i + 1 - w)
        out[i] = (csum[i + 1] - csum[lo]) / (i + 1 - lo)
    return out


def _time_to_threshold(traj: np.ndarray, theta: float, w: int, n_censor: int) -> tuple[int, bool]:
    """First index within ``n_censor`` where the smoothed error ≤ ``theta``;
    censored at ``n_censor`` (reached=False) otherwise."""
    n = min(n_censor, traj.size)
    if n == 0:
        return n_censor, False
    sm = _smooth(traj[:n], w)
    hits = np.nonzero(sm <= theta)[0]
    if hits.size:
        return int(hits[0]), True
    return n_censor, False


# --- statistics ----------------------------------------------------------------


def _margin(name: str, a: dict[int, int], b: dict[int, int]) -> Margin:
    """Paired per-seed margin ``b − a`` (tau is lower-better, so ``fresh − seeded``
    is positive when the seeded arm is faster)."""
    per_seed: list[float] = []
    n_better = 0
    for s in sorted(a):
        if s in b:
            m = float(b[s] - a[s])
            per_seed.append(m)
            if m > 0:
                n_better += 1
    arr = np.asarray(per_seed, dtype=np.float64)
    n = int(arr.size)
    mean = float(arr.mean()) if n else 0.0
    std = float(arr.std()) if n else 0.0
    se = float(std / np.sqrt(n)) if n else 0.0
    return Margin(name, per_seed, mean, std, se, n_better, n)


def _superiority(m: Margin) -> bool:
    return bool(m.n >= 2 and m.mean > m.bound_superiority)


def _noninferior(m: Margin) -> bool:
    return bool(m.n >= 2 and m.mean >= m.bound_noninferiority)


# --- orchestration -------------------------------------------------------------


def _hop(
    seed: int, params: SeedingParams, map_label: str, theta: float
) -> dict[str, tuple[np.ndarray, SystemState | None]]:
    """Run all three arms' probe trajectories on ``map_label`` for one seed.
    Returns arm -> (trajectory, seed_state used) so hop 2 can chain the seeded
    and maturity arms onward."""
    seeded_seed = _pretrain(seed, params, permute=False)
    maturity_seed = _pretrain(seed, params, permute=True)
    return {
        "seeded": (_probe_trajectory(seed, seeded_seed, params, map_label), seeded_seed),
        "fresh": (_probe_trajectory(seed, None, params, map_label), None),
        "maturity": (_probe_trajectory(seed, maturity_seed, params, map_label), maturity_seed),
    }


def run_seeding(seeds: list[int], mode: str, params: SeedingParams) -> SeedingResult:
    """Run the brain-seeding experiment (hop 1: A→B). ``mode`` is ``"pilot"``
    (calibration read, no bars) or ``"confirmatory"`` (decide B1/B2)."""
    readings: list[ArmReading] = []
    tau_b: dict[str, dict[int, int]] = {"seeded": {}, "fresh": {}, "maturity": {}}
    reached_b: dict[str, dict[int, bool]] = {"seeded": {}, "fresh": {}, "maturity": {}}
    fresh_curves: list[np.ndarray] = []

    for seed in seeds:
        arms = _hop(seed, params, "B", params.theta_b)
        n_cens = min(traj.size for traj, _ in arms.values())
        for arm, (traj, _) in arms.items():
            tau, reached = _time_to_threshold(traj, params.theta_b, params.w_smooth, n_cens)
            final_err = float(_smooth(traj, params.w_smooth)[-1]) if traj.size else float("nan")
            readings.append(
                ArmReading(arm, seed, "B", params.theta_b, tau, reached, final_err, n_cens)
            )
            tau_b[arm][seed] = tau
            reached_b[arm][seed] = reached
        fresh_curves.append(arms["fresh"][0])

    margins = {
        "margin1": _margin("margin1", tau_b["seeded"], tau_b["fresh"]),
        "marginM": _margin("marginM", tau_b["seeded"], tau_b["maturity"]),
    }
    reach_rates = {
        f"{arm}_B": (sum(reached_b[arm].values()) / len(seeds) if seeds else 0.0)
        for arm in ("seeded", "fresh", "maturity")
    }

    bars: list[Bar] = []
    overall: str | None = None
    calibration: dict | None = None
    if mode == "confirmatory":
        b1 = _superiority(margins["margin1"])
        b2 = _superiority(margins["marginM"])
        bars = [
            Bar(
                "B1",
                "seeded reaches theta_B before fresh (transfer)",
                "PASS" if b1 else "FAIL",
                _fmt_margin(
                    margins["margin1"], reach_rates, "seeded_B", "fresh_B", superiority=True
                ),
            ),
            Bar(
                "B2",
                "seeded reaches theta_B before the maturity control (transfer, not maturity)",
                "PASS" if b2 else "FAIL",
                _fmt_margin(
                    margins["marginM"], reach_rates, "seeded_B", "maturity_B", superiority=True
                ),
            ),
        ]
        overall = "PASS" if (b1 and b2) else "FAIL"
    else:  # pilot: report the median fresh learning curve for theta calibration
        calibration = _calibrate(fresh_curves, params)

    return SeedingResult(
        mode=mode,
        seeds=list(seeds),
        params=params,
        readings=readings,
        margins=margins,
        reach_rates=reach_rates,
        bars=bars,
        overall=overall,
        calibration=calibration,
    )


def _calibrate(fresh_curves: list[np.ndarray], params: SeedingParams) -> dict:
    """Pilot calibration read: the median fresh smoothed curve's initial and
    plateau levels, and the p=0.5 gap threshold suggestion."""
    if not fresh_curves:
        return {}
    n = min(c.size for c in fresh_curves)
    stacked = np.vstack([_smooth(c[:n], params.w_smooth) for c in fresh_curves])
    median = np.median(stacked, axis=0)
    initial = float(median[0])
    plateau = float(np.mean(median[-max(1, n // 4) :]))
    theta_half = plateau + 0.5 * (initial - plateau)
    return {
        "n_probe_steps": int(n),
        "fresh_initial": initial,
        "fresh_plateau": plateau,
        "suggested_theta_p0.5": theta_half,
    }


def _fmt_margin(m: Margin, reach: dict, a_key: str, b_key: str, *, superiority: bool) -> str:
    bound = m.bound_superiority if superiority else m.bound_noninferiority
    op = ">" if superiority else ">="
    return (
        f"margin {m.mean:+.1f} +/- {m.std:.1f} (SE {m.se:.1f}) {op} "
        f"{'+' if superiority else ''}{NONINFERIORITY_T}*SE={bound:+.1f}; "
        f"seeded faster in {m.n_better}/{m.n} seeds; "
        f"reach {a_key} {reach.get(a_key, 0.0):.2f} / {b_key} {reach.get(b_key, 0.0):.2f}"
    )


# --- config, rendering ---------------------------------------------------------


def params_from_dict(d: dict) -> SeedingParams:
    """Build SeedingParams from a JSON dict; unrecognized keys feed the base
    rover Config (schedule dials)."""
    known = {"n_pretrain", "n_probe", "theta_b", "theta_c", "w_smooth"}
    base_overrides = {k: v for k, v in d.items() if k not in known}
    if "seeds" in base_overrides:
        base_overrides["seeds"] = tuple(base_overrides["seeds"])
    if "horizon_checkpoints" in base_overrides:
        base_overrides["horizon_checkpoints"] = tuple(base_overrides["horizon_checkpoints"])
    base = Config(**base_overrides) if base_overrides else Config()
    return SeedingParams(
        n_pretrain=int(d.get("n_pretrain", 24)),
        n_probe=int(d.get("n_probe", 30)),
        theta_b=float(d.get("theta_b", 0.30)),
        theta_c=float(d.get("theta_c", 0.30)),
        w_smooth=int(d.get("w_smooth", 200)),
        base_config=base,
    )


def render_text(result: SeedingResult) -> str:
    p = result.params
    lines = [
        f"BRAIN SEEDING  ({result.mode})  seeds {len(result.seeds)}  "
        f"n_pretrain={p.n_pretrain} n_probe={p.n_probe} "
        f"theta_B={p.theta_b:g} theta_C={p.theta_c:g} W_smooth={p.w_smooth}",
    ]
    if result.mode == "pilot" and result.calibration:
        c = result.calibration
        lines.append("  pilot calibration (median fresh curve on map B):")
        lines.append(
            f"    probe steps {c['n_probe_steps']}  initial {c['fresh_initial']:.4f}  "
            f"plateau {c['fresh_plateau']:.4f}  ->  suggested theta (p=0.5) "
            f"{c['suggested_theta_p0.5']:.4f}"
        )
        lines.append("  (no bar verdicts in pilot mode; freeze theta/budgets, then confirmatory)")
    for bar in result.bars:
        lines.append(f"  {bar.name}  {bar.description}")
        lines.append(f"      {bar.detail}   [{bar.verdict}]")
    if result.overall is not None:
        lines.append(f"  OVERALL  seeding holds (B1 & B2): [{result.overall}]")
    return "\n".join(lines)


def to_json(result: SeedingResult) -> dict:
    p = result.params
    return {
        "mode": result.mode,
        "seeds": result.seeds,
        "frozen": {
            "n_pretrain": p.n_pretrain,
            "n_probe": p.n_probe,
            "theta_b": p.theta_b,
            "theta_c": p.theta_c,
            "w_smooth": p.w_smooth,
        },
        "readings": [dataclasses.asdict(r) for r in result.readings],
        "margins": {
            name: {
                "mean": m.mean,
                "std": m.std,
                "se": m.se,
                "n_better": m.n_better,
                "n": m.n,
                "per_seed": m.per_seed,
            }
            for name, m in result.margins.items()
        },
        "reach_rates": result.reach_rates,
        "bars": [dataclasses.asdict(b) for b in result.bars],
        "overall": result.overall,
        "calibration": result.calibration,
    }
