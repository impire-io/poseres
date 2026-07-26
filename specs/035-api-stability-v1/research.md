# Phase 0 Research: API Stability & v1.0

No NEEDS CLARIFICATION markers survived the spec (three scope choices
were recorded as assumptions there). The decisions below resolve the
technical unknowns the plan needs.

## D1 — Where the public inventory lives

**Decision**: a Python module `tests/contract/surface_inventory.py`
declaring the surface as data (family → list of entries: import path,
kind, minimal shape), imported by the surface-guard test; documented
prose lives in the new design doc `hq/02-DESIGN/0008-public-api-versioning.md`,
with a test asserting the doc lists exactly the inventory's names.

**Rationale**: the repo's own enforcement pattern is "a document plus a
test that keeps it honest" (`tests/test_hq_structure.py`). Executable
data inside the test tree cannot ship behavior into the package
(constitution I), needs no new runtime file, and makes the guard
trivial: iterate, import, assert shape. A JSON/YAML sidecar was
rejected (another parser, no type help); a `pra.api` runtime registry
was rejected (ships code for a documentation problem).

**Alternatives considered**: `__all__`-only convention (unenforceable
across modules, silent drift); Sphinx-style autodoc as source of truth
(heavyweight, Phase D docs-site territory, and generated docs cannot
gate a release).

## D2 — What the guard checks

**Decision**: for every inventory entry — (a) the import path resolves;
(b) the kind matches (class / function / protocol / dataclass / CLI
entry point / constant); (c) for callables, the positional-or-keyword
parameter names the inventory declares are present in the live
signature (extra keyword-only additions allowed — additive is legal in
minor releases); (d) CLI entry points exist in `pyproject.toml` and
resolve to importable callables. Plus one negative test: a copy of the
guard run against a mutated inventory entry must FAIL (the
demonstrated-failure requirement, spec SC-003).

**Rationale**: shape-checking parameter names catches the breakages
users actually hit (renamed/removed arguments, vanished symbols)
without freezing implementation details like annotations or defaults —
which minor releases may legitimately improve.

**Alternatives considered**: full signature snapshots incl. annotations
and defaults (brittle: legitimate additive change fails the guard);
public-API snapshot tools (e.g. griffe-based diff) — new dev
dependency for what 60 lines of stdlib `inspect` does; rejected for
now, revisitable when the docs site lands.

## D3 — Version single-sourcing

**Decision**: `pyproject.toml` stays the single source;
`pra.__version__` is added via `importlib.metadata.version("poseres")`
with a try/except fallback `"0.0.0+uninstalled"` for source-tree use.

**Rationale**: zero duplication, stdlib-only, and the reported version
provably matches the tag (spec SC-004) because both read the same
metadata.

**Alternatives considered**: hardcoded `__version__` string (drifts
from the tag — exactly what SC-004 forbids); setuptools-scm (couples
versions to git state; the project tags deliberately, not per-commit).

## D4 — Deprecation mechanism

**Decision**: `pra/_deprecation.py` with one helper —
`deprecated(replacement: str, removal: str)` — emitting a
`DeprecationWarning` via `warnings.warn(..., stacklevel=2)` whose
message always carries the element name, the replacement, and the
earliest removal release; CLI deprecations print the same sentence to
stderr once per invocation. The policy text (announce in changelog +
notice on use; ≥ one minor release grace; removal only at a major;
urgent-removal exception documented) lives in Doc 0008. No existing
element is deprecated in this feature — the mechanism ships with a
synthetic test only.

**Rationale**: stdlib `DeprecationWarning` is what Python tooling
(pytest, linters, IDEs) already surfaces; a single helper guarantees
the notice format is uniform (spec SC-005's 100% clause becomes a
one-place property).

**Alternatives considered**: `warnings.deprecated` decorator (PEP 702,
3.13+) — attractive but the floor is 3.12; revisit when the floor
moves. Third-party `Deprecated` package — dependency for a one-function
job.

## D5 — The release itself

**Decision**: version bump to `1.0.0` in `pyproject.toml`, a root
`CHANGELOG.md` (Keep-a-Changelog shape) whose v1.0.0 entry states the
compatibility promise and links Doc 0008, and an annotated signed tag
`v1.0.0` created on `main` after the feature merges — the tag is cut
from the merged, gate-green main, never from the feature branch. The
README gains a short "Public API & versioning" section linking Doc
0008.

**Rationale**: matches the roadmap exit ("v1.0 tag; the seams
documented as public API") and the house rule that records land with
the work; tagging post-merge keeps the tag on a gate-proven commit.

**Alternatives considered**: GitHub Release with generated notes —
fine later, but the repo-local changelog is the artifact the promise
lives in; PyPI publication — explicitly not in the roadmap exit,
deferred (Phase D "shareable brains"/docs-site items may pull it in).

## D6 — The inventory's contents (the six families)

**Decision**: enumerate from the design docs outward, family by
family: (1) world/body seam — `EventSource` protocol surface,
`make_world`, `GymnasiumBody`, the ROS2 adapter's declared surface,
the pra-mc transport contract doc; (2) anatomy — Doc 0002's Body /
Sensor / Actuator / tool-registration surface; (3) drives — the drive
protocol + the three shipped drives + `WeightedDriveSet`; (4)
persistence — the SnapshotStore protocol, encode/decode, snapshot
compatibility helpers; (5) run surface — `Config`, `Engine`,
`run_suite`, `PerSeedRunSummary.serialize`; (6) operational — the four
CLI tools with their documented flags, and the versioned NATS subject
family as documented in Doc 0006 §5b/B6. Exact membership is fixed at
implementation time by walking Docs 0002–0007 and the adapters'
`__all__`s; anything not listed is internal by default (spec
assumption).

**Rationale**: the design docs are already the project's statement of
what each seam is; the inventory operationalizes them rather than
inventing a second taxonomy.

**Alternatives considered**: freezing every name currently importable
(blesses internals forever); seams-only minimalism (leaves Config/CLI
unclassified — the spec's recorded assumption rejects this).
