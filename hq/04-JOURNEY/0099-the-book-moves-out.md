# Episode 0099 — The book moves out (2026-08-14)

The owner's call: the book gets its own repository. `book/` is extracted
into [impire-io/poseres-book](https://github.com/impire-io/poseres-book)
with `git filter-repo --subdirectory-filter book` — all eight commits of
book history preserved, the extracted tree verified identical to
`book/` at HEAD before the move [measured]. The new repo renders with
mdBook (chapters under `src/`, a `SUMMARY.md` table of contents) and
deploys via GitHub Actions to Pages at
<https://impire.io/poseres-book/>, mirroring the website's workflow.
`mdbook build` green; the audiobook builders repointed at `src/` and
re-verified by regeneration — 24,051 spoken words, ~2h40m at 150 wpm
[measured].

The regeneration exposed pre-existing drift, not caused by the move: the
committed narration scripts still told the robot-vacuum version of
chapter 1 while the 2026-08-13 voice sweep had made it a lawnmower. The
scripts are regenerated from current text in the new repo; the
elevenlabs previews and epub still predate the sweep (REVISIT item
narrowed there).

What the split changes: the book no longer travels in the same
change-set as the record it cites, so staying honest becomes an explicit
act instead of a free ride. The link is two artifacts in the book repo
[judgment]: `SOURCES.lock` pins the poseres commit the book last synced
against (pinned at 1c87650, this repo's HEAD at extraction), and the
`/sync-from-pra` skill diffs `hq/04-JOURNEY`, `hq/01-RESEARCH`, and
`hq/02-DESIGN` since that pin, audits every chapter's Draws-on citations
and snapshot numbers against the checkout, and lands findings in the
book's REVISIT.md before bumping the pin. Read-only toward this repo;
prose changes stay owner-driven. `book/` is removed here; the README's
Documentation section points across.

Reversal condition: if a publication-gate numbers audit in the book repo
finds claims that drifted precisely because the record moved while the
`SOURCES.lock` pin sat unmoved across multiple episodes — the same-repo
arrangement would have surfaced them at commit time — the split cost
more honesty than it bought, and the book folds back in.

Trail: poseres-book commits 72b285a (mdBook layout + Pages), d8e43cd
(narration regeneration), 51bd3fc (sync skill + lock);
`poseres-book/.claude/skills/sync-from-pra/SKILL.md`; episode 0047 (the
book decision), episode 0098 (the voice sweep the regeneration caught up
with); this commit (removal + pointer).
