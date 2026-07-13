# Quickstart: Multi-Stream Experience

## K explorers, one brain

```python
from pra.config import Config
from pra.core.engine import Engine

cfg = Config(n_streams=4)          # four instances of the same world,
summary = Engine(cfg).run(seed=1)  # four explorers, one brain
```

All four world instances share one hidden structure (the run seed builds
it once); each is explored by its own deterministically-seeded action
stream; every observation feeds the single frame population in a fixed
round-robin of episodes. Same seed → byte-identical summary, at any K.

## With continuous worlds (the interesting case)

```python
cfg = Config(n_streams=4, episode_mode="continuous")
Engine(cfg, world_factory=my_world_factory).run(seed=1)
```

Each stream boots its world exactly once and wanders independently — four
positions in the same world, merged into one brain. In episodic mode
streams are statistically near-identical (every episode resets anyway —
the pre-registered null); continuous mode is where multi-stream
experience genuinely differs.

## What to expect

- `n_streams=1` (default) is byte-identical to the validated build.
- Consolidation cadence counts *total* experience: a K-stream run and a
  single-stream run of the same schedule consolidate at the same
  experience milestones — so comparisons across K are equal-experience by
  construction.
- Snapshots with `n_streams > 1` fail loudly at configuration time:
  multi-stream capture is ROADMAP B5's work, by design.
- The measured comparison (K ∈ {1, 2, 4} vs the single-stream baseline,
  noninferiority bar) lives in `specs/009-multi-stream/reading.md`.
