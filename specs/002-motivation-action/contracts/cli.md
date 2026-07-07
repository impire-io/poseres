# Contract: `pra-validate agency` command

The T7 measurement runs as its own command so the T1–T6 regression gate stays
exactly as validated (plan: Complexity Tracking). Text protocol, exit-code
semantics, and honest-summary rules are identical to the existing commands.

## Command: `agency`

Run the curious-vs-random comparison (T7) across all configured seeds and emit
an honest verdict.

```
pra-validate agency [--seeds 1,2,...] [--true-dim 3] [--config PATH]
                    [--json OUT.json] [--strict] [--workers N]
```

| Option | Default | Meaning |
|---|---|---|
| `--seeds` | `1,...,8` | Comma list; multi-seed default; single-seed runs carry the FOR-DEBUGGING-ONLY label |
| `--true-dim` | 3 | Reference world dimensionality (T7 is validated at the reference scale first) |
| `--config` | none | JSON config overriding any parameter (incl. drive/policy params) |
| `--json` | none | Also write the machine-readable report |
| `--strict` | off | Exit non-zero if T7 FAILs (CI gating) |
| `--workers` | 0 (auto) | Parallel seed processes; never changes results |

**Per seed** the harness runs two full predictive runs with the **same seed** —
identical world and schedule, equal experience — one under
`CuriosityLookaheadPolicy`, one under `RandomPolicy` (research R7).

**Output (stdout) MUST include:**
- the T7 claim, the exact criterion (`curious improvement ≥ random improvement
  in a strict majority of seeds`), and PASS/FAIL;
- the **per-seed table**: curious improvement, random improvement, margin —
  never a mean alone (FR-009);
- agency telemetry for the curious arm: mean value signal, mean
  learning-progress and novelty terms, directed-action fraction (FR-010);
- the FOR-DEBUGGING-ONLY banner for single-seed runs.

**JSON:** `mode: "agency"`; a `tests[]` entry with `id: "T7"` and a
`t7_detail` block carrying the per-seed arrays; `run_metadata` as in the
existing schema. (Schema addition is versioned as a superset: existing fields
and semantics are unchanged.)

**Exit code:** 0 when the command ran and produced a report (a FAIL verdict is
data); non-zero only on execution error, or on FAIL with `--strict`.

## Unchanged commands

`suite`, `determinism`, `scale`, and `scan` accept no new flags and behave
byte-identically to the validated build (FR-008). `suite` does not run T7.
