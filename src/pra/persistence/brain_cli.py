"""``pra-brain`` — publish, inspect, and load portable brain artifacts (feature 037).

"Here's my rover brain after 100k steps — load it": ``export`` turns
one snapshot from a store directory into a single shareable file,
``inspect`` shows what a file claims to be without loading the brain,
and ``import`` verifies the file (format versions + sha256) and writes
it into a directory the ordinary file snapshot store serves for resume.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import UTC, datetime

from pra.persistence.portable import export_brain, import_brain, inspect_brain
from pra.persistence.store import FileSnapshotStore

__all__ = ["main"]

_FLOW = """the flow:
  person A   pra-brain export --store runs/snapshots --out rover.brain \\
                 --note "rover, 100k steps, seed 7"
  anyone     pra-brain inspect rover.brain          # manifest only, brain never loaded
  person B   pra-brain import rover.brain --store my-runs/snapshots
  person B   resume as usual: FileSnapshotStore("my-runs/snapshots") -> Engine.run(
                 seed, resume_from=blob)  # byte-identical continuation

The file is a zip: manifest.json (sha256, format versions, pra version,
obs_dim/n_actions, step/cycle/population, note, created-at) + snapshot.bin
(the snapshot blob, byte-untouched). Import refuses damaged or unknown
files loudly and writes nothing. The sha256 guards against damage, not
forgery — load brains from people you trust."""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="pra-brain",
        description="Share a brain as one portable file.",
        epilog=_FLOW,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_export = sub.add_parser(
        "export",
        help="publish one snapshot from a store directory as a portable file",
        description="Publish one snapshot from a store directory as a portable file.",
    )
    p_export.add_argument("--store", required=True, help="snapshot store directory to read")
    p_export.add_argument("--out", required=True, help="portable file to write")
    p_export.add_argument("--snapshot", default=None, help="snapshot id (default: newest)")
    p_export.add_argument("--note", default="", help="free-text provenance for the manifest")

    p_inspect = sub.add_parser(
        "inspect",
        help="print a portable file's manifest as JSON (the brain is never loaded)",
        description="Print a portable file's manifest as JSON. The brain is never loaded.",
    )
    p_inspect.add_argument("file", help="portable brain file")

    p_import = sub.add_parser(
        "import",
        help="verify a portable file and write it into a snapshot store directory",
        description=(
            "Verify a portable file (format versions + sha256) and write the snapshot "
            "into a store directory; resume from it exactly as from your own snapshots."
        ),
    )
    p_import.add_argument("file", help="portable brain file")
    p_import.add_argument("--store", required=True, help="snapshot store directory to write into")

    args = parser.parse_args(argv)
    try:
        return _run(args)
    except (ValueError, KeyError, OSError) as exc:
        print(f"pra-brain: {exc}", file=sys.stderr)
        return 1


def _run(args: argparse.Namespace) -> int:
    if args.command == "export":
        manifest = export_brain(
            args.out,
            store=FileSnapshotStore(args.store),
            snapshot_id=args.snapshot,
            note=args.note,
            created_at=datetime.now(UTC).isoformat(timespec="seconds"),
        )
        print(
            f"exported step {manifest['step']} / cycle {manifest['cycle']} "
            f"(population {manifest['population']}, obs_dim {manifest['obs_dim']}, "
            f"n_actions {manifest['n_actions']}) -> {args.out}"
        )
        return 0
    if args.command == "inspect":
        print(json.dumps(inspect_brain(args.file), indent=2, sort_keys=True))
        return 0
    # import: verified blob + manifest -> the ordinary file store, so the
    # existing resume path serves it under the same snapshot id as person A's.
    blob, manifest = import_brain(args.file)
    metadata = {
        "timestamp": time.time(),
        "step": manifest["step"],
        "cycle": manifest["cycle"],
        "population": manifest["population"],
        "format_version": manifest["snapshot_format_version"],
    }
    snapshot_id = FileSnapshotStore(args.store).write(blob, metadata)
    print(f"imported {snapshot_id} into {args.store} — resume with this store as usual")
    return 0


if __name__ == "__main__":
    sys.exit(main())
