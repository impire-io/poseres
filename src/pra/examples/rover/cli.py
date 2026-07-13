"""``pra-rover`` — one command: start the run, serve the viewer, watch.

A dedicated entry point, deliberately not a ``pra-validate`` subcommand
(research R9): the harness runs-judges-exits; this serves an experience —
single seed, paced for watching, holding the viewer open afterwards. The
summary it prints is the same honest per-seed summary the harness records,
with the single-seed caveat stated (a demo, never a validated claim).
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import webbrowser
from pathlib import Path

from pra.config import Config
from pra.core.engine import Engine
from pra.examples.rover.viewer import RoverTelemetry, start_viewer
from pra.examples.rover.world import make_rover_body

__all__ = ["main"]

DEFAULT_PORT = 8765
DEFAULT_FPS = 50.0


def _build_config(path: str | None) -> Config:
    overrides: dict = {}
    if path:
        overrides.update(json.loads(Path(path).read_text()))
        if "seeds" in overrides:
            overrides["seeds"] = tuple(overrides["seeds"])
        if "horizon_checkpoints" in overrides:
            overrides["horizon_checkpoints"] = tuple(overrides["horizon_checkpoints"])
    return Config(**overrides)


def _fmt(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.4f}"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pra-rover",
        description="watch a PRA brain learn a 2D rover world, live in your browser",
    )
    parser.add_argument("--seed", type=int, default=1, help="run seed (default 1)")
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help=f"viewer port (default {DEFAULT_PORT}; 0 = ephemeral)",
    )
    parser.add_argument(
        "--fps",
        type=float,
        default=DEFAULT_FPS,
        help=f"pacing in steps/second (default {DEFAULT_FPS:g}; 0 = unthrottled). "
        "Pacing changes wall-clock only, never the run's bytes.",
    )
    parser.add_argument("--config", help="JSON file with Config overrides (schedule dials etc.)")
    parser.add_argument("--json", help="write the canonical per-seed summary to this path")
    parser.add_argument(
        "--no-open", action="store_true", help="never attempt to open a browser tab"
    )
    parser.add_argument(
        "--exit-when-done",
        action="store_true",
        help="shut the viewer down after the run instead of serving until Ctrl+C",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(sys.argv[1:] if argv is None else argv)
    config = _build_config(args.config)
    step_delay = 0.0 if args.fps <= 0 else 1.0 / args.fps

    tap = RoverTelemetry(config)
    try:
        server, url = start_viewer(tap, args.port)
    except OSError as err:
        sys.stderr.write(f"pra-rover: {err}\n")
        return 2

    total_steps = (
        config.warmup_episodes + config.effective_n_cycles * config.episodes_per_cycle
    ) * config.steps_per_episode
    sys.stdout.write(f"viewer: {url}\n")
    if step_delay > 0.0:
        minutes = total_steps / args.fps / 60.0
        sys.stdout.write(
            f"run: seed {args.seed}, {total_steps} steps at {args.fps:g} steps/s "
            f"(~{minutes:.1f} min; --fps 0 for full speed)\n"
        )
    else:
        sys.stdout.write(f"run: seed {args.seed}, {total_steps} steps, unthrottled\n")
    sys.stdout.flush()

    if not args.no_open and sys.stdout.isatty():
        try:  # best-effort: a missing browser must never kill the run
            webbrowser.open(url)
        except Exception:
            pass

    def factory(cfg: Config, rng):
        return make_rover_body(cfg, rng, telemetry=tap, step_delay=step_delay)

    try:
        summary = Engine(config, world_factory=factory, bus_factory=tap.bus_factory).run(args.seed)
    except KeyboardInterrupt:
        sys.stdout.write("\ninterrupted — no summary (partial runs are not recorded)\n")
        server.shutdown()
        server.server_close()
        return 130
    tap.finish(summary)

    sys.stdout.write(
        f"run complete: {summary.observation_steps} observation steps\n"
        f"  pred_error: early {_fmt(summary.pred_error_early)} -> "
        f"late {_fmt(summary.pred_error_late)} (improvement {_fmt(summary.improvement)})\n"
        f"  best_dim: {summary.best_dim}   final population: {summary.final_population}\n"
        "  (single seed - a demo, not a validated claim; spreads live in pra-validate)\n"
    )
    if args.json:
        out = Path(args.json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(summary.canonical(), indent=2))
        sys.stdout.write(f"summary written: {out}\n")

    if not args.exit_when_done:
        sys.stdout.write(f"viewer still serving at {url} - press Ctrl+C to exit\n")
        sys.stdout.flush()
        try:
            while True:
                time.sleep(0.5)
        except KeyboardInterrupt:
            pass
    server.shutdown()
    server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
