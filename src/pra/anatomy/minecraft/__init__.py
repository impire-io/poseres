"""Minecraft body adapter (feature 027): a pra-mc/1 transport for the 013 seam.

`Ros2Body` mounts unchanged over :class:`MinecraftTransport` — hardware,
simulators, and now a live game world through one seam (hq/04-JOURNEY/0026,
extended). The in-repo :class:`FakeBridge` carries the whole quality
gate; the mineflayer bridge in ``examples/minecraft/`` is the worked
deployment. See specs/027-minecraft-body/.
"""

from pra.anatomy.minecraft.anatomy import (
    C1_ACTUATORS,
    C1_N_ACTIONS,
    C1_OBS_DIM,
    C1_SENSORS,
    c1_anatomy,
)
from pra.anatomy.minecraft.fake import FakeBridge
from pra.anatomy.minecraft.protocol import PROTOCOL_VERSION
from pra.anatomy.minecraft.transport import MinecraftTransport

__all__ = [
    "C1_ACTUATORS",
    "C1_N_ACTIONS",
    "C1_OBS_DIM",
    "C1_SENSORS",
    "FakeBridge",
    "MinecraftTransport",
    "PROTOCOL_VERSION",
    "c1_anatomy",
]
