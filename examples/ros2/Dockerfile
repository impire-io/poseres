# The ROS2 worked example (feature 013, contracts C7): a pinned ROS 2 LTS,
# Gazebo, a minimal diff-drive robot, and PRA driving it in stepped
# simulation. Build from the repository root:
#
#     docker build -t pra-ros2-example -f examples/ros2/Dockerfile .
#     docker run --rm pra-ros2-example
#
# R8 probe 1, resolved (recorded here per the plan): ROS 2 Jazzy (LTS,
# supported to 2029) runs Ubuntu 24.04 / Python 3.12, and rclpy binds to the
# distro interpreter — so PRA must run on 3.12 inside this container. The
# repository's full quality-gate suite (including the byte-frozen baseline
# values) was run on CPython 3.12.8 and passed 346/346 before
# requires-python was relaxed to >=3.12 (feature 013 closing commit).
# Jazzy vendors Gazebo Harmonic in the ROS apt repository (ros-jazzy-ros-gz).
FROM ros:jazzy

RUN apt-get update && apt-get install -y --no-install-recommends \
        ros-jazzy-ros-gz \
        python3-venv \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/pra

# The package first (better layer caching), the example files after.
COPY pyproject.toml README.md ./
COPY src ./src
# --system-site-packages: rclpy comes from the ROS distro, PRA from pip,
# one interpreter sees both.
RUN python3 -m venv --system-site-packages /opt/pra/venv \
    && /opt/pra/venv/bin/pip install --no-cache-dir .

COPY examples/ros2/world.sdf examples/ros2/run.py examples/ros2/entrypoint.sh /opt/pra/example/
RUN chmod +x /opt/pra/example/entrypoint.sh

# Headless rendering for the lidar (gpu_lidar renders via ogre2; llvmpipe
# software GL is the standard container answer).
ENV LIBGL_ALWAYS_SOFTWARE=1

ENTRYPOINT ["/opt/pra/example/entrypoint.sh"]
