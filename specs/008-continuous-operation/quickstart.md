# Quickstart: Continuous Operation

## Run any world unbroken

```python
from pra.config import Config
from pra.core.engine import Engine

cfg = Config(episode_mode="continuous")   # one change; everything else as before
summary = Engine(cfg).run(seed=1)
```

The world is booted exactly once (its `reset()` — for hardware a homing
routine, for a service a login) and then experiences one unbroken stream.
Learning rhythm is unchanged: virtual episodes the length of
`steps_per_episode` carry every boundary mechanism (protection windows,
scoring windows, the lifetime cap) exactly where episodic mode puts them.
Runs are byte-reproducible per seed, as always.

## A world that genuinely cannot restart

Your environment object needs `reset()` to mean *boot*, called once —
after that, only `step()`. If restarting is impossible, make `reset()`
raise on a second call; the engine guarantees it never issues one in
continuous mode (that guarantee is tested against exactly such a world).

```python
cfg = Config(episode_mode="continuous", obs_dim=..., n_actions=...)
Engine(cfg, world_factory=my_persistent_world).run(seed=1)
```

Drives, bodies, and ladder worlds compose unchanged — the mode moves
*when boundaries happen*, nothing else.

## Snapshots of continuous runs

Opt-in as always (`snapshot_every_n_cycles > 0` + a store). One extra
rule: in continuous mode the world's own state must travel in the
snapshot, so the world must implement the small capture protocol
(`state_dict`/`load_state_dict` — the in-repo worlds all do). A world
that can't capture raises at snapshot time with a clear message; resume
reproduces the uninterrupted run byte-for-byte on worlds that can.
External services and hardware can't be captured — that's the roadmap's
B5, not this feature.

## The honest reading

`specs/008-continuous-operation/reading.md` records the first
episodic-vs-continuous comparison (same world, same seeds, both modes) —
investigatory, judged by nothing, recorded whichever way it landed.
