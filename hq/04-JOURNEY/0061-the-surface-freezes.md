# Episode 0061 — The surface freezes: v1.0 (2026-07-26)

Phase D's first item, landed the day it was activated
([episode 0060](0060-c2-parked-phase-d-active.md)): the public surface
is now a versioned promise. Feature 035 shipped the freeze as
documents, tests, and metadata — **zero behavior change to any
existing mode** [measured: the full byte-frozen gate, all green, zero
skips, on the landing commit].

**What v1.0 promises.** Everything listed in Doc 0008 — 110 elements
across six families (the world/body seam, anatomy, drives,
persistence, the run surface, and the operational surface incl. the
four CLI tools and the `pra.v1.>` subject space) — exists at its path,
keeps its kind, and keeps its promised parameter names for all of
v1.x. Patch = fixes; minor = additive/opt-in only, with constitution I
restated outward: the T1–T6 reference values reproduce exactly on
every v1.x release; removals only at a major, after a deprecation with
at least one minor of grace and a uniform notice naming replacement
and removal horizon. Everything unlisted is internal by default —
importable and unpromised, which the research arcs' copy-patch
instrument discipline explicitly relies on.

**The mechanism is the house pattern.** The inventory is executable
data (`tests/contract/surface_inventory.py`), the document is its twin
(Doc 0008), and a surface guard in the all-green gate keeps them
honest: every element imports and matches its declared shape
[measured], the doc and inventory agree bidirectionally [measured],
the version single-sources from the package metadata (fresh-venv
install reports 1.0.0 [measured]), and the guard's own failure mode is
demonstrated, not assumed — a removed symbol and a renamed parameter
both FAIL the negative controls [measured]. Kinds were classified by
live inspection, not by hand, so the initial inventory cannot
misdeclare what it froze.

**Calls recorded for the review trail** (inventory-draft.md in the
spec folder): public extends beyond the roadmap's four seams to the
config/entry surface, CLI tools, and subject space (users build
against them daily — owner-approved assumption); dash/flush library
internals, example module names, and the harness stay internal;
`import pra` stays exactly as light as before (the new top-level
re-exports are lazy, PEP 562) so the BLAS-pinning import order the
determinism story depends on is untouched [mechanism-argument].

Reversal condition: the promise loosens only at a major release. The
classification (not the promise) is revisited if a real user or the
first external contribution is measurably blocked by an
internal-by-default element — the fix is additive reclassification in
a minor, recorded in the changelog and Doc 0008.

Trail: `specs/035-api-stability-v1/` (spec, plan, research,
data-model, contracts, quickstart, tasks, inventory-draft);
`hq/02-DESIGN/0008-public-api-versioning.md`; `CHANGELOG.md`; the
`v1.0.0` tag on the landing commit.
