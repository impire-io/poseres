"""The dashboard's one documented command (feature 015 US4, contracts §6).

Finds or starts a JetStream-enabled NATS server, runs a paced rover brain
(tap + world-view channel + object-store snapshots), starts the dashboard
in-process, prints the URL for a human — and verifies the proofs headlessly:
live telemetry consumed into the model, the world view served by the state
endpoint, and a control round-trip (pause → frozen → resume → snapshot)
through the dashboard's own ctrl endpoint. Exit zero only when every proof
passed; the browser is the reward, not the requirement.

Usage: python examples/nats/dashboard_demo.py
Needs: pip install "poseres[nats]", plus a NATS server (running, on PATH as
`nats-server`, or Docker).
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from demo import _start_server  # noqa: E402 — the B6 server bootstrap, reused

RUN_ID = "rover"


def _get(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=5) as response:
        return json.loads(response.read())


def _post(url: str, body: dict, timeout: float = 90.0) -> dict:
    request = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read())


def _fail(message: str) -> int:
    print(f"dashboard_demo: FAIL — {message}", flush=True)
    return 1


def main() -> int:
    try:
        import nats  # noqa: F401 — presence check only
    except ImportError:
        sys.exit('dashboard_demo: the NATS client is not installed — pip install "poseres[nats]"')

    from pra.dash import DashboardModel, start_dashboard
    from pra.nats import NatsTransport

    server_proc = _start_server()
    brain = None
    try:
        brain = subprocess.Popen([sys.executable, str(HERE / "brain_rover.py"), "--run-id", RUN_ID])
        transport = NatsTransport("nats://127.0.0.1:4222")
        model = DashboardModel(transport)
        model.start()
        http_server, url = start_dashboard(model, port=0)
        print(f"dashboard_demo: dashboard live at {url} — open it in a browser", flush=True)

        # proof 1: the model consumes live telemetry, including the world view
        deadline = time.monotonic() + 60
        while True:
            state = model.state_of(RUN_ID)
            if (
                state is not None
                and state["census"] is not None
                and state["view"] is not None
                and state["view"]["static"] is not None
            ):
                break
            if time.monotonic() > deadline:
                return _fail(f"telemetry/world view never arrived ({state})")
            time.sleep(0.25)
        print("dashboard_demo: live telemetry + world view consumed", flush=True)

        # proof 2: the endpoints serve it (what a browser would read)
        rows = _get(url + "runs")["runs"]
        if not any(r["run"] == RUN_ID and r["has_view"] for r in rows):
            return _fail(f"/runs does not list the rover with a view ({rows})")
        served = _get(url + f"run/{RUN_ID}/state")
        if served["view"]["kind"] != "rover" or "arena_half" not in served["view"]["static"]:
            return _fail("the state endpoint does not serve the rover view")
        print("dashboard_demo: endpoints serve the world view and the census", flush=True)

        # proof 3: the control round-trip through the dashboard's own surface
        paused = _post(url + f"run/{RUN_ID}/ctrl", {"cmd": "pause"})
        if not paused.get("ok"):
            return _fail(f"pause refused: {paused}")
        time.sleep(0.4)
        a = _get(url + f"run/{RUN_ID}/state")["last_step"]
        time.sleep(0.4)
        b = _get(url + f"run/{RUN_ID}/state")["last_step"]
        if a != b:
            return _fail(f"paused run still moving ({a} -> {b})")
        resumed = _post(url + f"run/{RUN_ID}/ctrl", {"cmd": "resume"})
        if not resumed.get("ok"):
            return _fail(f"resume refused: {resumed}")
        snap = _post(url + f"run/{RUN_ID}/ctrl", {"cmd": "snapshot"})
        if not snap.get("ok"):
            return _fail(f"snapshot refused: {snap}")
        snapshot_id = snap["snapshot_id"]
        print(
            f"dashboard_demo: control round-trip ok (frozen at {a}, snapshot {snapshot_id})",
            flush=True,
        )

        brain_rc = brain.wait(timeout=180)
        http_server.shutdown()
        http_server.server_close()
        model.stop()
        transport.close()
        if brain_rc != 0:
            return _fail(f"brain exit {brain_rc}")
        print("dashboard_demo: ALL PROOFS PASS", flush=True)
        return 0
    except (subprocess.TimeoutExpired, urllib.error.URLError) as err:
        return _fail(str(err))
    finally:
        if brain is not None and brain.poll() is None:
            brain.terminate()
        if server_proc is not None:
            server_proc.terminate()


if __name__ == "__main__":
    sys.exit(main())
