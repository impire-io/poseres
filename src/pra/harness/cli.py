"""Harness CLI entry point.

Full command set (suite / determinism / scale) is implemented in Phase 3+.
This module currently exposes ``main`` so the ``pra-validate`` console script
resolves; commands are added in the user-story phases.
"""

from __future__ import annotations

import sys


def main(argv: list[str] | None = None) -> int:
    """Console entry point. Returns a process exit code."""
    argv = list(sys.argv[1:] if argv is None else argv)
    sys.stderr.write("pra-validate: CLI not yet implemented (Phase 3).\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
