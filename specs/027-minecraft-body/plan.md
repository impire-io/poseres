# Feature 027 — implementation plan

**Tech**: Python 3.12+ (stdlib socket/json only — zero new hard deps);
Node + mineflayer and Docker in `examples/minecraft/` only.

## Structure

    src/pra/anatomy/minecraft/
      __init__.py       exports: MinecraftTransport, FakeBridge, c1_anatomy,
                        C1_SENSORS, C1_ACTUATORS, PROTOCOL_VERSION
      protocol.py       wire protocol: framing (newline JSON), ops, version,
                        the channel-table handshake shape
      transport.py      MinecraftTransport — the 013 Transport surface over a
                        TCP bridge; queued presets; one round-trip per tick;
                        overrun accounting (wall budget); state_dict seam
      fake.py           FakeBridge — deterministic voxel mini-world serving
                        the same protocol on a localhost socket (thread);
                        full state capture; optional resettable
      anatomy.py        c1_anatomy(): the R3/R4 SensorSpec/ActuatorSpec lists
    tests/unit/test_minecraft_adapter.py   the contract suite (FR-005)
    tests/integration/test_minecraft_continuous.py  determinism + snapshot
                        round-trip over FakeBridge (SC-002)
    examples/minecraft/
      bridge/bridge.js  mineflayer bridge (hello/tick/state/bye), package.json
      docker-compose.yml   itzg/minecraft-server (small, offline, peaceful)
      run_c1.py         the C1 launcher: continuous, cap 1.2, snapshots +
                        resume-from-latest, optional NATS tap
      README.md         the runbook (two commands; stop/resume/watch)

## Constitution check

- The validated baseline is untouched: a new module + examples only; no
  existing behavior, RNG stream, or serialized summary changes.
- Gate: all tests pass with zero skips on a machine with no Node, no
  Docker, no Minecraft (FR-005). The real-stack smoke is measured
  separately and recorded (014 discipline).
- Research instruments stay in the scratchpad; the example ships as the
  worked deployment.

## Risks / notes

- Live-server nondeterminism is *stated*, not hidden (class 4; FR-006).
- Bridge liveness: a dead bridge is a loud AnatomyError at the next
  tick; the runbook's restart path is resume-from-latest (FR-004).
- mineflayer tracks server versions; the compose file pins a known-good
  server version and the README says how to move the pin.
