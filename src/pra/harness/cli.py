"""Harness CLI (contracts/cli.md, FR-002/006/007/012).

``python -m pra.harness.cli <command>`` or the ``pra-validate`` console script.
Human-readable summary to stdout; optional JSON to a file. Exit 0 when the command
ran and produced a report (a test FAIL is data, not a CLI error); non-zero only on
an execution error, or — with ``--strict`` — when a T1-T6 test FAILs.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from time import perf_counter

from pra.config import Config
from pra.harness.acceptance import FAIL, evaluate_suite, evaluate_t7
from pra.harness.agency import run_agency
from pra.harness.report import (
    build_agency_report,
    build_determinism_report,
    build_scale_report,
    build_scale_t3_report,
    build_suite_report,
    render_json,
    render_text,
)
from pra.harness.runner import auto_workers, check_determinism, run_suite
from pra.harness.scale import run_scale, run_scale_t3
from pra.harness.scan import render_scan_text, run_scan

__all__ = ["main"]


def _int_list(text: str) -> tuple[int, ...]:
    return tuple(int(x) for x in text.split(",") if x.strip())


def _build_config(args: argparse.Namespace) -> Config:
    overrides: dict = {}
    if getattr(args, "config", None):
        overrides.update(json.loads(Path(args.config).read_text()))
    if "seeds" in overrides:
        overrides["seeds"] = tuple(overrides["seeds"])
    if "horizon_checkpoints" in overrides:
        overrides["horizon_checkpoints"] = tuple(overrides["horizon_checkpoints"])
    if getattr(args, "seeds", None):
        overrides["seeds"] = _int_list(args.seeds)
    if getattr(args, "true_dim", None) is not None:
        overrides["true_dim"] = args.true_dim
    if getattr(args, "obs_dim", None) is not None:
        overrides["obs_dim"] = args.obs_dim
    if getattr(args, "checkpoints", None):
        overrides["horizon_checkpoints"] = _int_list(args.checkpoints)
    return Config(**overrides)


def _write_json(path: str, report) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(render_json(report), indent=2))


def _resolve_workers(args: argparse.Namespace, n_tasks: int) -> int:
    requested = getattr(args, "workers", 0)
    return auto_workers(n_tasks) if requested <= 0 else requested


def _cmd_suite(args: argparse.Namespace) -> int:
    config = _build_config(args)
    suite_run = run_suite(config, workers=_resolve_workers(args, len(config.seeds)))
    if not suite_run.predictive:
        sys.stderr.write("pra-validate: every seed errored; the suite could not complete.\n")
        return 2
    tests = evaluate_suite(suite_run)
    report = build_suite_report(suite_run, tests)
    sys.stdout.write(render_text(report) + "\n")
    if args.json:
        _write_json(args.json, report)
    any_fail = any(t.verdict == FAIL for t in tests)
    if args.strict and (any_fail or suite_run.failed_seeds):
        return 1
    return 0


def _cmd_determinism(args: argparse.Namespace) -> int:
    config = _build_config(args)
    t0 = perf_counter()
    result = check_determinism(config, args.seed)
    report = build_determinism_report(config, result, perf_counter() - t0)
    sys.stdout.write(render_text(report) + "\n")
    if args.json:
        _write_json(args.json, report)
    return 0 if result.verdict == "PASS" else 1


def _cmd_scale(args: argparse.Namespace) -> int:
    base = _build_config(args)
    true_dims = list(_int_list(args.true_dims)) if args.true_dims else [20, 35, 50]
    seeds = list(_int_list(args.seeds)) if args.seeds else list(base.seeds)
    t0 = perf_counter()
    if args.t3:
        results = run_scale_t3(base, true_dims, seeds, workers=_resolve_workers(args, len(seeds)))
        report = build_scale_t3_report(base, seeds, results, perf_counter() - t0)
    else:
        readings = run_scale(base, true_dims, seeds, workers=_resolve_workers(args, len(seeds)))
        report = build_scale_report(base, seeds, readings, perf_counter() - t0)
    sys.stdout.write(render_text(report) + "\n")
    if args.json:
        _write_json(args.json, report)
    # T-SCALE is investigatory: a poor dimensionality result is never a build failure.
    return 0


def _parse_dims(text: str) -> list[int]:
    """Accept '1-30' (inclusive range) or a comma list '1,2,4,8'."""
    if "-" in text and "," not in text:
        lo, hi = text.split("-", 1)
        return list(range(int(lo), int(hi) + 1))
    return [int(x) for x in text.split(",") if x.strip()]


def _cmd_scan(args: argparse.Namespace) -> int:
    base = _build_config(args)
    true_dim = args.true_dim if args.true_dim is not None else base.true_dim
    dims = _parse_dims(args.dims) if args.dims else list(range(1, true_dim + 11))
    hidden_sizes = list(_int_list(args.hidden_sizes)) if args.hidden_sizes else [12]
    seeds = list(_int_list(args.seeds)) if args.seeds else [1, 2, 3]
    points = run_scan(
        base,
        true_dim,
        dims,
        hidden_sizes,
        seeds,
        train_episodes=args.train_episodes,
        eval_episodes=args.eval_episodes,
    )
    sys.stdout.write(render_scan_text(points, true_dim, seeds, args.train_episodes) + "\n")
    if args.json:
        out = Path(args.json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            json.dumps(
                {
                    "mode": "scan",
                    "true_dim": true_dim,
                    "seeds": seeds,
                    "train_episodes": args.train_episodes,
                    "eval_episodes": args.eval_episodes,
                    "points": [vars(p) for p in points],
                },
                indent=2,
            )
        )
    # diagnostic: never a pass/fail.
    return 0


def _cmd_agency(args: argparse.Namespace) -> int:
    config = _build_config(args)
    agency_run = run_agency(config, workers=_resolve_workers(args, len(config.seeds)))
    if not agency_run.curious:
        sys.stderr.write("pra-validate: every seed errored; agency run could not complete.\n")
        return 2
    t7 = evaluate_t7(agency_run)
    report = build_agency_report(agency_run, t7)
    sys.stdout.write(render_text(report) + "\n")
    if args.json:
        _write_json(args.json, report)
    if args.strict and (t7.verdict == FAIL or agency_run.failed_seeds):
        return 1
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pra-validate", description="PRA validation harness")
    sub = parser.add_subparsers(dest="command")

    p_suite = sub.add_parser("suite", help="run the acceptance suite T1-T6")
    p_suite.add_argument("--seeds")
    p_suite.add_argument("--true-dim", dest="true_dim", type=int)
    p_suite.add_argument("--obs-dim", dest="obs_dim", type=int)
    p_suite.add_argument("--checkpoints")
    p_suite.add_argument("--config")
    p_suite.add_argument("--json")
    p_suite.add_argument("--strict", action="store_true")
    p_suite.add_argument(
        "--workers",
        type=int,
        default=0,
        help="parallel seed processes (0 = one per seed up to CPU count); never changes results",
    )
    p_suite.set_defaults(func=_cmd_suite)

    p_det = sub.add_parser("determinism", help="run one seed twice; assert byte-identical")
    p_det.add_argument("--seed", type=int, default=1)
    p_det.add_argument("--true-dim", dest="true_dim", type=int)
    p_det.add_argument("--config")
    p_det.add_argument("--json")
    p_det.set_defaults(func=_cmd_determinism)

    p_scale = sub.add_parser("scale", help="investigatory T-SCALE run at large true_dim")
    p_scale.add_argument("--true-dims", dest="true_dims")
    p_scale.add_argument("--seeds")
    p_scale.add_argument(
        "--t3",
        action="store_true",
        help="run the T3 ablation triad per true_dim (predictive vs effort-only vs "
        "identity) and report the T3 verdict at each scale (investigatory)",
    )
    p_scale.add_argument("--config")
    p_scale.add_argument("--json")
    p_scale.add_argument(
        "--workers",
        type=int,
        default=0,
        help="parallel seed processes (0 = one per seed up to CPU count); never changes results",
    )
    p_scale.set_defaults(func=_cmd_scale)

    p_scan = sub.add_parser(
        "scan", help="diagnostic dimension scan: honest error per pose-dim, equal experience"
    )
    p_scan.add_argument("--true-dim", dest="true_dim", type=int)
    p_scan.add_argument("--dims", help="'1-30' or '1,2,4,8' (default 1..true_dim+10)")
    p_scan.add_argument("--hidden-sizes", dest="hidden_sizes", help="comma list (default 12)")
    p_scan.add_argument("--seeds")
    p_scan.add_argument("--train-episodes", dest="train_episodes", type=int, default=100)
    p_scan.add_argument("--eval-episodes", dest="eval_episodes", type=int, default=10)
    p_scan.add_argument("--config")
    p_scan.add_argument("--json")
    p_scan.set_defaults(func=_cmd_scan)

    p_agency = sub.add_parser("agency", help="curious vs random comparison (T7) + agency telemetry")
    p_agency.add_argument("--seeds")
    p_agency.add_argument("--true-dim", dest="true_dim", type=int)
    p_agency.add_argument("--config")
    p_agency.add_argument("--json")
    p_agency.add_argument("--strict", action="store_true")
    p_agency.add_argument(
        "--workers",
        type=int,
        default=0,
        help="parallel seed processes (0 = one per seed up to CPU count); never changes results",
    )
    p_agency.set_defaults(func=_cmd_agency)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)
    if not getattr(args, "command", None):
        # default command is the suite (contracts/cli.md)
        args = parser.parse_args(["suite", *(sys.argv[1:] if argv is None else argv)])
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
