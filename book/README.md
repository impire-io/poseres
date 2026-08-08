# The PRA book

A book about the Pose Resolution Architecture: why frozen models fail, what a
sensorimotor triplet is, and how a population of competing frames learns
structure nobody specified.

Read `STYLE.md` before writing a single sentence. It is the contract.

## Layout

```
book/
  README.md            this file
  STYLE.md             the writing contract — voice, two-lane rule, AI-tell bans
  GLOSSARY.md          every plain-words definition, in order of appearance
  NOTES-ai-tells.md    research notes behind the style rules (not part of the book)
  outline.md           the working outline (parts → chapters → beats)
  part-1-the-problem/
    01-....md
  part-2-the-triplet/
  part-3-the-mechanism/
  part-4-the-continuity-guarantee/
  part-5-the-long-run/
```

One chapter per file, numbered for order (`01-`, `02-`, ...). Chapter titles
live in the file's H1, not the filename. Figures go in `figures/` next to the
chapter that uses them, as SVG where possible.

## Working rules

- Chapters cite the project record: when a chapter tells a story from
  `hq/04-JOURNEY/`, link the episode and commits it draws on in an HTML comment at
  the top of the file, so claims stay checkable as the code moves.
- Empirical numbers in the book are snapshots. Each one carries a comment
  noting where it was measured, so a later edition can re-verify or update.
- The book builds with any markdown toolchain; don't add build tooling until
  the text needs it (mdBook or Pandoc when we get to producing an artifact).
- Every merged chapter passes the revision checklist at the bottom of
  `STYLE.md`.
