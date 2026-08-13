"""Minecraft body adapter (feature 027): a pra-mc/1 transport for the 013 seam.

`Ros2Body` mounts unchanged over :class:`MinecraftTransport` — hardware,
simulators, and now a live game world through one seam (hq/04-JOURNEY/0026,
extended). The mineflayer bridge in ``examples/minecraft/`` is the ONLY
world implementation — there is no fake side of this seam (the owner's
rule, 2026-08-13); the adapter contract is proven against the live
bridge by ``examples/minecraft/contract_check.py``. See
specs/027-minecraft-body/.
"""

from pra.anatomy.minecraft.anatomy import (
    C1_ACTUATORS,
    C1_MINING_INDEX,
    C1_N_ACTIONS,
    C1_OBS_DIM,
    C1_POCKET_TOTAL_INDEX,
    C1_SENSORS,
    c1_anatomy,
)
from pra.anatomy.minecraft.protocol import PROTOCOL_VERSION
from pra.anatomy.minecraft.transport import MinecraftTransport

__all__ = [
    "C1_ACTUATORS",
    "C1_MINING_INDEX",
    "C1_N_ACTIONS",
    "C1_OBS_DIM",
    "C1_POCKET_TOTAL_INDEX",
    "C1_SENSORS",
    "MinecraftTransport",
    "PROTOCOL_VERSION",
    "c1_anatomy",
]
