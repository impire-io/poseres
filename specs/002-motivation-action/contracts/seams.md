# Contract: Drive and Policy seams (Doc 05 §2.1 / §4.1)

Two new swappable seams, held to the same isolation standard as feature 001's
five (PRA-01 §7.3): swapping either MUST NOT require edits to any other
component. The Engine depends only on the interfaces.

---

## 1. Drive — the fixed innate preference (Doc 05 §2)

```python
class Drive(Protocol):
    def id(self) -> str: ...
    def value(self, context: DriveContext) -> float: ...
```

**Default:** `CuriosityDrive` — `w_progress·learning_progress + w_novelty·novelty`
(research R5): windowed learning progress (`max(0, baseline − recent)`, 60/600
steps), min-distance novelty over a 200-deep bounded observation memory (empty
memory ⇒ 1.0).
**MUST:** be a pure function of the context and fixed parameters — no RNG, no
hidden mutable policy state (bookkeeping FIFOs are state, updated by the drive
after valuation, never read-modified by anything else). Return a finite float
for every reachable context including the first step (FR-001).
**MUST NOT:** be modifiable at runtime — parameters and weights are frozen
(FR-003, Doc 05 §6); no runtime process may write them.
**Contract test:** a substitute constant drive is accepted by the Engine
unchanged and the value signal equals the configured weighted sum; parameter
mutation attempts raise; valuation consumes no RNG (generator state unchanged
across `value()`).

## 2. WeightedDriveSet — combination (Doc 05 §2.2)

```python
class WeightedDriveSet:
    def value(self, context: DriveContext) -> float:  # Σ w[d.id()]·d.value(ctx)
```

**MUST:** use weights fixed at configuration; evaluate drives in fixed
registration order (deterministic accumulation); reject construction when
weights and drive ids do not match one-to-one.
**Contract test:** two drives with weights (0.7, 0.3) produce exactly
`0.7·v1 + 0.3·v2`; adding the second drive is configuration only (US5).

## 3. Policy — action selection (Doc 05 §4)

```python
class Policy(Protocol):
    def select_action(self, context: PolicyContext, rng: np.random.Generator) -> int: ...
```

**Defaults:**
- `RandomPolicy` (the pinned validation baseline): exactly one
  `rng.integers(n_actions)` draw — byte-identical to the validated engine's
  inline sampling (FR-008). This is the default `policy_mode`.
- `CuriosityLookaheadPolicy`: ε-gate draw first; random when exploring, when no
  best frame exists, or when the best frame is younger than
  `lookahead_min_age_cycles`; otherwise argmax over candidate actions of the
  drive-valued, best-frame-predicted, decoded next observation; ties to the
  lowest action index with no further draws (research R6).

**MUST:** draw randomness only from the passed seeded generator, in the fixed
order above (FR-007); be stateless across steps (all state lives in the frames,
the drive bookkeeping, and the generator).
**MUST NOT:** mutate frames, drive parameters, or any engine state.
**Contract test:** a substitute policy (e.g. always-action-0) is accepted by the
Engine unchanged; `RandomPolicy` reproduces the validated reference summary
byte-for-byte; the curiosity policy's re-run is byte-identical.

---

## Cross-seam invariants

- One seeded generator per run; drives consume none of it; policies consume it
  in the documented order (PRA-01 §7.1 carries over).
- The Engine builds the contexts; drives and policies never reach around them.
- Telemetry fields produced by these seams appear in the run summary **only**
  in agency mode (research R2) — the validated baseline artifact is frozen.
