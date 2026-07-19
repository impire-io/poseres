# Feature 027 — tasks

- **T1** `protocol.py` — framing, ops, version, handshake shapes; loud
  error mapping. (FR-002)
- **T2** `fake.py` — FakeBridge: deterministic voxel mini-world (flat
  ground, a few walls/pillars from a seed-free fixed layout), serving
  the protocol on a localhost socket in a thread; full `state` /
  `load_state`; optional resettable. (FR-005, FR-007)
- **T3** `transport.py` — MinecraftTransport over the 013 Transport
  surface; hello validation; queued presets; one round-trip per tick;
  wall-budget overruns; state seam; single-boot; loud close. (FR-001,
  FR-003, FR-004)
- **T4** `anatomy.py` — `c1_anatomy()` per R3/R4; widths match the
  contract table by construction. (FR-002)
- **T5** tests — unit contract suite over FakeBridge (handshake,
  widths, ordering journal, staleness, single-boot, unknown command,
  second-client refusal, close); integration: same-seed byte-identity
  and snapshot round-trip in continuous mode. Gate green, no skips.
  (SC-001, SC-002)
- **T6** `examples/minecraft/bridge/bridge.js` — mineflayer bridge
  implementing the same contract; package.json pinned. (SC-003)
- **T7** `examples/minecraft/` — docker-compose.yml, run_c1.py
  (continuous, cap 1.2, snapshots + resume-from-latest, optional NATS
  tap), README runbook. (SC-004)
- **T8** real-stack smoke: dockerized server + bridge + short brain
  run + snapshot + resume; measured and recorded; gate re-run clean
  without the stack. (SC-003)
- **T9** propagation: ROADMAP C1 world note, JOURNEY ch. 42, memory.
