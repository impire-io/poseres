# Research: The Gymnasium Adapter

Phase 0 of `plan.md`. Every decision below is stated as
decision / rationale / alternatives, and each traces to a functional
requirement of `spec.md` or a working rule of `AGENTS.md`. Feasibility
was probed in the session scratchpad before planning (per AGENTS.md:
experiments stay out of the repo; conclusions land here): gymnasium
1.3.0 on Python 3.14 — CartPole spaces confirmed (`Box(4,)` float32 /
`Discrete(2)`), seeded resets and rollouts reproduce exactly, zero
warnings under `-W error` (the repo's pytest promotes warnings to
errors), a full reference-schedule engine run on CartPole takes ~3.1 s
and reproduces byte-identically, and random-policy CartPole terminates
~8 times per 200 steps (so the respawn path is exercised constantly, not
theoretically).

## R1 — Adapter shape: an EventSource core, composed by the *existing* sensor/actuator pair

**Decision.** Two classes in one new leaf module
(`src/pra/anatomy/gymnasium_body.py`):

1. `GymnasiumWorld` — an `EventSource` wrapping a `gymnasium.Env`:
   space validation, observation flattening to float64, action-label
   mapping, per-reset seeding, respawn semantics, `resets`/`respawns`
   counters. Usable directly as the Engine's `world_factory` product.
2. `GymnasiumBody(Body)` — the convenience composition: wires
   `WorldSensor` + `WorldActuator` (the existing classes from `body.py`,
   unmodified) around a `GymnasiumWorld`, and offers
   `GymnasiumBody.factory(env_id_or_maker, ...)` returning an
   Engine-ready `world_factory` that validates the config's
   `obs_dim`/`n_actions` against the environment at mount time (FR-007).

**Rationale.** This is Doc 02's own reference pattern, replayed:
`SensorimotorWorld` / `WorldSensor` / `WorldActuator` / `Body`. The
body layer already routes actions, composes observations, enforces
widths, and feeds `WorldSensor` instances on reset — and feature 004's
research R1 *proved* the world-through-body path byte-identical to the
direct connection. Reusing that pair means the Gym-specific logic is
exactly one class (the ROADMAP's "~50 lines of adapter" spirit), the
composition path is already validated, and users get body perks (tool
registration, extra sensors alongside the Gym feed) for free.

**Alternatives considered.** (a) A standalone
`GymnasiumSensor`/`GymnasiumActuator` pair holding the env directly —
rejected: duplicates `WorldSensor`'s caching contract, and `Body.reset`
feeds only `WorldSensor` instances, so a parallel sensor class would
need `Body` edits or override subtleties — core-adjacent churn for zero
capability. (b) `EventSource` only, no Body wrapper — rejected: loses
the documented GETTING-STARTED §4 mounting pattern and mid-run body
growth; the Body costs nothing (004 R1). (c) A Body-only design with no
public `EventSource` core — rejected: the core *is* the adapter; hiding
it would force tests and future composition through the Body
unnecessarily.

## R2 — Termination semantics: immediate seeded respawn (the named B2 design question)

**Decision.** PRA episodes stay fixed-length. When `env.step` reports
`terminated` **or** `truncated`, the adapter immediately calls
`env.reset(seed=<next in sequence>)` and returns the fresh reset
observation as that step's outcome. The terminal observation is
discarded. Each respawn increments a counter readable outside the
learning surface (`body.respawns`). PRA's own episode starts
(`Body.reset`) reset the environment the same way, consuming the next
seed in the same sequence.

**Consequences for learning (documented, not hidden).** The brain
experiences the boundary as an action whose outcome is a teleport to a
fresh start state — an *irreducibly unpredictable* transition, the same
property as the ladder's unlearnable region (L1), localized at episode
boundaries instead of a latent half-space. Under the pinned random
policy on CartPole that is roughly one to two respawns per 40-step PRA
episode (measured: ~8 per 200 steps), i.e. a few percent of transitions
carry irreducible prediction error. Two honest observations follow:
prediction-error readings on self-terminating worlds include this floor
(exactly as L1 runs include region noise — the readings stay honest,
the world is just genuinely harder); and the floor is
*competence-dependent* — a policy that keeps the pole up respawns less,
so the boundary noise shrinks as mastery grows, which is the right
direction for a learning signal to point.

**Alternatives considered.** (a) Gymnasium-1.0-style *delayed* autoreset
(return the terminal observation; the next `step` ignores its action
and returns the reset observation) — rejected: it makes one action per
boundary a silent no-op, corrupting action-conditioned prediction with
a *false* action→outcome pairing, which is worse than an honest teleport;
it also smears one boundary across two steps and would make the
actuator's `apply` semantics inconsistent. (b) End-of-PRA-episode
alignment (freeze or hold the terminal observation until the fixed
episode length runs out) — rejected: under an early random policy
CartPole ends in ~20 steps, so most of every 40-step episode would be
frozen repeats — degenerate experience at scale, and the frozen spans
would poison the survival EMAs that episode structure feeds. (c) End
the PRA episode when the environment ends — rejected: that is an engine
semantics change (episode length drives consolidation cadence, the fair
judge's `score_window_steps`, and every validated schedule constant);
ROADMAP B3 owns engine-side episode semantics, with a written design
first. The adapter conforms the world to the engine — that is what
keeps this feature purely additive.

## R3 — Determinism: a child seed sequence from a pure state read, engine stream untouched

**Decision.** At mount time the adapter derives an entropy value `E`
from the engine's run generator **without drawing from it**: a pure
read of the PCG64 bit-generator state integer
(`rng.bit_generator.state["state"]["state"]`). The Engine calls
`world_factory(cfg, rng)` as its very first act after creating
`rng = np.random.default_rng(seed)`, so `E` is a pure function of the
run seed. Reset `k` (0-based, one counter across PRA episode starts and
respawns alike) seeds the environment with
`int(np.random.SeedSequence(E, spawn_key=(k,)).generate_state(1, dtype=np.uint32)[0])`.
The adapter holds no reference to the engine generator afterwards and
never draws from it. For standalone use (no engine), the constructor
accepts an explicit `seed=` whose value is used as `E` directly;
exactly one of `rng`/`seed` must be supplied. Non-PCG64 generators
(no readable state integer) are rejected with a message directing the
caller to pass `seed=` explicitly.

**Rationale.** The byte-frozen rule makes "no extra draws" absolute: a
single extra draw at mount would shift every subsequent birth weight
and action choice in *any* mode that ever composed with this adapter.
A state read costs nothing and perturbs nothing (verified in the probe:
state identical before/after). `SeedSequence` with `spawn_key` is
numpy's own mechanism for independent, reproducible child streams —
no hand-rolled hashing, and the per-reset index makes the scheme
self-documenting and testable (reset `k`'s seed is a closed-form
function of `(E, k)`). The alternative of passing the run seed twice
(once to the factory, once to `run(seed=...)`) invites silent drift
when the two diverge; deriving from the generator the Engine already
hands the factory keeps one source of truth.

**Alternatives considered.** (a) Draw a seed from the engine generator —
forbidden outright (perturbs the validated stream). (b) Require the
user to close the seed over the factory — rejected as default (duplicate
source of truth; kept possible via `seed=` for standalone/tests).
(c) Reseed only at PRA episode starts and let respawns continue the
env's own stream — workable but weaker: the respawn state would depend
on the full action history, making unit-level reasoning about the seed
scheme harder for no benefit; one counter over all resets is simpler
and equally deterministic. (d) Hash of `repr(state)` — fragile across
numpy versions; the state integer is the stable, documented field.

**Determinism scope (spec Assumption, restated).** The guarantee is
conditional on the Gymnasium API contract: an environment whose
stochasticity flows through its own seeded `np_random` reproduces
exactly; an environment consulting outside randomness breaks its own
reproducibility, not the adapter's. CartPole (fully deterministic
dynamics, seeded start state) reproduces byte-identically end-to-end
(probed).

## R4 — Space support: Discrete actions, Box observations, honest conversion

**Decision.** v1 supports exactly: **action space** `Discrete(n, start)`
— PRA's local action index `i ∈ [0, n)` maps to env action `start + i`;
**observation space** `Box` of any shape/dtype — flattened C-order
(`ravel()`) to float64, declared width = element count. Everything else
is rejected at mount with `AnatomyError` naming the offending space.
The factory additionally validates `cfg.obs_dim`/`cfg.n_actions`
against the environment and reports both numbers on mismatch (FR-007).

**Rationale.** PRA's action surface *is* a discrete index into the
body's actuators (Doc 02 §4); float64 1-D is the frame contract. The
`start` offset costs one addition and removes a real Gymnasium footgun
(spaces that label actions from 1 or −1). C-order flattening is numpy's
default and stated in the module docs, so an image-shaped Box has a
defined, reproducible channel order.

**Alternatives considered.** Binning Box action spaces — a learning-
semantics decision (bin count, ranges) that should be a user's explicit
experiment, not a hidden adapter default; documented as v1 out-of-scope
(spec Assumptions). `gymnasium.spaces.flatten` for Dict/Tuple/Discrete
observations — rejected for v1: it silently one-hot-encodes discrete
members, so the declared width would misrepresent what the channels
mean; honest support needs per-space design, not a blanket cast.

## R5 — Optional dependency: a `gym` extra, `dev` always has it, the error path is tested

**Decision.** `pyproject.toml` gains
`[project.optional-dependencies] gym = ["gymnasium>=1.0"]`, and `dev`
gains `gymnasium>=1.0` so the quality gate always exercises the adapter
tests — **none skipped** (repo rule; no `importorskip` anywhere). The
adapter module imports gymnasium lazily through one internal helper;
when the package is missing the user gets
`ImportError: ... pip install "poseres[gym]"` naming the package and
install command (FR-006). The error path is tested by monkeypatching
the module's import handle to simulate absence — the test suite never
depends on a gymnasium-less environment existing.

**Rationale.** Core stays numpy-only (SC-002); hobbyists who never
mount Gym pay nothing. The dev-extra rule keeps the "all green, none
skipped" gate meaningful: a skipped adapter suite would be a silent
hole exactly where an optional dependency makes bugs likeliest.

**Alternatives considered.** Module-level hard import — a bare
`ModuleNotFoundError` traceback with no install hint, rejected by
FR-006. `pytest.importorskip` — banned by the repo's no-skip rule.

## R6 — The worked example: one file, self-proving, under a minute

**Decision.** `examples/cartpole.py` — a single heavily commented
script: builds the adapter around `CartPole-v1` via
`GymnasiumBody.factory`, runs the engine's reference schedule on seed 1
(~3 s, probed), prints the summary in plain language (early → late
prediction error, population, respawn count), then **runs the same seed
again and prints the byte-identity verdict** — the project's
determinism promise demonstrated, not asserted. Ruff-clean (the
`examples/` directory is inside lint scope deliberately).

**Rationale.** The roadmap exit names the example; GETTING-STARTED is
stop one, this is stop two, so it teaches by the same values the guide
does — honest numbers, reproducibility you can check yourself, comments
that explain *why* (fixed episodes + respawn, why reward is discarded)
rather than narrating the obvious.

**Alternatives considered.** A multi-environment gallery — scope creep
ahead of measurement (no non-CartPole result exists to show honestly).
A CLI subcommand (`pra-validate gym`) — the harness is for validation
instruments with criteria; a worked example is documentation, and
`examples/` is where the roadmap points B1 as well.

## R7 — Named deferrals (documented, with owners)

- **Snapshot/resume of Gymnasium-mounted runs** — not supported in v1:
  the env's internal state is not a pure function of PRA's seed stream
  once actions depend on learned state, so a resumed run would silently
  diverge from the uninterrupted one. Stated in the module docs and
  quickstart; the honest external-world persistence story is ROADMAP
  B5 (the roadmap already names it).
- **Box (continuous) action spaces** — future adapter work (R4).
- **Reward as an optional sensor** — plausible future work; v1 discards
  reward and says so (PRA's motivation is intrinsic and structurally
  immutable, Doc 05).
- **Rendering** — the adapter passes no `render_mode`; a user who wants
  to watch passes their own configured env to `GymnasiumBody`/`factory`.
  Rendering does not affect determinism, only speed; the example keeps
  it off to stay honest about run time.
