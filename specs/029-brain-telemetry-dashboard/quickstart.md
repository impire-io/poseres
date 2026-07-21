# Quickstart: Brain Telemetry & Introspection Dashboard (feature 029)

## The gate (no broker, no browser)

```bash
./.venv/bin/ruff format --check . && ./.venv/bin/ruff check . && ./.venv/bin/pytest -q
```

Everything this feature claims is proven on the in-repo fake transport:
`tests/contract/test_brain_subjects.py`, `tests/integration/
test_brain_telemetry_run.py`, the dash tests, and the untouched
byte-frozen suite.

## See it live (the C1 stack)

```bash
cd examples/minecraft && ./up.sh          # world + nats + bridge + dash + brain
```

Open the dashboard (auto-opened, else http://127.0.0.1:8600), select the
run, and open the **Brain** tab:

- **Anatomy** — the body drawn from its published metadata: sensor groups
  (pose/vitals/env/blocks) with live per-channel activity bars, actuator
  nodes with the chosen action highlighted as the brain acts.
- **Channels** — named strip charts per group + the scrolling decoded log.
- **Frames** — every frame: id, dim, age, errors, score; the best frame
  marked.
- **Lifecycle** — spawn/evict timeline from your attach point onward.

Any other world works the same way: `python examples/nats/brain.py`
(reference world → generic labels, structural fallback), the rover demo,
or the Gymnasium adapter — same tab, zero body-specific dashboard code.

## SC-006 (live soak, not a gate test)

Accelerated posture: `TICK_RATE=80 ./up.sh --tick-ms 62`, leave the Brain
tab open ≥1 h: the page must stay live (bounded lag, bounded memory —
the model's windows are maxlen-bounded by construction).
