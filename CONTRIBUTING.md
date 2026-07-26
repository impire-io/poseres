# Contributing to PRA

PRA is a continuously-learning brain with deliberately clean seams: a
world emits observations and takes actions, a body composes sensors
and actuators, a drive turns experience into value. The seams are
frozen for all of v1.x — see
[Doc 0008](hq/02-DESIGN/0008-public-api-versioning.md), the
public-surface promise, machine-enforced by the surface guard in the
test gate. That freeze exists so that *you* can build on the seams
without them shifting under you.

One honest note up front: this is a research-driven project with a
constitution (`hq/00-GENESIS/constitution.md`), and the rules below
are its articles, not house style. They are short, and none of them
is negotiable.

## What we want

**New worlds, bodies, sensors, actuators, and drives** — against the
frozen public seams. That is the natural on-ramp: the brain is only
as interesting as the worlds it can learn, and every new world,
sensor, or actuator extends what it can be measured against without
touching what is already validated.

**Core changes need a conversation first.** The validated behavior is
byte-frozen (constitution I): every change must keep the T1–T6 suite
under the pinned baseline reproducing its reference values *exactly*,
and new capability must be opt-in — existing modes' RNG stream,
behavior, and serialized summaries untouched. A core PR that arrives
without a prior issue conversation will almost certainly need
reshaping into that form, so have the conversation before writing the
code. Open an issue; the templates ask the right questions.

## How to build one

The seams are small protocols. Read the protocol, then copy a worked
example.

**A world** implements `EventSource`
(`src/pra/world/event_source.py`): `reset()` begins an episode and
returns the first observation, `step(action)` returns the next, plus
`obs_dim` / `n_actions` properties. Two rules matter more than the
protocol itself:

- *Determinism* — draw all randomness from the single
  `np.random.Generator` you are handed, in a fixed documented order,
  so the same `(config, seed)` reproduces byte-identically.
- *Instrument panel* (constitution V) — every new world keeps known
  ground truth, determinism, and steppable time. Hide the ground
  truth from the engine (it sees only `reset`/`step`); expose it
  through a harness-only accessor, as the ladder worlds do with
  `ladder_readings()` and the rover does with `layout()`.

Mount it with `Engine(config, world_factory=your_factory)` where
`your_factory(config, rng)` returns the world — no config or core
change needed. Worked examples: the ladder worlds
(`src/pra/world/ladder.py`, five difficulty axes behind one seam),
the Gymnasium adapter (`src/pra/anatomy/gymnasium_body.py`, with
`examples/cartpole.py` as the walkthrough), and the rover
(`src/pra/examples/rover/world.py`, a full body from named parts).

**A sensor or actuator** implements the `Sensor` / `Actuator`
protocols in `src/pra/anatomy/body.py`: a sensor is
`id()` / `width()` / `read()`, an actuator is
`id()` / `action_count()` / `apply(local_index)` — and `apply`
returns nothing; the only feedback path from an action is subsequent
observations. The `Body` concatenates sensors and unions actuators in
fixed declared order, and that order is semantic: changing it changes
the meaning of every observation dimension. The rover's
`RoverSensor` / `RoverDrive` parts are the pattern to copy.

**A drive** implements the `Drive` protocol in
`src/pra/motivation/drive.py`: `id()` and `value(context)` — a pure
function of a read-only `DriveContext` and its own frozen parameters.
No RNG, no mutable policy state; the running system cannot modify its
own drive. `CuriosityDrive`, `CompetenceDrive`, and `FrontierDrive`
are the three worked examples, each with its mechanism documented in
its docstring. Fair warning: a drive is a claim about what is worth
doing, and claims here get measured — expect the review to ask for
numbers, not intuitions.

## Dev setup

```bash
git clone https://github.com/impire-io/poseres.git
cd poseres
python3 -m venv .venv
./.venv/bin/pip install -e ".[gym]" ruff pytest
```

Use the repo venv (`./.venv/bin/python`) for everything — system
interpreters on most platforms are PEP-668-managed and will fight
you.

## The quality gate

Done means this is green, with nothing skipped:

```bash
./.venv/bin/ruff format --check . && ./.venv/bin/ruff check . && ./.venv/bin/pytest -q
```

- **Zero skips.** A skipped test is a claim the gate cannot check;
  the suite is written so nothing needs skipping (optional
  dependencies are proven through in-repo fakes).
- **Sign your commits.** Every commit in this repository is signed;
  yours too.
- **If your change grows the public surface**, update
  `tests/contract/surface_inventory.py` and Doc 0008 together — the
  surface guard checks them against each other in both directions and
  will fail the gate if they drift.

## Honesty rules for measured claims

Constitution II applies to contributions exactly as it applies to the
maintainer's own work:

- Report **spreads, not bare means** — a mean without its spread is
  not a measurement here.
- **A FAIL is data.** Show it, with the numbers that explain it;
  never tune quietly until green.
- Write pass/fail criteria **before** running the experiment; if a
  criterion proves degenerate, amend it openly with the raw
  measurements recorded.

If your world makes the brain look bad, that is a *finding* — some of
this project's best results started as failures (the journey log is
full of them).

## How work flows

**Features** run the spec-kit flow — spec → plan → tasks → implement
on a numbered branch under `specs/NNN-*/`, with the plan checked
against the constitution; for an external contribution, the proposal
issue is where scope gets agreed and the maintainer handles the repo
ceremony at landing. **Research** never goes through spec-kit — it
runs on pre-registration: the pass/fail bars are written down in
`hq/01-RESEARCH/` *before* any experiment runs, and an abandoned
topic is a result, recorded with the same care as a success.

## Where the story lives

`hq/04-JOURNEY/` is the append-only narrative: one numbered episode
per landed feature, concluded investigation, or load-bearing decision
— including the refuted hypotheses and reversals, because those are
as load-bearing as the shipped code. Read
[`hq/04-JOURNEY/README.md`](hq/04-JOURNEY/README.md) ("Where things
stand") before proposing anything large; there is a fair chance the
idea has a history, and the history says why things are the way they
are.
