---
title: "Public API & versioning"
layout: page
---

From v1.0 the public surface is a promise: everything listed in
**[Doc 0008 — the public API, its versioning promise, and its
deprecation policy](design/0008-public-api-versioning.md)** — the
world/body seam, anatomy, drives, persistence, the run surface, the CLI
tools, and the versioned subject space — is stable for all of v1.x.
Patch releases are fixes only, minors are additive only (existing
modes' behavior stays byte-identical — the acceptance suite under the
pinned baseline reproduces its recorded reference values on every v1.x
release), and removals happen only at a major release after a
deprecation grace period.

The surface list lives in exactly one place. Doc 0008 is the
human-readable half; its machine-checked twin is
[`tests/contract/surface_inventory.py`](https://github.com/impire-io/poseres/blob/main/tests/contract/surface_inventory.py),
and the surface guard in the test gate keeps the two in exact agreement
— so this page deliberately does not restate the list. Everything not
listed there is internal by default: importable (research
instrumentation depends on reaching internals), but visibly outside the
promise.

Releases and deprecations are announced in the
[changelog](https://github.com/impire-io/poseres/blob/main/CHANGELOG.md).
