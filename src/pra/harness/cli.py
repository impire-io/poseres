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
from pra.harness.acceptance import FAIL, evaluate_suite
from pra.harness.report import (
    build_determinism_report,
    build_suite_report,
    render_json,
    render_text,
)
from pra.harness.runner import check_determinism, run_suite

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


def _cmd_suite(args: argparse.Namespace) -> int:
    config = _build_config(args)
    suite_run = run_suite(config)
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
    p_suite.set_defaults(func=_cmd_suite)

    p_det = sub.add_parser("determinism", help="run one seed twice; assert byte-identical")
    p_det.add_argument("--seed", type=int, default=1)
    p_det.add_argument("--true-dim", dest="true_dim", type=int)
    p_det.add_argument("--config")
    p_det.add_argument("--json")
    p_det.set_defaults(func=_cmd_determinism)

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
