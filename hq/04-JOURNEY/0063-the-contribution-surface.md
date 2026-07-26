# Episode 0063 — The contribution surface: the on-ramp is bodies (2026-07-27)

Phase D's third item (feature 038, parallel worktree): the project can
now receive contributors. CONTRIBUTING.md points them where the
roadmap always said the on-ramp is — **new worlds, bodies, sensors,
actuators, and drives against the frozen v1.0 seams** (Doc 0008), with
core changes gated on a conversation first because the validated
behavior is byte-frozen (constitution I). The gate command ships
verbatim, the honesty rules are stated (spreads not means, FAILs are
data), and the feature-vs-research flow is a sentence each with the
journey as the narrative entry point.

The mechanics: issue templates (new-world proposal asks what the world
would teach the brain and holds it to constitution V's instrument
panel — ground truth, determinism; bug reports ask for seed and
expected byte-determinism), a PR template whose four checkboxes are
the constitution in miniature (gate green, additive/opt-in only,
surface inventory updated if public grew, claims honest), and a seeded
on-ramp: five labels and four good-first-issue drafts, **each verified
against the live APIs before being written** [measured] — an
Acrobot-v1 Gymnasium example (Box(6)/Discrete(3), checked), a
delayed-echo world on the EventSource protocol, a rover odometry
sensor copying the real feature-028 pattern, and the reward-as-sensor
deferral that `gymnasium_body.py` itself documents. Gate on the
feature: 665 green, zero skips — documents only, nothing behavioral
[measured].

The roadmap exit ("first external world contribution merged") depends
on a human who is not us and is recorded as **pending-external**,
claimed nowhere. Label and issue creation on the repository is the
owner-side publishing step; performed at landing where permitted,
otherwise listed in `.github/contribution-seed/README.md` as exact
commands.

Reversal condition: none — records a completed build; the seeded
issues are revisited if they age without takers (stale seeds read as
an unwelcoming surface, and the drafts should be re-cut smaller).

Trail: `specs/038-contribution-surface/`; `CONTRIBUTING.md`;
`.github/ISSUE_TEMPLATE/`, `.github/PULL_REQUEST_TEMPLATE.md`,
`.github/contribution-seed/`.
