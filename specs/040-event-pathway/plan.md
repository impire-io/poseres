# Implementation Plan: The Event Pathway

**Branch**: `040-event-pathway` | **Date**: 2026-08-09 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/040-event-pathway/spec.md`

## Summary

Promote the measured motivation-stack G3 prototype (episode 0071) into the
product: an **event head** — per-action normalized-LMS linear models of the
next-observation delta, owned by the FrameStore beside the frames — and a
shipped **CompletionItchPolicy** that reads it through a new PolicyContext
accessor. Config-gated by `event_head_eta` (0.0 = off: no state, no float
work, no RNG, byte-identical). Head state persists in snapshots as an
additive-optional key; anatomy resize is zero-init/no-RNG. The v1 surface
grows additively (inventory + Docs 0005/0007/0008; version 1.1.0 → 1.2.0).
The feature closes with the research-side obligation: the G3 confirmatory
rerun on the shipped components, recorded in the topic README (episode 0071's
reversal condition).

## Technical Context

**Language/Version**: Python 3.12 (repo venv `./.venv`)
**Primary Dependencies**: numpy (only runtime dep of the core)
**Storage**: versioned `.npz` snapshot blobs (Doc 0006; `allow_pickle=False`)
**Testing**: pytest (`tests/unit`, `tests/integration`, `tests/contract` incl.
the public-surface guard and the hq structural lint)
**Target Platform**: library (pip-installable), macOS/Linux
**Project Type**: single library project (`src/pra`)
**Performance Goals**: when off — zero added work per step; when on — O(A·D²)
per directed step for prediction (A=12, D=32 at C1: trivial) and one O(D²)
NLMS update per executed transition
**Constraints**: Article I (byte-frozen reference behavior — feature off must
be bit-identical everywhere: RNG stream, summaries, snapshot bytes);
deterministic (no RNG in the head, draw order untouched); additive-only v1
surface (feature 035 semver policy)
**Scale/Scope**: ~5 src files touched, 2 docs, 1 inventory, ~6 test files;
plus the research-closure rerun script (scratchpad) and topic README record

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Reference-Preserving Forever**: PASS by design — `event_head_eta = 0.0`
  default adds no state/floats/RNG (the channel-weighting gating pattern,
  feature 016); explicitly tested (byte-identical summaries + snapshot bytes
  with the feature off; `test_baseline_unchanged.py` untouched).
- **II. Honest Measurement**: PASS — the feature's own acceptance includes the
  G3 rerun with all three bars recorded pass or fail; the policy ships honesty
  counters (false completions) rather than hiding them.
- **III. Diagnose Before Fixing**: PASS — this is not a behavioral fix; the
  mechanism was diagnosed and measured through G1→G1L→G3 with the trail in
  `hq/01-RESEARCH/motivation-stack/` and episodes 0070/0071. Research ran in
  the scratchpad; only the principled build lands.
- **IV. Research Gates Before Showcase Spends**: PASS — the gate (G3) ran
  first and passed; this build is what the gate licensed.
- **V. Never Lose the Instrument Panel**: PASS — no new world; the rerun uses
  the deterministic FakeBridge instrument.
- **VI. All-Green Quality Gate**: the working rule; every commit on the branch
  keeps the full gate green.

**Post-Phase-1 re-check**: PASS — the design introduces no new project, no
new dependency, no surface mutation (additive entries only).

## Project Structure

### Documentation (this feature)

```text
specs/040-event-pathway/
├── plan.md              # This file
├── research.md          # Phase 0: the load-bearing design decisions
├── data-model.md        # Phase 1: entities and state shapes
├── quickstart.md        # Phase 1: how a user enables and reads the pathway
├── contracts/
│   └── surface.md       # Phase 1: the additive v1 surface contract
└── tasks.md             # Phase 2 (/speckit-tasks — not created by /speckit-plan)
```

### Source Code (repository root)

```text
src/pra/
├── config.py                      # + event_head_eta field & validation
├── core/
│   ├── frame.py                   # + _EventHead owned by FrameStore:
│   │                              #   event_learn / event_predict / resize /
│   │                              #   state_dict/load_state_dict keys
│   └── engine.py                  # + one guarded event_learn call at the
│   │                              #   step-loop transition site; PolicyContext
│   │                              #   gains the predict_event_delta closure
├── action/policy.py               # + PolicyContext.predict_event_delta field
│                                  # + CompletionItchPolicy (+ watch counters)
├── anatomy/minecraft/anatomy.py   # + C1_MINING_INDEX / C1_POCKET_TOTAL_INDEX
│                                  #   derived from C1_SENSORS
└── persistence/snapshot.py        # + eh__* arrays + meta flag (additive-
                                   #   optional, the channel_stats pattern)

tests/
├── unit/test_event_head.py        # NLMS math, cold start, resize, per-action
├── unit/test_completion_itch_policy.py  # draw order, completion rule, counters
├── integration/test_event_pathway.py    # off = byte-identical; on: snapshot
│                                        # roundtrip + resume equivalence
└── contract/surface_inventory.py  # + additive entries (guard enforces)

hq/02-DESIGN/
├── 0005-motivation-action.md      # + event pathway §, CompletionItchPolicy §
├── 0007-configuration-reference.md# + event_head_eta row
└── 0008-public-api-versioning.md  # + 1.2.0 additive entries note

pyproject.toml                     # version 1.1.0 → 1.2.0
```

**Structure Decision**: single library project; every touched path exists
today — the feature adds seams to established files, mirroring feature 016's
shape (config dial + store-owned estimator + snapshot key + docs).

## Complexity Tracking

No constitution violations; table intentionally empty.
