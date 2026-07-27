# Episode 0066 — The book goes on the website, as a draft (2026-07-27)

A communication decision, follow-on to
[episode 0047](0047-the-book-decision.md). The decision [judgment,
Daan's]: the twelve drafted chapters and the glossary publish on
impire.io now, every page carrying a draft label, instead of waiting
for the numbers audit. 0047's reversal condition — no publication in
any form before the audit re-verifies every empirical claim — is
refined, not dropped: the audit still gates calling anything final,
and the draft label is the honesty mechanism in the meantime. Every
generated page says the audit hasn't run and that measured numbers
read as provisional, which is the same rule the site already follows
(each page says plainly what doesn't work or exist yet).

Mechanics: the pages are generated from `book/` markdown by the
website repository's `tools/build-book.py`, which asserts, per page,
that the visible text matches the source markdown after normalizing
markup — so the site cannot silently drift from the book
[mechanism-argument: the check strips tags and markers from both
sides and demands equality, so any dropped, reordered, or reworded
passage fails the build]. Contents page, twelve chapter pages,
glossary; Part 5 is listed on the contents page as not written, with
the reason. Website commit `4b04f27`.

What it opens: readers reach the draft while the REVISIT arbitration
(11 of 12 chapters flagged,
[episode 0065](0065-phase-d-in-a-day.md)) and the numbers audit are
still open, which raises the cost of leaving them open — a reader
can now cite a provisional number. That trade is the decision, made
with eyes open.

Reversal condition: if draft numbers get cited outside the site as
if final, or arbitration shows the drafts claiming experiences that
are not the maintainer's, faster than pages can be corrected, the
chapters come off the site and 0047's original no-publication
condition is restored until the audit runs.

Trail: [episode 0047](0047-the-book-decision.md) (the original
gate); `book/REVISIT.md` (the open arbitration backlog); the website
repository (`tools/build-book.py`, `pra/book/`), commit `4b04f27`;
this commit.
