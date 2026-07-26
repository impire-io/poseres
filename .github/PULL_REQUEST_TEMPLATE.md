# What this is

<!-- One or two sentences. If it implements an issue, link it. If it
touches core behavior and there was no prior conversation, expect the
first review round to be that conversation. -->

## The non-negotiables

<!-- These come from the project constitution (hq/00-GENESIS/
constitution.md). Check them because they are true, not to make the
boxes green — the gate re-checks most of them mechanically. -->

- [ ] **Gate green, zero skips** — ran locally and everything passed:
  `./.venv/bin/ruff format --check . && ./.venv/bin/ruff check . && ./.venv/bin/pytest -q`
- [ ] **Additive / opt-in only** — no existing mode's RNG stream,
  behavior, or serialized summaries move (constitution I); new
  capability is off unless explicitly enabled
- [ ] **Surface inventory** — if the public surface grew, both
  `tests/contract/surface_inventory.py` and
  `hq/02-DESIGN/0008-public-api-versioning.md` are updated together
  (or: the surface did not grow)
- [ ] **Honest claims** — any measured claim in this PR shows spreads,
  not bare means; FAILs are shown with the numbers that explain them
  (constitution II)

## How I tested it

<!-- Beyond the gate: what did you actually run, with which seeds, and
what did you observe? For a new world: the determinism check and what
the brain's telemetry did on it. -->
