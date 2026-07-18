"""Subject scheme v1 + canonical wire form (feature 014, data-model §2/§3).

Everything the bus backend says lives under a versioned root and inside a
run-scoped namespace: two runs on one server cannot cross-talk because every
run-scoped subject embeds the run id (FR-004). ``pra.v1.brain.*`` is reserved
for the inter-brain horizon and deliberately unimplemented.

Wire form is canonical JSON with the recorder's discipline (fixed key order by
construction, compact separators, ``ensure_ascii``) and **no wall-clock time**
(research R3): the only ordering facts are sequence numbers and the run's own
counters, so payloads over a scripted transport are byte-deterministic.
"""

from __future__ import annotations

import json
import uuid

__all__ = [
    "DISCOVER_SUBJECT",
    "SCHEME_VERSION",
    "census_subject",
    "control_subject",
    "default_run_id",
    "episode_subject",
    "from_bytes",
    "run_subjects",
    "snapshot_subject",
    "status_subject",
    "step_subject",
    "to_bytes",
    "validate_run_id",
]

SCHEME_VERSION = "v1"
_ROOT = f"pra.{SCHEME_VERSION}"

DISCOVER_SUBJECT = f"{_ROOT}.discover"

# Characters with subject-atom meaning in NATS; a run id may carry none of them.
_FORBIDDEN = set('.*> \t\n"')


def validate_run_id(run_id: str) -> str:
    """Return ``run_id`` if it is a legal subject atom; raise ``ValueError`` otherwise."""
    if not isinstance(run_id, str) or not run_id:
        raise ValueError("run_id must be a nonempty string")
    bad = sorted(_FORBIDDEN.intersection(run_id))
    if bad:
        raise ValueError(f"run_id {run_id!r} contains subject-reserved characters: {bad}")
    return run_id


def default_run_id() -> str:
    """A fresh ``run-<8 hex>`` token. OS entropy (uuid4) — the engine's seeded
    generator is never touched (contracts §2.2)."""
    return f"run-{uuid.uuid4().hex[:8]}"


def status_subject(run_id: str) -> str:
    return f"{_ROOT}.run.{validate_run_id(run_id)}.status"


def step_subject(run_id: str) -> str:
    return f"{_ROOT}.run.{validate_run_id(run_id)}.tele.step"


def episode_subject(run_id: str) -> str:
    return f"{_ROOT}.run.{validate_run_id(run_id)}.tele.episode"


def census_subject(run_id: str) -> str:
    return f"{_ROOT}.run.{validate_run_id(run_id)}.tele.census"


def snapshot_subject(run_id: str) -> str:
    return f"{_ROOT}.run.{validate_run_id(run_id)}.tele.snapshot"


def control_subject(run_id: str) -> str:
    return f"{_ROOT}.run.{validate_run_id(run_id)}.ctrl"


def run_subjects(run_id: str) -> dict[str, str]:
    """The full subject set for one run — the discover reply's payload."""
    return {
        "status": status_subject(run_id),
        "step": step_subject(run_id),
        "episode": episode_subject(run_id),
        "census": census_subject(run_id),
        "snapshot": snapshot_subject(run_id),
        "ctrl": control_subject(run_id),
    }


def to_bytes(payload: dict) -> bytes:
    """Canonical wire form: insertion-ordered keys, compact separators, ascii."""
    return json.dumps(payload, separators=(",", ":"), ensure_ascii=True).encode("ascii")


def from_bytes(data: bytes) -> dict:
    """Parse a wire payload; raises ``ValueError`` unless it is a JSON object."""
    obj = json.loads(data.decode("utf-8"))
    if not isinstance(obj, dict):
        raise ValueError("payload must be a JSON object")
    return obj
