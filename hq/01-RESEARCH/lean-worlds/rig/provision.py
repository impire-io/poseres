"""One-time provisioning for the contested-worlds rig world (rung 1).

The N1 probe kit's declared setup, verbatim, retargeted at the
lw1-minecraft container: difficulty normal, mob spawning off, spawn
pinned at (0, -60, 0), the three melon patches with the game's own
regrowth. After this script exits, nothing outside the game touches
the world except the registered between-arms classroom admin.

Usage: python provision.py   (container lw1-minecraft must be up)
"""

from __future__ import annotations

import sys
from pathlib import Path

RIG = Path(__file__).parent
REPO = RIG.parents[3]
sys.path.insert(0, str(REPO / "examples" / "minecraft" / "survival" / "probe"))
import provision as n1  # noqa: E402 — the probe kit's builder, retargeted

n1.CONTAINER = "lw1-minecraft"

if __name__ == "__main__":
    sys.exit(n1.main())
