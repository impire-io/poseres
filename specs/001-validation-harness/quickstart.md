# Quickstart: PRA Validation Harness

How to set up, build, run, and verify the harness. Commands assume the repo root
`/Users/calmera/Work/personal/pra` and the repo-root `.venv` (Python 3.14, numpy 2.4.6;
the system interpreter is externally managed per PEP 668, so always use the venv).

## 1. Environment

```bash
# The venv already exists at ./.venv (numpy installed). If recreating:
python3 -m venv .venv
./.venv/bin/python -m pip install -e ".[dev]"   # numpy (runtime) + pytest, ruff (dev)
```

The package is installed editable from `pyproject.toml`; that file declares numpy as the
sole runtime dependency and pytest + ruff as dev extras. No broker, database, or vector
index is installed — they are out of scope (PRA-01 §1.2).

## 2. Run the acceptance suite (the primary deliverable)

```bash
./.venv/bin/pra-validate suite                       # default: 8 seeds, true_dim=3, checkpoints 18/30/50
./.venv/bin/pra-validate suite --json out/report.json
```

Expect a PASS/FAIL line for each of T1–T6 with the measured aggregate (mean ± std) and
the exact criterion (SC-001, SC-004). T4 additionally prints the per-seed `best_dim`
spread at each checkpoint with within-one/exact counts; it PASSes only if the within-one
majority holds at **every** checkpoint (SC-002). At the validated reference config all of
T1–T6 PASS (SC-005), reproducing the v4 reference behavior.

## 3. Check reproducibility

```bash
./.venv/bin/pra-validate determinism --seed 1
```

Runs seed 1 twice and asserts the two run summaries are **byte-identical** (SC-003,
SC-007). Any non-zero difference is a hard FAIL pointing at the first divergence.

## 4. Run the investigatory scale test

```bash
./.venv/bin/pra-validate scale --true-dims 20,35,50 --json out/scale.json
```

Emits, per `true_dim`, the per-seed `best_dim` spread, `throughput`, and wall-clock,
labelled **INVESTIGATORY** (SC-006). A poor dimensionality result at scale is a research
finding, never a build failure.

## 5. Quality gate (must be green before "done" — CLAUDE.md)

```bash
./.venv/bin/ruff format --check .     # formatting
./.venv/bin/ruff check .              # linting
./.venv/bin/pytest -q                 # all tests pass, none skipped
```

All three MUST be green. The test suite includes the batched-vs-reference equivalence
proof (PRA-01 §7.2), the five seam contract tests (PRA-01 §7.3), and the integration
tests that encode the spec's explicit behaviors: determinism (FR-006), T4 horizon-drift
FAIL (US2), T5 still-growing FAIL (US4), and the edge cases (not-available,
seed-error, warmup-births, capped population).

## 6. Map each acceptance scenario to its check

| Spec scenario | How to verify |
|---|---|
| US1 — per-test PASS/FAIL with measure + criterion | `suite`; `tests/integration/test_reference_config.py` |
| US2 — T4 cannot be a lucky snapshot | `tests/integration/test_t4_horizon_drift.py` (early-pass/late-drift ⇒ FAIL) |
| US3 — byte-identical re-run | `determinism`; `tests/integration/test_determinism.py` |
| US4 — T5 self-limiting, not capped | `tests/integration/test_t5_still_growing.py` (below cap but growing ⇒ FAIL) |
| US5 — scale runnable & measured | `scale`; `tests/integration/test_scale_runnable.py` |
| Edge cases | `tests/integration/test_edge_cases.py` |

## 7. Oracle for behavior

`design/validate/pra_sim_v4.py` is the validated reference. Run it for the expected
shape of the numbers (from `design/validate/`, with `../../.venv/bin/python
pra_sim_v4.py`). The new core must reproduce its T1–T6 verdicts at the default config;
the batched-equivalence test enforces that the vectorized path matches a reference
per-frame computation.
