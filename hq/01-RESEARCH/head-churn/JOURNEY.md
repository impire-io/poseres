# head-churn — journey (opened 2026-08-11)

## 2026-08-11 — pilot (8 seeds/arm, drift world unless noted)

Aggregate ruinous share / total trades:

- raw-0.5 (anchor): 0.253 / 202 — reproduces 0091.
- norm-0.5: 0.312 / 202 — normalization HURTS at high eta.
- raw-0.1: 0.191 / 230; norm-0.1: 0.241 / 191 — hurts there too.
- norm-0.05: 0.177 / 141.
- raw-0.02: **0.000 / 58** — perfect refusal; per-seed gems
  [2,1,6,12,17,11,0,9], rate medians 3–9 (lean preserved).
- raw-0.0 (head frozen after replay schooling): **zero trades ever** —
  online learning is what drives trading at all.
- raw-0.02 in the REACTIVE world: ruin 0.225 (80 trades) — the slow head
  cannot track a rate that moves in response to you; stale beliefs trade
  ruinously. The eta dial is a ruin-vs-tracking tradeoff, fully mapped:
  fast churns (drift 0.25), slow goes blind (react 0.225), zero goes inert.
- C4 pilot (4 seeds, sample-field taught+lived at eta): 0.02 keeps the
  completion-itch pathway working (gains 325–427 vs 416–478 at 0.5, all
  alive) — dense-event teaching survives a slow head.

**Frozen recipe for the confirmatory: raw features, eta = 0.02, no
normalization** (normalization refuted at pilot — worse in every pairing).
The reactive-world ruin (no registered bar constrains it) will be reported
in the verdict as a named boundary, not hidden inside a pass.
