"""Ladder runner (feature 005, ROADMAP A3) — run the complexity-ladder rungs
and judge them against the pre-registered criteria in
``design/validate/LADDER-CRITERIA.md``.

Investigatory at the build level: a rung FAIL is a finding, reported with
its numbers, never an exit-code failure. Each rung composes existing
instruments — per-seed engine runs in worker processes (reassembled in seed
order; parallelism never changes results), the L1 paired degenerate twin
(same seed, machinery-equal — the T3SCALE lesson), the L2 churn-matched
pairing via the ``run_suite`` quartet plus the snapshot census (the Doc 06
persistence seam as instrument), and the L3 horizon-checkpoint reading
(the T4 rule applied to the controllable ``true_dim``).

Default dial grid: when ``base.world`` already selects a rung's world, that
rung runs the base config as its single dial set; otherwise the rung runs
the pre-registered first-results dials (LADDER-CRITERIA / research R9).
"""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
from time import perf_counter

from pra.config import Config
from pra.core.engine import Engine
from pra.harness.acceptance import FAIL, PASS, AcceptanceVerdict, Measured, strict_majority
from pra.harness.runner import run_suite
from pra.persistence.snapshot import decode
from pra.persistence.store import InMemorySnapshotStore
from pra.telemetry.recorder import PerSeedRunSummary
from pra.world.ladder import make_world

__all__ = ["RungResult", "run_ladder", "rung_dial_sets"]

RUNGS = ("l1", "l2", "l3")


@dataclass
class RungResult:
    rung: str
    label: str
    config: Config
    rows: list[dict]
    verdict: AcceptanceVerdict
    failed_seeds: list[int] = field(default_factory=list)
    wall_clock_seconds: float = 0.0


def rung_dial_sets(base: Config, rung: str) -> list[tuple[str, Config]]:
    """The (label, config) dial sets a rung runs — the base config when it
    already selects this rung's world, else the pre-registered first-results
    dials (LADDER-CRITERIA.md)."""
    if rung == "l1":
        if base.world == "nonuniform":
            return [(f"L1@noise={base.region_noise_std:g}", base)]
        return [
            (
                f"L1@noise={sigma:g}",
                base.replace(world="nonuniform", region_noise_std=sigma),
            )
            for sigma in (0.2, 0.8)
        ]
    if rung == "l2":
        if base.world == "compositional":
            dims = base.factor_dims if base.factor_dims else (base.true_dim,)
            return [(f"L2@dims={'+'.join(map(str, dims))}", base)]
        return [
            (
                f"L2@dims={'+'.join(map(str, dims))}",
                base.replace(world="compositional", true_dim=6, obs_dim=18, factor_dims=dims),
            )
            for dims in ((3, 3), (2, 2, 2))
        ]
    if rung == "l3":
        if base.world == "distractor":
            return [(f"L3@{base.distractor_mode}", base)]
        return [
            (
                f"L3@{mode}",
                base.replace(
                    world="distractor",
                    obs_dim=20,
                    distractor_dim=3,
                    distractor_channels=10,
                    distractor_mode=mode,
                ),
            )
            for mode in ("structured", "noise")
        ]
    raise ValueError(f"unknown rung {rung!r} (expected one of {RUNGS})")


# --- per-seed workers (module-level: picklable) -----------------------------


def _captured_run(cfg: Config, seed: int) -> tuple[PerSeedRunSummary, dict]:
    """One engine run capturing the world instance for its harness-only
    ``ladder_readings()`` (the closure never crosses a process boundary)."""
    holder: dict = {}

    def factory(config: Config, rng):
        world = make_world(config, rng)
        holder["world"] = world
        return world

    summary = Engine(cfg, world_factory=factory).run(seed)
    readings = (
        holder["world"].ladder_readings() if hasattr(holder["world"], "ladder_readings") else {}
    )
    return summary, readings


def _run_l1_seed(cfg: Config, seed: int) -> tuple[int, dict]:
    summary, readings = _captured_run(cfg, seed)
    twin = Engine(cfg.replace(region_noise_std=0.0), world_factory=make_world).run(seed)
    return seed, {
        "seed": seed,
        "occupancy": readings.get("occupancy"),
        "best_dim": summary.best_dim,
        "improvement": summary.improvement,
        "twin_best_dim": twin.best_dim,
        "twin_improvement": twin.improvement,
    }


def _run_l2_census_seed(cfg: Config, seed: int) -> tuple[int, dict]:
    """The census run: same (config, seed) as the quartet's predictive arm —
    identical by determinism — with one end-of-run snapshot decoded for the
    per-dim population (Doc 06 seam as instrument)."""
    store = InMemorySnapshotStore()
    cadence = cfg.effective_n_cycles
    summary = Engine(
        cfg.replace(snapshot_every_n_cycles=cadence), snapshot_store=store, world_factory=make_world
    ).run(seed)
    census: dict[int, dict] = {}
    snapshots = store.list()
    if snapshots:
        state = decode(store.read(snapshots[0][0]))
        patience = cfg.effective_min_age_cycles
        for dim, tensors in state.frame_store["groups"].items():
            ages = tensors["age_cycles"]
            census[int(dim)] = {
                "frames": int(len(tensors["frame_ids"])),
                "mature": int((ages >= patience).sum()),
            }
    return seed, {
        "seed": seed,
        "best_dim": summary.best_dim,
        "census": {str(d): census[d] for d in sorted(census)},
    }


def _run_l3_seed(cfg: Config, seed: int) -> tuple[int, dict]:
    summary, readings = _captured_run(cfg, seed)
    return seed, {
        "seed": seed,
        "best_dim": summary.best_dim,
        "improvement": summary.improvement,
        "checkpoints": {
            str(c): summary.checkpoints[c].best_dim for c in sorted(summary.checkpoints)
        },
        "controllable_obs_dim": readings.get("controllable_obs_dim"),
    }


def _pool_map(
    worker, cfg: Config, seeds: list[int], workers: int
) -> tuple[dict[int, dict], list[int]]:
    """Run a per-seed worker across seeds; reassemble in seed order; surface
    failed seeds instead of dropping them (FR-008 house rule)."""
    rows: dict[int, dict] = {}
    failed: list[int] = []
    if workers > 1 and len(seeds) > 1:
        with ProcessPoolExecutor(max_workers=min(workers, len(seeds))) as pool:
            futures = {seed: pool.submit(worker, cfg, seed) for seed in seeds}
            for seed, fut in futures.items():
                try:
                    rows[seed] = fut.result()[1]
                except Exception:  # noqa: BLE001 — reported, not fatal
                    failed.append(seed)
    else:
        for seed in seeds:
            try:
                rows[seed] = worker(cfg, seed)[1]
            except Exception:  # noqa: BLE001 — reported, not fatal
                failed.append(seed)
    return rows, failed


# --- judges (LADDER-CRITERIA.md, pre-registered) ----------------------------


def _judge_l1(rows: list[dict], n: int, label: str) -> AcceptanceVerdict:
    near = sum(
        1
        for r in rows
        if r["best_dim"] is not None
        and r["twin_best_dim"] is not None
        and abs(r["best_dim"] - r["twin_best_dim"]) <= 1
    )
    held = sum(
        1
        for r in rows
        if r["improvement"] is not None
        and r["twin_improvement"] is not None
        and r["improvement"] >= 0.5 * r["twin_improvement"]
    )
    occ_ok = sum(1 for r in rows if r["occupancy"] is not None and 0.25 <= r["occupancy"] <= 0.75)
    verdict = (
        PASS
        if strict_majority(near, n) and strict_majority(held, n) and strict_majority(occ_ok, n)
        else FAIL
    )
    occs = [r["occupancy"] for r in rows]
    measured = Measured(
        per_seed=occs,
        note=(
            f"best_dim within 1 of twin in {near}/{n}; improvement >= half of twin's in "
            f"{held}/{n}; occupancy in [0.25, 0.75] in {occ_ok}/{n} (per_seed = occupancy)"
        ),
    )
    return AcceptanceVerdict(
        label,
        "Non-uniform world — structure survives beside a region nothing can learn, "
        "and the occupancy instrument reads.",
        "paired vs degenerate twin: best_dim within 1 AND improvement >= 0.5x, "
        "each in a strict majority; occupancy in [0.25, 0.75] in a strict majority",
        verdict,
        measured,
    )


def _judge_l2(
    rows: list[dict], n: int, label: str, factor_dims: tuple[int, ...]
) -> AcceptanceVerdict:
    lo, hi = min(factor_dims) - 1, sum(factor_dims) + 1
    margins = [r.get("paired_margin") for r in rows]
    beat = sum(1 for m in margins if m is not None and m > 0)
    enveloped = sum(1 for r in rows if r["best_dim"] is not None and lo <= r["best_dim"] <= hi)
    verdict = PASS if strict_majority(beat, n) and strict_majority(enveloped, n) else FAIL
    measured = Measured(
        per_seed=margins,
        note=(
            f"churn-matched beat identity in {beat}/{n}; best_dim in [{lo}, {hi}] in "
            f"{enveloped}/{n} (per_seed = paired margins); census recorded per seed"
        ),
    )
    return AcceptanceVerdict(
        label,
        "Compositional world — the system still learns dynamics beyond persistence, "
        "and the discovered structure lands inside the known parts envelope.",
        "churn-matched predictive > identity (paired) in a strict majority AND "
        f"best_dim within [min part - 1, sum + 1] = [{lo}, {hi}] in a strict majority",
        verdict,
        measured,
    )


def _judge_l3(rows: list[dict], n: int, label: str, true_dim: int) -> AcceptanceVerdict:
    checkpoints = sorted({c for r in rows for c in r["checkpoints"]}, key=int)
    all_pass = True
    per_cp = []
    for c in checkpoints:
        within = sum(
            1 for r in rows if c in r["checkpoints"] and abs(r["checkpoints"][c] - true_dim) <= 1
        )
        per_cp.append(f"@{c}: {within}/{n}")
        if not strict_majority(within, n):
            all_pass = False
    measured = Measured(
        per_seed=[r["best_dim"] for r in rows],
        note=(
            f"within 1 of controllable true_dim={true_dim} — "
            + "; ".join(per_cp)
            + " (per_seed = final best_dim)"
        ),
    )
    return AcceptanceVerdict(
        label,
        "Distractor world — selection tracks the controllable structure, not the "
        "channels that move on their own.",
        f"|best_dim - {true_dim}| <= 1 in a strict majority at EVERY checkpoint "
        "(controllable true_dim; the T4 horizon rule)",
        PASS if all_pass else FAIL,
        measured,
    )


# --- rung runners ------------------------------------------------------------


def _run_l1(label: str, cfg: Config, seeds: list[int], workers: int) -> RungResult:
    t0 = perf_counter()
    rows_by_seed, failed = _pool_map(_run_l1_seed, cfg, seeds, workers)
    rows = [rows_by_seed[s] for s in seeds if s in rows_by_seed]
    verdict = _judge_l1(rows, len(seeds), label)
    return RungResult("l1", label, cfg, rows, verdict, failed, perf_counter() - t0)


def _run_l2(label: str, cfg: Config, seeds: list[int], workers: int) -> RungResult:
    t0 = perf_counter()
    suite = run_suite(
        cfg.replace(seeds=tuple(seeds)),
        with_ablation=True,
        with_matched=True,
        workers=workers,
        world_factory=make_world,
    )
    census_by_seed, census_failed = _pool_map(_run_l2_census_seed, cfg, seeds, workers)
    by_seed = {s.seed: s for s in suite.predictive}
    rows = []
    for seed in seeds:
        if seed not in by_seed or seed not in census_by_seed:
            continue
        matched = suite.matched.get(seed)
        ident = suite.identity.get(seed)
        margin = (
            matched.improvement - ident.improvement
            if matched is not None
            and ident is not None
            and matched.improvement is not None
            and ident.improvement is not None
            else None
        )
        rows.append(
            {
                "seed": seed,
                "best_dim": by_seed[seed].best_dim,
                "improvement": by_seed[seed].improvement,
                "matched_improvement": matched.improvement if matched else None,
                "identity_improvement": ident.improvement if ident else None,
                "paired_margin": margin,
                "census": census_by_seed[seed]["census"],
            }
        )
    factor_dims = cfg.factor_dims if cfg.factor_dims else (cfg.true_dim,)
    verdict = _judge_l2(rows, len(seeds), label, factor_dims)
    failed = sorted(set(suite.failed_seeds) | set(census_failed))
    return RungResult("l2", label, cfg, rows, verdict, failed, perf_counter() - t0)


def _run_l3(label: str, cfg: Config, seeds: list[int], workers: int) -> RungResult:
    t0 = perf_counter()
    rows_by_seed, failed = _pool_map(_run_l3_seed, cfg, seeds, workers)
    rows = [rows_by_seed[s] for s in seeds if s in rows_by_seed]
    verdict = _judge_l3(rows, len(seeds), label, cfg.true_dim)
    return RungResult("l3", label, cfg, rows, verdict, failed, perf_counter() - t0)


def run_ladder(
    base: Config,
    rungs: tuple[str, ...] | list[str] = RUNGS,
    seeds: list[int] | None = None,
    *,
    workers: int = 1,
) -> list[RungResult]:
    """Run the requested rungs across seeds and judge each dial set against
    the pre-registered criteria. Never raises on a rung FAIL — the verdict is
    the data."""
    seeds = list(seeds) if seeds is not None else list(base.seeds)
    runners = {"l1": _run_l1, "l2": _run_l2, "l3": _run_l3}
    results: list[RungResult] = []
    for rung in rungs:
        if rung not in runners:
            raise ValueError(f"unknown rung {rung!r} (expected one of {RUNGS})")
        for label, cfg in rung_dial_sets(base, rung):
            results.append(runners[rung](label, cfg, seeds, workers))
    return results
