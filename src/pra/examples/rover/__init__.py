"""The watchable rover world (feature 006, ROADMAP B1).

Public surface::

    from pra.examples.rover import make_rover_body          # the world_factory
    from pra.examples.rover import RoverTelemetry, start_viewer   # the viewer
"""

from pra.examples.rover.viewer import RoverTelemetry, start_viewer
from pra.examples.rover.world import RoverDrive, RoverSensor, RoverWorld, make_rover_body

__all__ = [
    "RoverWorld",
    "RoverSensor",
    "RoverDrive",
    "make_rover_body",
    "RoverTelemetry",
    "start_viewer",
]
