# Episode 0098 — The book clears its throat: voice rules land, REVISIT empties (2026-08-13)

The book's working debt got paid in one sitting. The owner asked for two
things: a looser, story-first voice, and the REVISIT.md backlog cleared
rather than carried. Both happened the same day, and the second turned
out to depend on the first.

**Voice rules** [judgment — owner's direction, codified]. STYLE.md gained
"Told, not presented": callbacks to earlier chapters are retold, not
cited ("Remember chapter 7's law: never let the system grade its own
homework" — the reader never flips back); virtue announcements ("I want
to be precise", "recorded without spin") are banned, replaced by the
moment that produced them; loose ends get one line and a forward
pointer, not a status report. A second rule, "Verbs stay verbs", bans
minting abstract nouns from verbs in running prose ("toward wanting
something easy", never "toward wants that are easy") — named components
and one aphorism per chapter excepted. Chapter 9 was rewritten as the
reference; a three-agent audit then swept all sixteen chapters
(~280 flags; ~35 applied — virtue announcements, bare citations, the
owner's flagged colon-fragment passages; the paragraph-final aphorisms
were reviewed and deliberately kept as voice). A same-day follow-up
ruling added footnotes-as-pointers: retold callbacks drop their chapter
numbers into sparse markdown footnotes ("[^homework-law]: Chapter 7."),
never content, forward hooks keep numbers inline; nine placed across
eight chapters, and `build-narration.py` now strips markers and
definitions so footnotes are never read aloud [measured — strip
verified on ch 9/12].

**The arbitration** [judgment — owner rulings, ~24 items across six
question rounds]. Highlights: the ch 1 opener is now the *real* origin
story (a robot lawnmower wedged against the same tree trunk, not the
ghostwriter's vacuum); "a year of removing dishonesty" corrected to the
git-recorded three weeks (repo starts 2026-06-20 with a baseline import;
prehistory exists but is unmeasured, so the book claims only what the
log supports); ch 9 now foreshadows the ch 13 reversal instead of
freezing the superseded competence verdict; ch 10's cap question and
ch 12's channel-weighting sentence de-staled against journeys 0041/0030/
0060; teacher hooks renumbered Part 5 → Part 6 and re-tensed against
0054–0058; canonical terminology is **motivation** (titles keep their
verbal forms); Thousand Brains lineage acknowledged in a new
`ACKNOWLEDGMENTS.md` (back matter, per §9 of the architecture doc);
ch 11's two strongest editorials softened, ch 12's register rewritten
plain, three of four flagged metaphors cut (the baby's experiments
stay).

**What it taught**: the stale-content items (ch 9/10/12 vs the record)
were all the same failure — chapters freezing a live record — and the
fix that survives is the one ch 9 got: keep the story as it was true at
the time, and point forward. REVISIT.md shrank from ~340 lines of
arbitration debt to a publication-gate checklist; the numbers audit and
audiobook regeneration remain gated on release, not on decisions.

Refuted along the way: "five features after snapshots shipped" (the
record counts six, 004–009); "four hundred simulation runs" (the 0024
grid alone was 576; the book now says "a pile"); "months of
measurement" (weeks).

Reversal condition: if read-aloud passes or reader feedback show the
retold callbacks reading as padding, or the motive-beats ("it bothered
me, so I chased it") hardening into a detectable formula, the
"Told, not presented" section gets rebalanced — the ban on virtue
announcements stays either way.

Trail: `book/STYLE.md`, `book/REVISIT.md`, `book/ACKNOWLEDGMENTS.md`,
`book/GLOSSARY.md`, all sixteen chapters, `book/outline.md`; committed
with this episode.
