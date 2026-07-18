# Quickstart: The External Bus Backend (NATS at the Seams)

Phase 1 of `plan.md`. Two paths: the fake-transport path runs on any
machine with the repo venv (it is also what the test suite does); the
real path needs `pip install "poseres[nats]"` and a NATS server.

## 1. Attach the tap to a run (fake transport — any machine)

```python
from pra.config import Config
from pra.core.engine import Engine
from pra.nats import NatsTap
from pra.nats.fake import FakeBusTransport

transport = FakeBusTransport()
tap = NatsTap(transport, run_id="quickstart")

cfg = Config()
engine = Engine(
    cfg,
    world_factory=tap.world_factory(),   # default: wraps the standard world
    bus_factory=tap.bus_factory,         # the B1 viewer capture, off-process
)
tap.start()
summary = engine.run(seed=1)
tap.finish(summary)                       # publishes status: completed

# Everything the run published is in the fake's journal:
for subject, payload in transport.journal:
    print(subject, payload.decode()[:80])
```

The same seed without the tap produces a byte-identical
`summary.serialize()` — that is the observer-safety contract, and the
integration suite asserts it.

## 2. Watch a live brain from another process (real transport)

Terminal 0 — a throwaway server (JetStream on):

```bash
nats-server -js        # or: docker run --rm -p 4222:4222 nats:latest -js
```

Terminal 1 — the brain:

```python
from pra.nats import NatsTap, NatsTransport

transport = NatsTransport("nats://127.0.0.1:4222")
tap = NatsTap(transport, run_id="rover-1")
# ... Engine(...) exactly as above, then tap.start(); engine.run(...); tap.finish(...)
```

Terminal 2 — any consumer (here, the nats CLI):

```bash
nats sub 'pra.v1.run.rover-1.tele.>'
nats req 'pra.v1.run.rover-1.ctrl' '{"cmd":"inspect"}'
nats req 'pra.v1.run.rover-1.ctrl' '{"cmd":"pause"}'
nats req 'pra.v1.run.rover-1.ctrl' '{"cmd":"resume"}'
nats req 'pra.v1.discover' '{}'
```

The run never waits on any of this: kill the server mid-run and the
brain finishes at full stride with `tap.publish_failures > 0` and a
byte-identical summary.

## 3. Snapshots through the object store (shareable brains)

```python
from pra.nats import NatsSnapshotStore, NatsTransport

store = NatsSnapshotStore(NatsTransport("nats://127.0.0.1:4222"))
cfg = Config(snapshot_every_n_cycles=2)
engine = Engine(cfg, snapshot_store=tap.wrap_store(store),
                world_factory=tap.world_factory(), bus_factory=tap.bus_factory)
summary = engine.run(seed=1)

# On another machine, against the same server:
store = NatsSnapshotStore(NatsTransport("nats://server:4222"))
snapshot_id, meta = store.list()[0]           # newest first
blob = store.read(snapshot_id)
resumed = Engine(cfg, snapshot_store=store).run(seed=1, resume_from=blob)
```

Doc 06 §5b's per-class guarantees carry over unchanged — the transport
moves the blob, it never reinterprets it. Note the honest cost: a
store-backed run blocks at each snapshot boundary for the duration of
the network write.

With the tap's store wrapper attached (as above), a control-plane
`{"cmd":"snapshot"}` request is fulfilled at the next boundary and the
reply carries the new snapshot's id; `pra.v1.run.<id>.tele.snapshot`
announces every write to any subscriber.

## 4. The whole proof in one command (worked example)

```bash
pip install "poseres[nats]"
python examples/nats/demo.py
```

`demo.py` finds or starts a `-js` server, runs `brain.py` and
`watch.py` as separate processes, and exits zero only when live
telemetry was consumed, the control round-trip completed, and a
snapshot round-tripped byte-identical through the object store.

## 5. What to expect when things are absent

- **No `nats-py`**: constructing `NatsTransport` or `NatsSnapshotStore`
  raises a clear error naming `pip install "poseres[nats]"`. The fake
  transport and the whole test suite never need it.
- **No server**: telemetry drops (counted, visible); explicit
  operations — store ops, `request` — fail loudly naming the
  operation. The run itself never fails because the network did.
- **`{"cmd":"snapshot"}` on an unconfigured run**: an immediate error
  reply naming the missing store/cadence — configure
  `snapshot_every_n_cycles` and inject a store first.
