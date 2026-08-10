# Doc 0008 — The public API, its versioning promise, and its deprecation policy

Feature 035 (`specs/035-api-stability-v1/`), roadmap Phase D, episode
0060. This document is one half of a pair: the machine-checked twin is
`tests/contract/surface_inventory.py`, and the surface guard
(`tests/contract/test_public_surface.py`) keeps the two in exact
agreement — a name listed here and absent there (or vice versa) fails
the gate. What this document adds is the *promise* around the list.

## The promise (semantic versioning, tightened by constitution I)

- **Patch (1.0.x)**: fixes only. No public name or shape changes;
  behavior of existing modes byte-identical.
- **Minor (1.x.0)**: additive only — new opt-in capability, new
  keyword-only parameters, new public names. Existing modes' RNG
  stream, behavior, and serialized summaries stay untouched
  (constitution I restated as a compatibility promise: the T1–T6
  suite under the pinned baseline reproduces its recorded reference
  values on every v1.x release). Deprecations may be announced.
- **Major (2.0.0+)**: removals allowed, only of elements deprecated at
  least one minor release earlier. An urgent removal (safety/security)
  may shortcut the grace period only with a changelog entry stating
  the reason.
- **Snapshots**: same-version round-trip is exact (measured to 500k
  steps, episode 0041). Within v1.x, an older snapshot loads on a
  newer release under Doc 0006's config-in-force rules. Anything
  beyond that is documented explicitly when it exists; silence means
  no promise.
- **Release notes (additive minors)**: v1.2.0 (feature 040, the event
  pathway) adds `Config.event_head_eta` (default 0.0 = off,
  byte-identical), the defaulted `PolicyContext.predict_event_delta`
  accessor, `CompletionItchPolicy`, and the two C1 channel-index
  constants — keyword-only-legal additions under this policy; snapshot
  blobs gain an additive-optional event-head key (head-off blobs stay
  bit-identical).
- **Release notes (additive minors)**: v1.3.0 (feature 041) adds the
  praise label to `CompletionItchPolicy` (keyword-only, off by default,
  bit-exact when off) and `pra.action.recipe` (Recipe, RecipeMemory,
  RecipePolicy) — the measured recipe-reach mechanism as product.
- **Release notes (additive minors)**: v1.4.0 (feature 042) adds the
  deficit gate to `CompletionItchPolicy`/`RecipePolicy`
  (`deficit_index`, `deficit_kappa`, keyword-only, off by default,
  bit-exact when off): the effective label weight grows with the
  sensed homeostatic deficit — the coupling-promotion topic's
  timing-primary bars license it (episodes 0083/0084).
- **Internal by default**: everything not listed below. Internals stay
  importable — the research arcs' copy-patch instrument discipline
  depends on reaching them — but they are visibly outside the promise
  and may move in any release. (The deprecation helper
  `pra._deprecation` is itself internal: the policy is public, the
  tooling is the maintainer's.)

## Deprecation policy

1. Announce: the changelog entry of the release that deprecates.
2. Notice on use: one uniform sentence —
   *"ELEMENT is deprecated and may be removed in REMOVAL; use
   REPLACEMENT."* — as a `DeprecationWarning` for library elements,
   a once-per-invocation stderr line for CLI surfaces.
3. Grace: at least one minor release between announcement and removal.
4. Removal: at a major release only (urgent exception above).

## The public surface

Each element below is promised for all of v1.x: it exists at its
path, matches its kind, and keeps its promised parameter names
(keyword-only additions are legal in minors). The five CLI names are
console commands; `pra.v1.>` is the versioned telemetry/control
subject space whose per-subject grammar is Doc 0006 §5b and the
subject-builder functions listed under Operational below.

### Run surface

*configure a brain, run it, read its summary.*

| Element | Kind | Promised parameters |
|---|---|---|
| `pra.Config` | dataclass | — |
| `pra.Engine` | class | — |
| `pra.__version__` | constant | — |
| `pra.config.Config` | dataclass | — |
| `pra.config.DistractorMode` | constant | — |
| `pra.config.EpisodeMode` | constant | — |
| `pra.config.HIDDEN_REF` | constant | — |
| `pra.config.OBS_DIM_REF` | constant | — |
| `pra.config.PolicyMode` | constant | — |
| `pra.config.ScoringMode` | constant | — |
| `pra.config.ShiftMode` | constant | — |
| `pra.config.TRUE_DIM_REF` | constant | — |
| `pra.config.WorldKind` | constant | — |
| `pra.core.contracts.SensorimotorEvent` | dataclass | — |
| `pra.core.engine.Engine` | class | config, scoring_mode, world_factory, scorer, proposal, decay, bus_factory, policy, drives, snapshot_store |
| `pra.core.engine.Engine.run` | function | seed, do_offline, resume_from |
| `pra.harness.runner.DeterminismResult` | dataclass | — |
| `pra.harness.runner.SuiteRun` | dataclass | — |
| `pra.harness.runner.check_determinism` | function | — |
| `pra.harness.runner.run_suite` | function | config, with_ablation, workers, proposal_factory, with_matched, world_factory |
| `pra.telemetry.recorder.PerSeedRunSummary` | dataclass | — |
| `pra.telemetry.recorder.PerSeedRunSummary.serialize` | function | — |

### World / body seam

*mount a world or an embodied transport.*

| Element | Kind | Promised parameters |
|---|---|---|
| `pra.anatomy.gymnasium_body.GymnasiumBody` | class | — |
| `pra.anatomy.gymnasium_body.GymnasiumWorld` | class | — |
| `pra.anatomy.minecraft.C1_ACTUATORS` | constant | — |
| `pra.anatomy.minecraft.C1_MINING_INDEX` | constant | — |
| `pra.anatomy.minecraft.C1_N_ACTIONS` | constant | — |
| `pra.anatomy.minecraft.C1_OBS_DIM` | constant | — |
| `pra.anatomy.minecraft.C1_POCKET_TOTAL_INDEX` | constant | — |
| `pra.anatomy.minecraft.C1_SENSORS` | constant | — |
| `pra.anatomy.minecraft.FakeBridge` | class | — |
| `pra.anatomy.minecraft.MinecraftTransport` | class | — |
| `pra.anatomy.minecraft.PROTOCOL_VERSION` | constant | — |
| `pra.anatomy.minecraft.c1_anatomy` | function | — |
| `pra.anatomy.ros2.ActuatorSpec` | dataclass | — |
| `pra.anatomy.ros2.CommandActuator` | class | — |
| `pra.anatomy.ros2.FakeTransport` | class | — |
| `pra.anatomy.ros2.RclpyTransport` | class | — |
| `pra.anatomy.ros2.Ros2Body` | class | — |
| `pra.anatomy.ros2.SensorSpec` | dataclass | — |
| `pra.anatomy.ros2.TopicSensor` | class | — |
| `pra.anatomy.ros2.Transport` | protocol | — |
| `pra.anatomy.ros2.apply_fields` | function | — |
| `pra.anatomy.ros2.extract_vector` | function | — |
| `pra.world.event_source.EventSource` | protocol | — |
| `pra.world.event_source.SensorimotorWorld` | class | — |
| `pra.world.ladder.CompositionalWorld` | class | — |
| `pra.world.ladder.DistractorWorld` | class | — |
| `pra.world.ladder.MultiRegionWorld` | class | — |
| `pra.world.ladder.NonUniformWorld` | class | — |
| `pra.world.ladder.ShiftingWorld` | class | — |
| `pra.world.ladder.make_world` | function | config, rng |

### Anatomy

*declare sensors, actuators, and runtime tools (Doc 0002).*

| Element | Kind | Promised parameters |
|---|---|---|
| `pra.anatomy.body.Actuator` | protocol | — |
| `pra.anatomy.body.AnatomyError` | class | — |
| `pra.anatomy.body.Body` | class | — |
| `pra.anatomy.body.ConstantSensor` | class | — |
| `pra.anatomy.body.Sensor` | protocol | — |
| `pra.anatomy.body.WorldActuator` | class | — |
| `pra.anatomy.body.WorldSensor` | class | — |

### Drives & policies

*value outcomes and select actions (Doc 0005).*

| Element | Kind | Promised parameters |
|---|---|---|
| `pra.action.policy.CompletionItchPolicy` | class | params, kappa, progress_index, pocket_index, completion_threshold, potential_of, label_index, label_beta, deficit_index, deficit_kappa |
| `pra.action.recipe.Recipe` | dataclass | — |
| `pra.action.recipe.RecipeMemory` | class | pocket_index, label_index |
| `pra.action.recipe.RecipePolicy` | class | params, memory, kappa, progress_index, pocket_index, lambda_r, position_indices, position_scale, completion_threshold, label_index, label_beta, deficit_index, deficit_kappa |
| `pra.action.policy.CuriosityLookaheadPolicy` | class | — |
| `pra.action.policy.Policy` | protocol | — |
| `pra.action.policy.PolicyContext` | dataclass | — |
| `pra.action.policy.PolicyParams` | dataclass | — |
| `pra.action.policy.RandomPolicy` | class | — |
| `pra.motivation.context.DriveContext` | dataclass | — |
| `pra.motivation.drive.CompetenceDrive` | class | — |
| `pra.motivation.drive.CuriosityDrive` | class | — |
| `pra.motivation.drive.CuriosityParams` | dataclass | — |
| `pra.motivation.drive.Drive` | protocol | — |
| `pra.motivation.drive.FrontierDrive` | class | — |
| `pra.motivation.drive.WeightedDriveSet` | class | — |

### Persistence

*snapshot, resume, and store brains (Doc 0006).*

| Element | Kind | Promised parameters |
|---|---|---|
| `pra.nats.NatsSnapshotStore` | class | — |
| `pra.persistence.portable.PORTABLE_FORMAT_VERSION` | constant | — |
| `pra.persistence.portable.PortableIntegrityError` | class | — |
| `pra.persistence.portable.PortableVersionError` | class | — |
| `pra.persistence.portable.export_brain` | function | path, blob, store, snapshot_id, note, created_at |
| `pra.persistence.portable.import_brain` | function | path |
| `pra.persistence.portable.inspect_brain` | function | path |
| `pra.persistence.snapshot.FORMAT_VERSION` | constant | — |
| `pra.persistence.snapshot.SnapshotCompatibilityError` | class | — |
| `pra.persistence.snapshot.SnapshotVersionError` | class | — |
| `pra.persistence.snapshot.SystemState` | dataclass | — |
| `pra.persistence.snapshot.config_from_dict` | function | — |
| `pra.persistence.snapshot.decode` | function | blob |
| `pra.persistence.snapshot.encode` | function | state |
| `pra.persistence.snapshot.validate_body_compatibility` | function | — |
| `pra.persistence.store.FileSnapshotStore` | class | — |
| `pra.persistence.store.InMemorySnapshotStore` | class | — |
| `pra.persistence.store.SnapshotStore` | protocol | — |
| `pra.persistence.store.snapshot_id_for` | function | — |

### Operational

*CLI tools, telemetry tap, subject space (B6/B7).*

| Element | Kind | Promised parameters |
|---|---|---|
| `pra-brain` | cli | — |
| `pra-dash` | cli | — |
| `pra-flush` | cli | — |
| `pra-rover` | cli | — |
| `pra-validate` | cli | — |
| `pra.dash.start_dashboard` | function | model, port, host |
| `pra.nats.BusTransport` | protocol | — |
| `pra.nats.NatsTap` | class | — |
| `pra.nats.NatsTransport` | class | — |
| `pra.nats.TransportError` | class | — |
| `pra.nats.subjects.DISCOVER_SUBJECT` | constant | — |
| `pra.nats.subjects.SCHEME_VERSION` | constant | — |
| `pra.nats.subjects.brain_anatomy_subject` | function | — |
| `pra.nats.subjects.brain_events_subject` | function | — |
| `pra.nats.subjects.brain_frames_subject` | function | — |
| `pra.nats.subjects.census_subject` | function | — |
| `pra.nats.subjects.control_subject` | function | — |
| `pra.nats.subjects.default_run_id` | function | — |
| `pra.nats.subjects.episode_subject` | function | — |
| `pra.nats.subjects.from_bytes` | function | — |
| `pra.nats.subjects.run_subjects` | function | — |
| `pra.nats.subjects.snapshot_subject` | function | — |
| `pra.nats.subjects.status_subject` | function | — |
| `pra.nats.subjects.step_subject` | function | — |
| `pra.nats.subjects.to_bytes` | function | — |
| `pra.nats.subjects.validate_run_id` | function | — |
| `pra.nats.subjects.view_live_subject` | function | — |
| `pra.nats.subjects.view_static_subject` | function | — |
| `pra.v1.>` | subject-family | — |

## How this document stays honest

`tests/contract/test_public_surface.py` — part of the all-green gate —
checks every element above (import, kind, promised parameters, CLI
resolution), checks this section against the inventory in both
directions, checks the version single-source, and demonstrates its own
failure mode on mutated entries (a removed symbol and a renamed
parameter must FAIL). The guard growing does not touch any runtime
path: the whole feature is additive (plan 035, constitution check).
