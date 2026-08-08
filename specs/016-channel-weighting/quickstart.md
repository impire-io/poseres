# Quickstart: Learned Channel Weighting

## Turn it on

```python
from pra.config import Config
from pra.core.engine import Engine

cfg = Config(
    world="distractor",
    true_dim=3,
    obs_dim=20,
    distractor_dim=3,
    distractor_channels=10,
    distractor_mode="noise",  # the recorded L3 FAIL configuration
    channel_weight_floor=0.2,  # 0.0 = off (default); 0.2 = the measured recommendation
)
summary = Engine(cfg).run(seed=1)
print(summary.best_dim, summary.canonical().get("channel_weighting"))
```

`channel_weight_floor=0.0` (the default) is the pinned validated build,
byte for byte. Anything greater turns the estimator on; the value is the
weight floor — no channel is ever silenced below it.

## Through the ladder harness

```bash
cat > /tmp/cw.json <<'EOF'
{"channel_weight_floor": 0.2}
EOF
./.venv/bin/pra-validate ladder --rungs l3 --config /tmp/cw.json
```

The report echoes the two feature parameters in its config block when on.

## What to expect

- On worlds with no static (reference, structured distractors) the weights
  sit near 1 and behavior is measurably unchanged (E4 bars).
- On the L3 noise rung the static channels converge to the floor within
  ~5 episodes (readiness = 200 steps at the pinned β = 0.995) and the
  survival scores regain their dimensional gradient (the trail doc's E1/E3
  record).
- Snapshots taken with the feature on carry the estimator (`chanw__*`
  keys); resume continues byte-identically. Snapshots with it off are
  bit-identical to the pre-016 format.

## The science trail

`design/validate/CHANNELWEIGHT-DIAGNOSIS.md` — pre-registration, P1/E1
results (recorded), E2/E3/E4 protocols and bars, failure exits. FR-010:
that document is normative for this feature's claims.
