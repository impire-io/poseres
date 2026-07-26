<!--
Title: An opt-in odometry sensor for the rover
Labels: good first issue, new-sensor-actuator
-->

The rover (`src/pra/examples/rover/world.py`) senses the world — a
5-ray rangefinder, a compass, a GPS beacon, a bumper — but nothing
about its *own motion*. An odometry sense (how far did I just move,
how much did I just turn) is proprioception: a channel that is almost
perfectly predictable from the action taken, sitting next to
exteroceptive channels that are much harder. That contrast is exactly
the kind of structure the frame ecology is supposed to discover.

## The task

Add an opt-in `odo` sense to `RoverWorld`, following the pattern
feature 028 already established with the back ray (`emit_back` /
`BACK_RAY_ANGLE` in the same file — read that first; it is the whole
pattern):

- Width 2, RNG-free, computed in the physics step from the pose
  delta: signed distance moved (negative for reverse) and signed
  heading change, both scaled to roughly ±1 like the other senses.
- Behind a constructor flag (`emit_odo: bool = False`), default off.
  **Off must be byte-identical to today** — the rover is used in
  measured experiments and the pinned baselines must not move; the
  flag-off case is the acceptance test, not a courtesy.
- When on: the sense is appended after the standard channels (order
  is semantic — Doc 02, `src/pra/anatomy/body.py` module docstring),
  composed via a `RoverSensor(world, "odo", 2)` part in
  `make_rover_body` — which needs a matching flag of its own and an
  adjusted `expected_obs` width check, exactly as `extra_ray` has —
  so `obs_dim` becomes 12 and the anatomy metadata reports the new
  group.
- Define `reset()` semantics explicitly (no previous pose → zeros)
  and say so in the docstring.

## Where the seams are

- `src/pra/examples/rover/world.py` — `RoverWorld._emit`, the
  `SENSOR_PARTS` table, `RoverSensor`, `make_rover_body`, and the
  `emit_back` pattern to copy.
- `tests/contract/test_rover_contract.py` — where the new tests live:
  flag-off byte-identity, flag-on widths/metadata.

The rover internals are *internal* surface (not in Doc 0008's
inventory), so no public-surface inventory change is needed — but the
`pra-rover` CLI is public and must behave identically by default.

## Acceptance

- With the flag off: existing rover tests pass unchanged and a new
  test proves serialized summaries are byte-identical to the
  flag-absent world.
- With the flag on: `obs_dim == 12`, the `odo` group appears in
  `anatomy_meta()`, values match hand-computed pose deltas for a few
  scripted actions, and the run is byte-reproducible per seed.
- Repo gate green, zero skips
  (`./.venv/bin/ruff format --check . && ./.venv/bin/ruff check . && ./.venv/bin/pytest -q`).

## Honest scope

~60 lines of source plus ~40 of tests. The pattern to copy is in the
same file, which is what makes this a first issue rather than a
design exercise. The one judgment call — scaling of the two channels
— is worth one comment in the thread before you commit to it.
