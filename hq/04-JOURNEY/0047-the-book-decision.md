# Episode 0047 — The book decision: one builder, two lanes (2026-07-18 → 07-21)

A communication decision, recorded now that `book/` is committed (the
REVISIT backlog asked for exactly this episode and marked it the
maintainer's call). The decision [judgment, Daan's]: PRA gets a long-form
narrative book — why frozen models fail, what a triplet is, how a
population of rival frames learns structure nobody specified — governed by
a written contract (`book/STYLE.md`) with three load-bearing choices:

- **Voice: first person, one builder.** "I expected X. I measured Y.
  Here's what that broke" is the chapter rhythm; opinions are stated and
  owned. The stated rationale [mechanism-argument]: the project's record is
  full of refuted beliefs, and those reversals are the plot — a book that
  presents only the final correct design reads like marketing, and
  marketing is what AI text sounds like.
- **The two-lane rule.** Every chapter serves a smart 11-year-old in the
  main text and an engineer in fenced "Under the hood" asides; the main
  text must be complete on its own — skipping every box loses precision,
  never plot.
- **Register.** Concrete before abstract, names reused verbatim, and the
  researched AI-tell list (`book/NOTES-ai-tells.md`) banned outright — with
  the deeper countermeasure stated: specificity ("one seed climbed to dim
  18 of a true 20") over surface-tell scrubbing.

The process is honest about its own authorship: chapters were AI-drafted,
and `book/REVISIT.md` flags every ghostwriter-invented beat, emotional
coloring, and unverified first-person opinion for the maintainer's
arbitration rather than shipping them silently. Chapters cite their journey
episodes and commits in provenance comments; every empirical number is a
dated snapshot with a numbers-audit-before-publication rule.

State at recording [measured]: 12 chapters across four parts drafted plus
outline, glossary, style contract, and revisit backlog — 18 files, 2,373
lines, first committed (references fixed to the hq layout) in `ffb83c0`.
Part 5 (teachers) is deliberately undrafted: it has no measured foundation
beyond multi-stream ([episode 0022](0022-multi-stream.md)) and waits on the
teacher-world research candidate. Bookkeeping folded into this episode: the
book joins the roadmap as an open Phase D item — it is unbuilt product work
and the plan should say so.

Reversal condition: if arbitration of the REVISIT backlog shows the
ghost-written first person systematically claiming experiences or opinions
that are not the maintainer's — faster than they can be reclaimed or cut —
the voice contract is renegotiated before further drafting. Independently:
no publication in any form before the numbers audit re-verifies every
empirical claim against the repo (constitution II/IV).

Trail: `book/STYLE.md` (the contract), `book/REVISIT.md` (the backlog),
`book/NOTES-ai-tells.md` (the research); commits `ffb83c0`, this one.
