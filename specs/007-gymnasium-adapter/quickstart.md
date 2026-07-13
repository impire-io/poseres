# Quickstart: The Gymnasium Adapter

## Install

```bash
pip install "poseres[gym]"        # core + gymnasium
# or, from a source checkout (dev already includes gymnasium):
pip install -e ".[dev]"
```

## Run the worked example

```bash
./.venv/bin/python examples/cartpole.py
```

Under a minute: runs the engine's reference schedule on CartPole-v1
(seed 1), prints the honest per-seed summary and the respawn count,
then re-runs the same seed and prints the byte-identity verdict.

## Mount CartPole yourself (three lines of glue)

```python
from pra.anatomy.gymnasium_body import GymnasiumBody
from pra.config import Config
from pra.core.engine import Engine

cfg = Config(obs_dim=4, n_actions=2)   # match the env; the factory checks
summary = Engine(cfg, world_factory=GymnasiumBody.factory("CartPole-v1")).run(seed=1)
print(summary)
```

`GymnasiumBody.factory` also takes a zero-argument callable if you want
to configure the environment yourself (e.g. a render mode):

```python
import gymnasium

factory = GymnasiumBody.factory(lambda: gymnasium.make("CartPole-v1"))
```

## What to know before pointing it at other environments

- **Supported in v1**: `Discrete` action spaces, `Box` observation
  spaces (any shape — flattened C-order to float64). Anything else is
  rejected at mount time with a message naming the space.
- **Termination**: PRA episodes are fixed-length. When the environment
  ends its own episode (`terminated`/`truncated`), the adapter
  immediately respawns it with the next deterministic seed and the PRA
  episode continues — the boundary transition is irreducibly
  unpredictable (by design, and documented). `body.respawns` tells you
  how often it happened.
- **Determinism**: same `(config, seed)` → byte-identical run
  summaries, for any environment that follows Gymnasium's seeding
  convention. Per-reset seeds derive from the run seed; the engine's
  own random stream is never touched.
- **No reward**: PRA's motivation is intrinsic (the drive); the
  environment's reward is discarded, honestly and openly.
- **No snapshot/resume** for Gymnasium-mounted runs in v1 — external
  env state cannot be re-derived from the seed stream (ROADMAP B5 owns
  the honest story).

## Compose it like any body

`GymnasiumBody` is a Doc 02 `Body`: you can register extra sensors or
actuators alongside the Gym feed and they compose in fixed order,
taking effect at the next consolidation boundary:

```python
import gymnasium
from pra.anatomy.body import ConstantSensor
from pra.anatomy.gymnasium_body import GymnasiumBody

body = GymnasiumBody(gymnasium.make("CartPole-v1"), seed=1)
body.register_sensor(ConstantSensor("bias", [0.5]))   # obs_dim 4 → 5 next slow loop
```
