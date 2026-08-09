# Quickstart: The Event Pathway (feature 040)

Give the brain a second, sharp way of expecting what its actions do — and a
policy that wants to finish what it starts. Measured provenance: motivation-
stack G3 (episode 0071): election 24/24, chains 13/24 (double the oracle),
progress-prediction error 0.0081 vs the frames' 0.0612.

## Enable the head

```python
from pra import Config, Engine

config = Config(
    # ... your run configuration ...
    event_head_eta=0.5,   # 0.0 (default) = off, byte-identical behavior.
                          # 0.5 is the G3-measured operating point.
)
```

That is the whole switch. The head learns online from every executed
transition, costs O(actions · obs_dim²) per directed step, consumes no
randomness, and travels in snapshots like the rest of the brain. Old blobs
resume fine — the head cold-starts when the blob predates it.

## Run the completion itch

```python
from pra.action.policy import CompletionItchPolicy, PolicyParams
from pra.anatomy.minecraft import C1_MINING_INDEX, C1_POCKET_TOTAL_INDEX

policy = CompletionItchPolicy(
    PolicyParams.from_config(config),
    kappa=0.25,                        # G3-measured
    progress_index=C1_MINING_INDEX,    # your anatomy's sensed progress channel
    pocket_index=C1_POCKET_TOTAL_INDEX,# your anatomy's acquisition channel
    # completion_threshold=1/128,      # half an item at C1's 1/64-per-item scale
    # potential_of=my_hold,            # optional per-action "stay near the work" term
)
engine = Engine(config, policy=policy, ...)
summary = engine.run(seed)

print(policy.completions_fired, policy.false_completions,
      policy.progress_pred_error_ema)   # the honesty watch
```

Notes worth knowing (all measured):

- The itch **composes**: itch-only wanders (G1's control arm: 2/8 dug, none
  chained). Pair it with something that keeps the agent near its work — the
  `potential_of` seam exists for exactly that.
- With the head **off**, the itch term is inert and the policy behaves as the
  curiosity lookahead — safe to construct unconditionally.
- The completion rule generalizes: any action whose predicted pocket gain
  clears the threshold counts as completing — crafting became itchy in G3
  without anyone designing it. Watch `false_completions` if you change the
  threshold.

## Verify your setup

```bash
./.venv/bin/pytest tests/unit/test_event_head.py \
                   tests/unit/test_completion_itch_policy.py \
                   tests/integration/test_event_pathway.py -q
```
