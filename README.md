# PRA — Pose Resolution Architecture

An in-memory, batched, deterministic core (PRA-01) and the validation harness
(PRA-02) that runs the acceptance suite **T1–T6** plus the investigatory
**T-SCALE**, emitting an honest, reproducible PASS/FAIL verdict per test.

New here? **[GETTING-STARTED.md](GETTING-STARTED.md)** walks you from install
to hooking up your own sensors/actuators and configuring the drive — or just
run `pra-rover` and watch a PRA brain learn a 2D rover world, live in your
browser (one command, zero extra dependencies, byte-reproducible).
**[hq/03-IMPLEMENTATION/roadmap.md](hq/03-IMPLEMENTATION/roadmap.md)** is where the project is going: an OSS
continuously-learning brain for hobbyists and makers.

See `specs/001-validation-harness/` for the spec, plan, and contracts, and
`hq/02-DESIGN/` for the architecture documents. The behavioral oracle is
`hq/02-DESIGN/validate/pra_sim_v4.py`.

## Quickstart

**Fastest — install from PyPI with [`uv`](https://docs.astral.sh/uv/):**

```bash
uvx --from poseres pra-validate suite
```

No Python version juggling, no venv to manage. `uv` fetches Python 3.13 automatically if you don't have it.

**From source:**

```bash
git clone https://github.com/impire-io/poseres.git
cd pra
python3.13 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"            # numpy + pytest + ruff

pra-validate suite                 # 8 seeds, true_dim=3, checkpoints 18/30/50
pra-validate suite --json out/report.json
pra-validate determinism --seed 1  # byte-identical re-run check
pra-validate scale --true-dims 20,35,50
pra-validate scan --true-dim 20 --hidden-sizes 12,32,64   # diagnostic dimension scan
pra-validate agency                # curious vs random (T7) + value-signal telemetry

ruff format --check . && ruff check . && pytest -q
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

## Documentation

The docs site — getting started, the design documents 0001–0008, a
worlds gallery, and the public-API promise — lives at
**<https://impire-io.github.io/poseres/>**. It is built from this
repository by `.github/workflows/docs.yml`: the committed pages under
`docs/` plus build-time copies of `hq/02-DESIGN/*.md`,
[GETTING-STARTED.md](GETTING-STARTED.md), and the interactive
explainer — the repo holds exactly one copy of each document, and
`tests/unit/test_docs_site.py` guards every file the site references.

## Public API & versioning

From v1.0 the public surface is a promise: everything listed in
[Doc 0008](hq/02-DESIGN/0008-public-api-versioning.md) — the world/body
seam, anatomy, drives, persistence, the run surface, the CLI tools, and
the versioned subject space — is stable for all of v1.x (patch = fixes,
minor = additive only, removals only at a major after a deprecation
grace). The list is machine-enforced by the surface guard in the test
gate; everything not listed is internal by default. See
[CHANGELOG.md](CHANGELOG.md).

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
  world/               # EventSource seam + SensorimotorWorld + the complexity-ladder worlds
  core/                # contracts, bus, scorer, policies, the batched FrameGroup kernel, engine
  motivation/          # Drive seam: curiosity (learning progress + novelty), competence, weighted set
  action/              # Policy seam: pinned random baseline + one-step curiosity lookahead
  persistence/         # snapshot/restore: versioned blob + atomic SnapshotStore (opt-in)
  anatomy/             # body: sensors/actuators, composition, tools + the Gymnasium and ROS2 adapters
  examples/rover/      # the pra-rover demo: 2D rover body + stdlib live viewer
  telemetry/recorder.py# deterministic per-seed summary
  harness/             # acceptance (T1-T7/T-SCALE), runner, report, cli, scale, scan, agency, ladder
examples/              # worked examples (CartPole via Gymnasium; a Gazebo rover via ROS2, in Docker)
tests/                 # unit (incl. batched-vs-reference proof) / contract (5 seams) / integration
```

## Behavioral oracle

`hq/02-DESIGN/validate/pra_sim_v4.py` is the validated reference run. The batched core
reproduces its T1–T6 trajectory at the default config (the per-frame-vs-batched
equivalence is enforced by `tests/unit/test_batched_equivalence.py`) at roughly 40×
the speed. The full default suite (8 seeds × predictive + ablation × 50 cycles)
completes in well under a minute.

## Contributing

New worlds, sensors, actuators, and drives are the on-ramp — the public seams
they mount through are frozen for all of v1.x ([Doc 0008](hq/02-DESIGN/0008-public-api-versioning.md)).
[CONTRIBUTING.md](CONTRIBUTING.md) has the seams, the worked examples, the gate, and the rules.
