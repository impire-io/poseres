# Inventory draft (T002) — classification rationale for PR review

The authoritative list is `tests/contract/surface_inventory.py`
(110 entries); the documented twin is Doc 0008. This note records the
classification calls so the membership can be reviewed as one list.

**Public, by family** — everything in the modules' own `__all__`s for
the seam-bearing modules, enumerated live (kinds inspected, not
guessed):

- *run*: `Config` + its mode aliases + reference-scale constants;
  `Engine` (+`.run`), `run_suite`/`check_determinism` + their result
  types; `PerSeedRunSummary` (+`.serialize`); `SensorimotorEvent`;
  `pra.__version__` and the lazy top-level `pra.Config`/`pra.Engine`.
- *world-body*: `EventSource`, `SensorimotorWorld`, `make_world` + the
  five ladder worlds; the Gymnasium pair; the pra-mc/1 surface
  (`c1_anatomy`, `FakeBridge`, `MinecraftTransport`, protocol/shape
  constants); the ROS2 ten (specs, body, transports, field helpers).
- *anatomy*: Doc 0002's seven (`Body`, `Sensor`, `Actuator`,
  `WorldSensor`, `WorldActuator`, `ConstantSensor`, `AnatomyError`).
- *drive*: the Policy five + the Drive six + `DriveContext` (required
  to implement a custom drive).
- *persistence*: the snapshot eight + the store four +
  `NatsSnapshotStore`.
- *operational*: the four CLI tools; the NATS tap/transport surface;
  the seventeen `pra.nats.subjects` names; the `pra.v1.>` subject
  space as a documented family.

**Deliberately internal** (reachable, unpromised): `pra.core.frame`
(FrameStore — the research arcs patch it and must stay able to),
`pra.core.bus/scorer/policies`, `FrameResult`/`GlobalPose`/
`FrameState` (introspection types), dash/flush library internals
(`DashboardModel`, `Flusher`, sinks — the CLIs are the promise),
rover example module names (examples are copied, not depended on),
`pra._deprecation` (policy public, tooling internal), the harness
internals behind `pra-validate`.

**Borderline calls made**: `start_dashboard` public (the embedding
hook examples use); `SuiteRun`/`DeterminismResult` public (returned
by public functions); telemetry record constants
(`EARLY_LATE_WINDOW` etc.) internal — they are instrument dials, not
user surface.
