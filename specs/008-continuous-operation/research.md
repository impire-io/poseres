# Research: Continuous Operation

Phase 0 of `plan.md` — **the written design the roadmap demanded before
any implementation** (FR-006). Decision / rationale / alternatives, each
traced to a requirement or a working rule.

## R1 — Mode surface: one config field, engine-owned semantics

**Decision.** `Config.episode_mode: "episodic" | "continuous"`, default
`"episodic"` (the pinned validated behavior, byte-identical). The engine
owns the semantics: in continuous mode it calls `world.reset()` exactly
once (the boot) and never again — the single-boot guarantee is engine
code, not world convention (FR-001).

**Rationale.** The mode must travel in snapshots (the config-in-force,
Doc 06 §2) and be visible to validation; an explicit field does both.
Engine-side enforcement makes the guarantee testable against a world that
*cannot* reset (FR-007) rather than hoping implementations behave.

**Alternatives considered.** World duck-typing (`hasattr(world,
'reset')`) — rejected: invisible in config and snapshots, and a world
that *can* reset but shouldn't (a persistent service you legitimately
could re-login) gets no say. A per-world declaration — rejected: the
mode is a property of the *run*, not the world (any resettable world can
run unbroken; US1 edge case).

## R2 — Virtual-episode mechanics: the one-line difference

**Decision.** The engine's episode loop changes in exactly one place. In
episodic mode an episode begins `obs = world.reset()`; in continuous mode
it begins `obs = pending` — the observation the world produced last —
with the boot supplying the very first `pending`. Everything else in the
loop is untouched: `prev_obs`/`prev_a` start `None` (the transition-chain
break), the step index `t` restarts (the fair-judge window
`t < score_window_steps`), and `steps_per_episode` bounds the span.

**Why this preserves every validated mechanism, mechanism by mechanism
(SC-004):**

| mechanism | keyed on | continuous-mode placement |
|---|---|---|
| transition-chain break | `prev_obs = None` at span start | identical — virtual boundary |
| weight-norm-cap projection | the store projects when `prev_obs is None` (frame kernel, LONGEVITY rule) | identical — fires at virtual boundaries with zero store changes |
| fair judge (`score_window_steps`) | within-episode index `t` | identical — window restarts at virtual boundaries |
| warmup | episode count | identical — counts virtual episodes |
| youth protection / cycles | offline-cycle count | untouched — cycles are episode-count-keyed, not reset-keyed |
| C4 snapshot safe points | end of offline cycle | untouched |

**The stream is gap-free and duplication-free (FR-004)** by construction:
in the episodic loop, the final `world.step` of each episode produces an
observation that is *discarded* (the episode ends before processing it).
In continuous mode that trailing observation becomes the next span's
first observation — nothing is synthesized, skipped, or double-processed.
The *only* behavioral difference between the modes is the absence of the
world's state jump; everything downstream of the world is bit-comparable
machinery.

**Alternatives considered.** Carrying the transition chain across
virtual boundaries — rejected for this feature (spec Assumptions): every
boundary mechanism keys off the chain break, so carrying it across would
change the meaning of the scoring window, the cap trigger, and the
first-step training in one silent move; the cost of the break (one
untrained transition per span, 1/40 at reference) is small and stated. A
separate `virtual_episode_steps` dial — rejected: the mechanisms were
validated at `steps_per_episode`; a new dial is future work if a
deployment demands it.

## R3 — What consolidation boundaries mean without resets (FR-006 q1)

**Decision.** Nothing about consolidation changes. Offline cycles were
never reset-keyed: they run every `episodes_per_cycle` episodes and do
frame-population work (spawn, evict, resize, snapshot). In continuous
mode "every N episodes" becomes "every N virtual episodes" = every
`N × steps_per_episode` observations — consolidation becomes purely a
*cadence in experience*, which is what it always was underneath. The
design makes this explicit rather than incidental: **the slow loop is a
rhythm of the brain, not of the world.**

**Rationale.** This is the honest reading of the validated system:
inspection shows no consolidation mechanism reads world state or reset
events. Making the statement explicit (and testing boundary positions,
SC-004) prevents the meaning from drifting later.

## R4 — The reproducibility story (FR-006 q2)

**Decision.** Three tiers, each stated:
1. **Episodic modes**: byte-frozen, untouched (FR-002) — the existing
   guard tests remain the proof.
2. **Continuous re-run**: deterministic per (config, seed) — same
   summary bytes, worker-invariant. Same argument as every mode: one
   seeded generator, fixed draw order; the mode adds no draws and removes
   none (the boot consumes exactly what the first reset consumed).
3. **Continuous snapshot/resume**: exact **iff the world captures
   state** (R5). Episodic resume never needed world state because every
   episode re-derived the world from the generator; continuous resume
   breaks that assumption — surfaced by this design, answered by R5,
   amended into the spec openly (FR-005).

## R5 — World-state capture: the optional protocol (FR-005, SC-003)

**Decision.** An optional, duck-typed world protocol (the
`apply_pending_tools` precedent): a world MAY implement
`state_dict() -> dict` / `load_state_dict(state)` covering its **mutable
run state only** (constructed arrays are seed-derived and rebuilt at
boot). The snapshot blob gains an optional `world_state` entry written
only when (a) the run is continuous and (b) the world implements the
protocol; `pending` (the carried observation) rides with it. Decode
tolerates absence (old blobs unchanged; episodic blobs bit-identical —
FR-002). Taking a snapshot in continuous mode on a world without the
protocol **raises at capture time** with a message naming the missing
protocol (FR-005: fail loudly, never a silently unresumable artifact).

In-repo implementations ship with the feature: `SensorimotorWorld`
(mutable state: current latent + object index — two fields) and the
ladder worlds (same, plus occupancy counters on L1 and the distractor
latent on L3). External/hardware worlds cannot capture — that limitation
is ROADMAP B5's named scope, unchanged by this feature.

**Alternatives considered.** Replay-to-resume (re-run the prefix) —
rejected: O(run) resume cost and requires the full action history the
snapshot deliberately doesn't carry. Making the protocol mandatory on
`EventSource` — rejected: breaks every existing world contract for a
need only continuous+snapshot has. Refusing snapshots in continuous mode
entirely — rejected: in-repo worlds can support exact resume trivially,
and long-running continuous deployments are precisely where snapshots
matter most.

## R6 — Single-boot for hardware and services (FR-006 q3, the C2 promise)

**Decision.** *Boot is the world's one chance to prepare* — the semantic
contract C2 was promised: for hardware, `reset()` implements a homing
routine and runs exactly once per run; for a persistent service, it is
the login/attach. The engine guarantees it is called exactly once in
continuous mode (tested against the guard world, R8), so an expensive or
physically meaningful boot is safe by contract, not by hope. Episode
rhythm continues virtually thereafter; the robot never teleports home
again. What boot does is the world's business; *that it happens once* is
the engine's.

## R7 — Composition: drives, bodies, ladder, harness (FR-006 q4)

**Decision.** No special cases anywhere. The mode changes *when
boundaries happen*, not what any subsystem does: drives and policies read
observations and histories that are episode-agnostic already; the Body
delegates `reset` 1:1 (boot passes through to the mounted world exactly
once); ladder worlds run continuously unchanged (L1 occupancy counters
keep counting across the unbroken stream); `run_suite`/ablation arms
compose (the T3 arms' `do_offline=False` path uses the same episode loop)
though no validated claim is made for continuous ablations. The validated
acceptance suite (T1–T7) remains episodic — continuous mode makes no
acceptance claims in this feature beyond its own determinism and
mechanism-placement tests; behavioral readings are investigatory (R9).

## R8 — The reset-less validation world (FR-007)

**Decision.** A test-shipped `SingleBootWorld` wrapper: wraps any
`EventSource`, permits exactly one `reset()`, raises `RuntimeError` on
any second call, and counts boots for assertions. Engine tests run
continuous mode over `SingleBootWorld(SensorimotorWorld)` for the full
schedule — the run completing at all *is* the single-boot proof, and the
boot counter makes it explicit. Lives with the tests (it is an
instrument, not a user artifact); the public example of "a world that
cannot restart" in docs is the concept, not this class.

## R9 — The investigatory reading (FR-008)

**Decision.** Same world (reference, `true_dim=3, obs_dim=10`), same 8
seeds, standard schedule, pinned random policy; episodic vs continuous;
per-seed improvement, `best_dim`, final population, side by side with
spreads. Recorded in `specs/008-continuous-operation/reading.md`,
labeled investigatory, whichever way it lands. Pre-registered
expectation, stated before running: continuous runs lose the per-episode
re-draw of the start state (less start-state diversity, the latent
wanders far from the origin as variance accumulates step by step) and the
tanh emission saturates as `‖latent‖` grows — so *some* degradation of
improvement is plausible and would be a finding about worlds that drift,
not a defect of the mode; structure size should be less affected. The
reading exists to replace this guess with numbers.

## R10 — What this feature deliberately does not do

Real-time/wall-clock operation (arrives with C2; everything here is
steppable simulated time); multi-stream experience (B4); external-world
state capture (B5); a carry-across-transitions dial or a separate
virtual-episode-length dial (future, if a deployment demands them);
continuous-mode acceptance criteria beyond determinism and mechanism
placement (the suite stays episodic — new claims need their own measured
criteria, the ladder discipline).
