"""The one documented command (feature 014 US4, contracts §6).

Finds or starts a JetStream-enabled NATS server, runs the brain and the
watcher as separate processes, and exits zero only when every proof passed:
live telemetry consumed off-process, the control round-trip (inspect, pause,
resume, snapshot-on-request), and the snapshot pulled back from the object
store and verified.

Usage: python examples/nats/demo.py
Needs: pip install "poseres[nats]", plus a NATS server — either a running
server on 127.0.0.1:4222, a `nats-server` binary on PATH, or Docker.
"""

from __future__ import annotations

import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent
PORT = 4222


def _port_open(port: int) -> bool:
    with socket.socket() as sock:
        sock.settimeout(0.3)
        return sock.connect_ex(("127.0.0.1", port)) == 0


def _start_server() -> subprocess.Popen | None:
    """Return a server process we own, or None if one is already reachable."""
    if _port_open(PORT):
        print("demo: using the NATS server already on :4222", flush=True)
        return None
    if shutil.which("nats-server"):
        print("demo: starting nats-server -js", flush=True)
        proc = subprocess.Popen(
            ["nats-server", "-js", "-p", str(PORT)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    elif shutil.which("docker"):
        print("demo: starting nats:latest -js via docker", flush=True)
        proc = subprocess.Popen(
            ["docker", "run", "--rm", "-p", f"{PORT}:{PORT}", "nats:latest", "-js"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    else:
        sys.exit(
            "demo: no NATS server found. Either run one on :4222, install the "
            "`nats-server` binary (https://docs.nats.io), or install Docker "
            "(the demo will run `docker run --rm -p 4222:4222 nats:latest -js`)."
        )
    deadline = time.monotonic() + 30
    while not _port_open(PORT):
        if time.monotonic() > deadline or proc.poll() is not None:
            proc.terminate()
            sys.exit("demo: the NATS server failed to come up on :4222")
        time.sleep(0.25)
    return proc


def main() -> int:
    try:
        import nats  # noqa: F401 — presence check only
    except ImportError:
        sys.exit('demo: the NATS client is not installed — pip install "poseres[nats]"')

    server = _start_server()
    procs: list[subprocess.Popen] = []
    try:
        brain = subprocess.Popen([sys.executable, str(HERE / "brain.py")])
        procs.append(brain)
        watch = subprocess.Popen([sys.executable, str(HERE / "watch.py")])
        procs.append(watch)
        watch_rc = watch.wait(timeout=300)
        brain_rc = brain.wait(timeout=60)
    except subprocess.TimeoutExpired:
        print("demo: FAIL — a process hung", flush=True)
        return 1
    finally:
        for proc in procs:
            if proc.poll() is None:
                proc.terminate()
        if server is not None:
            server.terminate()
    if watch_rc == 0 and brain_rc == 0:
        print("demo: ALL PROOFS PASS", flush=True)
        return 0
    print(f"demo: FAIL — brain exit {brain_rc}, watch exit {watch_rc}", flush=True)
    return 1


if __name__ == "__main__":
    sys.exit(main())
