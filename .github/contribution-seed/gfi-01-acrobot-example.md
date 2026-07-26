<!--
Title: A second Gymnasium worked example: Acrobot-v1
Labels: good first issue, new-world
-->

`examples/cartpole.py` is the repository's worked Gymnasium example:
mount an environment you already know as a PRA body, run the
unchanged engine, prove byte-reproducibility. One example proves the
adapter works; a second, on an environment with a different episode
character, proves it *generalizes* — and gives readers a telemetry
contrast worth staring at.

## The task

Write `examples/acrobot.py`, modeled directly on
`examples/cartpole.py`, mounting Gymnasium's `Acrobot-v1`:

- Observation: `Box` of width 6 (`cos`/`sin` of both joint angles +
  two angular velocities) → `Config(obs_dim=6, n_actions=3)`.
- Actions: `Discrete(3)` (torque −1 / 0 / +1) — inside the adapter's
  v1 scope (Discrete actions, Box observations).
- Use `GymnasiumBody.factory("Acrobot-v1")` as the engine's
  `world_factory`, exactly like the CartPole script.

The interesting contrast to write up in the script's docstring:
CartPole under a random policy *terminates constantly* (the pole
falls), so the run is dense with respawn teleports; Acrobot under a
random policy almost never reaches its goal and instead truncates at
500 steps, so respawns are rare and the observation stream is long
and continuous — and the observation manifold is a torus embedding
(two cos/sin pairs), a genuinely curved structure for frames to
discover. Print the respawn count next to CartPole's so the contrast
is a number, not a claim.

## Where the seams are

- `src/pra/anatomy/gymnasium_body.py` — the adapter (read the module
  docstring: respawn semantics, determinism, what never crosses the
  seam).
- `examples/cartpole.py` — the model to copy, including its honest
  framing (the reward is discarded; PRA predicts, it does not
  balance).

## Acceptance

- The script runs with `pip install "poseres[gym]"` and nothing else
  (Acrobot is in Gymnasium's base classic-control set).
- It runs one seed twice and asserts the serialized summaries are
  byte-identical, like the CartPole script does.
- No `src/` changes at all; the repo gate stays green
  (`./.venv/bin/ruff format --check . && ./.venv/bin/ruff check . && ./.venv/bin/pytest -q`).

## Honest scope

One file, ~80 lines of which most are prose comments. No new APIs, no
tests beyond the script's own self-check. A comfortable first PR: the
hard part is writing the docstring honestly, not the code.
