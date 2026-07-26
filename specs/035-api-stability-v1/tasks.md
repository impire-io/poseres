# Tasks: API Stability & v1.0

**Input**: Design documents from `/specs/035-api-stability-v1/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/public-surface.md, quickstart.md

**Tests**: The spec's success criteria demand enforcement tests (the
surface guard and its negative control, the notice-format check, the
version-match check) — these are deliverables, not TDD ceremony, and
are tasked as such.

**Organization**: grouped by user story; US1 alone is a viable MVP
(the classified, guarded, documented surface), US2 adds the evolution
policy machinery, US3 cuts the release.

## Phase 1: Setup

- [ ] T001 Confirm branch `035-api-stability-v1` is current and the full gate is green before any change: `./.venv/bin/ruff format --check . && ./.venv/bin/ruff check . && ./.venv/bin/pytest -q` (zero skips) — the byte-frozen baseline this feature must not move

## Phase 2: Foundational (blocking all stories)

- [ ] T002 Enumerate the candidate surface: walk `hq/02-DESIGN/0002-anatomy-io-bus.md` … `0007-configuration-reference.md`, `src/pra/world/`, `src/pra/action/policy.py`, `src/pra/motivation/drive.py`, persistence/snapshot modules, `src/pra/config.py`, `src/pra/core/engine.py`, `src/pra/harness/runner.py`, adapters (`gymnasium`, `ros2`, `nats` tap surface) and `pyproject.toml [project.scripts]`; produce the classified list (public per family / internal) as a working note in `specs/035-api-stability-v1/inventory-draft.md` for review in the PR
- [ ] T003 Create `tests/contract/surface_inventory.py`: the `SurfaceEntry` structure (path, kind, family, params, doc — per data-model.md) and the declared entries from T002; module docstring states it is THE single source of truth for the public surface

## Phase 3: User Story 1 — build against the documented surface, upgrade safely (P1) 🎯 MVP

**Goal**: every user-reachable element classified; the surface guarded
by the gate; the seams documented as public API.

**Independent Test**: the guard passes on the declared inventory; Doc
0008 and the inventory agree bidirectionally; the quickstart example
runs using only public names.

- [ ] T004 [US1] Implement the surface guard in `tests/contract/test_public_surface.py`: every inventory entry imports/resolves; kind matches; declared param names present in live signatures (keyword-only additions legal); CLI entries exist in `pyproject.toml` and resolve to callables (contract §guard 1–3)
- [ ] T005 [P] [US1] Add `pra.__version__` (importlib.metadata, fallback `"0.0.0+uninstalled"`) and the curated public re-exports to `src/pra/__init__.py` (import-time only, no side effects; research D3)
- [ ] T006 [US1] Write `hq/02-DESIGN/0008-public-api-versioning.md`: the public surface by family (from the inventory), the semver promise (contract §promise, incl. the byte-frozen clause and snapshot guarantees), the deprecation policy, the internal-by-default rule with the research-instrument allowance
- [ ] T007 [US1] Add the doc↔inventory agreement check to `tests/contract/test_public_surface.py`: every inventory name appears in Doc 0008 and Doc 0008 names no public element absent from the inventory (contract §guard 4)
- [ ] T008 [P] [US1] Add a "Public API & versioning" section to `README.md` linking Doc 0008 and stating the one-sentence promise
- [ ] T009 [US1] Verify the quickstart example (`specs/035-api-stability-v1/quickstart.md`) runs using only public names — add it as a small test in `tests/contract/test_public_surface.py` or adjust the quickstart to match reality; record which

**Checkpoint**: US1 alone = classified, guarded, documented surface (MVP)

## Phase 4: User Story 2 — evolve internals without breaking users (P2)

**Goal**: the deprecation mechanism with uniform notices; the guard
demonstrably catches surface breakage.

**Independent Test**: synthetic deprecation produces the exact notice
sentence; mutated-inventory copy makes the guard fail.

- [ ] T010 [P] [US2] Create `src/pra/_deprecation.py`: `deprecated(replacement, removal)` decorator emitting `DeprecationWarning` with the exact sentence from contracts/public-surface.md §notice (stacklevel=2); unused by any existing mode (dead code for the frozen baseline)
- [ ] T011 [US2] Add notice-format tests in `tests/unit/test_deprecation.py`: synthetic deprecated function warns once with the exact sentence naming element, replacement, removal (SC-005)
- [ ] T012 [US2] Add the negative control to `tests/contract/test_public_surface.py`: run the guard logic against a mutated inventory copy (one removed symbol, one renamed param) and assert it FAILS both ways (contract §guard 5, SC-003's demonstrated-failure clause)

**Checkpoint**: policy is enforceable and enforcement is demonstrated

## Phase 5: User Story 3 — v1.0 ships as a referenceable release (P3)

**Goal**: version, changelog, tag-readiness.

**Independent Test**: fresh-venv install reports 1.0.0; changelog
entry states the promise and links Doc 0008.

- [ ] T013 [P] [US3] Create `CHANGELOG.md` (Keep-a-Changelog shape) with the v1.0.0 entry: the compatibility promise, link to Doc 0008, pointer to the surface guard
- [ ] T014 [US3] Bump `pyproject.toml` version `0.1.0` → `1.0.0`; add a version-match check (installed metadata == pyproject) to `tests/contract/test_public_surface.py`
- [ ] T015 [US3] Verify install-from-tree in a fresh venv: `pip install .` then `python -c "import pra; print(pra.__version__)"` prints `1.0.0`; record the transcript in the PR description (SC-004 evidence; the signed `v1.0.0` tag itself is cut on main AFTER merge — quickstart §release, plan D5)

## Phase 6: Polish & Landing (house rules: same merge)

- [ ] T016 Full gate green with the new guard in it: `./.venv/bin/ruff format --check . && ./.venv/bin/ruff check . && ./.venv/bin/pytest -q` — zero skips, byte-frozen baseline untouched (constitution I evidence)
- [ ] T017 Update `hq/03-IMPLEMENTATION/roadmap.md`: Phase D "API stability & v1.0" item marked landed with its episode link; ledger row added
- [ ] T018 Write journey episode `hq/04-JOURNEY/0061-the-surface-freezes.md` (via `/journey-log`): what v1.0 promises, the inventory-as-contract-test mechanism, evidence tags, reversal condition; update episode index + "Where things stand"
- [ ] T019 Merge `035-api-stability-v1` → `main` (gate green), push, then cut the annotated signed tag `v1.0.0` on main and push the tag; verify the tag's gate evidence

## Dependencies

- Phase 2 (T002→T003) blocks all stories.
- US1: T004 needs T003; T006 needs T003; T007 needs T004+T006; T005, T008 parallel; T009 needs T005.
- US2: T010/T011 independent of US1 (parallel with it after Phase 2); T012 needs T004.
- US3: T013 parallel; T014 needs T005 (version check imports `pra.__version__`); T015 needs T014.
- Phase 6 strictly last; T019 after everything.

## Parallel Example

After T003 lands: T004 (guard), T005 (`__init__`), T006 (Doc 0008),
T010 (deprecation helper), T013 (changelog) can all proceed in
parallel — five files, no shared edits.

## Implementation Strategy

MVP = Phase 1–3 (US1): the classified, guarded, documented surface.
US2 and US3 are small increments on top. Single-session feasible; the
one review-heavy artifact is the inventory itself (T002's draft is in
the PR precisely so the owner reviews membership as one list).
