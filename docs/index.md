---
title: "PRA — Pose Resolution Architecture"
layout: home
---

# PRA — Pose Resolution Architecture

PRA is an **OSS continuously-learning brain for hobbyists and makers**:
a configurable body of sensors and actuators, a fixed innate drive, and
a brain that learns and restructures itself online — it is never
trained-then-frozen. It is a research system, validated at small scale.
What it claims is backed by a measured, reproducible record — runs are
byte-identical on re-run, and an acceptance suite prints honest
PASS/FAIL verdicts with the numbers behind them — and what it cannot do
yet is written down just as plainly (no multi-step planning, no
distributed brain, no tool self-invention; the
[getting-started guide](getting-started.md) keeps the current list).

```bash
uvx --from poseres pra-validate suite   # prove the install learns, in ~a minute
pra-rover                               # watch a brain learn a 2D rover world, live
```

## Start here

- **[Getting started](getting-started.md)** — install, run, hook up
  your own sensors and actuators, configure the drive, snapshots, NATS.
- **[Worlds gallery](worlds.md)** — every shipped world and adapter:
  what it is, how to mount it, and what was measured on it.
- **[Design documents](design/index.md)** — the system specification,
  docs 0001–0008.
- **[Public API & versioning](api.md)** — what v1.x promises, and where
  the frozen surface is defined.
- **[How PRA works — the interactive explainer](explainer/)** — the
  core mechanisms, playable, running the real math in your browser.
- **[The journey](https://github.com/impire-io/poseres/blob/main/hq/04-JOURNEY/README.md)**
  — how the project got here, one numbered episode at a time, including
  the dead ends: the refuted hypotheses are as load-bearing as the
  shipped code.

## Where the claims live

Every capability statement in these docs traces to a journey episode
with the measurement behind it. Where a test fails, the record shows
the FAIL and the numbers that explain it — a failing test is data, not
an embarrassment. The source of truth is the
[repository](https://github.com/impire-io/poseres); this site is built
from it (the design docs and the getting-started guide are copied in at
deploy time, never forked).
