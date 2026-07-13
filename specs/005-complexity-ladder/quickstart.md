# Quickstart: The Complexity Ladder

## Run the whole ladder (all implemented rungs, 8 seeds)

```bash
./.venv/bin/pra-validate ladder --json ladder-report.json
```

One report: per rung — configuration, per-seed readings, the
pre-registered criterion, and a PASS/FAIL verdict that is *data*
(exit code is 0 either way; a failing rung is a finding).

## Run one rung with explicit dials

```bash
# L1 — the noisy-TV region (strong dial)
./.venv/bin/pra-validate ladder --rungs l1 --config - <<'EOF'
{"world": "nonuniform", "region_noise_std": 0.6}
EOF

# L2 — three parts of two dimensions each
./.venv/bin/pra-validate ladder --rungs l2 --config - <<'EOF'
{"world": "compositional", "true_dim": 6, "obs_dim": 18, "factor_dims": [2, 2, 2]}
EOF

# L3 — structured distractor: 3 hidden dims over 10 of 20 total channels
# (obs_dim is the total, system-visible width; controllable core = 10)
./.venv/bin/pra-validate ladder --rungs l3 --config - <<'EOF'
{"world": "distractor", "obs_dim": 20, "distractor_dim": 3,
 "distractor_channels": 10, "distractor_mode": "structured"}
EOF
```

## Use a ladder world directly (library / drive research)

```python
from pra.config import Config
from pra.core.engine import Engine
from pra.world.ladder import make_world

cfg = Config(world="nonuniform", region_noise_std=0.6,
             policy_mode="curiosity",
             drive_weights=(("competence", 1.0),))
summary = Engine(cfg, world_factory=make_world).run(seed=1)
```

This is the A4 entry point: ladder worlds mount through the same seam as
the reference world, so drives, bodies, and snapshots work unchanged.

## Where the readings live

- Occupancy (L1), census (L2), and per-checkpoint `best_dim` (L3) are in
  the ladder report (text and `--json`).
- The criteria — and the first recorded results, including failures —
  live in `design/validate/LADDER-CRITERIA.md`.

## What to expect

- `world="reference"` (the default) is byte-identical to the validated
  system; every rung at its degenerate dial is byte-identical too (and
  tested).
- Ladder verdicts never fail a build. They tell you where the brain is
  on the staircase — that is the product.
