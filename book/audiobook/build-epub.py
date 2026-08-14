#!/usr/bin/env python3
"""
Build an EPUB for ElevenLabs Studio from the PRA book manuscript.

This is a different artifact from scripts/. Those are for a human narrator
and are full of bracketed direction. ElevenLabs would either read that
direction aloud (v2 models) or interpret it as an audio tag (v3), so none of
it can survive into this file.

What this produces:
    elevenlabs/pra-book.epub      one h1 per chapter, which is what Studio
                                  uses to split the project into chapters
    elevenlabs/pronunciation.pls  lexicon to upload in project settings
    elevenlabs/preview/*.txt      plain text of each chapter, for eyeballing

Usage:
    python3 build-epub.py                  # default: v2, breaks on
    python3 build-epub.py --model v3       # no break tags; v3 rejects them
    python3 build-epub.py --breaks no      # structural pauses only
    python3 build-epub.py --boxes keep     # include technical asides
"""

import argparse
import html
import importlib.util
import pathlib
import re
import sys
import zipfile

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

# build-narration.py is not a legal module name, so load it by path.
_spec = importlib.util.spec_from_file_location("build_narration", HERE / "build-narration.py")
_bn = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_bn)
PART_NAMES, parse = _bn.PART_NAMES, _bn.parse

from normalize import normalize  # noqa: E402

BOOK = HERE.parent
OUT = HERE / "elevenlabs"

# Placeholders the author must fill. Kept identical to FRONT-BACK-MATTER.md.
TITLE = "«TITLE»"
AUTHOR = "Daan Gerits"
URL = "«URL»"


def brk(seconds: float, on: bool) -> str:
    """A pause. ElevenLabs caps break tags at 3 seconds and warns that heavy
    use destabilises a generation, so these are placed only at structural
    joins — never between ordinary paragraphs, where the paragraph break
    already does the work."""
    if not on:
        return ""
    # Escaped on purpose. A real <break> element is markup, and an EPUB text
    # extractor drops markup it does not recognise. Escaped, it survives
    # import as literal text in the Studio editor, which is where a break tag
    # has to live for the model to act on it.
    return html.escape(f'<break time="{seconds}s" />')


def to_xhtml(title: str, blocks: list[str]) -> str:
    body = "\n".join(blocks)
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        "<!DOCTYPE html>\n"
        '<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">\n'
        f"<head><title>{html.escape(title)}</title>"
        '<meta charset="utf-8" /></head>\n'
        f"<body>\n{body}\n</body>\n</html>\n"
    )


def para(text: str) -> str:
    return f"<p>{html.escape(text)}</p>"


def build_part(part_open, breaks, model):
    """A part opening gets its own document, and therefore its own h1.

    It cannot be a paragraph at the head of the first chapter: Studio splits
    on Heading 1, so a line placed above the chapter's h1 lands at the tail
    of the *previous* chapter instead.
    """
    use = breaks and model == "v2"
    blocks = [f"<h1>{html.escape(part_open)}</h1>"]
    if use:
        blocks.append(f"<p>{brk(2.5, True)}</p>")
    return to_xhtml(part_open, blocks), part_open


def build_chapter(num, title, segs, breaks, model):
    """Return (xhtml, plain_text). Bracketed direction never appears in either."""
    blocks, plain = [], []
    use_breaks = breaks and model == "v2"

    # The chapter title is the h1 Studio splits on. Everything else is <p>.
    blocks.append(f"<h1>Chapter {num}. {html.escape(title)}.</h1>")
    plain.append(f"Chapter {num}. {title}.")
    if use_breaks:
        blocks.append(f"<p>{brk(2.0, True)}</p>")

    for kind, body in segs:
        if kind in ("omitted", "summarise"):
            continue  # boxes are not in the audio edition
        body = normalize(body)
        if kind == "head":
            blocks.append(f"<h2>{html.escape(body)}.</h2>")
            plain.append(f"{body}.")
            if use_breaks:
                blocks.append(f"<p>{brk(1.5, True)}</p>")
            continue
        if kind == "box":
            # No spoken label: the print edition marks these visually, and a
            # spoken "under the hood" heading would be an invention.
            for p in body.split("\n\n"):
                blocks.append(para(p))
                plain.append(p)
            continue
        for p in body.split("\n\n"):
            if not p.strip():
                continue
            blocks.append(para(p))
            plain.append(p)

    return to_xhtml(title, blocks), "\n\n".join(plain)


def front_matter(breaks, model):
    lines = [
        f"{TITLE}.",
        f"Written and read by {AUTHOR}.",
        "A word about this recording. The book it comes from has two layers. "
        "The story you are about to hear is one of them, and it is complete "
        "on its own. The other layer is a set of technical asides, the "
        "mathematics, the failure data, the exact measurements, printed in "
        "boxes that a reader can skip. They are not in this recording. "
        "Nothing in the story depends on them. If you want them, they are in "
        "the text edition, and they are worth your time.",
        "The book also asks you, in part four, to install the system and "
        f"watch it learn on your own screen. You will find what you need at {URL}. "
        "You do not need it to follow the story.",
    ]
    blocks = [f"<h1>{html.escape(TITLE)}</h1>"] + [para(ln) for ln in lines]
    return to_xhtml("Opening credits", blocks), "\n\n".join(lines)


def back_matter():
    lines = [
        f"{TITLE}, written and read by {AUTHOR}.",
        "The system described in this book is open source. You can find it, "
        f"run it, and check every claim in it at {URL}.",
        "«Publisher or production credit, if any.»",
        "«Copyright line — year and rights holder.»",
    ]
    blocks = ["<h1>Closing credits</h1>"] + [para(ln) for ln in lines]
    return to_xhtml("Closing credits", blocks), "\n\n".join(lines)


def write_epub(path, docs):
    """docs: list of (filename, title, xhtml)."""
    opf_items, opf_refs, nav_items = [], [], []
    for i, (fn, title, _) in enumerate(docs):
        opf_items.append(f'<item id="c{i}" href="{fn}" media-type="application/xhtml+xml"/>')
        opf_refs.append(f'<itemref idref="c{i}"/>')
        nav_items.append(f'<li><a href="{fn}">{html.escape(title)}</a></li>')

    opf = f"""<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="bookid">urn:uuid:pra-book-audio-edition</dc:identifier>
    <dc:title>{html.escape(TITLE)}</dc:title>
    <dc:creator>{html.escape(AUTHOR)}</dc:creator>
    <dc:language>en</dc:language>
    <meta property="dcterms:modified">2026-08-13T00:00:00Z</meta>
  </metadata>
  <manifest>
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
    {chr(10).join("    " + i for i in opf_items).strip()}
  </manifest>
  <spine>
    {chr(10).join("    " + r for r in opf_refs).strip()}
  </spine>
</package>
"""
    nav = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:epub="http://www.idpf.org/2007/ops" lang="en" xml:lang="en">
<head><title>Contents</title><meta charset="utf-8" /></head>
<body><nav epub:type="toc" id="toc"><h1>Contents</h1><ol>
{chr(10).join(nav_items)}
</ol></nav></body></html>
"""
    container = """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles><rootfile full-path="OEBPS/content.opf"
    media-type="application/oebps-package+xml"/></rootfiles>
</container>
"""
    with zipfile.ZipFile(path, "w") as z:
        # mimetype must be first and stored uncompressed.
        z.writestr(
            zipfile.ZipInfo("mimetype"), "application/epub+zip", compress_type=zipfile.ZIP_STORED
        )
        z.writestr("META-INF/container.xml", container)
        z.writestr("OEBPS/content.opf", opf)
        z.writestr("OEBPS/nav.xhtml", nav)
        for fn, _, xhtml in docs:
            z.writestr(f"OEBPS/{fn}", xhtml)


# --------------------------------------------------------------- lexicon
# Alias pairs only. ElevenLabs phoneme tags are documented as working with
# eleven_flash_v2, not Multilingual v2, so a phoneme lexicon would silently
# do nothing on the model this book is narrated with. Aliases work everywhere.
#
# Two documented gotchas drive the design here:
#   - matching is case sensitive;
#   - the dictionary is checked start to end and only the FIRST match is used,
#     so entries are emitted longest-grapheme-first to stop a short entry
#     shadowing a longer one that contains it.
LEXICON = [
    ("PRA", "P R A", "the architecture. Never 'prah'."),
    ("ROS2", "ross two", "robotics framework"),
    ("ULP", "U L P", "unit in the last place"),
    ("CartPole", "Cart Pole", "two words"),
    ("poseres", "pohz res", "the package name"),
    ("pra-rover", "P R A rover", "the demo command"),
    ("lidar", "LY dar", "not spelled out"),
    ("odometry", "oh dom uh tree", ""),
    ("diff-drive", "diff drive", "no spoken hyphen"),
    ("Gerits", "Herits", "Dutch. VERIFY WITH THE AUTHOR before use."),
    ("Daan", "Dahn", "Dutch. VERIFY WITH THE AUTHOR before use."),
    ("Frobenius", "fro bee nee us", "technical asides only"),
]


def write_pls(path):
    entries = sorted(LEXICON, key=lambda e: -len(e[0]))
    body = []
    for grapheme, alias, note in entries:
        if note:
            body.append(f"  <!-- {html.escape(note)} -->")
        body.append("  <lexeme>")
        body.append(f"    <grapheme>{html.escape(grapheme)}</grapheme>")
        body.append(f"    <alias>{html.escape(alias)}</alias>")
        body.append("  </lexeme>")
    path.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<lexicon version="1.0"\n'
        '  xmlns="http://www.w3.org/2005/01/pronunciation-lexicon"\n'
        '  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n'
        '  xsi:schemaLocation="http://www.w3.org/2005/01/pronunciation-lexicon\n'
        '  http://www.w3.org/TR/2007/CR-pronunciation-lexicon-20071212/pls.xsd"\n'
        '  alphabet="ipa" xml:lang="en-GB">\n' + "\n".join(body) + "\n</lexicon>\n",
        encoding="utf-8",
    )
    return len(entries)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", choices=["v2", "v3"], default="v2")
    ap.add_argument("--breaks", choices=["yes", "no"], default="yes")
    ap.add_argument("--boxes", choices=["omit", "keep"], default="omit")
    a = ap.parse_args()
    breaks = a.breaks == "yes"

    OUT.mkdir(exist_ok=True)
    (OUT / "preview").mkdir(exist_ok=True)

    docs, previews = [], []
    xhtml, plain = front_matter(breaks, a.model)
    docs.append(("front.xhtml", "Opening credits", xhtml))
    previews.append(("00-front-matter.txt", plain))

    seen_part = None
    for path in sorted(BOOK.glob("part-*/[0-9]*.md"), key=lambda p: p.name):
        num = int(re.match(r"(\d+)", path.name).group(1))
        title, segs = parse(path.read_text(encoding="utf-8"), a.boxes, code_mode="tts")
        part = path.parent.name
        if part != seen_part and part in PART_NAMES:
            po = PART_NAMES[part]
            xhtml, plain = build_part(po, breaks, a.model)
            docs.append((f"{part}.xhtml", po, xhtml))
            previews.append((f"{num:02d}a-{part}.txt", plain))
        seen_part = part
        xhtml, plain = build_chapter(num, title, segs, breaks, a.model)
        stem = f"{num:02d}-{path.stem.split('-', 1)[1]}"
        docs.append((f"{stem}.xhtml", f"Chapter {num}. {title}", xhtml))
        previews.append((f"{stem}.txt", plain))

    xhtml, plain = back_matter()
    docs.append(("back.xhtml", "Closing credits", xhtml))
    previews.append(("99-back-matter.txt", plain))

    for fn, text in previews:
        (OUT / "preview" / fn).write_text(text + "\n", encoding="utf-8")

    epub = OUT / "pra-book.epub"
    write_epub(epub, docs)
    n_lex = write_pls(OUT / "pronunciation.pls")

    # --- checks that must hold before a single credit is spent -------------
    all_text = "\n".join(t for _, t in previews)
    problems = []
    for m in re.finditer(r"\[[^\]]*\]", all_text):
        problems.append(
            f"square brackets would be read or parsed as an audio tag: {m.group(0)[:50]}"
        )
    for m in re.finditer(r"\x01MISSING-PARAPHRASE\x01\s*(\S.*)", all_text):
        problems.append(
            f"displayed block with no spoken version — add one to "
            f"audio-overrides.json keyed on: {m.group(1)[:60]}"
        )
    for m in dict.fromkeys(re.findall(r"«[^»]*»", all_text)):
        problems.append(f"unfilled placeholder: {m}")
    for rx, what in (
        (r"\b\d+/\d+\b", "unnormalised slash"),
        (r"\b\d+[–—]\d+\b", "unnormalised range"),
        (r"\b\d{1,2}:\d{2}\b", "unnormalised clock time"),
        (r"[≈≥≤±→·×π_]", "unnormalised symbol"),
        (r"\bv\d+\b", "unnormalised version"),
    ):
        for m in re.finditer(rx, all_text):
            problems.append(f"{what}: {m.group(0)}")

    # Billable size is what actually reaches ElevenLabs, escaped break tags
    # included — they arrive as literal characters and are charged as such.
    epub_text = "\n".join(html.unescape(re.sub(r"<[^>]+>", " ", x)) for _, _, x in docs)
    chars = len(re.sub(r"[ \t]+", " ", epub_text))
    n_words = len(epub_text.split())
    n_breaks = epub_text.count("<break")

    print(f"EPUB written: {epub}")
    print(f"Lexicon written: {OUT / 'pronunciation.pls'} ({n_lex} entries)")
    print(
        f"{len(docs)} documents ({len(docs) - 8} chapters, 6 part openings, credits front and back)"
    )
    print(f"{n_words:,} words, about {n_words // 150}m at 150 wpm")
    print(f"{chars:,} characters billable, including {n_breaks} break tags")
    print(f"model={a.model} breaks={'on' if breaks and a.model == 'v2' else 'off'} boxes={a.boxes}")
    if problems:
        print(f"\n{len(problems)} problems — do NOT upload yet:")
        for p in dict.fromkeys(problems):
            print(f"  {p}")
    else:
        print("clean: no director markers, no unnormalised numerals, no unfilled placeholders")


if __name__ == "__main__":
    main()
