# Episode 0072 — The event pathway ships: the brain keeps its expectations (2026-08-09)

Feature 040 (`specs/040-event-pathway/`, branch `040-event-pathway`,
v1.2.0): the measured G3 mechanism (episode
[0071](0071-wanting-follows-expecting.md)) moved from scratchpad
prototype to product, through the full spec-kit lifecycle, the morning
after its gate passed. The owner's word — "build it for real" — is the
license episode 0071 recorded as pending.

**What shipped:**

- **The event head as brain state** — per-action normalized-LMS delta
  models over all sensed channels, owned by the FrameStore beside the
  frames (the channel-weighting precedent), learning once per executed
  transition at the engine's step-loop site — the only call site that
  sees the continuous-mode boundary transitions the measured instrument
  learned from `[mechanism-argument, verified by the updates == obs_steps
  test]`. Config-gated by `event_head_eta` (0.0 = off: no state, no
  float work, no RNG — byte-identity proven by test, the pinned baseline
  untouched). The head persists in snapshots (additive-optional key,
  head-off blobs bit-identical), cold-starts on pre-040 blobs, and
  resizes with the anatomy zero-initialized, drawing nothing.
- **`CompletionItchPolicy`** — the measured gate policy generalized:
  drive + optional injected per-action potential + κ·(progress_after −
  progress_now), the itch read through the new
  `PolicyContext.predict_event_delta` accessor with the learnable
  completion rule. Channel indices are constructor knowledge (the
  Minecraft anatomy now exports `C1_MINING_INDEX`/`C1_POCKET_TOTAL_INDEX`,
  derived, never literal); the hold stays caller-injected because the
  clone-step potential is research instrumentation, not brain. The
  honesty watch ships bounded: completions fired, false completions,
  progress prediction-error EMA.
- **Surface**: additive only — v1.1.0 → v1.2.0, inventory + Doc 0008
  both directions, Docs 0005/0007 updated. 25 new tests; full gate
  green throughout.

**The closure `[measured]`:** episode 0071's reversal condition — "the
src-built event head fails to reproduce Bar A at its own gate" — was
answered the same day at a stronger standard than it asked for. The G3
confirmatory rerun on shipped components reproduced the prototype's
confirmatory **row for row**: every seed's logs, chain ticks, dwell,
completion counters, and prediction errors identical (Bar P 0.0081,
Bar A 24/24 with 303 logs, Bar B 13/24, 812/1,957 false completions,
159 s). Not bar-level replication — behavioral identity: the shipped
pathway computes the measured instrument's floats in its order. The
house replication standard (P0, bar-level) was the floor; exact
identity removes the instrument-vs-mechanism question entirely.

**What it changed beyond the record:** the prototype's head relearned
from zero every run; the shipped head is snapshot state — a long-run
brain now *keeps* its learned expectations across restarts. That is new
capability the gates never measured (they ran fresh worlds), noted
here as an open observation, not a claim.

**What it opened:** G5 — approval revisited — is the queue's unblocked
front (layer 5's prerequisite now exists *in the product*); G2/G4
behind it; E2.1 refinements compete on top of a shipped mechanism. The
sparse-event regime (approval pulses, orders rarer than dig ticks) is
the named risk the NLMS head has not yet faced.

Reversal condition: the off-default is load-bearing — if any v1.2.x
reading shows the disabled head changing a validated mode's bytes, the
release is broken and rolls back; and 0071's sparse-regime condition
stands unchanged (a G5-style gate failing to form expectations under
this architecture splits "event-sensitive" into dense/sparse designs).

Trail: `specs/040-event-pathway/` (spec e501b12, plan 85abb5d, tasks
ed3012f, implementation 60a7322); closure recorded in
`hq/01-RESEARCH/motivation-stack/README.md` (this change-set); runner
`src_closure.py` + `src-closure-rows.json` (session scratchpad);
episodes [0071](0071-wanting-follows-expecting.md),
[0070](0070-the-first-elected-chains.md).
