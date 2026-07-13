# Proposed JOURNEY.md chapter — feature 007 (merge-time integration)

This branch runs parallel to other work, so `JOURNEY.md` is not edited here
(merge-conflict discipline). At merge: append the chapter below with the next
free chapter number, and fold the one-sentence addition into "Where things
stand".

---

## Chapter N — Feature 007: the Gymnasium adapter — hundreds of worlds through one seam (2026-07-13)

ROADMAP B2 asked for a small thing with one hard question inside it: mount
any Gymnasium environment as a PRA body (~50 lines of adapter), and resolve
the episode mismatch — PRA episodes are fixed-length, Gymnasium episodes end
themselves — *explicitly*. Built as a pure leaf: `GymnasiumWorld` (an
`EventSource` over `gymnasium.Env` — Discrete actions, Box observations
flattened C-order to float64, reward and termination flags never crossing
the seam) composed through the **existing** `WorldSensor`/`WorldActuator`
pair into `GymnasiumBody` — the feature-004 pattern replayed, and the 004
world-through-body byte-equivalence replayed with it (tested: body-mounted ≡
direct-mounted, byte-identical). Zero engine, config, or harness edits; the
dependency is a new `gym` extra (and lives in `dev`, so the gate runs the
adapter tests always — none skipped).

The termination decision: **immediate seeded respawn**. On
`terminated`/`truncated` the adapter reseeds and resets mid-step, returns
the fresh observation as the step's outcome, discards the terminal
observation, and counts the respawn. The consequence is documented rather
than hidden: the boundary transition is irreducibly unpredictable — the
ladder's unlearnable-region property, localized at episode boundaries — and
it is *competence-dependent* (a policy that keeps the pole up respawns
less), so the noise floor shrinks as mastery grows. The alternatives died on
honesty grounds: Gymnasium-1.0-style delayed autoreset silently voids one
action per boundary (a false action→outcome pairing is worse than an honest
teleport), and freezing until the PRA episode ends would feed mostly-frozen
episodes under early random policies (CartPole falls in ~20 steps).

Determinism came down to one constraint: the engine's generator must not be
perturbed — a single extra draw at mount would shift every downstream birth
and action in any composed mode. The adapter therefore derives its seed
entropy from a **pure state read** of the run generator (a pure function of
the run seed; verified no-draw) and seeds env reset *k* from
`SeedSequence(E, spawn_key=(k,))`, one counter across episode starts and
respawns. Measured on CartPole-v1: the full reference schedule runs in
~3 s/seed and reproduces byte-identically; under the pinned random policy
the example run respawns 473 times across 13 000 steps (~3.6% of
transitions carry the boundary noise). The worked example
(`examples/cartpole.py`, the newcomer's second stop) prints the honest
summary and *proves* its own determinism by re-running its seed. One honest
non-claim recorded with it: on CartPole under the random baseline, selection
lands at `best_dim` 1 — an observation, not a validated criterion; no
Gymnasium world has acceptance criteria yet, and the example says what the
brain is doing (prediction, not reward-seeking) so nobody mistakes it for an
RL demo.

What it opened: B2's exit criterion is met (worked example, contract tests,
termination decision documented), and the deferrals are named with owners —
Box-action support and reward-as-sensor (future adapter work), engine-side
episode semantics (B3), snapshot/resume of externally-stateful worlds (B5:
a Gymnasium env cannot be re-derived from the seed stream, so v1 documents
the limitation loudly instead of shipping silent divergence). Trail:
`specs/007-gymnasium-adapter/` (spec, research R1–R7, contracts);
`src/pra/anatomy/gymnasium_body.py`; `examples/cartpole.py`; commits
<hashes at merge>.

---

## Proposed "Where things stand" addition (one sentence, slot after the ladder sentence)

**The first external-world adapter is in** (Chapter N): any
Discrete-action/Box-observation Gymnasium environment mounts through the
existing body seam (`GymnasiumBody`, optional `gym` extra) with explicit
respawn-on-termination semantics and byte-identical seeded runs — CartPole
worked example in `examples/`, ROADMAP B2 closed.
