# Audiobook production package

Two routes out of the same manuscript, because they need opposite things.

**Recording with ElevenLabs?** Start at **`ELEVENLABS-SETUP.md`**. Everything
else here is for a human narrator.

**Hiring a narrator?** Start at **`NARRATOR-BRIEF.md`**.

Generated 2026-08-13 from the working draft.

## The two routes

| | Human narrator | ElevenLabs |
|---|---|---|
| Build with | `build-narration.py` | `build-epub.py` |
| Output | `scripts/*.txt`, `MANIFEST.md` | `elevenlabs/pra-book.epub`, `pronunciation.pls`, `preview/*.txt` |
| Guide | `NARRATOR-BRIEF.md`, `PRONUNCIATION.md` | `ELEVENLABS-SETUP.md` |
| Direction markers | `[PAUSE 3]`, `[SECTION]`, `[NARRATOR NOTE]` | none — they would be read aloud or parsed as audio tags |
| Numbers | rules for a human to apply | pre-substituted by `normalize.py` |
| Credits | `FRONT-BACK-MATTER.md` | built into the EPUB |

The scripts and the EPUB are not interchangeable. Uploading `scripts/` to
ElevenLabs produces a voice reading stage directions aloud.

## Regenerating

Everything under `scripts/`, `elevenlabs/`, and `MANIFEST.md` is
**generated**. Do not hand-edit it; the next build overwrites it. After any
manuscript revision:

```
python3 build-narration.py     # human-narrator scripts + manifest
python3 build-epub.py          # ElevenLabs EPUB + lexicon + previews
python3 normalize.py --report  # audit every text substitution
```

Options for `build-narration.py`:

```
--boxes omit        default. Technical asides dropped from audio.
--boxes summarise   asides replaced with a marker for the author to rewrite.
--boxes keep        asides read verbatim. Not recommended — see the brief.
--wpm 150           narration pace used for runtime estimates.
```

Options for `build-epub.py`:

```
--model v2          default. Emits <break> tags; v3 does not support them.
--model v3          no break tags; pauses come from structure.
--breaks no         drop break tags on v2 too.
--boxes keep        include technical asides. Reports problems; see the brief.
```

## The three files you edit by hand

Everything else is generated.

- **`audio-overrides.json`** — spoken versions of displayed data blocks,
  keyed by the block's first line. `04-before-action-after` is a worked example.
- **`LEXICON`** in `build-epub.py` — the ElevenLabs pronunciation dictionary.
- **`TITLE`, `URL`, and `back_matter()`** in `build-epub.py` — the credits.
  Four placeholders are still unfilled and the build says so on every run.

## Current state and the honest caveat

The manuscript is a working draft. `../REVISIT.md` lists unresolved items
including several claims written in the author's first-person voice that he
has not yet verified as his own — the chapter 1 opener, the chapter 2
emotional beats, the chapter 7 closing thesis. Part 5 has one chapter where
the outline implies more.

Narration is normally the last step in a book's production, after the text is
locked, because re-recording is expensive and re-recording a first-person
admission you decided wasn't true is worse than expensive. Everything in this
package was built to survive revision — the brief and the pronunciation guide
are draft-independent, and the scripts regenerate in one command — but the
recommendation stands: lock the text first.

## What this package does not include

Audio. No listenable text-to-speech was available in the environment where
this was built, and the ElevenLabs connector available here drives voice
*agents*, not Studio projects — so the EPUB has to be uploaded by hand.
Everything up to that upload is done.

One thing in the ElevenLabs route is unverified against a live import:
whether escaped `<break>` tags survive EPUB import as usable text.
`ELEVENLABS-SETUP.md` gives a six-thousand-character test that settles it
before you convert the other fifteen chapters.
