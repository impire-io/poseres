<!--
Title: A delayed-echo world — observations that lag actions by k steps
Labels: good first issue, new-world
-->

Every world the brain currently learns emits the consequence of an
action *immediately*: `step(a)` returns the observation that already
reflects `a`. Real sensors lag. A world whose observation echoes the
latent state from `k` steps ago introduces a difficulty axis none of
the existing worlds have — delayed consequences — and it is small
enough to be a first contribution.

## The task

Write a standalone `EventSource` world (suggested home:
`examples/delayed_echo.py` — no `src/` changes needed) with:

- A latent state random-walked by per-action displacement vectors and
  a fixed nonlinear (`tanh`) emission — structurally like the
  reference world (`src/pra/world/event_source.py`, worth reading in
  full first; the module docstring is the determinism contract).
- A `delay: int = k` dial: the observation returned at each step is
  the emission of the latent from `k` steps earlier (keep a bounded
  deque of latents; during the first `k` steps of an episode, emit
  the oldest available). `k = 0` must behave as a plain
  immediate-emission world.
- Determinism: draw *only* from the `np.random.Generator` passed in,
  in a fixed, documented order — same `(config, seed)` must
  byte-reproduce. Put a two-run self-check in `__main__`.
- Ground truth stays hidden from the engine (it sees only
  `reset`/`step`/`obs_dim`/`n_actions`); expose the true delay and
  current latent through a harness-only accessor, the way the ladder
  worlds expose `ladder_readings()` (`src/pra/world/ladder.py`) and
  the rover exposes `layout()`.

Mount it without touching config or core:

```python
engine = Engine(config, world_factory=lambda cfg, rng: DelayedEchoWorld(cfg, rng, delay=3))
```

## What becomes measurable

The one-step curiosity lookahead implicitly assumes actions have
immediate observable consequences. With `k > 0` that assumption is
false in a controlled, dose-adjustable way — how prediction error and
`best_dim` respond to increasing `k` is a real question nobody has
measured here. You do not have to answer it to land the world; you do
have to keep the ground truth accessible so someone can.

## Acceptance

- Satisfies the `EventSource` protocol (`isinstance(world, EventSource)`
  — it is `runtime_checkable`).
- Two runs at the same `(config, seed)` produce byte-identical
  serialized engine summaries; the script proves it.
- `k = 0` and `k > 0` both run under the unchanged engine.
- Repo gate green
  (`./.venv/bin/ruff format --check . && ./.venv/bin/ruff check . && ./.venv/bin/pytest -q`).

## Honest scope

~100–150 lines plus the self-check. The delicate part is the
draw-order documentation and the first-`k`-steps semantics — decide
them, write them down in the module docstring, and keep them. If you
would rather land it inside `src/pra/world/` with contract tests,
say so in the thread first; that is a bigger PR (surface questions
apply) and entirely optional.
