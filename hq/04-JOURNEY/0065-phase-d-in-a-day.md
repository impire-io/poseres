# Episode 0065 — Phase D in a day: four parallel worktrees, one serial landing (2026-07-27)

The owner's instruction was "do all in parallel autonomously," and the
day after v1.0 the remaining Phase D items ran as four isolated
worktree agents — docs site (036), shareable brains (037),
contribution surface (038), and the book STYLE audit — each building
and gating in its own venv on its own branch, with every landing done
serially by the coordinator so episode numbers, roadmap rows, and the
README merged without collision. All four came back gate-green and
scope-clean [measured: 673 / 665(+276 targeted) / 665 on the feature
gates; the landing gates green on every merge]. **v1.1.0 is tagged**:
the surface grew additively by one CLI and seven elements, and the
byte-frozen suite held through all of it.

Two external actions were correctly stopped at the permission
boundary and stay the owner's: **Pages enablement** (episode 0062's
exit clause pending one click or one gh call) and **seeded issue
creation** (exact commands in `.github/contribution-seed/README.md`;
the five labels were created). The exits read honestly: docs =
built-and-linked, deploy pending owner; contribution = built, "first
external contribution merged" pending an external human; shareable
brains = **exit met** twice over; book = audit complete, 11 of 12
chapters awaiting the maintainer's arbitration (`book/REVISIT.md`,
2026-07-27 section — the three sharpest findings: ch. 9's drive
posture predates the 0053 reversal, ch. 8's "a year" timeline has no
support in the record, ch. 12's channel-weighting claim is doubly
stale).

**The one deliberate deferral [judgment]: show-then-tell.** A C1 demo
video cut today would show a brain whose emergence question is an
open, pre-registered experiment mid-run — a demo outrunning measured
capability, which constitution IV exists to prevent. The item resumes
when the c1c R1–R5 read lands, whichever way it reads; the video
publishes with that telemetry.

Housekeeping folded in: stale tracked `src/pra.egg-info/` untracked
(it shadowed the installed version in `pip list`).

Reversal condition: the show-then-tell deferral lifts when the c1c
read is recorded (either verdict — an honest miss is publishable
under constitution II); it would also lift early if the owner decides
a mechanism-demo video (explainer-style, no capability claims) serves
better than waiting — that variant makes no emergence claims and
needs no run data.

Trail: episodes [0062](0062-the-docs-site.md),
[0063](0063-the-contribution-surface.md),
[0064](0064-shareable-brains.md); `book/REVISIT.md`; `CHANGELOG.md`
v1.1.0; branches 036–039 on origin; tag `v1.1.0`.
