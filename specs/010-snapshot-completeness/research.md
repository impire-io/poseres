# Research: Snapshot Completeness

Phase 0+1 combined (the feature is three well-understood debts; the
design carries the plan). Decision / rationale / alternatives.

## R1 — Grown bodies: record current dims in the population blob

**Decision.** `FrameStore.state_dict()` gains `"obs_dim"`/`"n_actions"`
(the store's *current* dims); the snapshot meta writes a
`"current_dims"` key **only when they differ from the boot config**
(unresized blobs bit-identical — FR-002). `load_state_dict` rebuilds
groups at the recorded dims and restores the store's current dims and
effective scale (the resize bookkeeping of feature 004). On resume the
engine verifies the booted world presents the recorded dims
(`world.obs_dim`/`n_actions` — the Body derives them from its grown
parts) and raises naming the mismatch otherwise.

**Rationale.** Code from the caller, state from the blob — Doc 06's
existing rule: sensors/actuators are code, so the resuming factory
builds the grown anatomy; the blob records and verifies dimensions.
The alternative (serializing tools) was rejected in Doc 06 already.

## R2 — Capture-required worlds: one marker, both modes

**Decision.** A world MAY set `snapshot_needs_state = True` (duck-typed
class attribute). The engine captures `world_state` when the mode is
continuous (feature 008, unchanged) **or** the world declares the
marker; marker-without-protocol raises at run start (loud, before any
artifact). `GymnasiumWorld` sets the marker and implements
`state_dict/load_state_dict` over its reset counter — at C4 safe points
(episode boundaries) the counter fully determines the next reseed, so
episodic Gymnasium resume is exact *given the env's own `reset(seed)`
determinism* (stated in docs; `GymnasiumBody` already delegates capture
per feature 008's instance-attribute pattern).

**Alternatives considered.** Capturing state for every
protocol-implementing world in episodic mode — rejected: reference-world
episodic blobs would change format for no need (world-from-seed already
exact). Documentation-only — rejected: the counter fix is one integer
and turns silent divergence into a real guarantee.

## R3 — Multi-stream: an optional `streams` record

**Decision.** The blob gains an optional `"streams"` meta key (written
only when `n_streams > 1`): the merge position (`episode_index`) and,
per stream, the generator state plus — when continuous or
capture-required — the world state and carried observation. Resume
rebuilds K worlds by identical construction seeding (feature 009),
then restores each stream's generator/world/pending. The feature-009
config-time rejection is lifted; capture requirements apply per stream
world exactly as at K=1.

## R4 — Format discipline

Everything additive-optional, format version stays 1 (the 003/008
precedent): `current_dims` only when resized; `world_state` only when
continuous or marker; `streams` only when K>1. The feature-008
"episodic blobs carry no trace" test generalizes to "unresized, K=1,
derivable-world blobs are bit-identical."

## R5 — The documentation exit artifact

Doc 06 gains **"What snapshots guarantee, per world class"**:
1. *Seed-derivable worlds* (reference family, ladder, rover): exact
   resume, both modes (continuous via capture protocol).
2. *Capture-supporting worlds*: exact resume; continuous mode requires
   the protocol (008).
3. *Capture-required worlds* (Gymnasium): exact resume in episodic mode
   via declared capture, conditional on the environment's own seeded
   determinism — stated; continuous external worlds remain unsupported.
4. *Non-capturable worlds* (hardware, live services): **no snapshot
   guarantee** — capture attempts fail loudly; persistence for such
   deployments means the brain's state, not the world's, and the world
   re-attaches at boot (the 008 single-boot contract).
