# PRA Constitution

The canonical copy of this file lives at `hq/00-GENESIS/constitution.md`;
`.specify/memory/constitution.md` is a symlink to it, so every spec-kit plan's
Constitution Check reads these articles. Decisions are held against this file
and [`vision.md`](vision.md) — see the decision test in [`README.md`](README.md).

## Core Principles

### I. Reference-Preserving Forever (NON-NEGOTIABLE)

The validated behavior is byte-frozen. Every change keeps the T1–T6 suite
under the pinned random baseline reproducing the recorded reference values
exactly (`tests/integration/test_baseline_unchanged.py` guards seed 1). New
capability is opt-in and leaves existing modes' RNG stream, behavior, and
serialized summaries untouched. Scale-dependent constants ship as effective
forms whose factors are exactly 1 at the validated reference scale. This
article does not relax for product work.

### II. Honest Measurement

Report spreads, never a bare mean where a spread is required. A FAIL is data,
shown with the numbers that explain it. Exit criteria are written down
*before* the work; if a criterion proves degenerate it is amended openly with
the raw measurements recorded — never tuned quietly until green. Negative
results are results. Every public artifact links the telemetry behind it.

### III. Diagnose Before Fixing

For behavioral problems: hypothesis → cheap discriminating experiment → only
then a principled fix — one variable at a time, with the trail recorded in a
`hq/02-DESIGN/validate/*-DIAGNOSIS.md` document. Research experiments live in
the session scratchpad, not the repo; only conclusions, documents, and
principled code changes land in git.

### IV. Research Gates Before Showcase Spends

The bottleneck is the brain, not the plumbing. Every user-facing milestone
names the research gate it depends on, and no demo outruns measured
capability. A showcase of a visibly flailing brain makes the project look
broken, not promising.

### V. Never Lose the Instrument Panel

Every new world keeps known ground truth, determinism, and steppable time
until the science says the brain is ready for worlds without them. Real-time
worlds come last: they run at 1× and can't be replayed.

### VI. All-Green Quality Gate

Done means the full gate is green with nothing skipped:
`./.venv/bin/ruff format --check . && ./.venv/bin/ruff check . && ./.venv/bin/pytest -q`
(which includes the hq structural lint). Use the repo venv; sign every
commit. Hook or gate failures are blocking — fixed before anything else
continues.

## The Working Agreement (Anti-Drift)

Adopted 2026-07-19 (journey 0042) after a live instance of the failure mode
it guards against: a fluent counterpart steering a maintainer who cannot
independently check the science, without either party intending it. Applies
to every load-bearing decision.

1. **Teach-back as a gate.** No load-bearing direction decision is recorded
   until the maintainer can restate the argument for it in his own words. If
   he can't, the decision isn't ready — the deficit is in the explanation,
   not the listener.
2. **Claims carry their evidence class.** Every load-bearing claim is tagged
   **[measured]** (a reading in the repo), **[mechanism-argument]** (a
   reasoned case, attackable by reasoning), or **[judgment]**. Only measured
   closes a debate.
3. **Decisions record the reversal condition.** Every direction decision gets
   a "what would change our minds" line written *when the decision is made*
   (the journey episode template requires it), so a future reversal is a
   clean, anticipated turn instead of drift.
4. **Adversarial pass on direction changes.** For vision-level calls, the
   other side is argued at full strength before the decision — the maintainer
   never sees only the most convincing case.

## Development Workflow

Work flows through `hq/` as described in [`how-we-work.md`](how-we-work.md):
research (`01-RESEARCH/`, lifecycle active → graduated | abandoned) → design
(`02-DESIGN/`, functional specs explicit enough for `/speckit-specify`) →
implementation (the spec-kit flow specify → plan → tasks → implement on a
numbered feature branch, tracked in `03-IMPLEMENTATION/roadmap.md`) → journey
(`04-JOURNEY/`, one numbered episode per landed feature, concluded research
topic, or load-bearing decision). Research never goes through spec-kit;
designs always do. Every behavioral change propagates into the design docs it
touches.

## Governance

This constitution supersedes all other practices. An amendment requires: the
explicit textual change, a semantic version bump (MAJOR: article removed or
redefined; MINOR: article added or materially extended; PATCH: clarification),
a journey episode recording the why and the reversal condition, and
propagation into any spec-kit template that depends on the changed text.
Spec-kit plans verify compliance through the Constitution Check; reviews call
out violations rather than accommodate them.

**Version**: 1.0.0 | **Ratified**: 2026-07-20 | **Last Amended**: 2026-07-20
