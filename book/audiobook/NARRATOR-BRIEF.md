# Narrator brief — the PRA book

For the narrator, the director, or whoever configures the synthetic voice.
Read this before the pronunciation guide and before any script.

The book's written contract is `../STYLE.md`. This brief translates that
contract into audio. Where the two disagree, STYLE.md wins and this file is
wrong.

---

## What the book is

A first-person account of building a machine brain that never stops
learning. One builder, one project, told as a sequence of things he believed,
measured, and turned out to be wrong about. It is a technical book that
refuses to sound like one.

Sixteen chapters in six parts. Read text runs 2 hours 38 minutes at 150 words
per minute; adding pauses, part openings, and front and back matter puts
finished audio near 2 hours 50. Chapter lengths run from six minutes to
twenty-four. All figures come from `MANIFEST.md`, which is regenerated with
the scripts — if this paragraph and the manifest disagree, the manifest is
current and this paragraph is stale.

## Who is listening

Two people, at once, and the book was written so neither is left out:

- a smart eleven-year-old, who follows the main story completely and will
  disengage the moment a sentence makes them feel stupid;
- an engineer, who wants the failure data and the commit-level honesty.

The narration must not choose between them. Do not soften into a
children's-book register for the first audience, and do not harden into a
lecture for the second. The prose already carries both; the voice's job is to
stay out of the way.

---

## Voice

**Cast a builder, not a presenter.** The right reference is someone
explaining a thing they made, at a kitchen table, to a friend who is
interested but not in the field. Not a documentary voice-over. Not an
audiobook "warm authoritative narrator". Not a podcast host.

Specific instructions:

**Own the first person.** Every "I" in this book is a real person who did the
thing being described. Read "I was wrong about this" the way someone says it
when it's true — flat, unbothered, slightly amused. The book's whole
credibility rests on those admissions not sounding performed.

**No enthusiasm injection.** STYLE.md bans exclaiming at how interesting
something is: "the reader decides what's interesting". The same ban applies
to delivery. When a result is surprising, let the sentence be surprising.
Lifting the pitch to tell the listener something is exciting is the audio
version of the writing tell the book spent a whole style guide avoiding.

**Understate the humour.** It is dry, occasional, and never signposted. "My
vacuum will bump the chair every day until its maker ships a smarter model,
which is to say: forever." Read that line straight. The pause before
"forever" does all the work; a smile in the voice kills it.

**Reversals are the plot.** The recurring rhythm is: I expected X. I measured
Y. Here's what that broke. Give the measurement its own weight — a small
beat before the number, none after. The temptation is to land hard on the
consequence; resist it. The number is the event.

**Pace.** Around 150 words per minute. Unhurried. The book uses very short
sentences deliberately ("It can't." "Not words, not pictures.") and they need
air on both sides. A narrator who averages the rhythm out flattens the prose.

**Paragraph-final lines.** STYLE.md forbids paragraphs that end by restating
themselves — they end on the last new fact instead. So do not add a falling,
conclusive cadence at every paragraph end. Many paragraphs stop mid-thought
on purpose. Let them.

---

## The box problem

The manuscript carries **32** technical asides across the sixteen chapters,
one to six per chapter, marked in print as `> **Under the hood:** ...`. In
the text edition they are skippable by design: STYLE.md guarantees that
"skipping every technical box loses precision, never plot", and that nothing
in a box is depended on later.

In audio they are a genuine problem. A reader's eye slides past a paragraph
of per-seed pass rates; a listener has to sit through it. Two real fragments,
both verbatim:

> "Bar A PASS 24/24, 303 logs; Bar B PASS 13/24; median dwell 100.0%"
> — chapter 14

> "Trail: `hq/02-DESIGN/validate/LONGEVITY-DIAGNOSIS.md`."
> — chapter 10

Spoken, the second is "trail: h q slash zero two dash D E S I G N slash
validate slash longevity dash diagnosis dot m d." That is not narratable, and
no delivery choice rescues it.

Three options, and the choice is the author's:

1. **Omit the boxes** (what `build-narration.py` does by default). The
   audiobook is the main text, complete and unbroken, 2h 38m of read text.
   The front matter tells listeners the technical asides exist in the text
   edition. This is safe by construction — the style contract already
   promises the main text stands alone.
2. **Rewrite the boxes for audio** (`--boxes summarise`). Each box becomes a
   spoken-friendly version: headline result only, no file paths, no per-seed
   tables, no symbols. Preserves the two-audience promise at the cost of
   **32 new pieces of writing**, which only the author can do. That is the
   real price of this option and it should not be underestimated.
3. **Read them verbatim** (`--boxes keep`). Not recommended. Measured at
   3h 04m against 2h 38m, so it adds 26 minutes, and it costs the engineer's
   attention rather than winning it.

If option 2 or 3 is chosen, boxes get a distinct treatment: move slightly
closer to the mic, drop about a third in energy, slow marginally, and return
to full voice afterwards. Announce nothing — no "under the hood" spoken as a
heading. The shift in delivery is the signal. Leave two seconds of air on
each side.

---

## Structural cues in the scripts

The generated scripts use bracketed markers. **Nothing in square brackets is
spoken.**

| Marker | Means |
|---|---|
| `[PAUSE n]` | Hold n seconds of room tone |
| `[SECTION — lift and re-set]` | Sub-heading. Read the title, then a beat. Re-set energy as if starting fresh |
| `[TECHNICAL ASIDE]` … `[END ASIDE]` | Box treatment described above |
| `[BOX OMITTED FROM AUDIO: ...]` | Nothing to read. Present so the author can see what was dropped |
| `[BOX NEEDS AUDIO REWRITE: ...]` | Author action required before recording |
| `[NARRATOR NOTE — ...]` | Instruction for a displayed block |
| `[DISPLAYED BLOCK — read this spoken version instead]` | Read the paragraph that follows |
| `[PART OPENING]` | Read the part title, then three seconds |
| `[END OF CHAPTER]` | Stop. New file |

## Emphasis

The manuscript italicises exactly one thing: a new term at its first
plain-words definition. That italic is a definition marker, not emphasis.
Read those terms with a very slight setting-down — the audio equivalent of
placing a word on the table — not with stress. Everything else in the book is
unitalicised on purpose, so if you feel the urge to punch a word, the text is
telling you not to.

Bold appears only at first definition, same treatment.

---

## Chapter and file structure

One audio file per chapter, sixteen files, named to match `scripts/`. Part
openings are recorded at the head of the first chapter of each part (already
placed in the scripts), not as separate files.

Front and back matter are separate files — see `FRONT-BACK-MATTER.md`.
Retail platforms require opening and closing credits as their own files or
topped-and-tailed onto the first and last chapters; check the distributor's
current spec before delivery, as these change.

## Technical delivery targets

If distributing through ACX or a similar retail channel, the usual
requirements are: each file is one chapter, 192 kbps or higher constant
bit-rate MP3, 44.1 kHz, consistent channel format across all files, RMS level
between −23 dB and −18 dB, peak no higher than −3 dB, noise floor below
−60 dB RMS, 0.5 to 1 second of room tone at the head of each file and 1 to 5
seconds at the tail, no file longer than 120 minutes, and a separate retail
sample of one to five minutes.

**Verify these numbers against the distributor's current published spec
before you record.** They have changed before, and this brief was written on
2026-08-13 from general knowledge rather than from a fetched copy of the
spec. Treat the list as a checklist of *what to look up*, not as authority.

For a retail sample, chapter 1 from the opening line through "The reason your
vacuum doesn't is a design choice, not a law of nature" runs close to five
minutes and is self-contained.

---

## Before the first session

- [ ] Confirm how the author's name is pronounced. It is a first-person book;
      getting it wrong in the credits is worse than getting it wrong anywhere
      else.
- [ ] Decide the box question above. It changes the runtime and the script.
- [ ] Read `PRONUNCIATION.md` end to end, especially the number rules. This
      book is unusually number-dense and the numbers are load-bearing.
- [ ] Record chapter 1 and the two hardest passages first — the displayed
      triplet in chapter 4 and any Part 6 box you plan to keep — and get them
      approved before recording the other thirteen chapters.

## A note if you are using a synthetic voice instead

Everything above still applies, but three things need extra attention:

1. Load `PRONUNCIATION.md` into the voice's lexicon before generating. The
   number rules in particular will not be inferred correctly.
2. Synthetic voices default to the enthusiasm this book is written against.
   Choose a flat, conversational voice and resist "expressive" settings.
3. Generate chapter 1 and listen to it whole before generating the rest.
   The failure mode is not obvious per-sentence — it shows up as three hours
   of unvarying rhythm, which is exactly the machine-written quality the
   manuscript works to avoid. A book about not sounding machine-made,
   narrated badly by a machine, is a bad trade.
