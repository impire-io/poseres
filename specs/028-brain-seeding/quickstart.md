# Quickstart: Brain Seeding experiment

Prereqs: the repo venv (`./.venv/bin/python`); no new dependencies.

## 1. Pilot — calibrate θ and budgets (exploratory)

```bash
./.venv/bin/pra-validate seeding --mode pilot --seeds 8 --json pilot.json
```

Reads the fresh-brain learning curves on maps B and C and reports the calibration
targets (median initial→plateau gaps, suggested `θ_B`/`θ_C` at `p = 0.5`,
suggested `N_pretrain`, `N_probe`, `W_smooth`). No bar verdicts are printed in
pilot mode.

## 2. Freeze the calibration (pre-registration)

Copy the pilot's chosen values into the frozen table in
`design/validate/SEEDING-DIAGNOSIS.md` (the `_TBD (pilot)_` rows), and **commit
that file before running step 3**. This is the pre-registration boundary — no
criterion changes after the confirmatory run.

## 3. Confirmatory run — decide the bars (24 seeds)

```bash
./.venv/bin/pra-validate seeding --mode confirmatory --seeds 24 --json seeding.json
```

Prints B1 (seeded vs fresh, hop 1), B2 (seeded vs maturity control, hop 1), and
C1 (seeded-vs-fresh margin non-shrink across the resize hop), each PASS/FAIL with
spread and reach-rates, plus the overall `B1 ∧ B2 ∧ C1` verdict.

## 4. Record

Append the confirmatory results (raw per-seed τ, margins, verdicts) to the
Results section of `SEEDING-DIAGNOSIS.md`, write JOURNEY chapter 44, and update
the ROADMAP seeding entry / Doc 06 persistence guidance to match the verdict —
including triggering the reversal condition if seeded loses or the margin shrinks.

## 5. Gate

```bash
./.venv/bin/ruff format --check . && ./.venv/bin/ruff check . && ./.venv/bin/pytest -q
```

All green, none skipped — including the byte-frozen baseline guard
(`tests/integration/test_baseline_unchanged.py`) and the new degenerate-dial
byte-identity tests.
