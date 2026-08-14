#!/usr/bin/env python3
"""
Build narration-ready scripts from the PRA book manuscript.

Re-run this after every draft revision. Nothing here is hand-edited output;
the scripts/ directory is generated and safe to delete.

Usage:
    python3 build-narration.py                    # default: boxes omitted
    python3 build-narration.py --boxes keep       # read boxes verbatim
    python3 build-narration.py --boxes summarise  # boxes marked for rewrite
    python3 build-narration.py --wpm 150          # narration speed estimate

Why boxes default to omitted: STYLE.md guarantees the main text is complete
without them ("Skipping every technical box loses precision, never plot").
A listener cannot skim past a paragraph of per-seed pass rates and file
paths; a reader can. See NARRATOR-BRIEF.md, section "The box problem".
"""

import argparse
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
BOOK = HERE.parent
OUT = HERE / "scripts"
OVERRIDES_PATH = HERE / "audio-overrides.json"

# Spoken replacements for displayed blocks. Keys are the first line of the
# block, whitespace-collapsed. Edit this file, not the generated scripts.
OVERRIDES = (
    json.loads(OVERRIDES_PATH.read_text(encoding="utf-8")) if OVERRIDES_PATH.exists() else {}
)

# ---------------------------------------------------------------- inline text


def strip_inline(text: str) -> str:
    """Remove markdown that has no spoken equivalent.

    Call this *after* unwrap(), never before: emphasis spans in the
    manuscript routinely straddle a hard wrap, and a newline-excluding
    regex silently leaves the asterisks in the narrator's script.
    """
    text = re.sub(r"\[\^[^\]\s]+\]", "", text)  # footnote markers
    text = re.sub(r"`([^`]+)`", r"\1", text)  # code spans
    text = re.sub(r"\*\*([^*]+?)\*\*", r"\1", text)  # bold
    text = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"\1", text)  # italics
    text = re.sub(r"__([^_]+?)__", r"\1", text)  # bold, underscore form
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)  # links
    text = re.sub(r"\\([*_`\[\]])", r"\1", text)  # escaped punctuation
    return text


def unwrap(block: str) -> str:
    """Join hard-wrapped lines into one paragraph per blank-line group."""
    paras = re.split(r"\n\s*\n", block.strip())
    return "\n\n".join(" ".join(p.split()) for p in paras if p.strip())


# ------------------------------------------------------------- block handling


def describe_code(body: str, mode: str = "narrator") -> str:
    """Turn a fenced code block into something that can be spoken.

    mode="narrator" adds bracketed direction for a human reader.
    mode="tts" emits speakable prose only — a speech model would read the
    direction aloud, or worse, parse the brackets as an audio tag.
    """
    lines = [ln for ln in body.strip().splitlines() if ln.strip()]
    key = " ".join(lines[0].split()) if lines else ""
    if key in OVERRIDES:
        spoken = OVERRIDES[key]
        return (
            spoken
            if mode == "tts"
            else ("[DISPLAYED BLOCK — read this spoken version instead]\n\n" + spoken)
        )

    if all(re.match(r"^(pip|pra-|python|npm|cargo|git|sudo)\b", ln.strip()) for ln in lines):
        cmds = [ln.strip() for ln in lines]
        if mode == "tts":
            spoken = ", then ".join(cmds)
            return f"The commands are {spoken}. They are printed in the text edition."
        return (
            "[NARRATOR NOTE — commands on the page. Read as: "
            f'"{"; then ".join(cmds)}". Do not spell out punctuation. '
            "The listener is told in the front matter where to find these in text.]"
        )

    if mode == "tts":
        # No paraphrase and not a command list: refuse rather than guess.
        return "\x01MISSING-PARAPHRASE\x01 " + key
    return (
        "[NARRATOR NOTE — displayed data block, not prose. "
        "Read the audio paraphrase supplied below it, not the block itself. "
        "If no paraphrase is present, flag it back to the author.]\n\n"
        + "\n".join("    " + ln for ln in lines)
    )


def parse(md: str, boxes: str, code_mode: str = "narrator"):
    """Split a chapter into (title, [(kind, text), ...])."""
    md = re.sub(r"<!--.*?-->", "", md, flags=re.S)

    # Footnote definitions are pointers for the text edition ("Chapter 7.")
    # and are never read aloud. Drop the definition block, including any
    # indented continuation lines.
    md = re.sub(r"^\[\^[^\]]+\]:.*(?:\n[ \t]+\S.*)*$", "", md, flags=re.M)

    # pull fenced code out first so it is not line-processed
    code = []

    def stash(m):
        code.append(m.group(1))
        return f"\n\n\x00CODE{len(code) - 1}\x00\n\n"

    md = re.sub(r"```[a-zA-Z]*\n(.*?)```", stash, md, flags=re.S)

    title = None
    segs, buf, mode = [], [], "prose"

    def flush():
        if buf:
            segs.append((mode, "\n".join(buf)))
            buf.clear()

    for line in md.splitlines():
        is_box = line.startswith(">")
        if is_box and mode != "box":
            flush()
            mode = "box"
        elif not is_box and mode == "box":
            flush()
            mode = "prose"

        if mode == "box":
            buf.append(re.sub(r"^>\s?", "", line))
            continue

        if line.startswith("# "):
            flush()
            title = strip_inline(line[2:].strip())
            continue
        if line.startswith("#"):
            flush()
            segs.append(("head", strip_inline(line.lstrip("#").strip())))
            continue
        buf.append(line)
    flush()

    out = []
    for kind, body in segs:
        if kind == "box":
            # Read the label off the raw bold run, not off stripped text: the
            # label itself may contain periods ("the label gate (E3.1)").
            m = re.search(r"\*\*Under the hood:\s*(.+?)\.?\*\*", body, flags=re.S)
            label = strip_inline(" ".join(m.group(1).split())) if m else "technical aside"
            if boxes == "omit":
                out.append(("omitted", label))
                continue
            if boxes == "summarise":
                out.append(("summarise", label))
                continue
            out.append(("box", strip_inline(unwrap(body))))
        elif kind == "head":
            out.append(("head", body))
        else:
            body = strip_inline(unwrap(body))
            for i, c in enumerate(code):
                body = body.replace(f"\x00CODE{i}\x00", describe_code(c, code_mode))
            if body.strip():
                out.append(("prose", body))
    return title, out


# ------------------------------------------------------------------- emitting

PART_NAMES = {
    "part-1-the-problem": "Part One. The problem.",
    "part-2-the-triplet": "Part Two. The triplet.",
    "part-3-the-mechanism": "Part Three. The mechanism.",
    "part-4-the-continuity-guarantee": "Part Four. The continuity guarantee.",
    "part-5-the-long-run": "Part Five. The long run.",
    "part-6-teachers": "Part Six. Teachers.",
}


def render(num, title, segs, part_open):
    L = []
    if part_open:
        L += ["[PART OPENING — read, then pause 3 seconds]", part_open, "", "[PAUSE 3]", ""]
    L += [f"Chapter {num}. {title}.", "", "[PAUSE 2]", ""]
    for kind, body in segs:
        if kind == "head":
            L += ["[PAUSE 2]", f"[SECTION — lift and re-set] {body}.", ""]
        elif kind == "omitted":
            L += [f"[BOX OMITTED FROM AUDIO: {body}]", ""]
        elif kind == "summarise":
            L += [
                f"[BOX NEEDS AUDIO REWRITE: {body} — replace this line with a "
                "spoken-friendly version: headline result only, no file paths, "
                "no per-seed tables, no symbols.]",
                "",
            ]
        elif kind == "box":
            L += [
                "[PAUSE 2]",
                "[TECHNICAL ASIDE — closer, slower, drop a third. Return to full voice after.]",
                body,
                "",
                "[END ASIDE] [PAUSE 2]",
                "",
            ]
        else:
            L += [body, ""]
    L += ["[PAUSE 3]", "[END OF CHAPTER]"]
    return "\n".join(L).replace("\n\n\n", "\n\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--boxes", choices=["omit", "keep", "summarise"], default="omit")
    ap.add_argument("--wpm", type=int, default=150)
    a = ap.parse_args()

    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("*.txt"):
        try:
            old.unlink()
        except OSError:
            pass  # some synced/mounted folders disallow delete; files are overwritten

    chapters = sorted(BOOK.glob("part-*/[0-9]*.md"), key=lambda p: p.name)
    if not chapters:
        sys.exit("No chapter files found. Is this script inside book/audiobook/ ?")

    seen_part, rows, total, warnings = None, [], 0, []
    for path in chapters:
        num = int(re.match(r"(\d+)", path.name).group(1))
        title, segs = parse(path.read_text(encoding="utf-8"), a.boxes)
        part = path.parent.name
        part_open = PART_NAMES.get(part) if part != seen_part else None
        seen_part = part

        text = render(num, title, segs, part_open)
        spoken = re.sub(r"\[[^\]]*\]", "", text)
        words = len(spoken.split())
        total += words

        # Self-check: anything below would be read aloud as literal punctuation.
        # Underscores inside identifiers (best_dim, turn_left, score_window_steps)
        # are real content and are covered by PRONUNCIATION.md, so the emphasis
        # check only fires on underscores that bound a span like markdown would.
        # A star bound to the end of a symbol (κ*, β*, κ₅*) is superscript-star
        # notation, escaped in the manuscript so markdown leaves it alone. It is
        # content, and PRONUNCIATION.md tells the narrator to say "star".
        spoken_chk = re.sub(r"(?<=\S)\*(?![*\w])", "", spoken)
        for pat, what in (
            (r"[*`]", "markdown emphasis or code span"),
            (r"(?<![\w])_[^_]+_(?![\w])", "markdown emphasis"),
            (r"^\s*\||\s\|\s", "table syntax"),
            (r"^#", "heading marker"),
            (r"^>", "blockquote marker"),
            (r"https?://", "raw URL"),
            (r"\x00", "unresolved code placeholder"),
        ):
            for i, line in enumerate(spoken_chk.splitlines(), 1):
                if re.search(pat, line):
                    warnings.append(f"  ch{num:02d} line {i}: {what} — {line[:70]}")

        dest = OUT / f"{num:02d}-{path.stem.split('-', 1)[1]}.txt"
        dest.write_text(text, encoding="utf-8")
        rows.append((num, title, words, words / a.wpm))

    def hms(mins):
        return f"{int(mins) // 60}h {int(mins) % 60:02d}m" if mins >= 60 else f"{mins:.0f}m"

    man = [
        "# Narration manifest",
        "",
        f"Generated by build-narration.py --boxes {a.boxes} --wpm {a.wpm}",
        "Regenerate after every manuscript revision. Do not hand-edit scripts/.",
        "",
        "| Ch | Title | Spoken words | Est. runtime |",
        "|---:|---|---:|---:|",
    ]
    for n, t, w, m in rows:
        man.append(f"| {n} | {t} | {w:,} | {hms(m)} |")
    man += [
        f"| | **Total** | **{total:,}** | **{hms(total / a.wpm)}** |",
        "",
        f"Runtime assumes {a.wpm} words per minute, which is a measured, unhurried "
        "non-fiction pace. Add roughly 8 percent for pauses, part openings, and "
        "front and back matter.",
        "",
        "Finished-hour cost planning: studio narrators quote per finished hour "
        "(PFH), and raw recording runs three to six times finished time. "
        "Synthetic narration is priced per character, not per hour.",
    ]
    (OUT.parent / "MANIFEST.md").write_text("\n".join(man) + "\n", encoding="utf-8")

    print(f"{len(rows)} chapters written to {OUT}")
    print(f"{total:,} spoken words, about {hms(total / a.wpm)} at {a.wpm} wpm")
    print(f"boxes: {a.boxes}")
    if warnings:
        print(f"\n{len(warnings)} lines contain syntax a narrator would read aloud:")
        print("\n".join(warnings[:20]))
        if len(warnings) > 20:
            print(f"  ... and {len(warnings) - 20} more")
    else:
        print("no stray markup in spoken text")


if __name__ == "__main__":
    main()
