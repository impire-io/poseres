"""The ROS2 adapter: mount topic-based worlds as a PRA body (feature 013).

Public surface — declaration (`SensorSpec`/`ActuatorSpec`), the body layer
(`TopicSensor`/`CommandActuator`/`Ros2Body`), and the transports
(`FakeTransport` for any machine, `RclpyTransport` for a sourced ROS2
environment). Nothing here imports ROS2 unless `RclpyTransport` is actually
started; the quality gate runs entirely on the fake transport (FR-007/008).

Start at specs/013-ros2-adapter/quickstart.md; the containerized worked
example lives in examples/ros2/.
"""

from pra.anatomy.ros2.body import CommandActuator, Ros2Body, TopicSensor
from pra.anatomy.ros2.fake import FakeTransport
from pra.anatomy.ros2.specs import ActuatorSpec, SensorSpec, apply_fields, extract_vector
from pra.anatomy.ros2.transport import RclpyTransport, Transport

__all__ = [
    "ActuatorSpec",
    "CommandActuator",
    "FakeTransport",
    "RclpyTransport",
    "Ros2Body",
    "SensorSpec",
    "TopicSensor",
    "Transport",
    "apply_fields",
    "extract_vector",
]
