# Style guide

This file is the contract for every chapter in `book/`. If a paragraph breaks
these rules, the paragraph loses, not the rules. The guide is written in the
style it demands, so if this file reads like a press release, fix the guide
first.

## Who we're writing for

Two readers share every chapter:

The **11-year-old** reads the main text. Not a dumbed-down adult — a smart kid
who has never heard the words "dimensionality" or "world-model" and will stop
reading the moment a sentence makes them feel stupid. If the main text needs a
term they don't have, we build it in front of them from something they do have.

The **engineer** reads the same main text plus the technical asides. They want
the math, the failure data, the commit-level honesty. They get it in clearly
marked boxes they can find fast — and the kid can skip without missing the
story.

The rule that keeps both happy: **the main text must be complete on its own.**
Skipping every technical box loses precision, never plot.

## Voice

First person, one builder. I made this thing. I was wrong about it a lot. The
book says so.

That's not a stylistic garnish — it's the load-bearing choice. The project's
own record (`hq/04-JOURNEY/`) is full of moments where a belief got refuted by a
measurement: the v3 prototype that passed its test only at a lucky horizon, the
curiosity drive that turned out to be *worse* than random. Those reversals are
the book's plot. A book that only presents the final, correct design reads like
marketing, and marketing is what AI text sounds like.

Concretely:

- "I expected X. I measured Y. Here's what that broke" is the default chapter
  rhythm.
- Opinions are stated as opinions and owned. "I think replay-based continual
  learning is a dead end" — not "some argue that replay-based approaches face
  challenges."
- When something is unknown or unproven, say so in the main text, not in a
  footnote. The project marks claims [V]alidated / [D]esigned / [O]pen
  internally; the book keeps that honesty even where it drops the tags —
  but in passing, not as a proceeding (see "Told, not presented" below).

## Told, not presented

(Added 2026-08-13 at Daan's request. The book was reading like a careful
presentation; it should read like a story told by someone who was there.)

**Callbacks are retellings.** When a chapter leans on an earlier chapter's
idea, don't cite it like a paper ("The reason is chapter 7's law, applied
one level up"). Recall it the way you'd remind a friend: say what the law
*was*, then make the connection. "Remember chapter 7's law: never let the
system grade its own homework. This is the same law, one level up." The
reader shouldn't have to flip back, and the retelling is a free rehearsal
of the idea. Keep the canonical wording verbatim when you retell it.

**Footnotes are pointers, never content** (added 2026-08-13, Daan's
call). Where a retelling makes the chapter number ceremonial, move the
number out of the prose into a footnote: "Remember the law: never let
the system grade its own homework.[^homework-law]" with
`[^homework-law]: Chapter 7.` at the bottom of the chapter file. Used
sparingly — laws, refuted results, promised payoffs; a handful per
chapter at most. The main text must stay complete with every footnote
unread (the same guarantee the boxes give), so a footnote may locate an
idea but never explain one. Forward hooks ("chapter 13 is that story")
keep their numbers inline; the promise *is* the number. Cross-references
that don't earn a footnote keep their inline chapter number as before.
The narration build strips markers and definitions; footnotes are never
read aloud.

**Never announce your own virtues.** "I want to be precise about...",
"I want to be clear that...", "to keep this honest...", "recorded without
spin", "in the interest of accuracy" — all banned. Precision and honesty
are things the reader concludes from the text; saying them is telling,
and it's exactly how marketing talks. Replace the announcement with the
moment that produced it: what bothered me, what I did about it. "It
bothered me enough that I spent two days chasing it" does the work "I
want to be honest" only claims to do. One warning: don't let the
replacement harden into a formula. If every chapter has an "it really
bothered me, so I dove in" beat, that's a new tell. Vary the moment, or
cut it and let the work speak.

**Loose ends get one line.** Unknowns and unproven claims still belong in
the main text (the Voice rule stands), but as a pointer, not a status
report: "one to come back to", "interesting, but not worth the detour
right now". One sentence, then back to the story. The full accounting
lives in the technical boxes and in `REVISIT.md`; the main text owes the
reader honesty, not paperwork.

**Verbs stay verbs.** (Added 2026-08-13.) Named components keep their
names: the drive, the judge, the price. But running prose must not mint
abstract nouns out of verbs. A system doesn't have "wants"; it wants
things. Write "toward wanting something that is easy to satisfy", not
"toward wants that are easy to satisfy"; "a drive to reach the far wall",
not "a reaching drive". The test: could you say it across a table without
sounding like a paper? Two exceptions, both narrow: a term at its
italicized first definition, and a deliberate aphorism ("understanding
proposes; wanting disposes") — one per chapter at most, and it has to
earn it.

## The two lanes

**Main text.** Short paragraphs, mostly short sentences, concrete before
abstract. Every new concept arrives through a physical, checkable example — a
robot arm, a thermostat, a kid learning to ride a bike — before it gets a name.
Once named, the name is reused verbatim; no elegant variation ("frames" stays
"frames", never "coordinate manifolds" for flavor).

**Technical asides.** Fenced-off sections titled `> **Under the hood:** ...`
(blockquote, bold label, descriptive title). They may use math, code, and
jargon freely, assume the main text was read, and must be skippable: never
introduce something in a box that a later main-text passage depends on. One box
per idea; if a box grows past ~half a page, it probably wants to be an appendix.

## How to not sound like a machine

I looked at what editors and detectors actually flag as AI writing (sources in
`book/NOTES-ai-tells.md`). The surface tells are easy to list; the deeper
problem is worth stating first:

**AI text is generic because it has no experiences.** It hedges because it has
no stake. It's symmetrical because it has no favorite. The single strongest
countermeasure isn't deleting "delve" — it's writing from the specific: real
measurements, real dates, real mistakes, real numbers with their real units.
"One seed climbed to dim 18 of a true 20" cannot be generated by a model that
wasn't there.

That said, the surface tells matter too, because readers now pattern-match on
them. Banned or rationed:

**Banned words and stock phrases.** delve, harness (as a verb — the
validation harness keeps its name), leverage (as a verb),
underscore, bolster, foster, robust (outside a technical claim), tapestry,
landscape (metaphorical), journey (metaphorical — yes, despite hq/04-JOURNEY/),
crucial, pivotal, "it's important to note", "it's worth mentioning", "in
today's world", "at its core", "stands as a testament", "plays a vital role",
"in conclusion".

**Banned constructions.**
- The not-just pivot: "It's not just X — it's Y." Also its cousins "more than
  just", "not only... but also". If the contrast is real, state the second half
  plainly.
- The rule of three as a reflex: "fast, flexible, and powerful." Lists of
  three adjectives are allowed only when there are actually three things.
- Trailing participle summaries: "..., highlighting the importance of
  adaptation." If the point matters, give it its own sentence; if it doesn't,
  cut it.
- Paragraph-final mini-conclusions that restate the paragraph. End on the last
  new fact instead.
- Virtue announcements and bare citations: see "Told, not presented". Both
  count as banned constructions for the checklist grep.
- Section-final summaries and chapter-final "In this chapter we saw..."
  recaps. The reader was there.

**Rationed punctuation and formatting.**
- Em dashes: almost never. A regular writer reaches for a comma, a colon,
  parentheses, or a new sentence first; so do we. Budget: a small handful
  per chapter, each one earning its place, and never as the not-just
  pivot above. (Rule tightened 2026-07-18 at Daan's request — earlier
  drafts allowed one per paragraph and read like it.)
- Interrupted sentences: keep them rare. A sentence with more than one
  aside, or commas doing the work of structure, gets rewritten as two
  plain sentences. Flow beats rhythm tricks.
- Bold: for terms at first definition only. Never for emphasis of ordinary
  sentences. Structural run-in labels (chapter 7's numbered cheats) count
  as headings, not emphasis, and are allowed (ruled 2026-08-13).
- Bullet lists: for genuinely enumerable things (rules, steps, options). Never
  as a substitute for a paragraph that should flow. A chapter with more list
  lines than prose lines is broken.
- Headings: sentence case, and only where a reader would want to navigate to.
  No heading for every three paragraphs.

**Required irregularity.** Human writing has texture: a two-word sentence after
a long one. A paragraph that's one line. An aside in parentheses that's
slightly too chatty (like this one). Vary paragraph length on purpose. If three
consecutive paragraphs have the same shape — topic sentence, two supports,
wrap-up — rewrite the middle one.

**Humor policy.** Dry, occasional, never signposted. No exclamation marks
except in dialogue or quoted machine output ("motors forward!" — ruled
2026-08-13). No "fun fact!".

**Register.** Clear is the goal; cute is a failure mode. The 11-year-old
test measures whether the *explanation* is followable, not whether the
prose sounds like a children's book — write for an intelligent adult and
let the clarity do the including. Metaphors must be load-bearing (they do
explanatory work the plain statement can't), used once, and dignified;
if a metaphor is decoration, cut it and say the thing. Never talk down:
no "you see," no rhetorical hand-holding, no exclaiming at how
interesting something is. The reader decides what's interesting.

The line between hand-holding and telling (2026-08-13): hand-holding is
direct address that does *no work* — telling the reader what to notice,
what to feel, how interesting this is. Direct address that carries real
content is just how stories get told: "Remember chapter 7's law..."
followed by an actual retelling is allowed and encouraged. The test is
whether the sentence would survive with the "you" removed. If yes, it
was decoration; cut it.

## Vocabulary mechanics for the young reader

- New technical term → concrete example first, name second, then a one-line
  plain-words definition in *italics* the first time it appears.
- Keep a running glossary in `book/GLOSSARY.md`; every italicized definition
  gets an entry.
- Numbers get anchors: "50 dimensions" means nothing to anyone; "imagine
  describing your body's position with 50 separate knobs" is checkable.
- Target reading ease: main text around grade 6–8; mechanism-heavy
  chapters may run higher when precision demands it. (Measure with the
  boxes stripped; it's a smoke alarm, not a judge — the real test is
  followability.) Technical boxes are exempt.

## Revision checklist (run on every chapter before commit)

1. Strip all `Under the hood` boxes. Does the story still work? If no, move
   content down into the main text.
2. Grep the chapter for the banned list. Zero hits.
3. Count em dashes per paragraph, bold outside definitions, lists vs prose.
4. Read the first sentence of every paragraph in sequence. If they form a
   perfectly parallel outline, the chapter was written by the outline, not by
   a person — break the symmetry.
5. Find at least one real, dated, specific event from `hq/04-JOURNEY/` or the
   commit history in the chapter. A chapter with no specifics is a blog post.
6. Read one page aloud. Anywhere you wouldn't say it to a friend, rewrite
   it. Cross-references especially: a citation you'd never speak ("the
   reason is chapter 7's law") gets retold, not cited.
7. Verify every empirical claim against the current specs/measurements —
   numbers in this project have changed before and will again.

## What this guide is not

It's not a promise that the book was typed unassisted. Tools draft; the
builder decides, verifies, and owns every claim. The test that matters is the
one in item 5: could this text have been written by someone who wasn't there?
If yes, it's not done.
