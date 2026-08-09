# Episode 0074 — The last scaffold falls: the hold goes brain-side (2026-08-09)

The topic opened and closed inside one afternoon, part of the owner's
parallel-and-autonomous grant. The question: the measured
stay/want/finish composition carried one piece of laboratory equipment —
the hold's Φ read the position after a candidate action from a
deep-copied world, an oracle no deployed brain can have. Can the shipped
event head (feature 040), which predicts per-action observation deltas,
supply Φ̂ from the brain's own model instead:
`Φ̂(a) = 64 · Chebyshev(obs[x,z] + Δ̂ₐ[x,z], goal[x,z])`, the goal being
the taught goal observation's position channels?

**The verdicts (24 G5 graduates, H = 5,000, λ = 0.25, 308 s both arms):**

- **H1a — the hold survives de-scaffolding: PASS, median dwell 98.22%**
  (bar ≥ 20%; clone reference 99.98%) `[measured]`. The mechanism is
  visible in the registered context row: the graduates' heads had never
  seen forward/back (the tape holds only turns), so movement models
  started cold — median dwell 91.5% over the first 1,000 steps rising to
  **100.0%** over the last 1,000. The head learns its own locomotion
  from ε-exploration inside the first fifth of the run, then holds at
  the clone's level.
- **H1b — the composition survives: PASS, 23/24 chains** (bar ≥ 6/24;
  clone reference 24/24), 647 logs, 1,919 sticks `[measured]`. Drive
  from the frames, hold from the head's predicted positions, itch from
  the head's predicted progress and pocket — **no ground-truth access
  anywhere in the loop.**

**What was refuted:** the July obs-form verdict ("goal-distance over
observations cannot hold — 3.8% dwell", episode 0055/0056) is scoped,
not contradicted: distance over the *full* observation fails; distance
over *predicted position channels* in world units succeeds. The wall was
never "observations can't carry a hold" — it was asking one number to
summarize thirty-two channels `[mechanism-argument]`.

**What it opened:** every component of the measured behavior is now
shipped or taught. A **c1d long run** — the composition live for weeks
on the observatory — is registrable with zero scaffolding; the design
doc this graduation creates
([Doc 0009](../02-DESIGN/0009-brain-side-hold.md)) specifies the
brain-side hold functionally for that build. The G5 cohort's heads also
arrive movement-competent for any future gate that reuses them past the
first thousand steps.

Reversal condition: the reading holds for taught goals whose work
position is stable; a c1d-scale run in which the head-hold drifts off
the goal after long homeostasis (position models overwritten by later
learning) would reopen the topic as a memory/consolidation question,
not a prediction one `[judgment]`.

Trail: topic `hq/01-RESEARCH/brain-side-hold/` (opened 0ef6297, verdict
a887d2b, retired this commit — full history in git); design
[Doc 0009](../02-DESIGN/0009-brain-side-hold.md) (this change-set);
episodes [0072](0072-the-event-pathway-ships.md) (the head),
[0069](0069-goal-homing.md) (the clone hold),
[0056](0056-a-floor-not-a-rate.md) (the obs-form wall); runner
`parallel_gates.py` + `h1-rows.json` (session scratchpad, arc
convention).
