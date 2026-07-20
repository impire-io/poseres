# Contract: `pra-validate seeding`

The feature's external interface is one CLI subcommand plus the config dials it
sets. This is the contract `tests/contract/test_seeding_cli.py` verifies.

## Command

```
pra-validate seeding [--seeds N|CSV] [--mode pilot|confirmatory] [--json PATH] [--config JSON]
```

| Flag | Meaning | Default |
|---|---|---|
| `--seeds` | seed count (e.g. `24`) or explicit CSV (`1,2,3`) | `24` |
| `--mode` | `pilot` (calibrate θ/budgets, no verdict) or `confirmatory` (frozen values, decide bars) | `confirmatory` |
| `--json` | also write the machine-readable report to PATH | off (human-readable to stdout) |
| `--config` | JSON overrides for pilot-set budgets/θ (used to *record* the frozen values) | reads frozen table |

**Determinism**: a given `(--seeds, --mode, frozen table, commit)` reproduces
byte-identical output. The command mutates no repository state except the report
files it is told to write.

## Human-readable output (stdout)

Per bar, the acceptance-verdict line shape already used by the suite:

```
B1  seeded reaches θ_B before fresh        margin +X.X ± Y.Y (SE Z.Z) vs +1.9·SE=+B.B   [PASS|FAIL]
    better in n/24 seeds; reach-rate seeded r1, fresh r2
B2  seeded reaches θ_B before maturity     ...                                          [PASS|FAIL]
C1  head start does not shrink (B→resize→C) margin2 +.. ; delta +.. ≥ −1.9·SE=..        [PASS|FAIL]
OVERALL  seeding holds: B1 ∧ B2 ∧ C1                                                    [PASS|FAIL]
```

Spreads and reach-rates are always printed; a mean is never printed alone.

## JSON output (`--json`)

```json
{
  "mode": "confirmatory",
  "seeds": [1, "...", 24],
  "frozen": {"N_pretrain": 0, "N_probe": 0, "theta_B": 0.0, "theta_C": 0.0, "W_smooth": 0, "p": 0.5},
  "readings": [
    {"arm": "seeded", "seed": 1, "map": "B", "theta": 0.0, "tau": 0, "reached": true, "final_error": 0.0}
  ],
  "margins": {
    "margin1": {"mean": 0.0, "std": 0.0, "se": 0.0, "n_better": 0, "n": 24, "per_seed": []},
    "marginM": {"...": "..."},
    "margin2": {"...": "..."},
    "delta":   {"...": "..."}
  },
  "reach_rates": {"seeded_B": 0.0, "fresh_B": 0.0, "maturity_B": 0.0, "seeded_C": 0.0, "fresh_C": 0.0},
  "bars": [
    {"bar": "B1", "verdict": "PASS", "mean": 0.0, "se": 0.0, "bound": 0.0, "note": "..."},
    {"bar": "B2", "verdict": "PASS", "...": "..."},
    {"bar": "C1", "verdict": "PASS", "...": "..."}
  ],
  "overall": "PASS"
}
```

## Contract guarantees (tested)

1. `--mode pilot` never prints a bar verdict (it reports the calibration read only).
2. `--mode confirmatory` prints all three bars and the overall verdict, always with
   spread + reach-rate.
3. Every reading carries `reached`; censored readings have `reached=false` and
   `tau == N_probe`.
4. Margin signs follow "positive = seeded faster" (τ is lower-is-better).
5. Running the command leaves the reference suite byte-identical (no engine/core
   mutation; the byte-frozen baseline test stays green).
