# Research: Multi-Stream Experience

Phase 0 of `plan.md` — the written design (FR-006). Decision / rationale /
alternatives.

## R1 — Randomness ownership: stream draws vs brain draws

**Decision.** Two kinds of generators, split by what the randomness
belongs to:
- **Brain generator** (the run's existing rng, seeded by the run seed):
  births, proposals, frame initialization, decay — everything that
  mutates the shared population. Consumed in merge order (deterministic
  because the merge is fixed, R3).
- **Stream generators** (one per stream, derived from the run seed via
  spawn keys — the feature-007 precedent): the stream's world noise and
  its policy draws (ε-gates, random actions). This is the roadmap's
  "per-stream seeds" named explicitly.

At K=1 none of this machinery exists: the single-stream path is the
untouched validated code (one generator for everything), byte-identical
by construction.

**Alternatives considered.** One shared generator for all streams —
rejected: any change in one stream's step count would shift every other
stream's draws (fragile, and worker-parallel world stepping later would
be impossible). Per-stream brain generators — rejected: the population is
one brain; its draws must have one deterministic order.

## R2 — Same world, K explorers: construction sharing by identical seeds

**Decision.** Every stream's world is constructed from an **identically
seeded** generator (the same construction draws → the same hidden
structure, emissions, actions — for any world built from its generator,
including bodies and ladder worlds, with zero world-side changes), after
which each stream's generator state is **overwritten** with its
per-stream stream (the Doc 06 restore-over-reconstruct pattern) so that
per-step noise and exploration diverge. One structure per run seed, K
independent explorations of it.

**Rationale.** This is the deployment story (N copies of one game; a
fleet in one room type), the only form under which "discovered structure"
keeps a single ground truth, and it needs no new world protocol — it
works for every existing `EventSource` today.

**Alternatives considered.** One shared world *instance* — rejected:
within-episode state collides across streams. A world-side `fork()`
protocol — rejected: a new contract on every world for something seeding
already provides. Different worlds per stream — rejected as out of scope
(multi-task learning, a different research question; spec Assumptions).

## R3 — The merge: round-robin episodes; cadence in total experience

**Decision.** The merged run is a single sequence of episodes; episode
`e` belongs to stream `e mod K`. Consolidation fires every
`episodes_per_cycle` episodes **of the merged sequence** and warmup
counts merged episodes — the cadence is in *total experience*,
mode-invariant (the feature-008 lesson made load-bearing): K-stream and
single-stream runs of the same schedule have identical total experience
and identical consolidation positions. At K=1 the schedule degenerates to
exactly today's.

**Consequences, stated:** each stream contributes ~1/K of the episodes;
every within-episode mechanism (transition chain, fair-judge window,
norm-cap projection at episode start) is episode-local and therefore
stream-local for free; the *only* regime change is which world state the
next episode continues from — which leads to R4.

**Alternatives considered.** Step-granular interleaving — rejected for
v1: it breaks within-episode locality of every validated mechanism for
no research gain the episode-granular form can't deliver (finer merges
are a future dial). Per-stream cadence (consolidate every
`episodes_per_cycle` *per stream*) — rejected: K-stream runs would
consolidate K× less often per observation, confounding the exit
comparison.

## R4 — The pre-registered null, and where the regime really changes

**Stated before any measurement.** In **episodic** mode on the reference
world under the random policy, stream identity is *nearly invisible*:
every episode starts with a world reset regardless of stream, so the
merged experience is statistically the same experience — the differences
reduce to which generator drew the noise. The exit measurement on this
configuration is therefore the **null case**, and the pre-registered
expectation is noninferiority holding comfortably: it validates that the
merge machinery does no harm, which is exactly what "matches the
baseline" means.

The regime genuinely changes in **continuous** mode (feature 008): K
explorers occupy K *different positions* of the same world and their
streams are not exchangeable. That is where multi-stream experience
earns its keep or doesn't — recorded as a secondary investigatory reading
on the bounded rover world (the continuous-healthy world from the 008
reading), K ∈ {1, 4}, seeds 1–3.

## R5 — The exit protocol (pre-registered bar)

Reference world, standard schedule and seeds (1–8), pinned random
policy, K ∈ {1, 2, 4}; total experience equal across K by construction
(R3); per-seed paired margins `improvement(K) − improvement(1)` (same
seed → same world structure across arms: perfectly paired).
**Bar (the T7 noninferiority precedent, the roadmap's "matches or
beats"):** per K, mean margin ≥ −1.9·SE (one-sided). `best_dim` and
population spreads recorded alongside. Judged and recorded in
`reading.md` whichever way it lands; the continuous-rover reading (R4)
is investigatory, no bar.

## R6 — Composition and the snapshot scope cut

- **Continuous mode**: composes per stream — each stream boots its world
  exactly once (K single-boot guarantees) and carries its own trailing
  observation. Episodic and continuous multi-stream are both
  deterministic.
- **Drives**: brain bookkeeping (error history, observation memory) is
  shared — the brain's own experience is the merged stream; each policy
  decision uses the acting stream's observation and generator. No
  directed-policy claims in this feature.
- **Snapshots**: **loud failure for K > 1 in v1** (FR-009's second
  branch): exact capture needs K stream-generator states plus K world
  states — real format work that belongs to B5 (*snapshot
  completeness*), where it joins the two already-deferred snapshot gaps
  (anatomy-resized runs from 003, external-state worlds from 008).
  Attempting `snapshot_every_n_cycles > 0` with `n_streams > 1` raises at
  run start, naming B5. K=1 snapshots are untouched.

## R7 — Config surface and validation

`Config.n_streams: int = 1` (≥ 1; byte-identical default). No other
dials: the merge order, seeding scheme, and cadence are semantics, not
knobs. Validation additionally rejects `n_streams > 1` with
`snapshot_every_n_cycles > 0` (R6) at configuration time when both are
knowable, else at run start.

## R8 — What this feature deliberately does not do

Thread/process parallelism inside one run (the merge order is the
semantics; wall-clock wins come from world-side stepping in real
deployments and, later, the external bus backend of the
distributed-operation horizon); multi-task streams; directed policies
under K streams (future research on this instrument); multi-stream
snapshot capture (B5); external bus backends (the Doc 02 seam's later
population — this feature is the *semantics* that backend will carry).
