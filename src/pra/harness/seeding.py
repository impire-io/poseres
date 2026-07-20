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

    # Defaults are the SEEDING-DIAGNOSIS frozen values (2026-07-20 pilot).
    n_pretrain: int = 30
    n_probe: int = 30
    theta_b: float = 0.30
    theta_c: float = 0.33
    w_smooth: int = 240
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


def _rover_factory(
    layout_seed, permute=False, permute_seed=None, extra_ray=False, extra_ray_pending=False
):
    def factory(cfg: Config, rng):
        return make_rover_body(
            cfg,
            rng,
            layout_seed=layout_seed,
            permute=permute,
            permute_seed=permute_seed,
            extra_ray=extra_ray,
            extra_ray_pending=extra_ray_pending,
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


def _probe(
    seed: int,
    resume_state: SystemState | None,
    params: SeedingParams,
    map_label: str,
    *,
    grow: bool = False,
) -> tuple[np.ndarray, SystemState]:
    """Run the probe phase on ``map_label`` and return (probe-map trajectory,
    final state) so an A→B→C chain can continue. For resumed arms the prior-map
    prefix is sliced off. ``grow`` selects the +1-sensor rover: a native 11-dim
    body for a fresh arm, or a pending 10→11 resize for a resumed chain."""
    layout = _layout_seed(seed, map_label)
    if resume_state is None:  # fresh: whole trajectory (warmup + probe cycles)
        base = params.base_config.replace(obs_dim=11) if grow else params.base_config
        cfg = _fixed_length_config(params.n_probe, base)
        factory = _rover_factory(layout, extra_ray=grow)
        final = _capture(cfg, factory, seed)
        return np.asarray(final.pred_errors, dtype=np.float64), final
    # seeded / maturity: extend the resumed run by n_probe cycles, slice the prefix
    prior_len = len(resume_state.pred_errors)
    total = resume_state.cycles_done + params.n_probe
    probe_cfg = _fixed_length_config(total, resume_state.config)
    probe_state = dataclasses.replace(resume_state, config=probe_cfg)
    factory = _rover_factory(layout, extra_ray_pending=grow)
    final = _capture(probe_cfg, factory, seed, resume_from=probe_state)
    return np.asarray(final.pred_errors[prior_len:], dtype=np.float64), final


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


def _hop1(seed: int, params: SeedingParams) -> dict[str, tuple[np.ndarray, SystemState | None]]:
    """Hop 1 (A→B): pretrain seeded (map A) and maturity (permuted), then probe
    all three arms on map B. Returns arm -> (probe trajectory, post-B state) so
    the seeded/maturity chains can continue into hop 2 (fresh does not chain)."""
    seeded_a = _pretrain(seed, params, permute=False)
    maturity_a = _pretrain(seed, params, permute=True)
    seeded_traj, seeded_ab = _probe(seed, seeded_a, params, "B")
    fresh_traj, _ = _probe(seed, None, params, "B")
    maturity_traj, maturity_mb = _probe(seed, maturity_a, params, "B")
    return {
        "seeded": (seeded_traj, seeded_ab),
        "fresh": (fresh_traj, None),
        "maturity": (maturity_traj, maturity_mb),
    }


def _hop2(
    seed: int, params: SeedingParams, seeded_ab: SystemState, maturity_mb: SystemState
) -> dict[str, np.ndarray]:
    """Hop 2 (B→resize→C): grow the seeded/maturity chains by one sensor onto
    map C; fresh-C mounts a native 11-dim rover. Returns arm -> trajectory."""
    seeded_traj, _ = _probe(seed, seeded_ab, params, "C", grow=True)
    fresh_traj, _ = _probe(seed, None, params, "C", grow=True)
    maturity_traj, _ = _probe(seed, maturity_mb, params, "C", grow=True)
    return {"seeded": seeded_traj, "fresh": fresh_traj, "maturity": maturity_traj}


def _score_hop(readings, tau, reached, seed, map_label, trajs, theta, w) -> None:
    """Common-length censoring + time-to-threshold for one seed's arms on one
    map; appends readings and fills the tau/reached tables in place."""
    n_cens = min(t.size for t in trajs.values())
    for arm, traj in trajs.items():
        t, r = _time_to_threshold(traj, theta, w, n_cens)
        final_err = float(_smooth(traj, w)[-1]) if traj.size else float("nan")
        readings.append(ArmReading(arm, seed, map_label, theta, t, r, final_err, n_cens))
        tau[arm][seed] = t
        reached[arm][seed] = r


def _delta_margin(margin2: Margin, margin1: Margin) -> Margin:
    """The non-shrink statistic: per-seed ``margin2 − margin1`` (both are paired
    over the same sorted seed set, so their per_seed lists align)."""
    per_seed = [m2 - m1 for m1, m2 in zip(margin1.per_seed, margin2.per_seed, strict=True)]
    arr = np.asarray(per_seed, dtype=np.float64)
    n = int(arr.size)
    mean = float(arr.mean()) if n else 0.0
    std = float(arr.std()) if n else 0.0
    se = float(std / np.sqrt(n)) if n else 0.0
    n_better = int(sum(1 for v in per_seed if v > 0))
    return Margin("delta", per_seed, mean, std, se, n_better, n)


def run_seeding(
    seeds: list[int], mode: str, params: SeedingParams, *, do_hop2: bool = True
) -> SeedingResult:
    """Run the brain-seeding experiment. ``mode`` is ``"pilot"`` (hop-1
    calibration read, no bars) or ``"confirmatory"`` (decide B1/B2, and — when
    ``do_hop2`` — the compounding bar C1)."""
    readings: list[ArmReading] = []
    tau_b: dict[str, dict[int, int]] = {"seeded": {}, "fresh": {}, "maturity": {}}
    reached_b: dict[str, dict[int, bool]] = {"seeded": {}, "fresh": {}, "maturity": {}}
    tau_c: dict[str, dict[int, int]] = {"seeded": {}, "fresh": {}, "maturity": {}}
    reached_c: dict[str, dict[int, bool]] = {"seeded": {}, "fresh": {}, "maturity": {}}
    fresh_curves: list[np.ndarray] = []
    hop2 = mode == "confirmatory" and do_hop2

    for seed in seeds:
        arms = _hop1(seed, params)
        _score_hop(
            readings,
            tau_b,
            reached_b,
            seed,
            "B",
            {a: t for a, (t, _) in arms.items()},
            params.theta_b,
            params.w_smooth,
        )
        fresh_curves.append(arms["fresh"][0])
        if hop2:
            c = _hop2(seed, params, arms["seeded"][1], arms["maturity"][1])
            _score_hop(readings, tau_c, reached_c, seed, "C", c, params.theta_c, params.w_smooth)

    margins = {
        "margin1": _margin("margin1", tau_b["seeded"], tau_b["fresh"]),
        "marginM": _margin("marginM", tau_b["seeded"], tau_b["maturity"]),
    }
    reach_rates = {
        f"{arm}_B": (sum(reached_b[arm].values()) / len(seeds) if seeds else 0.0)
        for arm in ("seeded", "fresh", "maturity")
    }
    if hop2:
        margins["margin2"] = _margin("margin2", tau_c["seeded"], tau_c["fresh"])
        margins["delta"] = _delta_margin(margins["margin2"], margins["margin1"])
        reach_rates.update(
            {
                f"{arm}_C": (sum(reached_c[arm].values()) / len(seeds) if seeds else 0.0)
                for arm in ("seeded", "fresh", "maturity")
            }
        )

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
        passes = [b1, b2]
        if hop2:
            d = margins["delta"]
            c_sup = _superiority(margins["margin2"])
            c_non = _noninferior(d)
            c1 = c_sup and c_non
            detail = _fmt_margin(
                margins["margin2"], reach_rates, "seeded_C", "fresh_C", superiority=True
            )
            detail += (
                f"; delta {d.mean:+.0f} (non-shrink "
                f"{'PASS' if c_non else 'fail'}, >= {d.bound_noninferiority:+.0f})"
            )
            bars.append(
                Bar(
                    "C1",
                    "head start does not shrink across the resize hop (B→resize→C)",
                    "PASS" if c1 else "FAIL",
                    detail,
                )
            )
            passes.append(c1)
        overall = "PASS" if all(passes) else "FAIL"
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
        n_pretrain=int(d.get("n_pretrain", 30)),
        n_probe=int(d.get("n_probe", 30)),
        theta_b=float(d.get("theta_b", 0.30)),
        theta_c=float(d.get("theta_c", 0.33)),
        w_smooth=int(d.get("w_smooth", 240)),
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
