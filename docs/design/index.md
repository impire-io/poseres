---
title: "Design documents"
layout: page
---

The system specification: what must exist and how each part behaves.
These pages are copied verbatim from
[`hq/02-DESIGN/`](https://github.com/impire-io/poseres/tree/main/hq/02-DESIGN)
at deploy time — the repository holds the single source, including the
status legend ([V] validated / [D] design / [O] open) and the normative
validation specs under `validate/`.

Read 01 first; it is the map. 03 and 04 describe the validated core.

| # | Document | Covers |
|---|---|---|
| 01 | [System overview](0001-system-overview.md) | What the system is, the component map, the runtime loop, boot/restore lifecycle, scope, glossary |
| 02 | [Anatomy, I/O and the bus](0002-anatomy-io-bus.md) | Sensors, actuators, tools, and the communication bus |
| 03 | [Sensorimotor core](0003-sensorimotor-core.md) | Reference frames, the SIMD requirement, scoring, the global pose |
| 04 | [Structural learning](0004-structural-learning.md) | Online/offline learning, spawn-and-select, eviction, earned persistence |
| 05 | [Motivation & action](0005-motivation-action.md) | The innate drive, the value signal, action selection |
| 06 | [State & persistence](0006-state-persistence.md) | What system state is, snapshot/restore, the storage layer |
| 07 | [Configuration reference](0007-configuration-reference.md) | Every configuration parameter, defaults, ranges |
| 08 | [Public API & versioning](0008-public-api-versioning.md) | The v1.x public surface, the semver promise, the deprecation policy |
| 09 | [The brain-side hold](0009-brain-side-hold.md) | The head-derived hold: the measured composition with zero scaffolding (episode 0074) |
