# PRA — Next Steps (handoff to Claude Code)

State as of 2026-06-20. Read this first, then work top-down. Do not skip the gate.

## Where things actually stand

- **Design spec** (`design/01..07`) — the real system to build. Complete, functional, tagged [V]/[D]/[O].
- **Validation spec** (`design/validate/PRA-01`, `PRA-02`) — the synthetic world, telemetry, and acceptance tests (T1–T6, T-SCALE) that define "correct" and "done."
- **Prototypes** (`design/validate/pra_sim{,_v2,_v3}.py`) — exploratory. v2 FAILED the load-bearing test (T4: best-frame dim collapsed toward 1 instead of growing to true=3; T5 population ballooned). v3 added a third scoring term (explanatory/reconstruction) to fix it.
- **Git**: one commit ("Initial commit from Specify template"). All design + validation work is **uncommitted**. The `.specify`/speckit scaffolding is staged for deletion.

## STEP 0 — The gate (do this before anything else)

Run v3 at true_dim=3 across all 8 seeds and read the verdicts:

```
cd design/validate && python3 pra_sim_v3.py
```

Decision rule:
- **T4 passes** (|best_dim − 3| ≤ 1 for a majority of seeds, read the *spread* not the mean) **and T5 passes** (population bounded, not still growing) → the architecture's central claim holds at small scale. Proceed to Step 1.
- **T4 still fails** → STOP. Do not build the real system. The scoring design is still wrong and building on it wastes the effort. Fix scoring in the prototype first; that's the whole ballgame.

Also confirm T1, T2, T3, T6 still PASS (they did in v2).

## STEP 1 — Commit a baseline

Commit the design + validation set as-is so there's a known-good reference before the build mutates anything. Decide deliberately whether to keep or remove the `.specify` scaffolding (currently staged for deletion).

## STEP 2 — Build the real validation harness (the test rig comes first)

The v3 prototype is a throwaway: per-step Python loops, single-file, no real harness. `PRA-02 §5` demands a proper one before the system is judged by it:
- multi-seed by default, across-seed aggregation with the **per-seed best_dim spread** surfaced (not just the mean);
- a **determinism check** (run one seed twice, assert byte-identical summaries — `PRA-01 §7.1`);
- per-test PASS/FAIL verdicts with the measured number and criterion;
- human-readable + optional JSON output; this is the only thing written to disk.

Build this against the `EventSource` world interface exactly as specified, including the **nonlinear `tanh` emission** and the hidden-state requirement.

## STEP 3 — Implement the validated core

Per `design/00-README-index.md`, start where the architecture is validated:
- **`03-sensorimotor-core`** — reference frames, the SIMD/batched scoring requirement, the global pose.
- **`04-structural-learning`** — zero-start birth, spawn-and-select, population-scaled decay, earned persistence.

Everything is tagged: **[V]** build as-specified; **[D]** build as-specified, expect refinement; **[O]** build the interface + default only, expect the internal to be replaced. **[O] is where implementation risk concentrates** (high-dim proposal policy `§6.5`, tool self-invention).

## STEP 4 — Batching (the biggest risk; required for "done")

T-SCALE / definition-of-done item 7 requires reaching **millions of observations on a single machine** at true_dim ∈ {20, 35, 50}, via **batched frame evaluation** (`PRA-01 §7.2`). The current prototypes loop per-step per-frame in pure Python — they will not get within orders of magnitude of that. Frame scoring must be vectorized over frames and observations from the start of the real build, not retrofitted. Treat this as the load-bearing engineering decision.

Note: T-SCALE's *dimensionality result* at scale is a **research finding, not a pass/fail gate**. The build is "done" when T-SCALE is runnable and measured — a "structure growth breaks at high dim" answer is a valid, important result, not a build defect.

## Out of scope for first build (seams exist; see named docs)

Distributed/multi-machine, external broker (NATS), vector DB pose index, multi-step planning, tool self-invention, drive evolution. Build only the in-memory backend and the one-step default policy.
