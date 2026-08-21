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

## 2026-08-21 — the variant machinery declared, before it is built

The variant lives **rig-side, zero src changes** (the second-body
precedent, stronger here: the frozen suite cannot even see the
machinery). `rig/embed.py`: `EmbeddedFrameGroup(FrameGroup)`
replaces the per-action transition slices `T1 (F,A,H,D)` /
`T2 (F,A,D,H)` with bilinear forms over an action embedding
`e_a ∈ R^E` — `W1e (F,H,D,E)`, `W2e (F,D,H,E)`, biases likewise —
so parameters are O(E), every executed act trains the shared
tensors (the starvation axis under test), and similar acts share
gradients. The store subclass carries the event-head variant the
same way (`(E, obs, obs+1)` instead of `(A, obs, obs+1)`) and the
anchor table `e_a = [onehot₄(d); p scaled]` (E = 5): **frozen** arm
= table constant; **learned** arm = table receives gradient too.
Wiring: the rig rebinds the engine's module-level `FrameStore` name
for variant runs — instrument code, on the trail like every runner.

Declared self-test, built before any variant arm: with **one-hot
anchors (E = A)** the bilinear form reduces exactly to per-action
slice selection, so the embedded machinery must reproduce the flat
kernel's structure — the rig's internal parity check that the new
math is the old math when the embedding carries no structure.
Selection stays exact brute-force argmax (the Doc 06 seam decision:
no index until a profile demands one); F3's mask is a candidate
filter at the policy seam.

**Self-test result [measured]:** PASS — one-hot embedded equals flat
to machine precision after 200 interleaved updates (transition) and
300 (event head), all actions checked.

## 2026-08-21 — THE FREEZE: world, budget, and F0 thresholds, before any comparison arm

Calibration read at m=3 (A=12), 24 seeds each, one budget
[measured]:

| arm | reach/1k back-half: min / median / max | seeds reaching |
|---|---|---|
| flat (curiosity) | 8.308 / **12.615** / 17.077 | 24/24 |
| random floor | 5.385 / **6.923** / 9.385 | 24/24 |

Flat performs: median ≥ 1.5× the random median (12.615 vs 10.385
required) and flat's minimum seed (8.308) clears the random median —
the directed policy's whole distribution sits above the floor's
center. Frames' pred_error_late median 0.6423; populations alive
(median 6). The modest margin is the tiny inventory: at m=3 chance
assembles patterns often; the knowledge component of reach grows
with m, which is the ladder's whole point.

**Frozen, from this line on (no comparison arm before this counts):**

- **World:** the declared dial world v1 with the revised ladder
  (B=4; m ∈ {3, 16, 64, 256}; obs 12; reach = redraw; rejection
  redraw). No further world revision without a journaled amendment.
- **Budget:** 13,000 world steps per run (nominal n_cycles=18; the
  horizon-checkpoint floor of 50 effective cycles — measured
  identical across all 48 calibration runs). Same budget at every
  rung: at A=1024 that is ~12.7 executed acts per flat slice, the
  starvation regime F1 exists to read.
- **F0 parity thresholds (variant arms at m=3, 24 seeds):** PASS iff
  back-half reach median ≥ **10.385** (1.5× random median, the same
  clause flat met), minimum seed > **6.923** (random median, mirror
  of flat's own showing), and frames' pred_error_late median ≤
  **0.803** (1.25× flat's 0.6423).
- **F1 baseline:** flat's own A=12 reach median **12.615** — F1
  requires flat at A=1024 median < **6.31** (0.5×).
- **F2:** a variant at A=1024 retains ≥ 0.8× its own A=12 median.

Arm order, declared: F0 first (m=3 frozen + learned) — no larger
rung runs for a variant until its parity passes; flat's rungs
(m=16, 64, 256) may run any time after this freeze.
