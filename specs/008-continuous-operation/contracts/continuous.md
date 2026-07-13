# Contracts: Continuous Operation

The binding promises of feature 008. Every MUST maps to a functional
requirement in `spec.md`; every contract has a test.

## 1. Mode contract

- `Config(episode_mode="episodic")` — the default — MUST leave every
  existing mode's behavior, RNG stream, and serialized summaries
  byte-identical to the validated build (FR-002; guarded by the frozen
  baseline suite and a mode-default equivalence test).
- `Config(episode_mode="continuous")` MUST run any `EventSource` world
  unbroken: `reset()` called exactly once per run (the boot), never
  again — enforced by the engine and proven against a world that raises
  on a second call (FR-001, FR-007).
- Validation MUST reject unknown `episode_mode` values with a
  constraint-naming message (FR-009).

## 2. Stream contract

- Virtual episodes are exactly `steps_per_episode` steps; the trailing
  observation of each span is the first observation of the next — no
  gaps, no duplication, no synthetic observations (FR-004; tested by
  observation accounting against the world's own production count).
- At every virtual boundary, and nowhere else: the transition chain
  breaks, the fair-judge window restarts, and the lifetime-cap projection
  triggers — the same placements episodic mode produces at real
  boundaries (FR-003, SC-004; boundary-position tests).
- Warmup counts virtual episodes; consolidation runs every
  `episodes_per_cycle` virtual episodes; C4 safe points are unchanged
  (FR-003).

## 3. Determinism contract

- Continuous runs are byte-identical per (config, seed) on re-run and
  under worker parallelism (FR-005).
- Snapshot/resume: a continuous run resumed from any C4 snapshot
  reproduces the uninterrupted summary byte-for-byte **when the world
  implements the capture protocol** (SC-003). Capturing a continuous-mode
  snapshot on a world without the protocol MUST raise at capture time,
  naming the protocol — never a silently unresumable artifact (FR-005).

## 4. World-state capture protocol (optional)

- A world MAY implement `state_dict() -> dict` /
  `load_state_dict(state)` covering its mutable run state only.
- In-repo worlds (`SensorimotorWorld`, the three ladder worlds) implement
  it with this feature; the `Body` delegates to its mounted environment
  when it implements the protocol.
- The snapshot blob's `world_state` entry exists only in continuous-mode
  snapshots of capturing worlds; episodic blobs are bit-identical to the
  pre-feature format, and old blobs decode unchanged (format version
  stays 1).

## 5. Scope contract

- No acceptance claims: T1–T7 remain episodic; continuous mode ships with
  determinism and mechanism-placement proofs plus one investigatory
  reading (FR-008, recorded in `reading.md`, judged by nothing).
- Real-time worlds, multi-stream experience (B4), and external-world
  state capture (B5) are named non-scope.
