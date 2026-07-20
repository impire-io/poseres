> **Provenance note (2026-07-20):** moved from the repo root during the hq
> restructure; content frozen — paths below refer to the pre-restructure
> layout (`design/`, `ROADMAP.md`, `JOURNEY.md` at the root).

# PRA — Next Steps (HISTORICAL — superseded by ROADMAP.md)

> **2026-07-19: this document is a June 2026 handoff, kept for provenance
> (feature 001's spec documents cite it). Everything below is done or
> superseded. The live plan is `ROADMAP.md`; the narrative is `JOURNEY.md`.
> Do not add new work here.**

Updated 2026-06-20, after running the STEP-0 gate, redesigning the scoring, and
propagating the fix into the spec. Read this first, then work top-down.

## STATUS — 2026-06-21: STEPS 2–4 BUILT (feature `001-validation-harness`)

Adopted GitHub Spec Kit and folded **STEPS 2, 3, and 4 into one delivered feature**
(`specs/001-validation-harness/`). The harness, the batched in-memory PRA-01 core,
and the batched frame evaluation are all implemented under `src/pra/` with tests
under `tests/`. Quality gate is green: `ruff format --check`, `ruff check`, and
`pytest` (55 tests, none skipped).

- **Reference suite passes (SC-005):** at the default config T1–T6 all PASS — T4
  holds the within-one majority at every checkpoint (8/8, 8/8, 6/8), T5 self-limits.
  The core reproduces the v4 oracle's per-checkpoint readings near bit-for-bit at
  ~40× the speed; full default suite runs in ~80s.
- **Determinism (SC-007):** a seed re-runs byte-identical (`pra-validate determinism`).
- **T-SCALE (SC-006):** runnable + measured at `true_dim ∈ {20,35,50}`; the batched
  core sustains ~60k observation×frame evaluations/s (>1.1M per dimensionality in a
  ~20s run). It is **investigatory** — high-dim `best_dim` does **not** converge to
  the true dim with the default proposal policy (`best_dim≈1`), the expected open
  research finding (the high-dim proposal is the `[O]` interface-only seam).

Remaining (research, not build): sharpen the world's dimensional elbow and/or a real
high-dim proposal policy so T-SCALE converges at large `true_dim` (see Open question
below). Everything in "Out of scope for first build" remains out of scope.

## Where things actually stand

- **Design spec** (`design/01..07`) — the real system to build. Now reflects the
  validated scoring (see "What the gate changed" below).
- **Validation spec** (`design/validate/PRA-01`, `PRA-02`) — the synthetic world,
  telemetry, and acceptance tests (T1–T6, T-SCALE). Updated to match.
- **Prototypes** (`design/validate/pra_sim{,_v2,_v3,_v4}.py`) — exploratory.
  **`pra_sim_v4.py` is the current reference**: it passes T1–T6 at `true_dim = 3`,
  with T4 robust across horizons (18/30/50) and T5 self-limiting. v3 is kept for
  provenance (it passed T4 only at a lucky 18-cycle horizon).
- **Git**: `8b8c802` baseline (design + validation + prototypes), `a6e6c6c` v4.
  Both signed. The `.venv` (Homebrew py3.14 + numpy) is gitignored.

## What the STEP-0 gate changed (done — do not redo)

The gate caught that v3's load-bearing test (T4) was a lucky-horizon snapshot and
its population was unbounded. Root cause: the survival score was gameable. The
fix, validated in v4 and now written into the spec:

1. **Prediction is scored in OBSERVATION space**, not the frame's pose space
   (Doc 03 §3.1 / PRA-01 §5.2). Pose-space prediction lets a collapsed frame ace
   the score while predicting the world no better than baseline.
2. **Survival EMAs are coverage-fair** — updated over every event the frame sees,
   not only the ones it elects to map (Doc 03 §4 / PRA-01 §5.4). Learning stays
   gated (sparsity / T1); only scoring changed.
3. **A parsimony term `w_complexity·dim`** is added to the survival score
   (Doc 03 §6 / Doc 07 / PRA-01 §6.2). Honest error keeps falling past the true
   dim via overfit; the penalty puts the winner at the diminishing-returns elbow.
4. **The population-scaled eviction threshold now DIVIDES** by the population
   factor (Doc 04 §5.3 / PRA-01 §6.4) so crowding tightens the bar and eviction
   paces spawn — the population self-limits instead of growing to the hard cap.
5. **T4 is judged across horizons** (PRA-02 §4 T4 + §1.4): within-one-majority must
   hold at 18/30/50 cycles, not at one snapshot. Exact `best_dim == true_dim` is
   not required — the world's dimensional elbow is shallow.

## STEP 2 — Build the real validation harness (the test rig comes first)

The v4 prototype is still a throwaway (per-step Python loops). `PRA-02 §5` demands
a proper harness, now implementing the **updated** scoring/decay above:
- multi-seed by default, across-seed aggregation with the per-seed `best_dim`
  **spread** surfaced **at each horizon checkpoint** (18/30/50), not just the mean;
- a **determinism check** (one seed twice, byte-identical summaries — `PRA-01 §7.1`);
- per-test PASS/FAIL with the measured number and criterion; T4 requires the
  within-one majority at **every** checkpoint;
- human-readable + optional JSON; the only thing written to disk.
Build against the `EventSource` world exactly as specified (nonlinear `tanh`
emission, hidden state).

## STEP 3 — Implement the validated core

Per `design/00-README-index.md`, build where the architecture is validated:
- **`03-sensorimotor-core`** — frames, the SIMD/batched scoring requirement, the
  global pose, and the **observation-space prediction + coverage-fair EMAs**.
- **`04-structural-learning`** — zero-start birth, spawn-and-select, the corrected
  population-scaled decay, the parsimony-driven selection, earned persistence.

Tags: **[V]** build as-specified; **[D]** build as-specified, expect tuning
(`w_complexity` and `survive_threshold_*` are the load-bearing [D] params); **[O]**
build interface + default only (high-dim proposal policy `§6.5`, tool self-invention).

## STEP 4 — Batching (the biggest risk; required for "done")

T-SCALE / definition-of-done item 7 requires millions of observations on one
machine at `true_dim ∈ {20, 35, 50}` via **batched frame evaluation** (`PRA-01 §7.2`).
The prototypes loop per-step per-frame in pure Python and will not get within orders
of magnitude. Frame scoring (now including the obs-space prediction decode) must be
vectorized over frames and observations from the start. Load-bearing engineering
decision. T-SCALE's dimensionality *result* at scale is a research finding, not a
pass/fail gate.

## Open validation question (not a blocker)

The default world's dimensional elbow is shallow (`PRA-02 §1.4`): exact `best_dim`
convergence to 3 is soft (some seeds sit one off, a few drift toward 1–2 at long
horizons). Within-one-across-horizons passes. If crisper convergence is wanted,
sharpen the world (lower `sensor_noise_std`, add a bottleneck) — an optional
`PRA-02` change, not an agent fix.

## Out of scope for first build (seams exist; see named docs)

Distributed/multi-machine, external broker (NATS), vector DB pose index, multi-step
planning, tool self-invention, drive evolution. Build only the in-memory backend and
the one-step default policy.
