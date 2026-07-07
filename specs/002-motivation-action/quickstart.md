# Quickstart: Motivation and Action Layer

Commands assume the repo root and the repo `.venv` (unchanged toolchain).

## 1. Run the agent (US1)

```bash
./.venv/bin/pra-validate agency                  # 8 seeds, curious vs random, T7 verdict
./.venv/bin/pra-validate agency --seeds 1        # FOR DEBUGGING ONLY banner
./.venv/bin/pra-validate agency --json out/agency.json
```

Expect: a T7 PASS/FAIL with the per-seed margin table (curious vs random
improvement), plus agency telemetry (mean value signal, learning-progress and
novelty terms, directed-action fraction). Two runs of a seed are byte-identical.

## 2. Confirm the validated core is untouched (US2)

```bash
./.venv/bin/pra-validate suite                   # T1–T6, pinned random baseline
./.venv/bin/pra-validate determinism --seed 1
```

Expect: T1–T6 all PASS with summaries byte-identical to the validated build
(guarded by `tests/integration/test_baseline_unchanged.py`).

## 3. Quality gate (must be green before "done")

```bash
./.venv/bin/ruff format --check . && ./.venv/bin/ruff check . && ./.venv/bin/pytest -q
```

## 4. Map each acceptance scenario to its check

| Spec scenario | How to verify |
|---|---|
| US1 — the system acts; finite value signal from step one | `agency`; `tests/integration/test_agency_determinism.py`, `tests/unit/test_curiosity_drive.py` |
| US2 — validated core untouched, byte-identical | `tests/integration/test_baseline_unchanged.py`; `tests/contract/test_policy_contract.py` |
| US3 — curious ≥ random (T7) | `agency`; `tests/integration/test_agency_t7.py` |
| US4 — drive immutable; LP self-limits | `tests/contract/test_drive_contract.py`; `tests/unit/test_curiosity_drive.py` |
| US5 — counter-drive by configuration | `tests/integration/test_multi_drive.py` |
| Edge cases (cold start, empty memory, ties, ε) | `tests/unit/test_lookahead_policy.py`, `tests/unit/test_curiosity_drive.py` |

## 5. Oracle for behavior

There is no v4-style oracle for this layer (it is new behavior); the oracles are
(a) the pinned random baseline — byte-identical to the validated build — and
(b) the unit-level truths of Doc 05 §3–§4 (LP ≈ 0 on flat histories, novelty
finite from the first step, argmax/tie-break/ε semantics), each encoded as a
test before implementation.
