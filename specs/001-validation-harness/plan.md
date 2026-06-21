# Implementation Plan: PRA Validation Harness

**Branch**: `001-validation-harness` | **Date**: 2026-06-21 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-validation-harness/spec.md`

## Summary

Deliver a reproducible, honest validation harness that runs the PRA acceptance suite
(T1–T6 plus the investigatory T-SCALE) across all configured seeds and emits a
per-test PASS/FAIL verdict with the measured number and the criterion it was judged
against. Because a harness cannot produce real verdicts without a conforming
system-under-test — and this feature's success criteria require T1–T6 to actually
PASS (SC-005) and T-SCALE to be runnable at millions of observation steps (SC-006) —
this feature **also builds the in-memory PRA core exactly as specified in PRA-01**
(Bus, Frame, Scorer, Proposal/Decay policies, Engine, and the EventSource world),
with the mandatory **batched, `dim`-grouped frame evaluation** (PRA-01 §7.2). The
throwaway v4 prototype (`design/validate/pra_sim_v4.py`) is the **behavioral oracle**
the new implementation is checked against, not a dependency.

The harness's distinguishing requirements over the prototype: it records `best_dim`
at multiple horizon checkpoints (default 18/30/50 cycles) and FAILs T4 unless the
within-one-of-true majority holds at **every** checkpoint; it judges T5 as
*self-limiting* (no seed still growing over its final third) rather than merely
capped; it provides a determinism mode that runs one seed twice and asserts
**byte-identical** summaries; it surfaces the per-seed `best_dim` spread (never the
mean alone); and it never smooths or cherry-picks.

**Technical approach**: a single Python package (`pra`) built on numpy, structured so
the five PRA-01 seams (Bus, Scorer, ProposalPolicy, DecayPolicy, EventSource) are each
swappable in isolation; a homogeneous frame kernel evaluated as batched array ops over
`dim`-grouped weight stacks; a single seeded `numpy.random.Generator` drawn in a fixed
order for full reproducibility; and a CLI that runs the suite, the determinism check,
and the investigatory scale test, writing only a result summary to disk.

## Technical Context

**Language/Version**: Python 3.14 (Homebrew; externally managed per PEP 668 — use the
repo-root `.venv`)
**Primary Dependencies**: numpy 2.4.6 (the only runtime dependency; carries the
batched/vectorized evaluation). Dev-only: pytest (tests), ruff (format + lint).
Explicitly **no** message broker / NATS, **no** database, **no** vector index, **no**
distribution framework (PRA-01 §1.2).
**Storage**: None for system/model state (FR-011, PRA-01 §1.2). The *only* artifact
written to disk is the result summary: a human-readable text report and an optional
machine-readable JSON (FR-007).
**Testing**: pytest — unit (frame kernel, scorer math, batched-vs-reference
equivalence), contract (the five swappable seams), and integration (determinism,
horizon-drift FAIL, T5-still-growing FAIL, edge cases). The acceptance suite itself is
the harness output, exercised by an end-to-end test at a small reference config.
**Target Platform**: Single machine, CPU only, macOS/Linux. No GPU requirement
(PRA-01 §1.2).
**Project Type**: Single project — a library (`pra`) with a CLI entry point (the
harness).
**Performance Goals**: T-SCALE must reach **millions** of observation steps on one
machine via batched evaluation (PRA-01 §7.2/§1.3, PRA-02 §3.3, T-SCALE); report
`throughput = observation_steps × mean_population ÷ wall-clock-seconds`. **Budget
reference config:** the default suite is 8 seeds × **2 runs each** (the predictive run
plus the T3 effort-only ablation, T027) × **50 effective offline cycles** (`n_cycles`
extended to cover the last horizon checkpoint, 50 — see data-model §1). That full
default suite — all 16 runs — should complete in **single-digit minutes**. The
pure-Python v4 prototype took ~3.5 min for a single 50-cycle seed; the batched
`dim`-grouped core (PRA-01 §7.2) must beat that by enough to absorb the 16 runs and
still land in single-digit minutes, and must not regress the single-seed 50-cycle figure.
**Constraints**:
- Full determinism from seed: every random draw comes from one seeded generator in a
  fixed order; two runs of a seed produce byte-identical telemetry (FR-010, SC-007,
  PRA-01 §7.1).
- In-memory only; model state is never persisted (FR-011).
- Homogeneous kernel: no per-frame conditional logic in encode/decode/transition/learn;
  all variation lives in `dim` and weight values (PRA-01 §7.2).
- Component isolation: Bus, Scorer, ProposalPolicy, DecayPolicy, EventSource each
  swappable without touching the others (PRA-01 §7.3).
- Honest reporting: no smoothing, no cherry-picking, no mean-only where a spread is
  required (FR-003, FR-008).
**Scale/Scope**: `true_dim ∈ {3 (default), 20, 35, 50}`; `obs_dim ≥ 3 × true_dim`; 8
seeds by default; `max_frames = 200`; the default suite runs each seed for 50 offline
cycles (`= max(horizon_checkpoints)`) so all three T4 checkpoints (18/30/50) are reached;
T-SCALE schedules long enough to reach millions of observation steps per seed.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The project constitution (`.specify/memory/constitution.md`) is still the unfilled
template (placeholder tokens only); there are **no ratified constitution gates** to
enforce. In their absence, this plan is gated against the binding requirements that the
project's own specifications and the user's global instructions impose. All gates pass
by design:

| Gate (source) | Requirement | Status |
|---|---|---|
| Determinism (PRA-01 §7.1, FR-010) | Single seeded RNG, fixed draw order, byte-identical re-runs | PASS — designed in (§ research R3) |
| Component isolation (PRA-01 §7.3) | Bus/Scorer/Proposal/Decay/EventSource each swappable | PASS — five seam interfaces (§ contracts) |
| Homogeneous batched kernel (PRA-01 §7.2) | No per-frame branching; `dim`-grouped batched eval | PASS — FrameGroup design (§ research R1) |
| No out-of-scope deps (PRA-01 §1.2) | No broker/NATS, DB, vector index, distribution, GPU | PASS — numpy only |
| Honest reporting (FR-003, FR-008) | Spread surfaced; no smoothing/cherry-picking | PASS — report contract forbids mean-only |
| Persistence boundary (FR-011) | Only the result summary is written to disk | PASS — no state serialization |
| Tests pass / lint clean / formatted (CLAUDE.md) | `ruff` clean, pytest green, none skipped, builds | PASS — gate in quickstart + tasks |
| Best practices / design patterns (CLAUDE.md) | Interfaces + DI for seams; no leakage | PASS — seam contracts |

**Complexity note**: this feature intentionally folds NEXT-STEPS steps 2–4 (harness +
core + batching) into one deliverable. This is not gold-plating: the spec's own success
criteria (SC-005 real T1–T6 PASS; SC-006 runnable T-SCALE) are unsatisfiable without a
conforming, batched core. The throwaway prototype cannot meet them. See Complexity
Tracking.

## Project Structure

### Documentation (this feature)

```text
specs/001-validation-harness/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
│   ├── cli.md               # Harness CLI command contract
│   ├── seams.md             # The five swappable seam interfaces (PRA-01 §7.3)
│   ├── config.md            # Configuration parameters + defaults (PRA-01 §8)
│   └── report-schema.json   # JSON schema for the machine-readable verdict report
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
src/pra/
├── __init__.py
├── config.py                # Config dataclass: every PRA-01 §8 parameter + default
├── world/
│   ├── __init__.py
│   └── event_source.py      # EventSource seam + SensorimotorWorld (PRA-02 §1): nonlinear
│                            #   tanh emission, hidden latent state, scaled configs
├── core/
│   ├── __init__.py
│   ├── contracts.py         # SensorimotorEvent, FrameResult, GlobalPose (PRA-01 §3)
│   ├── bus.py               # Bus interface + InMemorySyncBus (PRA-01 §4)
│   ├── frame.py             # Homogeneous frame kernel + FrameGroup (dim-grouped, batched §7.2)
│   ├── scorer.py            # Scorer interface + WeightedSumScorer w/ parsimony (PRA-01 §6.2)
│   ├── policies.py          # ProposalPolicy + DecayPolicy interfaces & defaults (§6.4/§6.5)
│   └── engine.py            # Engine: zero-start lifecycle, online/offline, telemetry (§6)
├── telemetry/
│   ├── __init__.py
│   └── recorder.py          # per-step / per-cycle / per-run summary (PRA-02 §3)
└── harness/
    ├── __init__.py
    ├── runner.py            # multi-seed orchestration, across-seed aggregation, determinism mode
    ├── acceptance.py        # T1–T6 + T-SCALE verdict logic incl. horizon-checkpoint + self-limiting rules
    ├── report.py            # human-readable text + optional JSON; honest-summary rules
    └── cli.py               # CLI entry point (suite / determinism / scale modes)

tests/
├── contract/                # one test module per seam: substitutability + interface conformance
│   ├── test_bus_contract.py
│   ├── test_scorer_contract.py
│   ├── test_policies_contract.py
│   └── test_event_source_contract.py
├── integration/             # behavior the spec calls out explicitly
│   ├── test_determinism.py          # byte-identical re-run (FR-006, SC-007)
│   ├── test_t4_horizon_drift.py     # early-pass/late-drift -> FAIL (US2, SC-002)
│   ├── test_t5_still_growing.py     # below cap but growing -> FAIL (US4)
│   ├── test_reference_config.py     # T1–T6 PASS at validated reference (SC-005)
│   ├── test_edge_cases.py           # not-available, seed-error, warmup-births, capped
│   └── test_scale_runnable.py       # T-SCALE emits spread+throughput, labelled investigatory (SC-006)
└── unit/                    # component internals
    ├── test_frame_kernel.py         # encode/decode/transition math
    ├── test_batched_equivalence.py  # batched dim-group == reference per-frame loop (PRA-01 §7.2)
    ├── test_scorer.py               # weighted sum + parsimony, tie-break by frame_id
    ├── test_world.py                # nonlinear emission, hidden-state, determinism
    └── test_aggregation.py          # mean/std + per-seed spread surfacing

pyproject.toml               # project metadata, deps (numpy), pytest + ruff config
```

**Structure Decision**: Single Python project (library + CLI). The package boundary
mirrors the PRA-01 component map so each seam is a separate module with an explicit
interface, satisfying the component-isolation requirement (PRA-01 §7.3). `core/`
carries the system-under-test; `harness/` carries the orchestration, verdict, and
reporting layer that the spec is centered on; `world/` is the EventSource boundary;
`telemetry/` records exactly the fields PRA-02 §3 enumerates. Tests are split into
contract (seam substitutability), integration (the spec's explicit behaviors and edge
cases), and unit (kernel/scorer/world internals incl. the batched-equivalence proof).

## Complexity Tracking

> Filled because this feature deliberately exceeds the narrowest reading of "harness".

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Feature builds the full PRA-01 core, not just harness orchestration | SC-005 requires T1–T6 to actually PASS and SC-006 requires T-SCALE runnable; both need a conforming system-under-test that does not yet exist | Driving the v4 prototype was rejected: it is explicitly throwaway, not seam-clean, and its per-step Python loops cannot reach millions of observations, so SC-006/T-SCALE would be unmeetable |
| Batched `dim`-grouped frame evaluation built now (not deferred) | PRA-01 §7.2 calls batching a "hard requirement, not an optimization"; T-SCALE (in this spec) is unreachable without it | Per-frame Python loops rejected: orders of magnitude too slow for millions of observations on one machine (NEXT-STEPS STEP 4) |
| Five explicit seam interfaces (Bus/Scorer/Proposal/Decay/EventSource) | PRA-01 §7.3 mandates each be swappable in isolation; the open research question (high-dim proposal policy) depends on swapping ProposalPolicy without touching others | A monolithic agent (like the prototype's single `PRAgent` class) rejected: it couples scoring/decay/proposal and cannot be substituted for the scale study |
