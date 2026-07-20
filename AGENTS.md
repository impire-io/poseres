# Agent guide for the PRA project

Durable instructions for any coding agent working in this repository. The
full rules live in `hq/00-GENESIS/`; this file is the orientation and the
non-negotiables.

## Orientation (read in this order)

1. `hq/00-GENESIS/` — [`vision.md`](hq/00-GENESIS/vision.md) (what PRA is
   and where it's pointed), [`constitution.md`](hq/00-GENESIS/constitution.md)
   (the articles no change may violate), and
   [`how-we-work.md`](hq/00-GENESIS/how-we-work.md) (pipeline, research
   lifecycle, working agreement). Decisions are held against these.
2. `hq/04-JOURNEY/README.md` — where things stand + the episode index: what
   was built, what was refuted, and why things are the way they are.
3. The current feature plan — pointed to by the SPECKIT block in `CLAUDE.md`
   (tech stack, structure, commands).
4. `hq/02-DESIGN/README.md` — the system design map; `hq/02-DESIGN/validate/`
   — the normative specs (PRA-01/PRA-02) and the evidence trails
   (`*-DIAGNOSIS.md`).

## Non-negotiables (constitution articles, in brief)

- **Quality gate before "done"** (all green, none skipped):
  `./.venv/bin/ruff format --check . && ./.venv/bin/ruff check . && ./.venv/bin/pytest -q`
  — this includes the hq structural lint (`tests/test_hq_structure.py`).
- **Use the repo venv** (`./.venv/bin/python`); sign commits; never commit
  `.claude/settings.local.json`.
- **The validated behavior is byte-frozen** (constitution I): the T1–T6
  suite under the pinned baseline reproduces its reference values exactly;
  new capability is opt-in and leaves existing modes' RNG stream, behavior,
  and serialized summaries untouched.
- **Honest measurement** (II): spreads not bare means; FAILs are data;
  criteria amended openly, never tuned quietly.
- **Diagnose before fixing** (III): hypothesis → cheap discriminating
  experiment → principled fix, trail in `hq/02-DESIGN/validate/`.
  Experiments live in the session scratchpad; conclusions land in git.

## The flow

- **Research** runs through `/research-start` → investigate →
  `/research-graduate` (`hq/01-RESEARCH/`; never through spec-kit).
- **Features** run the spec-kit flow (`/speckit-specify` → plan → tasks →
  implement) on a numbered branch, and land with the roadmap update, the
  journey episode, and design-doc propagation in the same merge.
- **The journey duty (required):** every landed feature, concluded
  investigation, or load-bearing decision gets a numbered episode in
  `hq/04-JOURNEY/` — `/journey-log` does this (template, index,
  where-things-stand, roadmap).
