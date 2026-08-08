# Quickstart: The Web Dashboard (One Face for Any Brain)

Phase 1 of `plan.md`. The fake-transport path runs on any machine (it is
what the test suite does); the real path needs `pip install
"poseres[nats]"` and a NATS server.

## 1. The whole story, one command (real stack)

```bash
pip install "poseres[nats]"
python examples/nats/dashboard_demo.py
# → prints http://127.0.0.1:<port>/ — open it: a rover driving its arena,
#   live, from another process; switch to Advanced for the instrument panel.
```

Exit code zero means the headless proofs passed (telemetry consumed,
world view served, control round-trip through the dashboard). The browser
is the reward, not the requirement.

## 2. Point the dashboard at any brain

Terminal 1 — any run with the tap attached (B6 quickstart §2), for the
rover with its world view:

```python
from pra.examples.rover.world import make_rover_body
from pra.nats import NatsTap, NatsTransport

tap = NatsTap(NatsTransport("nats://127.0.0.1:4222"), run_id="rover-1")
view = tap.world_view("rover")
engine = Engine(
    cfg,
    # the tap's wrapper carries the step mirror and the pause gate; the view
    # adapter carries the world's self-portrait — both, always
    world_factory=tap.world_factory(inner=lambda c, r: make_rover_body(c, r, telemetry=view)),
    bus_factory=tap.bus_factory,
)
tap.start()
summary = engine.run(seed=1)
tap.finish(summary)
```

Terminal 2 — the dashboard:

```bash
pra-dash --url nats://127.0.0.1:4222
# → http://127.0.0.1:8600/  (port 0 = ephemeral; --port to choose)
```

The dashboard discovers every live run on the server (`pra.v1.discover` +
observed traffic), lists them, and renders simple mode (state, liveness,
census, world view when offered) and advanced mode (census history,
best_dim trajectory, per-dim histogram, honesty counters, snapshot
notices, and the four control buttons — replies shown verbatim, including
B6's error replies).

A scaled run works identically — no world view, so simple mode shows the
instrument basics and advanced mode is the panel that matters:

```bash
pra-dash --url nats://your-lab-server:4222   # any tap-attached run appears
```

## 3. The fake-transport path (tests, development, no server)

```python
from pra.dash.model import DashboardModel
from pra.dash.server import start_dashboard
from pra.nats.fake import FakeBusTransport

transport = FakeBusTransport()  # share it with a tap-attached Engine run
model = DashboardModel(transport)
model.start()
server, url = start_dashboard(model, port=0)
# urllib against url + "runs" / f"run/{rid}/state" — the B1 discipline;
# this is exactly how tests/integration/test_dash_live.py proves the
# polling-hammer byte-identity.
```

## 4. What to expect when things are absent

- **No NATS extra**: `pra-dash` fails with the B6 message naming
  `pip install "poseres[nats]"`; the fake path above never needs it.
- **No live runs**: the dashboard serves an empty list and keeps
  discovering; a run started later appears without restart.
- **A run goes quiet**: its liveness age grows and is rendered — a dead
  server looks dead, a paused run looks paused; nothing pretends.
- **World with no view / unknown view kind**: instrument basics, or a
  present-but-unrenderable note naming the kind — never a crash.
