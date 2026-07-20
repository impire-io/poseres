# Chapter 28 — NATS at the seams: the off-process window that provably isn't there (2026-07-18)

B6 landed the same day it was scheduled — spec, plan, build, and the
real-stack proof in one sitting. The feature gives a live run an
off-process presence over NATS/JetStream: telemetry fanned out under a
versioned run-scoped subject scheme (`pra.v1.run.<id>.…`), snapshots
through a JetStream object store behind the existing four-method store
seam (Phase D's shareable-brains transport, bought once), and a
three-command request/reply control plane (inspect, pause/resume,
snapshot) — all opt-in, all through existing injection seams, zero
edits under `core/`, `harness/`, `persistence/`, or `config.py`.

**The design died once before it was born, on a read fact.** The
obvious shape — wrap the Doc 02 bus and mirror its published events —
observes nothing: the engine's hot loop drives the batched
`FrameProcessor` directly, and `Bus.publish` is only the contract-test
path (`bus.py`'s own docstring says so). What the B1 viewer had
actually proven was subtler: capture references at injection time,
mirror plain values on the run path, derive everything on a background
thread. `NatsTap` generalizes exactly that, binding three seams — a
delegating world wrapper (the per-step mirror *and* the pause gate: one
`Event.is_set` check, two integer increments, one small copy, one
bounded-deque append per step; no RNG, no floats, no locks), the
viewer's `bus_factory` store capture (the census derives off-path with
torn-read fallback), and a delegating snapshot-store wrapper at the
engine's C4 write site. Observer safety is proven, not argued:
same-seed runs with the backend absent and attached are
byte-identical, including multi-stream continuous, including a
transport that is down for the run's whole life (drops derived from
sequence gaps — the honesty meter), including a paused-then-resumed
run against a never-paused one.

**The honest decision of the chapter is the snapshot command.** A
snapshot is only well-defined at C4 — no external thread can force one
mid-cycle without tearing the state Doc 06 exists to protect — so
snapshot-on-request is *deferred fulfillment*: the reply arrives when
the engine's own cadence write is observed, and unconfigured runs get
an immediate error naming what is missing. Payloads carry no
wall-clock time (sequence numbers and the run's own counters only), so
the fake-transport journals are byte-deterministic and the contract
tests compare them as bytes.

The gate runs entirely on an in-repo fake transport — no NATS library,
no server, zero skips (the 013 pattern; unlike rclpy, `nats-py` is
pip-installable, so the `[nats]` extra honestly exists). The real
stack was **measured, not hoped**: `examples/nats/demo.py` ran green
end-to-end on first attempt against a local `nats-server -js` with
`nats-py` 2.15 — discovery, live telemetry in a second process, pause
frozen and verified twice, snapshot fulfilled at the C4 boundary
(`snap-000000000300-00002`), pulled back from JetStream and decoded as
a real brain, all proofs pass — then the library was uninstalled and
the full gate re-run clean without it. Doc 06 §5b now records every
NATS-touching mode's reproducibility class, with experience-in named
class 4 and *not built*, and inter-brain communication left as reserved
subject space (`pra.v1.brain.*`) — research, not plumbing. B7's gate is
met. Trail: `specs/014-nats-bus-backend/` (spec, plan, research R1–R9,
data-model, contracts, quickstart, tasks), `src/pra/nats/`,
`examples/nats/`; commits `30a1952` (spec), `49ea413` (plan),
`18447c2` (tasks), and the implementation commits following.
