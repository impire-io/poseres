# Quickstart: The Watchable Rover World

## Watch it learn (the five-minute path)

```bash
pip install poseres          # or: pip install -e ".[dev]" from a checkout
pra-rover
```

One command: the viewer URL is printed (and a browser tab opens when you
are at a terminal), a paced rover run starts, and the page shows — live —
the rover wandering its arena on the left and the brain's honest
telemetry on the right: the best frame's prediction-error EMA falling,
the frame population breathing, best_dim settling. The full default run
finishes in about four and a half minutes; learning is visible inside the
first one.

```
pra-rover --seed 7           # a different map and run — every seed is a fresh world
pra-rover --fps 0            # no pacing: full speed (seconds, not minutes)
pra-rover --port 0           # let the OS pick a free port (URL is printed)
pra-rover --json rover.json  # also write the canonical summary artifact
pra-rover --no-open --exit-when-done   # headless/CI-friendly
```

The run is byte-reproducible: the same command with the same seed and
configuration produces a byte-identical summary — pacing, polling, and
the viewer itself change nothing (that is tested, not promised).

## What you are watching (and what you are not)

The rover's policy is the pinned **random** baseline — it wanders; it
does not navigate. What improves is the brain: frames competing to
predict the rover's ten sensor channels (5 rangefinder rays, compass,
position beacon, bumper) restructure themselves online. The telemetry
shown is only what the system already measures: the survival-score
inputs, population size, best_dim. A single seed is a demo, not a
validated claim — spreads live in `pra-validate`.

## Use the rover world as a library (drives, harness, your own code)

```python
from pra.config import Config
from pra.core.engine import Engine
from pra.examples.rover import make_rover_body

summary = Engine(Config(), world_factory=make_rover_body).run(seed=1)
```

The rover mounts through the same seam as every world — so drives
(`policy_mode="curiosity"`), bodies, and the harness machinery work
unchanged. The anatomy is fixed at the validated reference widths
(`obs_dim=10`, `n_actions=4`); mounting with different widths fails with
a message naming the mismatch.

## Watch it with your own wiring

```python
from pra.config import Config
from pra.core.engine import Engine
from pra.examples.rover import RoverTelemetry, make_rover_body, start_viewer

cfg = Config()
tap = RoverTelemetry(cfg)
server, url = start_viewer(tap, port=0)
print(url)
summary = Engine(
    cfg,
    world_factory=lambda c, r: make_rover_body(c, r, telemetry=tap, step_delay=0.02),
    bus_factory=tap.bus_factory,
).run(seed=1)
tap.finish(summary)
```

The tap is pure observation: attach it, poll it, hammer `/state` from
ten tabs — the run's bytes cannot change.
