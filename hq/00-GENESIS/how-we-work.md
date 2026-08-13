# How we work

The process companion to [`constitution.md`](constitution.md): the pipeline,
the lifecycles, the duties, and how all of it is enforced. `hq/README.md`
holds the one-screen map.

## The pipeline

```
question ──/research-start──▶ 01-RESEARCH/<slug>/     (state: active)
                                   │
                     /research-graduate <slug>
                        │            │           │
                     design       artifact    abandoned
                        │            │           │
                        ▼            │           │
              02-DESIGN/NNNN-*.md    │           │
                        │            ▼           ▼
               /speckit-specify   04-JOURNEY episode (always; folder removed)
                        │
                        ▼
        specs/NNN-*/ + code  ──landed──▶ /journey-log episode
                        │                      + roadmap.md updated
                        ▼
        design docs updated (behavioral changes propagate back)
```

Two hard boundaries:

- **Research never goes through spec-kit.** Spec-kit assumes you know what
  you're building; research exists to find out whether to build. Research
  uses the pre-registration method below. (The repo's own history settled
  this: arcs that used the spec-kit scaffold drifted away from it.)
- **Implementation always goes through spec-kit.** A design doc in
  `02-DESIGN/` is written to be the argument to `/speckit-specify`; the
  generated plan's Constitution Check reads GENESIS through the
  `.specify/memory/constitution.md` symlink.

## Research (`01-RESEARCH/`)

One folder per topic, created with `/research-start <slug>`. The folder's
`README.md` (from `../01-RESEARCH/TEMPLATE.md`) carries: Title, State
(`active | graduated | abandoned`), Abstract, the Question, and
**pre-registered bars** — the pass/fail criteria written *before* any
experiment runs. The folder's `JOURNEY.md` records the investigation as it
happens.

- **Method:** hypothesis → cheap discriminating experiment → verdict, one
  variable at a time (constitution III). Experiment scripts live in the
  session scratchpad; conclusions, documents, and principled code changes
  land in git.
- **Evidence comes from the real world — and nothing is faked**
  (owner's rule 2026-08-13, hardened the same day: "I don't want you to
  fake anything anymore"): pilots, gates, and the adapter contract all
  run against the live environment. A live pilot is cheap (a 1,500-step
  segment is ~2 minutes at the 5× fabric); a fake pass is not evidence.
  The FakeBridge estate was deleted outright — the adapter's proof is
  the live contract check (`examples/minecraft/contract_check.py`).
- **Always committed and pushed** — even work that will be abandoned. The
  point is a permanent trail; abandoned research keeps its full history in
  git after the folder is gone.
- **Ending:** `/research-graduate <slug> --to design|artifact|abandoned`
  composes the topic's journey into the next-numbered `04-JOURNEY/` episode
  (verdict, evidence tags, reversal condition included), creates or updates
  the design doc when the outcome is a design, and removes the topic folder
  in every case. An abandoned topic is a *result*, recorded with the same
  care as a success.

## Design (`02-DESIGN/`)

Numbered documents (`0001-…` onward) describing architecture and features at
the functional level — explicit enough that `/speckit-specify` can turn one
into a spec without guessing: the capability, its seams, its configuration
surface, its acceptance criteria. `validate/` holds the normative
specifications (PRA-01, PRA-02), the founding bet
(`pose-resolution-architecture.md`), and the `*-DIAGNOSIS.md` evidence
trails. Every behavioral change made during implementation propagates back
into the design docs it touches — the docs describe the system as it *is*.

## Implementation (`03-IMPLEMENTATION/` + `specs/`)

`roadmap.md` is the live plan: phases, milestones, exit criteria, and the
research gate each milestone depends on. No dates — gates, not calendars.
Features run the spec-kit flow (`/speckit-specify` → clarify → plan → tasks →
implement) on a numbered feature branch; `specs/NNN-*/` artifacts freeze when
the feature lands. Landing a feature means: gate green (constitution VI),
roadmap updated, journey episode written, design docs propagated — in the
same merge.

## Journey (`04-JOURNEY/`)

The append-only log: one numbered episode (`NNNN-slug.md`) per landed
feature, concluded research topic, or load-bearing decision — written with
`/journey-log` (or `/research-graduate`, which writes it for research). The
`TEMPLATE.md` requires: what happened with the honest numbers, what was
refuted or reversed, evidence-class tags on load-bearing claims, and a
**Reversal condition** line. `README.md` carries the preamble, the episode
index, and the "Where things stand" summary — both refreshed with every
episode.

## The working agreement (anti-drift)

The four correctives are constitution articles (see The Working Agreement
there); this is how they run day to day:

- **When to teach-back:** any decision that changes direction, scope, a
  criterion, or a public claim. The assistant asks for the restatement; the
  decision is recorded only after it survives.
- **Tagging:** write `[measured]` / `[mechanism-argument]` / `[judgment]`
  inline where the claim is made — in conversation, in episodes, in design
  docs. If a debate is being closed by anything other than `[measured]`,
  stop and say so.
- **Reversal conditions:** phrased as observable evidence ("a reading
  showing X", "N features without Y"), not vibes. Written at decision time,
  never retrofitted.
- **Adversarial pass:** for vision-level calls the assistant argues the
  other side at full strength *before* the decision — or the question goes
  to an outside reader.

## Recurring principles (what the journey keeps teaching)

- **Senses first.** When something new seems needed, the first question
  is never "what mechanism do we add?" — it is "**what sense is
  missing?**" (owner's rule, 2026-08-11). The measured record keeps
  vindicating it: approval was a sense (the verdict channel, episodes
  0057/0073), hunger reaching wanting was a sense plus six lines (the
  felt meal, 0083), wealth was a sense (`pocket_index` names which one,
  0088), and worth itself was a *learnable* sense (the tongue, 0089) —
  while every mechanism-shaped alternative either failed its bars or was
  never needed (the splice, 0086/0087). The brain stays generic; new
  capability walks in through the body. Only when a sense-first design
  measurably fails its gate is new machinery licensed — which happened
  for the first time the day the rule was written down: sensing a moving
  price is not timing it (episode 0090), and the richer predictor was
  licensed by those numbers, exactly as the rule intends.
- **The fake world convinces; the real one refutes.** (Owner's rule,
  2026-08-13.) Three arcs in a row, effort was spent on behavior the fake
  bridge blessed and Minecraft broke: c1e's digs are client-wall-clock and
  its drops far-scatter (amendments 1/1b, 2026-08-11), teaching state
  leaked through bridge-virtual hands and split samples (native-survival
  amendments 2/3), and the same taught brain that ate 5× in the fake
  pilot ate zero times live (the parked stomach, 2026-08-13). Behavioral
  evidence is live-world evidence, full stop. The fake bridge's only
  remaining job is the automated quality gate's adapter-code-path checks
  — and the same day the owner hardened it to its clean form: no fake
  anything, anywhere; the estate was deleted and the adapter's proof
  moved to a live contract check.
- **Diagnose before fixing; one variable at a time.** The true mechanism
  shows up only after the obvious story is refuted with data.
- **Reference-preserving changes.** Every rule and layer keeps validated
  behavior byte-identical; regressions become structurally impossible, not
  merely unlikely.
- **Honest criteria, amended openly.** When a pass-bar proves degenerate, it
  is replaced in the open with the raw numbers recorded.
- **Negative results are results.** "Curiosity hurts at scale" produced the
  project's best positive finding one experiment later. The c1c run's
  pre-registered null (episode 0068) is the pattern at full size: because
  the bar, baseline, and duration were fixed before boot, "no emergence"
  is a publishable measurement, not a disappointment to dress up.
- **Watch items need detectors, not visits.** A pre-registered watch item
  checked by periodically looking at a dashboard is a watch item that will
  be missed: c1c's first-mined-log event went unseen for thirteen days
  because the watch lived in the visitor, not the pipeline (episode 0068).
  If an event matters enough to register, a detector runs on the stream
  and raises its hand when it fires.
- **The observer is part of the experiment.** In 17 days of c1c the
  subject crashed zero times; the instrumentation crash-looped 14 times
  and then filled its own disk, expiring 57,219 steps of the record
  (episode 0068). Observability gets the same engineering care as the
  system it watches: its disk is budgeted, its stores are pruned, and its
  loss modes are visible by design.

## Enforcement (how this stays true without willpower)

1. **The constitution symlink.** `.specify/memory/constitution.md` →
   `hq/00-GENESIS/constitution.md`, so every spec-kit plan is checked against
   GENESIS mechanically.
2. **The structural lint.** `tests/test_hq_structure.py` rides the standard
   gate (locally and in CI): hq layout, research-state legality, episode
   numbering and required fields, index completeness, symlink health, and
   that relative links inside `hq/` resolve.
3. **The skills.** `/research-start`, `/research-graduate`, `/journey-log`
   make the transitions one command each, so the right order is the easy
   order. They stage explicit paths, commit signed, and never push — pushing
   stays a human act.
4. **Orientation.** Root `CLAUDE.md` and `AGENTS.md` point every session
   here first.

## Quality gates (the non-negotiables, in one place)

- Gate: `./.venv/bin/ruff format --check . && ./.venv/bin/ruff check . && ./.venv/bin/pytest -q`
  — all green, nothing skipped, before any "done".
- Use the repo venv (`./.venv/bin/python`); the system interpreter is
  PEP-668-managed.
- Sign every commit. Never commit `.claude/settings.local.json`.
- The byte-frozen baseline (constitution I) and honest measurement
  (constitution II) apply to every change, product or research.
