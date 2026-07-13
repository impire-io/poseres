# Proposed shared-doc edits — feature 007 (merge-time integration)

The shared narrative files (`GETTING-STARTED.md`, `README.md`, `ROADMAP.md`)
are not edited on this branch (parallel-work discipline). Apply the edits
below at merge time; each is anchored to current text.

## GETTING-STARTED.md

**1. §4 ("Hook things up: the Body") — add a subsection after "Growing the
body mid-run":**

```markdown
### Already have a Gymnasium environment?

Skip the protocols entirely: the Gymnasium adapter mounts any environment
with a discrete action space and a continuous (Box) observation vector —
CartPole is obs_dim 4 / 2 actions, inside the validated range:

​```bash
pip install "poseres[gym]"
python examples/cartpole.py     # the worked example — under a minute
​```

​```python
from pra.anatomy.gymnasium_body import GymnasiumBody

cfg = Config(obs_dim=4, n_actions=2)    # must match the env; the factory checks
Engine(cfg, world_factory=GymnasiumBody.factory("CartPole-v1")).run(seed=1)
​```

Two honest notes: PRA discards the environment's reward (motivation is
intrinsic — you watch prediction error fall, not return rise), and when the
environment ends its own episode the world *respawns* inside PRA's
fixed-length episode (deterministic seeded reset, counted on
`body.respawns`). Details and scope: `specs/007-gymnasium-adapter/quickstart.md`.
```

(Strip the zero-width escapes on the inner code fences when applying.)

**2. §7 ("What PRA does not do yet") — amend the connectors clause.**

Current text (line ~205):

> and no pre-built connectors to cameras/robots/APIs — the Sensor/Actuator
> protocols above are the integration surface.

Proposed replacement:

> and one pre-built connector so far — the Gymnasium adapter (§4); for
> cameras/robots/APIs the Sensor/Actuator protocols above are the
> integration surface.

**3. §6 (snapshots) — optional, add after the "Known edge" sentence:**

> Snapshots of Gymnasium-mounted runs are also not yet supported — external
> environment state cannot be re-derived from the seed stream (see the
> roadmap's B5).

## README.md

**Layout block (line ~72)** — extend the `anatomy/` line and add
`examples/`:

```
  anatomy/             # body: sensors/actuators, composition, tools + the Gymnasium adapter
examples/              # worked examples (CartPole through the Gymnasium adapter)
```

If the README carries a feature list at merge time, one bullet:

> **Gymnasium adapter** — mount any Discrete-action/Box-observation
> environment (`pip install "poseres[gym]"`, `examples/cartpole.py`);
> deterministic seeded runs, explicit respawn-on-termination semantics.

## ROADMAP.md

**B2 section** — mark done in the house style, keeping the criterion text:

```markdown
### B2. The Gymnasium adapter — ✅ done (JOURNEY.md ch. N)
A `GymnasiumBody` (optional dependency) mounts any Gymnasium environment
with a discrete action space and Box observations behind the existing body
seam. The episode-termination mismatch is resolved explicitly: immediate
seeded respawn inside the fixed-length PRA episode, terminal observation
discarded, respawns counted (the boundary is honestly unpredictable —
and shrinks with competence).
*Exit criterion met:* CartPole worked example in `examples/` (runs the
reference schedule in ~3 s/seed, proves its own byte-identity); adapter
contract tests cover conformance, every rejection path, and the respawn
mechanics; the termination decision is documented with rejected
alternatives (specs/007-gymnasium-adapter/research.md R2). Deferred with
owners: Box actions (future), reward-as-sensor (future), episode
semantics (B3), external-world snapshots (B5).
```

**Phase B intro sentence** ("B1 and B2 need no Phase A results and can start
immediately") — adjust to reflect B2 done, e.g. "B1 needs no Phase A
results; B2 is done."

**Sequencing summary** (bottom) — "with B1/B2 startable immediately in
parallel" → "with B1 startable immediately (B2 done)".

## CLAUDE.md (SPECKIT pointer)

Only if this merge advances the "current plan" pointer:
`specs/004-anatomy-body/plan.md` → leave as the maintainer prefers; this
feature does not change the tech stack.
