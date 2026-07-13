# Research: The Complexity Ladder

Phase 0 of `plan.md`. Every decision below is stated as
decision / rationale / alternatives, and each traces to a functional
requirement of `spec.md` or a working rule of `AGENTS.md`.

## R1 — Non-uniform rung: region-based unlearnable *dynamics*, not noise channels

**Decision.** `NonUniformWorld`: identical to the reference world except
that when the current latent lies inside a configured region, the latent
transition gains fresh Gaussian noise —
`latent ← latent + displacement(action) + ε`, `ε ~ N(0, region_noise_std²)`
per step, drawn only when inside the region. The region is the half-space
`latent[0] > 0` (fixed convention). Emission stays the reference emission
everywhere. Degenerate dial: `region_noise_std = 0` — no extra draws, no
behavioral difference.

**Rationale.** The A4 drive study needs unlearnability that a *policy*
can seek (noisy-TV staring) or avoid (camping) — that requires the
unlearnable thing to be a place the agent's actions move it into and out
of (Doc 05: "worlds with unlearnable regions"; AGENCY-DIAGNOSIS caveat 1).
Channel noise is exposure-constant under every policy and measures
nothing about drives. The half-space along the first latent coordinate is
the simplest region with a known analytic volume share (~½ under the
symmetric start distribution) and natural in/out traffic under the
reference random walk. Transition noise (not emission noise) is the
strongest honest "nothing can learn this" property: the frame's inputs
are clean; what it must predict is irreducibly random.

**Alternatives considered.** (a) Unlearnable observation channels —
rejected: policy-independent exposure, useless for A4 (folded into the
distractor rung's unstructured extreme instead). (b) Noisy-TV *objects*
(some episode-objects unlearnable) — rejected: the object is drawn at
reset, so within an episode the policy cannot change its exposure; the
choice the drive study needs would not exist. (c) Radius-based region
(`‖latent‖ > r`) — workable but its volume share depends on `true_dim`
and drift; the half-space keeps the ground truth constant across scales.

## R2 — Rung 1 readings: occupancy from the world, quality from a paired baseline

**Decision.** Two readings, no core-telemetry changes:
1. **Occupancy** — the world counts its own steps inside/outside the
   region (plain counters, no RNG, never crossing the `EventSource`
   surface); the harness reads them after the run through a
   harness-only accessor.
2. **Structure quality, paired** — the harness runs the same seed on the
   rung world and on its degenerate twin (`region_noise_std = 0`,
   machinery-equal by construction) and reports paired per-seed deltas of
   the existing summary readings (improvement, best_dim).

**Rationale.** The T3SCALE lesson, applied in advance: population-mean
readings compare honestly only when the machinery is identical on both
sides of the comparison — so the baseline is the same world at the
degenerate dial, paired by seed, rather than an analytic floor or a
different world. Occupancy belongs to the world (it owns the ground
truth); counters keep the engine and the learning system ignorant of the
region, preserving FR-001's hiding requirement. No new per-step telemetry
in the recorder, so validated-mode summaries cannot drift (FR-006).

**Alternatives considered.** Per-channel/per-region error decomposition
in the recorder — rejected: invasive telemetry change touching validated
serialization for a reading the paired design gets for free. Post-hoc
frozen evaluation probes (scan-style) — rejected as the primary
instrument: heavier, and measures a frozen copy rather than the live run.

## R3 — Compositional rung: factored dynamics, joint emission, census via snapshots

**Decision.** `CompositionalWorld`: the hidden state is `K` independent
groups with sizes `factor_dims = (d_1, …, d_K)`, `Σ d_k = true_dim`. Each
action's displacement is non-zero **in exactly one group** (actions
assigned round-robin across groups at construction; within-group
displacement drawn as in reference). Start latents and the emission are
the reference draws over the full `true_dim` (one dense emission, tanh,
same normalization) — the *dynamics* are factored, the emission is joint.
Degenerate dial: `factor_dims = (true_dim,)` — one group, every action
moves it, identical draws to reference.

Census reading: the ladder runner snapshots the final state (the Doc 06
persistence seam, already the established census instrument from
PROPOSAL-DIAGNOSIS) and reports the stable frames' dims against
`factor_dims` and `Σ d_k`.

**Rationale.** Factored dynamics with joint emission is the honest form
of "structure made of parts": no channel gives the parts away (a
block-diagonal emission would let channel groups betray the composition),
yet each part is independently controllable — what a parts-discovering
learner could exploit. Round-robin action assignment keeps every group
reachable under the random policy with no new config surface. The
snapshot census avoids any new telemetry.

**Alternatives considered.** Block/additive emission per group —
rejected: leaks composition through channel structure and changes the
emission math relative to reference (breaks the degenerate-dial
byte-identity). Separate per-group observations — that is a *body*
composition (Doc 02 already covers multi-sensor), not a world property.

## R4 — Distractor rung: autonomous drift latent, dial to pure noise

**Decision.** `DistractorWorld`: alongside the reference controllable
structure (`true_dim`), an autonomous latent of size `distractor_dim`
evolves by a **fixed drift vector** drawn at construction
(`z_d ← z_d + drift` every step, action-independent) and emits into
`distractor_channels` extra observation channels through its own tanh
emission. Dial `distractor_mode`: `"structured"` (the drift dynamics —
predictable in principle) or `"noise"` (the distractor channels carry
fresh Gaussian noise each step — the unstructured extreme). Degenerate
dial: `distractor_channels = 0` — no extra construction or per-step
draws; total `obs_dim` = reference `obs_dim`.

**Rationale.** A fixed drift is the simplest deterministic autonomous
process in the world's own vocabulary (displacement steps): predictable
in principle by a frame that spends a dimension on it, yet carrying zero
action information — exactly the "structured but action-irrelevant"
property FR-003 names. The mode dial spans the two real-world nuisance
types (structured dashboards vs sensor static) in one world. The headline
reading needs nothing new: `best_dim` against controllable `true_dim`
(does selection buy dimensions for the distractor?).

**Alternatives considered.** Random-walk distractor (fresh random step
each time) — rejected as the "structured" mode: unpredictable beyond
persistence, so it would be noise wearing a structured label. Linear-map
dynamics (`z ← Az`) — more expressive but adds a stability/conditioning
question the first rung results don't need; drift suffices and stays in
the world's displacement idiom.

## R5 — Selection surface: one `world` config field + a world factory in the harness

**Decision.** `Config` gains `world: str = "reference"` plus the rung
dials, all defaulting to inert values (`region_noise_std = 0.0`,
`factor_dims = ()`, `distractor_channels = 0`, …), with validation per
FR-011 (constraint-naming errors). A factory
(`pra.world.ladder.make_world(cfg, rng)`) maps `world` to the class; the
Engine keeps receiving worlds via the existing `world_factory` parameter
— **no engine changes**. The harness's ladder runner builds the factory;
`Engine(Config())` behavior is untouched because the default `world`
value routes to `SensorimotorWorld` construction with identical draws.

**Rationale.** Config-carried selection keeps snapshots exact (the
config-in-force travels in the snapshot, Doc 06), keeps the CLI surface
declarative (`--config` JSON selects rungs, as every prior instrument
does), and adds zero risk to the validated path (defaults inert;
`test_baseline_unchanged` still guards seed 1 byte-identity).

**Alternatives considered.** Harness-only world selection with no config
field — rejected: snapshots of ladder runs would not know their world,
breaking resume-equivalence; and A4 needs drives *on* ladder worlds
through the normal config path. Subclassing `SensorimotorWorld` publicly
— implementation detail deferred to code; behavior contract is what
matters (degenerate byte-identity, R7).

## R6 — Rung criteria: pre-registered in-repo before results (FR-007)

**Decision.** A normative criteria document,
`design/validate/LADDER-CRITERIA.md`, written and committed **before**
the first recorded results, one section per rung:
- **L1 (non-uniform)**: paired against the degenerate twin per seed —
  quiet-side structure survives (best_dim within 1 of the twin's in a
  strict majority; improvement within a stated factor of the twin's,
  spread reported); occupancy under the random policy reported per seed
  (expected ≈ ½, sanity band stated) — the A4 baseline number.
- **L2 (compositional)**: improvement beats the persistence ablation
  (churn-matched, the T3 amended form) on the compositional world; the
  final census (stable frames' dims) recorded against `factor_dims` and
  `Σ d_k` with the envelope stated up front: which shape wins —
  per-part frames (dims ≈ d_k), monolith (≈ Σ d_k), or price-optimal
  in between — is the research finding, recorded whichever way it lands.
- **L3 (distractor)**: `best_dim` tracks the *controllable* `true_dim`
  (within-1 strict majority at every checkpoint, the T4 horizon rule) in
  structured mode at the stated dials; the same reading in noise mode;
  FAIL recorded as data if selection buys distractor dimensions.

**Rationale.** The T7/T3 precedent is now the house rule: criteria are
written before results, amended openly if they prove degenerate, and a
FAIL is a finding (FR-009). The L2 criterion deliberately does not
pre-judge the parts-vs-monolith outcome — the parsimony finding
(SCORER-DIAGNOSIS: selection is price-optimal, not truth-tracking) makes
the honest prediction genuinely uncertain, which is exactly why the rung
exists.

## R7 — Degenerate-dial byte-identity is a tested contract (FR-012)

**Decision.** For each rung world at its degenerate dial, an integration
test runs the full engine on the rung world and on `SensorimotorWorld`
with the same config/seed and asserts **byte-identical serialized
summaries**. Construction and per-step draw order is documented per rung
and arranged so the degenerate path consumes exactly the reference draw
sequence (extra draws happen only when a dial is non-degenerate, and
always *after* the reference draws at that point, in a documented order).

**Rationale.** "Reduces to the reference family" must mean bytes, not
vibes — the same standard the anatomy layer set (world-through-body ≡
direct world). This also future-proofs every rung against accidental RNG
reordering: the degenerate test pins the draw discipline.

## R8 — Ladder runner and baselines: reuse `run_suite` with a world factory

**Decision.** `run_suite` gains an optional `world_factory` pass-through
(default `None` → unchanged, the same opt-in pattern as
`proposal_factory`), so rung criteria that need ablation baselines (L2's
churn-matched persistence comparison) reuse the exact T3 quartet
machinery on ladder worlds. The ladder runner
(`pra.harness.ladder.run_ladder`) composes per-rung: engine runs across
seeds (workers, seed-order reassembly — the established parallel
pattern), paired-twin runs where the criterion needs them (L1), quartet
arms where needed (L2), the snapshot census (L2), and world-side
occupancy readout (L1). CLI: `pra-validate ladder` with `--rungs
l1,l2,l3`, `--config`, `--json`, `--workers`; investigatory exit code 0
always (FR-009/FR-010); single-seed runs carry the existing
debugging-only banner.

**Rationale.** Every measurement pattern the ladder needs already exists
in the harness (paired runs: T7 and the T3 amendment; quartet:
`scale --t3`; census: Doc 06 snapshots; parallel seeds: everywhere) —
the runner is composition, not invention. One command with one JSON
artifact satisfies FR-010/SC-006.

## R9 — First recorded results: reference-scale dials, pinned random policy

**Decision.** The first ladder results (the roadmap exit's "results
recorded per rung") run at reference-scale observation sizes with the
pinned random policy, 8 seeds, moderate stated dials:
L1 `true_dim=3, obs_dim=10, region_noise_std ∈ {0.5·action_scale,
2·action_scale}` (mild/strong); L2 `factor_dims=(3,3)` and `(2,2,2)`
(`obs_dim` sized by the standard rule); L3 `true_dim=3` plus
`distractor_dim=3` over `distractor_channels=10` extra channels, both
modes. Recorded into `LADDER-CRITERIA.md` result sections (the same
pre-register-then-fill pattern as T3SCALE-DIAGNOSIS), including failures.

**Rationale.** Spec assumption made concrete: first results at the scale
where the reference behavior is validated, so every surprise is
attributable to the rung's one new property rather than to scale rules —
the ladder's whole reason for existing. Scaled-dial ladder runs are
follow-up work once the reference-scale readings exist (and the
scale-rule interaction is a named, reported edge case, not silently
resolved here).
