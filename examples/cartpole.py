"""CartPole meets PRA — the worked Gymnasium example (ROADMAP B2).

This is a newcomer's second stop, after GETTING-STARTED.md. It mounts a world
you already know (Gymnasium's CartPole) as a PRA body, runs the unchanged
engine on it, and proves the run reproduces byte-for-byte. Total time: well
under a minute.

Run it:

    pip install "poseres[gym]"          # once — core + gymnasium
    python examples/cartpole.py

Three things to know before reading the output, because PRA is *not* an RL
agent and this example would mislead you otherwise:

1. **The reward is discarded.** PRA has no reward channel. Its motivation is
   intrinsic (a fixed drive; see design doc 05), and under this default
   config the policy is the pinned random baseline — the brain here learns to
   *predict* the world, not to balance the pole. What you watch is
   prediction error falling, not return rising.

2. **Episodes: PRA's are fixed-length, CartPole's end when the pole falls.**
   The adapter resolves that mismatch explicitly: when CartPole says
   "terminated", the world is immediately respawned (a fresh, deterministic
   seeded reset) and the PRA episode keeps going. The respawn transition is
   unpredictable in principle — the brain experiences a teleport — and the
   adapter counts how often that happened (printed below).

3. **Determinism is checked, not claimed.** The same (config, seed) must give
   byte-identical run summaries. This script runs seed 1 twice and compares
   the serialized summaries, so you see the guarantee hold on your machine.
"""

from pra.anatomy.gymnasium_body import GymnasiumBody
from pra.config import Config
from pra.core.engine import Engine

# CartPole-v1 observes 4 numbers (cart position/velocity, pole angle/angular
# velocity) and accepts 2 actions (push left / push right). The config must
# declare the same sizes — the factory checks and refuses a mismatch, because
# PRA's scale rules key off obs_dim. Everything else is the validated
# reference configuration.
config = Config(obs_dim=4, n_actions=2)

# `factory` returns a world factory for the engine: each run builds a fresh
# CartPole, wrapped as a Body (sensors -> one observation vector, actuators ->
# one action index). Per-reset seeds derive from the run seed — the engine's
# own random stream is never touched.
cartpole = GymnasiumBody.factory("CartPole-v1")

# Keep a handle on the mounted body so we can read its respawn counter after
# the run. (The engine itself never sees these counters — the learning system
# only ever sees observation vectors.)
mounted = []


def factory(cfg, rng):
    body = cartpole(cfg, rng)
    mounted.append(body)
    return body


print("Running the engine on CartPole-v1 (seed 1, reference schedule) ...")
summary = Engine(config, world_factory=factory).run(seed=1)
body = mounted[0]

# --- what happened, in plain language -------------------------------------
# pred_error_early/late: mean prediction error near the start vs the end of
# the run — falling error is the brain finding structure. population: how
# many competing predictive frames survived the ecology. respawns: how often
# the pole fell and the world respawned mid-episode (see note 2 above).
print()
print(f"  observation steps:     {summary.observation_steps}")
print(f"  prediction error:      {summary.pred_error_early:.4f} early")
print(f"                     ->  {summary.pred_error_late:.4f} late")
print(f"  surviving frames:      {summary.final_population}")
print(f"  best frame dimension:  {summary.best_dim}")
print(f"  pole falls (respawns): {body.respawns} across {body.resets} world resets")

# --- the determinism check --------------------------------------------------
print()
print("Re-running seed 1 to verify byte-identical reproduction ...")
again = Engine(config, world_factory=cartpole).run(seed=1)
identical = summary.serialize() == again.serialize()
print(f"  byte-identical: {identical}")
if not identical:
    raise SystemExit("determinism violated — please report this as a bug")

print()
print("Next steps: swap in any Discrete-action, Box-observation Gymnasium")
print("environment via GymnasiumBody.factory(<env id>), match Config sizes,")
print("and see specs/007-gymnasium-adapter/quickstart.md for the details.")
