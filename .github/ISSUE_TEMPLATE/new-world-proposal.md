---
name: New world proposal
about: Propose a new world, body, sensor, or actuator for the brain to learn against
title: "world: "
labels: new-world, proposal
---

<!--
Worlds are the natural contribution here. Before filling this in, skim
CONTRIBUTING.md ("How to build one") — the seam is small and the rules
below come from the project constitution, not from taste.
-->

## What the world is

<!-- One paragraph. What does it emit, what actions does it take, what
is the hidden structure? -->

## What it would teach the brain

<!-- What can be measured against this world that cannot be measured
against the existing ones (the reference world, the five ladder worlds,
the rover, Gymnasium mounts)? A new difficulty axis, a new sensor
modality, a new dynamics class — name it. "It would be cool" is
allowed, but say what becomes measurable. -->

## Ground truth and determinism (constitution V)

<!-- Every new world keeps known ground truth, determinism, and
steppable time. Answer all three: -->

- **Ground truth**: what does the harness know about this world that
  the engine must not see, and through what harness-only accessor?
- **Determinism**: all randomness from the single passed
  `np.random.Generator`, in a fixed documented draw order — same
  `(config, seed)`, byte-identical run. How?
- **Steppable time**: the world advances only when `step()` is called
  (real-time worlds come last in this project, and not yet).

## Seam and scope

- Mounts as: <!-- bare EventSource via world_factory / a Body of named
  sensors+actuators (rover pattern) / a Gymnasium env behind the
  adapter -->
- Expected size: <!-- honest estimate — lines of code, and whether it
  needs anything beyond numpy -->
- I intend to build it myself: yes / no / with guidance
