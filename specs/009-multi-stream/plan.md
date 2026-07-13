# Implementation Plan: Multi-Stream Experience

**Branch**: `009-multi-stream` | **Date**: 2026-07-13 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/009-multi-stream/spec.md`

## Summary

Build ROADMAP B4: `Config.n_streams=K` runs K world instances of one
hidden structure (identical construction seeding, per-stream generators
assigned post-construction — research R2), explored by K independent
action streams and merged into the single brain by a fixed episode
round-robin (`episode e → stream e mod K`). The consolidation cadence
counts **merged** episodes — total experience, mode-invariant (R3) — so
comparisons across K are equal-experience by construction. Randomness
splits by ownership: stream generators for world noise + policy
exploration, the shared brain generator (merge-order-consumed) for
births/proposals/decay (R1). Snapshots at K>1 fail loudly naming B5
(R6). The exit is a pre-registered measurement (R5): K ∈ {1,2,4} paired
per seed, T7-noninferiority bar; plus the investigatory continuous-rover
reading where streams genuinely differ (R4's pre-registered null/
substance split). K=1 is the untouched validated path, byte-identical.

## Technical Context

**Language/Version**: Python 3.14 (repo `.venv`)  **Dependencies**: numpy only
**Storage**: none (K>1 snapshots deferred to B5 by loud failure)
**Testing**: pytest — unit (validation, seeding derivation, scheduler math), integration (K=1 byte-identity, K>1 determinism, structure sharing, chain/cadence placement, continuous composition, snapshot loud-fail)
**Project Type**: extends the `pra` package — config field + an engine K-stream branch; no new modules
**Performance**: identical per-step cost; K worlds cost K× world memory (tiny)
**Constraints**:
- **Byte-identity** (SC-002): K=1 short-circuits to today's exact code; the frozen baseline plus an explicit K=1-equivalence test guard it.
- **Determinism** (SC-001): fixed merge order; per-stream generators from spawn keys; brain draws in merge order.
- **Regime isolation** (SC-003): the only K-dependent change is which world state an episode continues from; cadence/windows/chains provably fixed.
- **Honest measurement** (FR-007): bar pre-registered (R5); null expectation pre-registered (R4); recorded whichever way it lands.
**Scale/Scope**: reference-scale readings; scaled multi-stream is future research.

## Constitution Check

| Gate | Requirement | Status |
|---|---|---|
| Regression (SC-002) | K=1 byte-identical, default inert | PASS — untouched single-stream path + equivalence test |
| Design-first (FR-006) | ownership split, merge, construction sharing, composition — written before code | PASS — research R1–R8 in this phase |
| Honest measurement (FR-007) | pre-registered bar + null expectation, spreads | PASS — R4/R5; reading.md records regardless |
| Snapshot honesty (FR-009) | exact or loud | PASS — loud failure naming B5 (R6) |
| Seam isolation | no store/scorer/drive edits | PASS — episode-locality carries every mechanism (R3) |
| Quality gate | ruff + pytest green, none skipped | PASS — gated in tasks |

## Project Structure

```text
specs/009-multi-stream/
├── plan.md, research.md, data-model.md, quickstart.md, reading.md
├── checklists/requirements.md
├── contracts/multistream.md
└── tasks.md

src/pra/
├── config.py            # + n_streams (default 1) + validation (incl. B5 guard)
└── core/engine.py       # K-stream branch: worlds/stream_rngs/pending lists,
                         #   episode scheduler e mod K, stream rng for policy,
                         #   per-stream boot in continuous mode

tests/
├── unit/test_multistream.py         # validation, spawn-key derivation,
│                                    #   scheduler/cadence math
└── integration/test_multistream.py  # K=1 byte-identity; K=4 determinism;
                                     #   structure sharing across streams;
                                     #   cadence positions K-invariant;
                                     #   continuous composition (K boots);
                                     #   snapshot loud-fail at K>1
```

**Structure Decision**: like 008, a mode of the engine — no new runtime
modules; the reading is produced by scratchpad protocol scripts and
recorded in `reading.md` (conclusions in repo, experiments in scratchpad).

## Complexity Tracking

No gate violations. Accepted debts, named: multi-stream snapshot capture
→ B5; step-granular merges and directed-policy readings → future dials
on this instrument; thread-level parallelism → the external-bus horizon.
