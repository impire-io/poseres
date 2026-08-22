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
| 10 | [Recipes and the label](0010-recipes-and-the-label.md) | Taught reach as product: recipe memory, the recipe policy, the praise label (episode 0077) |
| 11 | [The dials](0011-the-dials.md) | What every tuning knob represents, the measured operating points, and the drive-band tuning protocol |
| 12 | [Anatomy from world](0012-anatomy-from-world.md) | The structured process for deriving a body from a target environment (skill: /anatomy-mapping) |
| 13 | [The palate](0013-the-aim.md) | Worth eaten into existence at the body seam, read at the distance (episode 0100; steering refuted, substrate stands) |
| 14 | [Commitment](0014-the-last-crack.md) | The hold that finishes: incumbency while progress advances, dying with its intention (episode 0101) |
| 15 | [The survival stack](0015-native-survival.md) | The operating point that lives: palate body + flood + commitment, gate off, on the world's own economy (episode 0103) |
| 16 | [The motivation stack](0016-motivation-stack.md) | The measured map: eight layers, their twins, their evidence, their shipped forms (episode 0107) |
| 17 | [Lean worlds](0017-lean-worlds.md) | When is another body worth sensing: race beats information; the partial-gap world gates every follow-up (episodes 0109–0110) |
| 18 | [Brain anatomy](0018-brain-anatomy.md) | The zones of the learner, visually: what each part holds and where knowledge lives |
| 19 | [Factored actions](0019-factored-actions.md) | The action side at vocabulary scale: flat's measured ceiling, the product-factoring requirement, the mobility–parity tension (episode 0112) |
