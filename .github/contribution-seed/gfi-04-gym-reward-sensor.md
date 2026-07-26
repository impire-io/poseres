<!--
Title: Gymnasium adapter: opt-in reward-as-sensor (a documented v1 deferral)
Labels: good first issue, new-sensor-actuator, proposal
-->

The Gymnasium adapter discards the environment's reward, openly —
PRA's motivation is intrinsic, and the module docstring of
`src/pra/anatomy/gymnasium_body.py` lists **reward-as-sensor** among
the documented v1 deferrals. This issue is that deferral, done as an
opt-in.

To be precise about what this is *not*: exposing the reward as an
observation channel does not make PRA reward-seeking. The drive never
sees it as value; it becomes one more channel the brain tries to
*predict*. That is still interesting — in CartPole the reward channel
is a constant 1.0 (trivially learnable), in other environments it
carries real structure — and it lets people compare "brain that can
see the reward number" against "brain that cannot" honestly.

## The task

- Add a keyword-only `reward_sensor: bool = False` to
  `GymnasiumBody` (and thread it through
  `GymnasiumBody.factory(...)`). Default off — **byte-identical to
  today when off**; the adapter's determinism tests already pin this.
- When on: compose a second 1-wide sensor after the observation
  sensor (the `Body` takes a sensor list — see how `GymnasiumBody`
  wires `WorldSensor`/`WorldActuator` around `GymnasiumWorld`),
  reading the last reward cached by the world's `step`. `obs_dim`
  grows by 1; `anatomy_meta()` reports the extra group.
- Two semantics need an explicit, documented decision (state your
  choice in the docstring; the maintainer will weigh in on the
  thread — that is why this carries the `proposal` label too):
  1. Before the first `step` (at `reset`): 0.0 is the obvious cache
     value.
  2. On respawn steps: the adapter already discards the terminal
     observation when an episode ends mid-step; the terminal reward
     should follow it, consistently and documentedly.

## Where the seams are

- `src/pra/anatomy/gymnasium_body.py` — `GymnasiumWorld.step` (where
  the reward currently dies), `GymnasiumBody.__init__`/`factory`.
- `src/pra/anatomy/body.py` — the `Sensor` protocol and composition
  rules (order is semantic).
- `tests/contract/test_gymnasium_contract.py` — where the tests live.

`GymnasiumBody` is public surface (Doc 0008), but a *keyword-only
addition* is exactly what the v1.x promise permits in a minor.
Whether the new keyword becomes a *promised* parameter in
`tests/contract/surface_inventory.py` is a maintainer call — raise it
in the PR.

## Acceptance

- Flag off: byte-identical summaries to current behavior (test it,
  not just assert it).
- Flag on: `obs_dim` = env obs width + 1; the reward channel's values
  match what the raw `gymnasium` env returns for the same seeded
  action sequence; respawn semantics match the documented choice;
  runs byte-reproduce per `(config, seed)`.
- Repo gate green, zero skips
  (`./.venv/bin/ruff format --check . && ./.venv/bin/ruff check . && ./.venv/bin/pytest -q`).

## Honest scope

~50 lines of source, ~50 of tests, plus the docstring paragraph that
keeps the honesty note intact (the reward is visible, never
optimized). The code is small; the two semantic decisions are the
actual work, which is why the conversation happens in the open before
the PR hardens.
