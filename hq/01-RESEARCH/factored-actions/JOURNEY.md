# Journey — factored-actions (started 2026-08-21)

## 2026-08-21 — the dial world declared, before the rig

The world implements the kernel's own `EventSource` seam
(`reset()/step(action)`, `pra/world/event_source.py`) — a lab world
in the T-suite tradition, seconds per run, no Minecraft. Declared
mechanics, v1:

- **State:** B dials, each in a position `p ∈ [0, m)`; one standing
  target pattern of B positions. Rungs: (B, m) =
  (3,4) / (8,8) / (16,16) / (32,32) → A = B·m ∈
  {12, 64, 256, 1024}.
- **Act:** flat index `a = d·m + p` = "set dial d to position p";
  deterministic snap. The product structure (dial × position) is the
  declared factorization — the stem × inflection miniature.
- **Observation** (`obs_dim = 3B`): per dial, three channels —
  its position scaled to [−1, 1], the target's position scaled the
  same, and a match flag (±1). At the calibration rung obs_dim = 9,
  beside the validated reference scale (10).
- **Reach:** when all B dials match the target, the target redraws
  (seeded); the redraw is the world's only novelty, so seeking
  matches is drive behavior, not reward — there is no reward wire,
  as everywhere. **Reach rate = redraws per 1,000 steps**, read on
  the back half of a run (the front half is the hungry-born
  transient of this world).
- **Held-out mask (F3):** a seeded 10% of acts is excluded from the
  policy's candidate set for the whole run; at test each is
  force-executed once from matched states and scored on
  first-execution prediction error.
- **Irregulars (F4):** a seeded 10% of acts (disjoint from F3's
  mask) snap dial d to a permuted position π(p) ≠ p — the
  compositional rule broken by exception, the is/was/went miniature.
  Off at calibration; on only in F4 arms.

**Ladder revision, before the rig exists (2026-08-21, same day):**
the declared ladder grew B and m together ((3,4)→(32,32)), which
confounds the axis under test — more dials is a longer assembly
horizon for ANY mechanism, so a reach collapse at A=1024 could be
horizon difficulty wearing the vocabulary's clothes. Revised:
**B = 4 dials at every rung, m ∈ {3, 16, 64, 256}** → A ∈
{12, 64, 256, 1024} exactly, obs_dim = 12 at every rung. Across the
whole ladder the world, the observation, and the task horizon are
identical; the single thing that changes is the size of the act
inventory. The factored anchor becomes `[onehot₄(d); p scaled]`,
dimension 5, constant across rungs. Nothing had run when this
revision landed.

**Calibration phase, declared:** flat at A=12 must first *perform*
on this world — one-step lookahead chasing redraws is not guaranteed
viable, and if flat-12 cannot work the world is miscalibrated, not
the kernel. The world may be revised openly during calibration (each
revision journaled here with its numbers); the moment flat-12
performs, the world config, the per-rung experience budget, and the
F0 parity thresholds freeze in this file, and **no comparison arm
run before that freeze counts** (the registered standing guard).
Machinery for the variant arms (shared transition conditioned on an
action vector; anchors `[structure of d ; scaled p]`; opt-in config;
off bit-exact) gets its own journaled entry when built — before any
variant arm runs.
