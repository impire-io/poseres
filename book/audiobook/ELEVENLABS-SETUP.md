# ElevenLabs Studio setup

Built for **Eleven Multilingual v2**. If you switch models, re-read the
"Model choice" section — the break tags in the EPUB are v2-only and will
show up as spoken gibberish on v3.

## Files to upload

| File | Where it goes |
|---|---|
| `elevenlabs/pra-book.epub` | Studio → create project → upload document |
| `elevenlabs/pronunciation.pls` | project settings → pronunciation dictionary |

`elevenlabs/preview/*.txt` is the exact text the EPUB carries, minus markup,
one file per Studio chapter. Read chapter 1 there before you upload anything;
it is faster than reading it in the editor. These files are also the fallback
if the EPUB import misbehaves — they can be uploaded as 24 individual text
documents instead.

Do **not** upload anything from `scripts/`. Those are for a human narrator
and are full of bracketed direction that v2 reads aloud and v3 parses as
audio tags.

---

## Before you upload: four placeholders

The build currently ends with:

```
4 problems — do NOT upload yet:
  unfilled placeholder: «TITLE»
  unfilled placeholder: «URL»
  unfilled placeholder: «Publisher or production credit, if any.»
  unfilled placeholder: «Copyright line — year and rights holder.»
```

`TITLE` and `URL` are constants at the top of `build-epub.py`. The other two
are lines inside `back_matter()` in the same file — delete them if you have
no publisher and no separate copyright line to read.

Fill them, re-run `python3 build-epub.py`, and confirm it says *"clean: no
director markers, no unnormalised numerals, no unfilled placeholders"*. The
build will not say that while a `«…»` survives anywhere in the text, which is
the point: a credit sequence with a visible placeholder in it is the one
error a listener is guaranteed to notice.

---

## Model choice

**Multilingual v2**, for three reasons that all point the same way:

1. It supports `<break time="x.xs" />`. v3 does not support break tags at
   all. The EPUB carries 80 of them at structural joins.
2. ElevenLabs' own documentation says the larger models read numbers more
   naturally than the small ones — their example is "$1,000,000", which
   Multilingual v2 reads as "one million dollars" and Flash v2.5 reads as
   "one thousand thousand dollars". This book is unusually number-dense and
   the numbers are the load-bearing part.
3. v3's selling point is emotional expressiveness through audio tags.
   `STYLE.md` bans exactly that — "no exclaiming at how interesting
   something is", humour "dry, occasional, never signposted". Paying v3's
   instability for a feature the book is written against is a bad trade.

If you want to try v3 anyway, rebuild with `--model v3`. That drops every
break tag and leaves pauses to paragraph structure and punctuation, which is
what the v3 docs recommend.

---

## Voice settings

The brief asks for a builder explaining something at a kitchen table, not a
documentary voice-over. In ElevenLabs terms:

- **Voice**: pick a conversational, unhurried voice. Avoid anything labelled
  "narration" that reads as broadcast-formal, and avoid the bright energetic
  ones outright. If you clone your own voice, the docs advise long
  continuous samples — short clips cause unnaturally fast pacing.
- **Stability**: high. You want the same voice in chapter 16 as in chapter 1
  across nearly three hours. Expressiveness is not the goal here.
- **Similarity**: high if using a clone, moderate otherwise.
- **Style exaggeration**: as low as it goes. This is the setting that
  produces the enthusiasm the book is written against.
- **Speed**: leave at 1.0 first. If it reads fast, drop toward 0.9 — the
  documented floor is 0.7, but anything below about 0.9 starts to sound
  drugged. Target is roughly 150 words per minute.

---

## The one thing to test before spending real credits

**Break tags in an imported EPUB are the unverified part of this setup.**

The tags are written into the EPUB escaped, so they arrive in Studio as the
literal text `<break time="2.0s" />` rather than as markup an importer might
strip. That is the reasoning, but it has not been confirmed against a live
import.

So, first action after upload, before converting anything else:

1. Open chapter 1 in the Studio editor.
2. Look at the block right after the `Chapter 1. The brain in the freezer.`
   heading. You should see `<break time="2.0s" />` as visible text.
3. Convert **only that chapter** and listen to the first thirty seconds.

Three possible outcomes:

- You hear "Chapter one, the brain in the freezer", a two-second silence,
  then the vacuum paragraph. Correct — carry on. ("Part One. The problem" is
  its own entry immediately above chapter 1, not part of it.)
- You hear the tag read aloud, something like "break time two point zero s".
  Rebuild with `python3 build-epub.py --breaks no` and re-upload. You lose
  the structural pauses; Studio lets you add them by hand where it matters.
- The tags are gone from the editor entirely. The importer stripped them.
  Same fix: rebuild with `--breaks no` and place pauses manually.

Chapter 1 is 1,093 words and 6,057 characters, so the test is cheap.

---

## Checks after import

- **Chapter split.** You should see **24** entries: opening credits, then for
  each of the six parts a short "Part N" entry followed by its chapters, then
  closing credits. Studio splits on Heading 1 and every document has exactly
  one. The part openings are separate documents on purpose — a part title
  placed as a paragraph above a chapter heading would attach to the *end* of
  the previous chapter, which is not where you want to hear "Part Three".
  If the whole book lands as a single blob, the EPUB did not import as
  structured, and it can be re-emitted as 24 separate text files instead.
- **Pronunciation dictionary.** Adding it marks affected blocks as
  unconverted, which is expected. Do it *before* the first full conversion,
  not after, or you pay twice.
- **"PRA".** Generate one block containing it and confirm you hear "P R A"
  and not "prah". This is the single highest-cost error in the book — it
  appears 23 times, and a listener who mishears it in the first minute
  mishears it for three hours.

---

## Size and cost

**141,957 billable characters**, about 2 hours 42 minutes at 150 words per
minute. That figure includes the 80 escaped break tags, which reach
ElevenLabs as literal text and are charged like any other characters; the
speakable text alone is about 140,000. Rebuilding with `--breaks no` costs
140,037.

ElevenLabs prices Studio by character, and a re-conversion after an edit
re-spends characters for the blocks that changed, so:

- get chapter 1 right before converting chapters 2 through 16;
- upload the pronunciation dictionary before the bulk conversion, not after;
- fill all four placeholders before the bulk conversion, not after.

Check the current per-character rate and what your plan includes on the
pricing page — I have not verified 2026 pricing and will not guess at it.

---

## What the normaliser already did to the text

The EPUB is not identical to the manuscript. `normalize.py` rewrote about
fifty things a speech model would plausibly get wrong. Run
`python3 normalize.py --report` to see every one with its surrounding
sentence — do that before spending credits, not after. Summary:

| Was | Is |
|---|---|
| `1/12` | one twelfth |
| `62–74`, `18–20` | 62 to 74, 18 to 20 (digits kept; the model reads them) |
| `13:11`, `21:55`, `22:49` | one eleven in the afternoon, nine fifty-five at night, ten forty-nine at night |
| `v3`, `v4` | vee three, vee four |
| `V0`, `V+` | V zero, V plus |
| `1.20.3` | one point twenty point three |
| `best_dim`, `turn_left` | best dim, turn left |
| `G1`, `G5`, `T7`, `STEP-0`, `E3.1` | gate one, gate five, test seven, step zero, E three point one |
| `x ≈ y` | x is about y |
| `→`, `π` | becoming, pi |

Plain decimals (`0.0081`), percentages (`98.22%`) and comma-grouped
thousands (`57,219`) were deliberately **left alone**. Multilingual v2 reads
those correctly, and rewriting them into words would add my errors on top of
a problem the model does not have.

If a chapter reads wrong in a way the table does not explain, the fix belongs
in `normalize.py`, not in the Studio editor — otherwise it is lost the next
time the manuscript changes and the EPUB is rebuilt.

---

## Rebuilding after a manuscript edit

```
python3 build-narration.py     # human-narrator scripts + manifest
python3 build-epub.py          # ElevenLabs EPUB + lexicon
```

Both read the manuscript directly. Nothing under `scripts/`,
`elevenlabs/`, or `MANIFEST.md` should ever be hand-edited — it is all
regenerated. The two files you *do* edit by hand are `audio-overrides.json`
(spoken versions of displayed data blocks) and the `LEXICON` table near the
bottom of `build-epub.py`.

---

## Sources

- [Studio overview](https://elevenlabs.io/docs/eleven-creative/products/studio)
- [Which file formats can I import with Studio?](https://help.elevenlabs.io/hc/en-us/articles/25708839235345-Which-file-formats-can-I-import-with-Studio)
- [Text to speech best practices — pauses, pronunciation dictionaries, normalisation](https://elevenlabs.io/docs/overview/capabilities/text-to-speech/best-practices)
- [Audiobooks](https://elevenlabs.io/docs/eleven-creative/products/audiobooks)
