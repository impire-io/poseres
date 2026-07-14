#!/usr/bin/env bash
# Bring up the paused sim, the bridge, then PRA (feature 013 worked example).
# No `set -u`: ROS setup scripts reference unset variables by design.
set -eo pipefail
source /opt/ros/jazzy/setup.bash

# 1. Gazebo server, headless, paused: the stepped transport owns time.
gz sim -s -v1 /opt/pra/example/world.sdf &
SIM_PID=$!
sleep 5

# 2. The ros_gz bridge: lidar + odometry out, cmd_vel in, and the
#    world-control step service (R8 probe 2) for the stepped transport.
ros2 run ros_gz_bridge parameter_bridge \
  '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan' \
  '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry' \
  '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist' \
  '/world/pra_world/control@ros_gz_interfaces/srv/ControlWorld' &
BRIDGE_PID=$!
sleep 3

# 3. PRA. Its exit status is the example's verdict.
set +e
/opt/pra/venv/bin/python /opt/pra/example/run.py
STATUS=$?
set -e

kill "$BRIDGE_PID" "$SIM_PID" 2>/dev/null || true
exit "$STATUS"
