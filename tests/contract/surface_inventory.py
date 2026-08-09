"""THE single source of truth for the v1 public surface (feature 035).

Every entry below is a public promise: the element exists at its path,
matches its declared kind, and (for callables) keeps its declared
parameter names for all of v1.x. Keyword-only additions are legal in
minor releases; anything else is a break and fails the surface guard
(test_public_surface.py). Everything NOT listed here is internal by
default -- importable, unpromised, and free to move (research
instruments rely on this; hq/02-DESIGN/0008-public-api-versioning.md
states the policy).

Kinds: class | dataclass | protocol | function | constant | cli |
subject-family. Families: run | world-body | anatomy | drive |
persistence | operational.
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["SurfaceEntry", "SURFACE"]

DOC = "hq/02-DESIGN/0008-public-api-versioning.md"


@dataclass(frozen=True)
class SurfaceEntry:
    path: str
    kind: str
    family: str
    params: tuple[str, ...] | None = None
    doc: str = DOC


E = SurfaceEntry

SURFACE: tuple[SurfaceEntry, ...] = (
    E("pra.config.Config", "dataclass", "run", None),
    E("pra.config.OBS_DIM_REF", "constant", "run", None),
    E("pra.config.HIDDEN_REF", "constant", "run", None),
    E("pra.config.TRUE_DIM_REF", "constant", "run", None),
    E("pra.config.ScoringMode", "constant", "run", None),
    E("pra.config.PolicyMode", "constant", "run", None),
    E("pra.config.WorldKind", "constant", "run", None),
    E("pra.config.DistractorMode", "constant", "run", None),
    E("pra.config.ShiftMode", "constant", "run", None),
    E("pra.config.EpisodeMode", "constant", "run", None),
    E(
        "pra.core.engine.Engine",
        "class",
        "run",
        (
            "config",
            "scoring_mode",
            "world_factory",
            "scorer",
            "proposal",
            "decay",
            "bus_factory",
            "policy",
            "drives",
            "snapshot_store",
        ),
    ),
    E("pra.core.engine.Engine.run", "function", "run", ("seed", "do_offline", "resume_from")),
    E(
        "pra.harness.runner.run_suite",
        "function",
        "run",
        ("config", "with_ablation", "workers", "proposal_factory", "with_matched", "world_factory"),
    ),
    E("pra.harness.runner.SuiteRun", "dataclass", "run", None),
    E("pra.harness.runner.check_determinism", "function", "run", None),
    E("pra.harness.runner.DeterminismResult", "dataclass", "run", None),
    E("pra.telemetry.recorder.PerSeedRunSummary", "dataclass", "run", None),
    E("pra.telemetry.recorder.PerSeedRunSummary.serialize", "function", "run", None),
    E("pra.core.contracts.SensorimotorEvent", "dataclass", "run", None),
    E("pra.world.event_source.EventSource", "protocol", "world-body", None),
    E("pra.world.event_source.SensorimotorWorld", "class", "world-body", None),
    E("pra.world.ladder.make_world", "function", "world-body", ("config", "rng")),
    E("pra.world.ladder.NonUniformWorld", "class", "world-body", None),
    E("pra.world.ladder.CompositionalWorld", "class", "world-body", None),
    E("pra.world.ladder.DistractorWorld", "class", "world-body", None),
    E("pra.world.ladder.ShiftingWorld", "class", "world-body", None),
    E("pra.world.ladder.MultiRegionWorld", "class", "world-body", None),
    E("pra.anatomy.gymnasium_body.GymnasiumWorld", "class", "world-body", None),
    E("pra.anatomy.gymnasium_body.GymnasiumBody", "class", "world-body", None),
    E("pra.anatomy.minecraft.c1_anatomy", "function", "world-body", None),
    E("pra.anatomy.minecraft.FakeBridge", "class", "world-body", None),
    E("pra.anatomy.minecraft.MinecraftTransport", "class", "world-body", None),
    E("pra.anatomy.minecraft.PROTOCOL_VERSION", "constant", "world-body", None),
    E("pra.anatomy.minecraft.C1_OBS_DIM", "constant", "world-body", None),
    E("pra.anatomy.minecraft.C1_N_ACTIONS", "constant", "world-body", None),
    # the completion-itch policy's anatomy knowledge (feature 040)
    E("pra.anatomy.minecraft.C1_MINING_INDEX", "constant", "world-body", None),
    E("pra.anatomy.minecraft.C1_POCKET_TOTAL_INDEX", "constant", "world-body", None),
    E("pra.anatomy.minecraft.C1_SENSORS", "constant", "world-body", None),
    E("pra.anatomy.minecraft.C1_ACTUATORS", "constant", "world-body", None),
    E("pra.anatomy.ros2.Ros2Body", "class", "world-body", None),
    E("pra.anatomy.ros2.TopicSensor", "class", "world-body", None),
    E("pra.anatomy.ros2.CommandActuator", "class", "world-body", None),
    E("pra.anatomy.ros2.SensorSpec", "dataclass", "world-body", None),
    E("pra.anatomy.ros2.ActuatorSpec", "dataclass", "world-body", None),
    E("pra.anatomy.ros2.Transport", "protocol", "world-body", None),
    E("pra.anatomy.ros2.FakeTransport", "class", "world-body", None),
    E("pra.anatomy.ros2.RclpyTransport", "class", "world-body", None),
    E("pra.anatomy.ros2.apply_fields", "function", "world-body", None),
    E("pra.anatomy.ros2.extract_vector", "function", "world-body", None),
    E("pra.anatomy.body.Body", "class", "anatomy", None),
    E("pra.anatomy.body.Sensor", "protocol", "anatomy", None),
    E("pra.anatomy.body.Actuator", "protocol", "anatomy", None),
    E("pra.anatomy.body.WorldSensor", "class", "anatomy", None),
    E("pra.anatomy.body.WorldActuator", "class", "anatomy", None),
    E("pra.anatomy.body.ConstantSensor", "class", "anatomy", None),
    E("pra.anatomy.body.AnatomyError", "class", "anatomy", None),
    E("pra.action.policy.Policy", "protocol", "drive", None),
    E("pra.action.policy.PolicyContext", "dataclass", "drive", None),
    E("pra.action.policy.RandomPolicy", "class", "drive", None),
    E("pra.action.policy.CuriosityLookaheadPolicy", "class", "drive", None),
    # the event pathway's shipped policy (feature 040; motivation-stack G3)
    E(
        "pra.action.policy.CompletionItchPolicy",
        "class",
        "drive",
        (
            "params",
            "kappa",
            "progress_index",
            "pocket_index",
            "completion_threshold",
            "potential_of",
            "label_index",
            "label_beta",
        ),
    ),
    # recipes: taught order as product (feature 041; recipe-reach, episode 0076)
    E("pra.action.recipe.Recipe", "dataclass", "drive", None),
    E("pra.action.recipe.RecipeMemory", "class", "drive", ("pocket_index", "label_index")),
    E(
        "pra.action.recipe.RecipePolicy",
        "class",
        "drive",
        (
            "params",
            "memory",
            "kappa",
            "progress_index",
            "pocket_index",
            "lambda_r",
            "position_indices",
            "position_scale",
            "completion_threshold",
            "label_index",
            "label_beta",
        ),
    ),
    E("pra.action.policy.PolicyParams", "dataclass", "drive", None),
    E("pra.motivation.drive.Drive", "protocol", "drive", None),
    E("pra.motivation.drive.CuriosityDrive", "class", "drive", None),
    E("pra.motivation.drive.CuriosityParams", "dataclass", "drive", None),
    E("pra.motivation.drive.CompetenceDrive", "class", "drive", None),
    E("pra.motivation.drive.FrontierDrive", "class", "drive", None),
    E("pra.motivation.drive.WeightedDriveSet", "class", "drive", None),
    E("pra.motivation.context.DriveContext", "dataclass", "drive", None),
    E("pra.persistence.snapshot.FORMAT_VERSION", "constant", "persistence", None),
    E("pra.persistence.snapshot.SystemState", "dataclass", "persistence", None),
    E("pra.persistence.snapshot.SnapshotVersionError", "class", "persistence", None),
    E("pra.persistence.snapshot.SnapshotCompatibilityError", "class", "persistence", None),
    E("pra.persistence.snapshot.encode", "function", "persistence", ("state",)),
    E("pra.persistence.snapshot.decode", "function", "persistence", ("blob",)),
    E("pra.persistence.snapshot.config_from_dict", "function", "persistence", None),
    E("pra.persistence.snapshot.validate_body_compatibility", "function", "persistence", None),
    E("pra.persistence.store.SnapshotStore", "protocol", "persistence", None),
    E("pra.persistence.store.FileSnapshotStore", "class", "persistence", None),
    E("pra.persistence.store.InMemorySnapshotStore", "class", "persistence", None),
    E("pra.persistence.store.snapshot_id_for", "function", "persistence", None),
    # portable brain artifacts (feature 037): the shareable one-file wrap
    E("pra.persistence.portable.PORTABLE_FORMAT_VERSION", "constant", "persistence", None),
    E("pra.persistence.portable.PortableIntegrityError", "class", "persistence", None),
    E("pra.persistence.portable.PortableVersionError", "class", "persistence", None),
    E(
        "pra.persistence.portable.export_brain",
        "function",
        "persistence",
        ("path", "blob", "store", "snapshot_id", "note", "created_at"),
    ),
    E("pra.persistence.portable.import_brain", "function", "persistence", ("path",)),
    E("pra.persistence.portable.inspect_brain", "function", "persistence", ("path",)),
    E("pra.nats.NatsSnapshotStore", "class", "persistence", None),
    E("pra.nats.NatsTap", "class", "operational", None),
    E("pra.nats.NatsTransport", "class", "operational", None),
    E("pra.nats.BusTransport", "protocol", "operational", None),
    E("pra.nats.TransportError", "class", "operational", None),
    E("pra.dash.start_dashboard", "function", "operational", ("model", "port", "host")),
    E("pra.nats.subjects.DISCOVER_SUBJECT", "constant", "operational", None),
    E("pra.nats.subjects.SCHEME_VERSION", "constant", "operational", None),
    E("pra.nats.subjects.brain_anatomy_subject", "function", "operational", None),
    E("pra.nats.subjects.brain_events_subject", "function", "operational", None),
    E("pra.nats.subjects.brain_frames_subject", "function", "operational", None),
    E("pra.nats.subjects.census_subject", "function", "operational", None),
    E("pra.nats.subjects.control_subject", "function", "operational", None),
    E("pra.nats.subjects.default_run_id", "function", "operational", None),
    E("pra.nats.subjects.episode_subject", "function", "operational", None),
    E("pra.nats.subjects.from_bytes", "function", "operational", None),
    E("pra.nats.subjects.run_subjects", "function", "operational", None),
    E("pra.nats.subjects.snapshot_subject", "function", "operational", None),
    E("pra.nats.subjects.status_subject", "function", "operational", None),
    E("pra.nats.subjects.step_subject", "function", "operational", None),
    E("pra.nats.subjects.to_bytes", "function", "operational", None),
    E("pra.nats.subjects.validate_run_id", "function", "operational", None),
    E("pra.nats.subjects.view_live_subject", "function", "operational", None),
    E("pra.nats.subjects.view_static_subject", "function", "operational", None),
    # the shipped command-line tools (pyproject [project.scripts])
    E("pra-validate", "cli", "operational"),
    E("pra-rover", "cli", "operational"),
    E("pra-dash", "cli", "operational"),
    E("pra-flush", "cli", "operational"),
    E("pra-brain", "cli", "operational"),
    # the versioned telemetry/control subject space (Doc 0006 S5b / B6);
    # documented, not importable -- the guard checks doc presence only
    E("pra.v1.>", "subject-family", "operational"),
    # the package version attribute + lazy top-level re-exports (feature 035)
    E("pra.__version__", "constant", "run"),
    E("pra.Config", "dataclass", "run"),
    E("pra.Engine", "class", "run"),
)
