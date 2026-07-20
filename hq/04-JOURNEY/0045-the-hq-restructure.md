# Episode 0045 — The HQ restructure: the process gets a constitution (2026-07-20)

Not a build or a measurement — a working-structure decision, recorded with
its reversal condition. The project's process artifacts had grown organically
(a 44-chapter `JOURNEY.md`, `ROADMAP.md`, `design/`, `AGENTS.md`) while the
spec-kit constitution sat as an unfilled placeholder — so the vision lived
only in journal chapters and nothing mechanically held decisions against it.
Decision [judgment], made with an explicit teach-back and an adversarial
review pass (15 findings folded into the plan before execution): everything
about *how the project is run* moves under `hq/`, with GENESIS as the fixed
point — `vision.md` (from episodes [0010](0010-the-product-thesis.md) and
[0042](0042-the-vision-re-broadened.md)), `constitution.md` v1.0.0 (the
articles, including the anti-drift working agreement adopted in 0042), and
`how-we-work.md` (pipeline, research lifecycle, duties).

What moved, one home per artifact: `design/` → `hq/02-DESIGN/` (docs
renumbered `0001–0007`, numbers stable so "Doc NN" prose survives),
`ROADMAP.md` → `hq/03-IMPLEMENTATION/roadmap.md` (~40 chapter refs became
links), `JOURNEY.md` → split into these 44 numbered episodes (chapter N =
episode `00NN`), `NEXT-STEPS.md` → `history/`, frozen. Root stubs keep the
72 frozen `specs/` references resolving; `book/` (untracked draft) was left
untouched.

The enforcement is mechanical, not aspirational [mechanism-argument]: the
spec-kit constitution is now a symlink into GENESIS so every feature plan's
Constitution Check reads the real articles; `tests/test_hq_structure.py`
rides the standard gate (states, numbering, required episode fields, symlink
health, link integrity — verified to fail on a planted violation); and the
lifecycle transitions are one-command skills (`/research-start`,
`/research-graduate`, `/journey-log`) that stage explicit paths, commit
signed, and never push. Research stays out of spec-kit — the repo's own
drift away from spec-kit scaffolds in arcs 022–026 settled that [measured];
designs always go through it.

Reversal condition: if, two to three features from now, hq lags reality —
missing episodes, a stale roadmap, illegal research states despite the lint
— the structure is failing its purpose and we fold back to the flat layout
rather than maintain a facade.

Trail: the six-commit `hq-restructure` series (GENESIS + wiring; design
move; journey split; roadmap move; machinery; this episode); plan reviewed
adversarially before execution.
