# PRA — Pose Resolution Architecture

An in-memory, batched, deterministic core (PRA-01) and the validation harness
(PRA-02) that runs the acceptance suite **T1–T6** plus the investigatory
**T-SCALE**, emitting an honest, reproducible PASS/FAIL verdict per test.

See `specs/001-validation-harness/` for the spec, plan, and contracts, and
`design/` for the architecture documents. The behavioral oracle is
`design/validate/pra_sim_v4.py`.

## Quickstart

```bash
./.venv/bin/python -m pip install -e ".[dev]"   # numpy + pytest + ruff

./.venv/bin/pra-validate suite                  # 8 seeds, true_dim=3, checkpoints 18/30/50
./.venv/bin/pra-validate suite --json out/report.json
./.venv/bin/pra-validate determinism --seed 1   # byte-identical re-run check
./.venv/bin/pra-validate scale --true-dims 20,35,50
./.venv/bin/pra-validate scan --true-dim 20 --hidden-sizes 12,32,64   # diagnostic dimension scan

./.venv/bin/ruff format --check . && ./.venv/bin/ruff check . && ./.venv/bin/pytest -q
```

Independent seeds run in parallel worker processes by default (`--workers`,
0 = one per seed up to the CPU count) — parallelism never changes results
(byte-identical to sequential; each run keeps its own seeded, single-threaded
pipeline). The full default suite runs in ~20s on a 14-core machine.

`suite` emits, for each of **T1–T6**, the measured aggregate (mean ± std), the
exact pass criterion, and PASS/FAIL. **T4** is shown as the full per-seed `best_dim`
spread at every horizon checkpoint and PASSes only if the within-one-of-true
majority holds at *every* checkpoint — it can never pass on a lucky single horizon.
**T5** PASSes only when the population genuinely self-limits (no seed strictly
growing over its final third), not merely because it hit a cap. A single-seed run is
labelled **FOR DEBUGGING ONLY**. Exit code is 0 even when a test FAILs (a FAIL is
data, not a CLI error) unless `--strict` is passed.

## Governing principle — honest summary

Where a tidy report and a faithful one conflict, the faithful one wins (FR-008): a
failing test is shown as FAIL *with the numbers that explain it*; a test needing a
spread is never reported by its mean alone; a seed that errors is surfaced and the
aggregate flagged incomplete, never silently dropped; too few samples reads
"not available", never a fabricated number. Two runs of a seed produce
byte-identical telemetry (single seeded RNG, fixed draw order, single-threaded BLAS).

## Layout

```
src/pra/
  config.py            # every PRA-01 §8 parameter + validation
  world/event_source.py# EventSource seam + SensorimotorWorld (nonlinear, hidden latent)
  core/                # contracts, bus, scorer, policies, the batched FrameGroup kernel, engine
  telemetry/recorder.py# deterministic per-seed summary
  harness/             # acceptance (T1-T6/T-SCALE), runner, report, cli, scale, scan
tests/                 # unit (incl. batched-vs-reference proof) / contract (5 seams) / integration
```

## Behavioral oracle

`design/validate/pra_sim_v4.py` is the validated reference run. The batched core
reproduces its T1–T6 trajectory at the default config (the per-frame-vs-batched
equivalence is enforced by `tests/unit/test_batched_equivalence.py`) at roughly 40×
the speed. The full default suite (8 seeds × predictive + ablation × 50 cycles)
completes in well under a minute.
