"""One-time provisioning for the separated-patches rig world.

The N1 probe kit's declared setup, verbatim, retargeted at the
pgw2-minecraft container: difficulty normal, mob spawning off, spawn
pinned at (0, -60, 0), the three melon patches with the game's own
regrowth. The patches it builds are erased and rebuilt to the
declared rung config at every birth (pgap.py); what this script
contributes is the gamerules and the spawn. After it exits, nothing
outside the game touches the world except the registered birth admin.

Usage: python provision.py   (container pgw2-minecraft must be up)
"""

from __future__ import annotations

import sys
from pathlib import Path

RIG = Path(__file__).parent
REPO = RIG.parents[3]
sys.path.insert(0, str(REPO / "examples" / "minecraft" / "survival" / "probe"))
import provision as n1  # noqa: E402 — the probe kit's builder, retargeted

n1.CONTAINER = "pgw2-minecraft"

if __name__ == "__main__":
    sys.exit(n1.main())
