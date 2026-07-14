#!/usr/bin/env bash
# The one documented command (feature 013, SC-004): build and run the
# ROS2 worked example. Needs Docker; everything else lives in the container.
set -euo pipefail
cd "$(dirname "$0")/../.."
docker build -t pra-ros2-example -f examples/ros2/Dockerfile .
exec docker run --rm pra-ros2-example
