"""The watcher half of the worked example (feature 014 US4) — a separate
process proving all three B6 surfaces against a live brain:

1. telemetry consumed from the run's subjects (steps, census, status),
2. a control round-trip (inspect → pause → verify frozen → resume → snapshot),
3. the snapshot pulled back from the JetStream object store and verified by
   decoding it as a real PRA snapshot with the expected seed.

Exit code 0 only if every proof passed.

Usage: python watch.py [--url nats://127.0.0.1:4222] [--run-id demo] [--seed 1]
"""

from __future__ import annotations

import argparse
import json
import sys
import threading
import time

from pra.nats import NatsSnapshotStore, NatsTransport, subjects
from pra.nats.transport import TransportError
from pra.persistence.snapshot import decode


def _ctrl(transport, run_id: str, request: dict, timeout: float = 5.0) -> dict:
    reply = transport.request(subjects.control_subject(run_id), subjects.to_bytes(request), timeout)
    return json.loads(reply)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="nats://127.0.0.1:4222")
    parser.add_argument("--run-id", default="demo")
    parser.add_argument("--seed", type=int, default=1)
    args = parser.parse_args()

    transport = NatsTransport(args.url)
    transport.start()
    run_id = args.run_id

    # -- proof 0: the run is discoverable -----------------------------------
    deadline = time.monotonic() + 30
    discovered = None
    while discovered is None:
        try:
            discovered = json.loads(
                transport.request(subjects.DISCOVER_SUBJECT, subjects.to_bytes({}), 2.0)
            )
        except TransportError:
            if time.monotonic() > deadline:
                print("watch: FAIL — no live run discovered within 30s", flush=True)
                return 1
            time.sleep(0.5)
    print(f"watch: discovered run {discovered['run']!r} ({discovered['state']})", flush=True)

    # -- proof 1: live telemetry --------------------------------------------
    lock = threading.Lock()
    seen = {"step": 0, "census": 0, "completed": None}

    def on_message(subject: str, payload: bytes) -> None:
        event = json.loads(payload)
        with lock:
            if subject.endswith(".tele.step"):
                seen["step"] += 1
            elif subject.endswith(".tele.census"):
                seen["census"] += 1
            elif subject.endswith(".status") and event.get("state") == "completed":
                seen["completed"] = event["summary"]

    transport.subscribe(f"pra.v1.run.{run_id}.>", on_message)

    deadline = time.monotonic() + 30
    while True:
        with lock:
            if seen["step"] >= 20 and seen["census"] >= 1:
                break
        if time.monotonic() > deadline:
            print(f"watch: FAIL — telemetry too quiet ({seen})", flush=True)
            return 1
        time.sleep(0.1)
    print(f"watch: live telemetry flowing ({seen['step']} steps so far)", flush=True)

    # -- proof 2: the control round-trip ------------------------------------
    inspected = _ctrl(transport, run_id, {"cmd": "inspect"})
    assert inspected["ok"] and inspected["state"] == "running", inspected
    print(f"watch: inspect ok at step {inspected['steps']}", flush=True)

    paused = _ctrl(transport, run_id, {"cmd": "pause"})
    assert paused["ok"], paused
    time.sleep(0.3)
    a = _ctrl(transport, run_id, {"cmd": "inspect"})["steps"]
    time.sleep(0.3)
    b = _ctrl(transport, run_id, {"cmd": "inspect"})["steps"]
    if a != b:
        print(f"watch: FAIL — paused run still moving ({a} -> {b})", flush=True)
        return 1
    print(f"watch: paused and frozen at step {a}", flush=True)

    resumed = _ctrl(transport, run_id, {"cmd": "resume"})
    assert resumed["ok"], resumed

    # deferred fulfillment: sized to the snapshot cadence, generously
    snap = _ctrl(transport, run_id, {"cmd": "snapshot"}, timeout=60.0)
    assert snap["ok"], snap
    print(f"watch: snapshot-on-request fulfilled: {snap['snapshot_id']}", flush=True)

    # -- proof 3: pull the snapshot back and verify it is a real brain -------
    store = NatsSnapshotStore(transport)
    blob = store.read(snap["snapshot_id"])
    state = decode(blob)
    if state.seed != args.seed:
        print(f"watch: FAIL — snapshot seed {state.seed} != {args.seed}", flush=True)
        return 1
    print(
        f"watch: snapshot verified — {len(blob)} bytes, seed {state.seed}, "
        f"cycle {state.cycles_done}, population {state.frame_store and 'present'}",
        flush=True,
    )

    # -- wait for the run to finish and check the published summary ----------
    deadline = time.monotonic() + 120
    while True:
        with lock:
            if seen["completed"] is not None:
                break
        if time.monotonic() > deadline:
            print("watch: FAIL — no completion status within 120s", flush=True)
            return 1
        time.sleep(0.25)
    with lock:
        summary = seen["completed"]
    print(f"watch: run completed — best_dim {summary['best_dim']}, all proofs PASS", flush=True)
    transport.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
