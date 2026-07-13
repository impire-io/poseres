# Getting started with PRA

PRA (Pose Resolution Architecture) is a continuously-learning machine
intelligence: a configurable body of sensors and actuators, a fixed innate
drive, and a brain that learns and restructures itself online — it is never
trained-then-frozen. This guide gets you from zero to a running system, shows
you how to hook up your own sensors and actuators, and explains how learning
actually happens.

One honest note before you start: PRA is a research system. It ships with a
synthetic world it learns from, and clean seams for connecting anything else —
but connecting your own environment means writing a small amount of Python
against two protocols. There is no plug-and-play catalogue of integrations
(yet). What *is* guaranteed: everything you see below is deterministic
(byte-identical on re-run) and covered by an acceptance suite.

## 1. Install and prove it works

Fastest, with [`uv`](https://docs.astral.sh/uv/) — no venv, no Python
juggling:

```bash
uvx --from poseres pra-validate suite
```

Or from source:

```bash
git clone https://github.com/impire-io/poseres.git
cd poseres
python3.13 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pra-validate suite
```

`pra-validate suite` runs the acceptance tests T1–T6 across 8 seeds and prints
a PASS/FAIL verdict per test, with the numbers behind each verdict. If that
passes, your installation learns, self-limits its own growth, and reproduces
bit-for-bit. Other commands worth trying:

```bash
pra-validate determinism --seed 1   # byte-identical re-run proof
pra-validate agency                 # T7: does directed exploration beat random?
pra-validate scale --true-dims 20,35,50
pra-validate ladder                 # the complexity ladder: harder worlds,
                                    # known ground truth, honest verdicts
```

And to *watch* it learn instead of reading numbers:

```bash
pra-rover        # a browser tab opens: a 2D rover world, live learning telemetry
```

One command starts a paced run and serves a built-in viewer (stdlib-only,
nothing to install): the rover wanders its arena under the pinned random
policy while the brain's own quantities move — prediction error falling,
the frame population breathing, best_dim settling. `--fps 0` runs
unthrottled; `--seed N` is a fresh map and run; the run is
byte-reproducible per seed. The rover does not navigate (the policy is
random — directed behavior is the drive research's job); what you are
watching improve is the brain.

## 2. The mental model (60 seconds)

- **World / environment** — anything that emits observation vectors and
  accepts actions. The built-in `SensorimotorWorld` is a synthetic environment
  with a hidden low-dimensional latent state; the system's job is to discover
  that structure without being told it exists.
- **Body** — the composition layer. Sensors are concatenated in fixed order
  into one observation vector; actuators are unioned in fixed order into one
  action space. The brain never knows what a dimension *means* — anatomy is
  deliberately meaning-free.
- **Frames** — the units of the brain. Each reference frame is a small
  learned model competing to predict observations. Frames are spawned,
  scored on honest prediction error, and evicted when they can't pay rent.
  Structure emerges from this ecology, not from a training script.
- **Drive** — the innate motivation. It is fixed at birth (the system cannot
  rewrite its own drive) and turns predicted experience into value, which the
  policy uses to pick actions.
- **Engine** — runs one seed: episodes of sensorimotor steps (the fast loop),
  interleaved with consolidation cycles (the slow loop) where spawning,
  eviction, and body growth happen.

Learning is not a phase. From the first observation, frames are updating
online; the longer it runs, the more structure it finds.

## 3. Run the engine yourself

```python
from pra.config import Config
from pra.core.engine import Engine

summary = Engine(Config()).run(seed=1)
print(summary)   # per-seed telemetry: prediction error, population, best_dim…
```

`Config()` is the validated reference configuration (a 10-dimensional
observation hiding a 3-dimensional world). Every parameter — world size,
cycles, learning rates, drive weights — is a `Config` field; see
`src/pra/config.py` and design doc `07-configuration-reference.md`.

## 4. Hook things up: the Body

The `Body` implements the same `EventSource` seam the synthetic world does, so
a world mounted through a body is byte-identical to the direct connection —
the wrapper costs you nothing:

```python
from pra.anatomy.body import Body, WorldSensor, WorldActuator
from pra.config import Config
from pra.core.engine import Engine
from pra.world.event_source import SensorimotorWorld

def body_factory(cfg, rng):
    world = SensorimotorWorld(cfg, rng)
    sensor = WorldSensor(world)
    return Body(world, sensors=[sensor], actuators=[WorldActuator(world, sensor)])

summary = Engine(Config(), world_factory=body_factory).run(seed=1)
```

For a full worked example of a multi-part body — four named sensors and an
actuator around a real environment — read `src/pra/examples/rover/world.py`
(the `pra-rover` demo): it is the integration surface this section
describes, in ~340 lines.

### Writing your own sensor and actuator

A sensor and an actuator are structural protocols — no base class to inherit,
just three methods each:

```python
import numpy as np

class Thermometer:                      # Sensor protocol
    def id(self) -> str: return "thermo"
    def width(self) -> int: return 1    # dimensions this sensor contributes
    def read(self) -> np.ndarray:
        return np.array([read_temperature()], dtype=np.float64)

class Heater:                           # Actuator protocol
    def id(self) -> str: return "heater"
    def action_count(self) -> int: return 2   # off, on
    def apply(self, local_action_index: int) -> None:
        set_heater(bool(local_action_index))  # returns nothing — feedback
                                              # arrives only via observations
```

Rules the body enforces for you: sensor ids must be unique, `read()` must
return exactly `width()` float64 values, and actuators return nothing — the
only feedback path from an action is what the sensors see next. Your
environment object needs one method, `reset()`, called at each episode start
— or exactly **once**, if your world cannot restart: set
`Config(episode_mode="continuous")` and the engine boots the world a single
time (a homing routine, a login) and learns from the unbroken stream, with
the same learning rhythm at *virtual* episode boundaries. One honest note
from the first measurement: continuous operation wants worlds whose state
stays in bounds (an arena, a game map) — a world that drifts without limit
stops being learnable by anything (`specs/008-continuous-operation/reading.md`).

Have several copies of your world? `Config(n_streams=K)` runs K instances
of the same world — K independent explorers, one brain, deterministic
merge. Learning per unit of experience matches single-stream (measured);
what K streams buy is world-side parallelism in real deployments, and,
with `episode_mode="continuous"`, K different vantage points of one world.

```python
def body_factory(cfg, rng):
    env = MyEnvironment()               # anything with reset()
    return Body(env, sensors=[Thermometer()], actuators=[Heater()])

cfg = Config(obs_dim=1, n_actions=2)    # match your body's dimensions —
                                        # the scale rules key off obs_dim
Engine(cfg, world_factory=body_factory).run(seed=1)
```

### Growing the body mid-run

Registrations are queued and applied at the next consolidation boundary; every
frame's learned weights are preserved bit-for-bit while its input/output
surfaces are resized:

```python
from pra.anatomy.body import ConstantSensor
body.register_sensor(ConstantSensor("bias", [0.5, -0.5]))
# next slow loop: obs_dim += 2, no forgetting, run stays deterministic
```

### Already have a Gymnasium environment?

Skip the protocols entirely: the Gymnasium adapter mounts any environment
with a discrete action space and a continuous (Box) observation vector —
CartPole is obs_dim 4 / 2 actions, inside the validated range:

```bash
pip install "poseres[gym]"
python examples/cartpole.py     # the worked example — under a minute
```

```python
from pra.anatomy.gymnasium_body import GymnasiumBody

cfg = Config(obs_dim=4, n_actions=2)    # must match the env; the factory checks
Engine(cfg, world_factory=GymnasiumBody.factory("CartPole-v1")).run(seed=1)
```

Two honest notes: PRA discards the environment's reward (motivation is
intrinsic — you watch prediction error fall, not return rise), and when the
environment ends its own episode the world *respawns* inside PRA's
fixed-length episode (deterministic seeded reset, counted on
`body.respawns`). Details and scope: `specs/007-gymnasium-adapter/quickstart.md`.

## 5. Get it to learn *toward* something: drives

By default the policy is random — the pinned validation baseline. Learning
still happens (frames learn from whatever experience arrives); the drive
decides *which* experience to seek. Two drives ship today:

- **`curiosity`** — learning progress + novelty. Measured result worth
  knowing: in a uniformly learnable world, pure novelty-seeking is *worse*
  than random (JOURNEY.md, Chapter 7).
- **`competence`** — mastery + familiarity (concentrated practice). The first
  drive measured to beat random exploration, at both tested scales.

```python
cfg = Config(policy_mode="curiosity",
             drive_weights=(("competence", 1.0),))
Engine(cfg).run(seed=1)
```

Blend drives by weight: `(("curiosity", 0.3), ("competence", 0.7))`. The
drive is structurally immutable at runtime — the system cannot learn to
reward-hack its own motivation.

## 6. Keep what it learned: snapshots

Off by default. Opt in with a store and a cadence, and a run resumed from any
snapshot is byte-identical to the uninterrupted run:

```python
from pra.persistence.store import FileSnapshotStore

store = FileSnapshotStore("snapshots/")
cfg = Config(snapshot_every_n_cycles=5)
Engine(cfg, snapshot_store=store).run(seed=1)

# later — resume from the newest snapshot:
snapshot_id, _ = store.list()[0]
Engine(cfg, snapshot_store=store).run(seed=1, resume_from=store.read(snapshot_id))
```

Known edge: snapshots of runs whose body was resized mid-run are not yet
supported (a format-version follow-up is planned). Snapshots of
Gymnasium-mounted runs are also not yet supported — external environment
state cannot be re-derived from the seed stream (see the roadmap's B5).

## 7. What PRA does not do yet

So you calibrate expectations before building on it: no multi-step planning
(the policy seam has a one-step default), no distributed operation (the bus
seam has only an in-memory backend), no tool self-invention (the registration
interface exists; the inventing mechanism is an open problem), and one
pre-built connector so far — the Gymnasium adapter (§4); for
cameras/robots/APIs the Sensor/Actuator protocols above are the
integration surface.

## 8. Where to go next

`design/00-README-index.md` is the map of the seven design documents (read 01
first). `JOURNEY.md` tells you how the project got here, including the dead
ends — the refuted hypotheses are as load-bearing as the shipped code. The
acceptance suite (`pra-validate suite`, plus `pra-validate agency` for T7) is
the contract: if you change something and T1–T7 still pass byte-identically,
you haven't broken the validated core. `pra-rover` is the watchable proof;
the acceptance suite is the contract.
