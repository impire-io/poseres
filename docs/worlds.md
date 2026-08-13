---
title: "Worlds gallery"
layout: page
---

Every world and adapter that ships with PRA: what it is, the
configuration that mounts it, and the journey episode that measured it.
The descriptions below stick to the measured record — including the
FAILs, because a recorded failure is as load-bearing as a pass. Worlds
mount through one seam (`Config.world` / the Engine's `world_factory`);
every synthetic world below keeps known ground truth, determinism, and
steppable time.

## The reference world

`pra.world.event_source.SensorimotorWorld` — the validated world: a
synthetic environment whose 10-dimensional observation hides a
3-dimensional latent state; the brain's job is to discover that
structure without being told it exists. Everything byte-frozen in the
project is frozen against this world: the acceptance suite T1–T6 runs
on it across 8 seeds, and two runs of a seed produce byte-identical
telemetry.

```python
from pra.config import Config
from pra.core.engine import Engine

Engine(Config()).run(seed=1)  # Config() is the validated reference config
```

```bash
pra-validate suite                # the full acceptance suite on this world
```

Measured: [episode 0003](https://github.com/impire-io/poseres/blob/main/hq/04-JOURNEY/0003-the-validation-harness.md)
(the harness and the batched core); the scaled record (true_dim
20/35/50, 24/24 anchored) closed in
[episode 0014](https://github.com/impire-io/poseres/blob/main/hq/04-JOURNEY/0014-the-eighth-rule.md).

## NonUniformWorld — L1, a region of unlearnable dynamics

A half-space of latent space (`latent[0] > 0`) where transitions gain
fresh Gaussian noise — unlearnable dynamics the agent's own actions
carry it into and out of. This is the noisy-TV/camping testbed the
drive research runs on. Measured: strong region noise widens the
selection landing, dose-dependently; and on this world the competence
drive and the frontier blend beat random exploration at every horizon
and both noise dials (24 seeds) — the A4 exit criterion, met at proper
power.

```python
Config(world="nonuniform", region_noise_std=0.2)  # harness dials: 0.2 and 0.8
```

```bash
pra-validate ladder               # runs the pre-registered rung criteria
```

Measured: [episode 0017](https://github.com/impire-io/poseres/blob/main/hq/04-JOURNEY/0017-the-complexity-ladder.md)
(the ladder's first results),
[episode 0024](https://github.com/impire-io/poseres/blob/main/hq/04-JOURNEY/0024-the-frontier-drive.md)
(drives measured on it at proper power).

## CompositionalWorld — L2, factored dynamics

The hidden state is K independent factor groups; action *a* displaces
only group *a mod K*, under the reference joint emission — so the parts
never leak through the channels. Measured (PASS): selection lands
*part-sized* — the brain finds the factors rather than modelling the
joint space.

```python
Config(world="compositional", true_dim=6, obs_dim=18, factor_dims=(3, 3))
```

Measured: [episode 0017](https://github.com/impire-io/poseres/blob/main/hq/04-JOURNEY/0017-the-complexity-ladder.md).

## DistractorWorld — L3, channels that carry no action information

Extra observation channels driven by an autonomous drifting latent
(`structured` mode) or fresh unit noise (`noise` mode) — signal with
zero action information. The record is two-sided: selection ignores
*structured* distractors (PASS), but high-amplitude channel static
collapses the landing — a recorded FAIL at the default config that
stands as the reference. The opt-in fix is learned channel weighting
(feature 016): with the weighting on, the noise rung passes at unit
amplitude at 24 seeds.

```python
Config(
    world="distractor",
    obs_dim=20,
    distractor_dim=3,
    distractor_channels=10,
    distractor_mode="structured",
)
```

Measured: [episode 0017](https://github.com/impire-io/poseres/blob/main/hq/04-JOURNEY/0017-the-complexity-ladder.md)
(first results),
[episode 0025](https://github.com/impire-io/poseres/blob/main/hq/04-JOURNEY/0025-channel-noise.md)
(the collapse diagnosed),
[episode 0030](https://github.com/impire-io/poseres/blob/main/hq/04-JOURNEY/0030-learned-channel-weighting.md)
(closed opt-in).

## ShiftingWorld — mastered, then changed

The reference world until a set step count, then the world changes
under the brain: in `dynamics` mode what the actions *do* swaps; in
`emission` mode the world is repainted (appearance swaps, dynamics
unchanged). Built as the camping/staleness testbed. Measured: camping
does cost — the camper recovers worst when the world shifts — and this
world pair carried the five-family staleness-detection program to its
honest closing verdict (no passive or active statistic separated a
world change from the brain's own nonstationarity).

```python
Config(world="shifting", shift_after_steps=1500)  # dynamics
Config(world="shifting", shift_after_steps=1500, shift_mode="emission")  # repaint
```

Measured: [episode 0031](https://github.com/impire-io/poseres/blob/main/hq/04-JOURNEY/0031-the-camping-bill.md)
(the camping bill),
[episode 0034](https://github.com/impire-io/poseres/blob/main/hq/04-JOURNEY/0034-the-repainted-world.md)
(emission mode),
[episode 0059](https://github.com/impire-io/poseres/blob/main/hq/04-JOURNEY/0059-scheduled-probing.md)
(the program's close).

## MultiRegionWorld — regions of graded difficulty

The NonUniformWorld mechanism generalized: two or four sign-defined
regions of latent space, each with its own transition-noise level — all
meant to stay inside the learnable band (difficulty, not noise traps).
Built alongside ShiftingWorld for the camping question; the measured
occupancy readings come from its harness-only ground truth.

```python
Config(world="multiregion", region_noise_levels=(0.0, 0.4))  # 2 regions
Config(world="multiregion", region_noise_levels=(0.0, 0.2, 0.4, 0.6))  # 4 regions
```

Measured: [episode 0031](https://github.com/impire-io/poseres/blob/main/hq/04-JOURNEY/0031-the-camping-bill.md).

## pra-rover — the watchable 2D rover world

A 2D rover body of named parts (rays, compass, gps, bump — four sensors
and a drive actuator) on the unchanged engine, with a stdlib live
viewer — install to watching
in under five minutes, one command, zero extra dependencies,
byte-reproducible per seed with the viewer attached. Honest note: the
rover does not navigate — the policy is the pinned random baseline; what
you watch improve is the brain (prediction error falling, the frame
population breathing, best_dim settling).

```bash
pra-rover                 # opens the live viewer; --fps 0 unthrottled, --seed N fresh map
```

Measured: [episode 0020](https://github.com/impire-io/poseres/blob/main/hq/04-JOURNEY/0020-the-watchable-rover-world.md);
it later served as the brain-seeding testbed in
[episode 0044](https://github.com/impire-io/poseres/blob/main/hq/04-JOURNEY/0044-brain-seeding.md).

## The Gymnasium adapter — hundreds of worlds through one seam

Mounts any Gymnasium environment with a discrete action space and a
continuous (Box) observation vector through the existing body seam,
with byte-identical seeded runs. Two honest notes: PRA discards the
environment's reward (motivation is intrinsic — you watch prediction
error fall, not return rise), and when the environment ends its own
episode the world respawns inside PRA's fixed-length episode (counted,
deterministic). Episodic snapshot/resume is exact, conditional on the
environment's own seeded determinism.

```bash
pip install "poseres[gym]"
python examples/cartpole.py       # CartPole: obs_dim 4 / 2 actions, under a minute
```

```python
from pra.anatomy.gymnasium_body import GymnasiumBody

cfg = Config(obs_dim=4, n_actions=2)  # must match the env; the factory checks
Engine(cfg, world_factory=GymnasiumBody.factory("CartPole-v1")).run(seed=1)
```

Measured: [episode 0019](https://github.com/impire-io/poseres/blob/main/hq/04-JOURNEY/0019-the-gymnasium-adapter.md);
snapshot exactness in
[episode 0023](https://github.com/impire-io/poseres/blob/main/hq/04-JOURNEY/0023-snapshot-completeness.md).

## The Minecraft body — the C1 showcase world

A small self-hosted Minecraft server reached through a mineflayer
bridge speaking the `pra-mc/1` protocol — a transport for the same
declared-anatomy seam the ROS2 adapter built, proven by a live
contract check against the real server (nothing is faked — no fake
bridge exists to develop
against it). The body senses properties and appearance signatures
rather than hand-named object classes, holds digging as an intention
with sensed progress, and exposes crafting as a ladder of one-step
primitives. The measured record, stated plainly: live learning is real
(prediction error 0.50 → 0.10 over 1,960 steps on the real stack, exact
resume after a hard kill), drives alone make contact with the crafting
mechanism but assemble no sequences (zero logs held in 328k
frontier-alone steps), and the project's only deliberate crafting
chains to date came from a goal-biased experiment whose own gate FAILed
— emergence in the long run is the open question the live run watches.

```bash
examples/minecraft/up.sh          # world + NATS + bridge + dash + brain, one command
```

```python
from pra.anatomy.minecraft import MinecraftTransport, c1_anatomy
from pra.anatomy.ros2 import Ros2Body

sensors, actuators = c1_anatomy()
factory = Ros2Body.factory(sensors, actuators, transport=MinecraftTransport)
# full wiring (config, snapshots, NATS): examples/minecraft/run_c1.py
```

Measured: [episode 0043](https://github.com/impire-io/poseres/blob/main/hq/04-JOURNEY/0043-the-brain-moves-into-minecraft.md)
(built to launch-ready), body evolution in episodes
[0049](https://github.com/impire-io/poseres/blob/main/hq/04-JOURNEY/0049-the-builders-body.md),
[0050](https://github.com/impire-io/poseres/blob/main/hq/04-JOURNEY/0050-the-ladder-not-the-button.md)
and [0052](https://github.com/impire-io/poseres/blob/main/hq/04-JOURNEY/0052-senses-without-my-ontology.md),
the live-run record in episodes
[0053](https://github.com/impire-io/poseres/blob/main/hq/04-JOURNEY/0053-the-brain-that-preferred-to-stand-still.md)–[0055](https://github.com/impire-io/poseres/blob/main/hq/04-JOURNEY/0055-the-first-deliberate-chains.md).

## Writing your own

The gallery above is the shipped set, not a catalogue of what is
possible: anything that emits observation vectors and accepts actions
can mount through the `Sensor`/`Actuator` protocols (three methods
each) or the `EventSource` seam. The
[getting-started guide](getting-started.md) walks through both, and new
worlds and bodies are the project's natural contribution surface.
