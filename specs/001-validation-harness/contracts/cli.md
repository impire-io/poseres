# Contract: Harness CLI

The harness is the user-facing interface (FR-002, FR-006, FR-007, FR-009, FR-012).
Invocable as `python -m pra.harness.cli <command> [options]` or via the console entry
point `pra-validate`. Text protocol: human-readable summary to **stdout**; errors to
**stderr**; optional JSON written to a file. Exit code `0` if the command ran and
produced a report (even if some tests FAIL — a FAIL is data, not a CLI error); non-zero
only on an execution error (e.g. a seed crashed and the suite could not complete).

> A FAIL verdict is a successful run with a negative result. The CLI MUST NOT translate
> a test FAIL into a non-zero exit unless asked to gate on it (see `--strict`).

## Command: `suite` (default)

Run the full acceptance suite T1–T6 across all configured seeds and emit per-test
verdicts.

```
pra-validate suite [--seeds 1,2,...] [--true-dim 3] [--obs-dim 10]
                   [--checkpoints 18,30,50] [--config PATH]
                   [--json OUT.json] [--strict]
```

| Option | Default | Meaning |
|---|---|---|
| `--seeds` | `1,2,3,4,5,6,7,8` | Comma list; multi-seed is the default (FR-001/FR-012) |
| `--true-dim` | 3 | Hidden true latent dimensionality (harness-only; T4 ground truth) |
| `--obs-dim` | 10 | Observation dimensionality (≥ 3·true_dim recommended) |
| `--checkpoints` | `18,30,50` | Horizon checkpoints for T4 (FR-004) |
| `--config` | none | Path to a config file overriding any PRA-01 §8 default |
| `--json` | none | Also write the machine-readable report (FR-007) |
| `--strict` | off | Exit non-zero if any of T1–T6 FAIL (for CI gating) |

**Output (stdout) MUST include**, for each of T1–T6: the measured aggregate (mean ± std
across seeds), the exact pass criterion, and `PASS`/`FAIL` (FR-002, SC-001, SC-004). For
T4 it MUST additionally print the **per-seed `best_dim` list at each checkpoint** with
within-one and exact counts, and the verdict requires the within-one majority at every
checkpoint (FR-003/FR-004, SC-002). A failing test is shown as `FAIL` with the numbers
that explain it — never hidden or smoothed (FR-008).

## Command: `determinism`

Run one seed twice and assert byte-identical run summaries (FR-006, SC-003).

```
pra-validate determinism [--seed 1] [--true-dim 3] [--config PATH]
```

**Output MUST** report `PASS` if the two summaries are byte-identical, or `FAIL` with a
pointer to the first differing summary/field if not. Any non-zero byte difference is a
hard `FAIL` (Edge Cases: nondeterminism is not averaged away).

## Command: `scale` (investigatory)

Run the T-SCALE investigation at large true dimensionality (FR-009, SC-006).

```
pra-validate scale [--true-dims 20,35,50] [--seeds ...] [--t3] [--config PATH] [--json OUT.json]
```

**Output MUST** emit, per `true_dim`, the per-seed `best_dim` spread, `throughput`
(observation×frame evaluations / s), and wall-clock, and MUST label the section
**INVESTIGATORY**. It MUST NOT report a poor `best_dim` at scale as a build failure;
there is no PASS/FAIL and `--strict` has no effect here.

With `--t3` (ROADMAP A2), the command instead runs the T3 quartet per
`true_dim` — the exact reference triad of PRA-02 §2 (predictive + effort-only
+ identity) under the scaled ecology defaults, plus the churn-matched fourth
arm of the amended scaled criterion (predictive training on the identity
arm's world, no consolidation) — and emits one T3 verdict per scale
(`T3@td=N`, the amended criterion: weak clause from the triad, strong clause
paired churn-matched) with the per-seed quartet improvements, the paired
margins, and the as-written identity counts kept in the record. The context
stays investigatory: the per-scale T3 verdict is data; the command's exit code
never depends on it.

## Single-seed debugging

Any command accepts a single `--seed`/`--seeds X`. When the result is from a single
seed, the output MUST be labelled **FOR DEBUGGING ONLY — not a validation of a
behavioral claim** (FR-012).

## Disk artifacts

The only files the CLI writes are the report summaries (`--json` target, and optionally
a text file). It MUST NOT persist frame/model state (FR-011).
