#!/usr/bin/env python3
"""
Text normalisation for text-to-speech.

A narrator reads PRONUNCIATION.md and applies judgement. A speech model
cannot: it only sees the characters you send it. So every rule in that
document that a model would plausibly get wrong has to become an actual
substitution in the text before the text is uploaded.

Scope is deliberately narrow. ElevenLabs Multilingual v2 is the largest of
their models and, per their own documentation, the best at reading ordinary
numbers ("$1,000,000" is read correctly as "one million dollars", where the
smaller Flash model says "one thousand thousand dollars"). Normalising things
it already handles adds risk without adding value, so plain decimals,
percentages, and comma-grouped thousands are left alone on purpose.

What gets rewritten is the set of forms that are genuinely ambiguous or that
have no spoken convention a model could infer:

    1/12          a fraction, not a score
    62-74         a range, not a subtraction
    21:55         a 24-hour clock time
    v3            a prototype generation, not a version string
    1.20.3        a software version, not a decimal
    best_dim      an identifier, not a word with an underscore in it
    pi, arrows, comparators, multiplication dots

Run `python3 normalize.py --report` to see every substitution that fires
against the current scripts, with surrounding context. Audit that output
before you spend credits.
"""

import argparse
import pathlib
import re
import sys

ONES = (
    "zero one two three four five six seven eight nine ten eleven twelve "
    "thirteen fourteen fifteen sixteen seventeen eighteen nineteen"
).split()
TENS = ("_ _ twenty thirty forty fifty sixty seventy eighty ninety").split()


def words(n: int) -> str:
    """Small integers to words. Enough for ranges, clock times, fractions."""
    if n < 20:
        return ONES[n]
    if n < 100:
        t, r = divmod(n, 10)
        return TENS[t] + (f"-{ONES[r]}" if r else "")
    if n < 1000:
        h, r = divmod(n, 100)
        return ONES[h] + " hundred" + (f" and {words(r)}" if r else "")
    return str(n)


ORDINALS = {
    2: "half",
    3: "third",
    4: "quarter",
    5: "fifth",
    6: "sixth",
    7: "seventh",
    8: "eighth",
    9: "ninth",
    10: "tenth",
    11: "eleventh",
    12: "twelfth",
    16: "sixteenth",
    20: "twentieth",
    24: "twenty-fourth",
    100: "hundredth",
}


def fraction(m):
    """x/y where the sentence is about a share or rate, not a score.

    PRONUNCIATION.md rule 5: a slash is normally "out of" (a pass rate like
    24/24), but a genuine fraction is read as a fraction. The distinction is
    semantic, so the fraction cases are listed explicitly rather than guessed.
    """
    num, den = int(m.group(1)), int(m.group(2))
    if den in ORDINALS:
        unit = ORDINALS[den]
        return f"{words(num)} {unit}" + ("s" if num > 1 else "")
    return f"{words(num)} over {words(den)}"


# Slash forms that are fractions. Everything else becomes "out of".
FRACTIONS = {"1/12"}


def slash(m):
    whole = m.group(0)
    if whole in FRACTIONS:
        return fraction(m)
    return f"{m.group(1)} out of {m.group(2)}"


def clock(m):
    """24-hour times. These mark how late in the day a gate was registered,
    so the hour has to stay audible."""
    h, mi = int(m.group(1)), int(m.group(2))
    suffix = "in the morning" if h < 12 else ("in the afternoon" if h < 18 else "at night")
    h12 = h % 12 or 12
    if mi == 0:
        return f"{words(h12)} o'clock {suffix}"
    return f"{words(h12)} {words(mi) if mi >= 10 else 'oh ' + words(mi)} {suffix}"


def dotted_version(m):
    """1.20.3 -> one point twenty point three. Tolerates a leading 'v',
    because the version rule that calls this matches v1.1.0 as well."""
    parts = m.group(0).lstrip("vV").split(".")
    return " point ".join(words(int(p)) if p.isdigit() and int(p) < 1000 else p for p in parts)


# Ordered. Earlier rules win, so put the specific before the general.
RULES = [
    # --- identifiers ------------------------------------------------------
    (r"\bbest_dim\b", "best dim", "identifier"),
    (r"\bturn_left\b", "turn left", "identifier"),
    (r"\b([a-z]+)_([a-z_]+)\b", lambda m: m.group(0).replace("_", " "), "identifier (generic)"),
    # --- versions and generations ----------------------------------------
    (r"\bv(\d+)\.(\d+)\.(\d+)\b", lambda m: "version " + dotted_version(m), "software version"),
    (r"\b(\d+)\.(\d+)\.(\d+)\b", dotted_version, "software version"),
    (r"\bv(\d+)\b", lambda m: f"vee {words(int(m.group(1)))}", "prototype generation"),
    # --- clock times ------------------------------------------------------
    (r"\b([01]?\d|2[0-3]):([0-5]\d)\b", clock, "clock time"),
    # --- fractions and ratios --------------------------------------------
    (r"\b(\d{1,3})/(\d{1,3})\b", slash, "fraction or ratio"),
    # --- ranges -----------------------------------------------------------
    (r"\b(\d+)\s*[–—]\s*(\d+)\b", lambda m: f"{m.group(1)} to {m.group(2)}", "numeric range"),
    (r"\b(\d+)-dim\b", lambda m: f"{words(int(m.group(1)))} dim", "dimension count"),
    # --- symbols ----------------------------------------------------------
    (r"\s*→\s*", ", becoming ", "arrow"),
    # "best dim is about 1", "one twelfth is about 0.083". Both readings in
    # the manuscript have a noun phrase on the left, so the copula fits.
    (r"\s*≈\s*", " is about ", "approximately"),
    (r"\s*≥\s*", " at least ", "comparator"),
    (r"\s*≤\s*", " at most ", "comparator"),
    (r"\s*±\s*", " plus or minus ", "comparator"),
    (r"(?<=\d)\s*·\s*(?=\d)", " times ", "multiplication dot"),
    (r"\s*·\s*", " times ", "multiplication dot"),
    (r"(?<=[\dA-Za-zα-ωΑ-Ω₀-₉])\*", " star", "superscript star"),
    (r"−(?=\d)", "minus ", "minus sign"),
    (r"×", " by ", "multiplication cross"),
    # --- greek ------------------------------------------------------------
    (r"π", "pi", "greek letter"),
    (r"κ", "kappa", "greek letter"),
    (r"λ", "lambda", "greek letter"),
    (r"β", "beta", "greek letter"),
    (r"Φ", "phi", "greek letter"),
    (r"Δ̂", "delta hat", "greek letter"),
    (r"Δ", "delta", "greek letter"),
    (r"σ", "sigma", "greek letter"),
    (r"μ", "mu", "greek letter"),
    (
        r"([₀-₉]+)",
        lambda m: " " + " ".join(words(ord(c) - 0x2080) for c in m.group(1)),
        "subscript digits",
    ),
    # --- labels -----------------------------------------------------------
    (r"\bG(\d)\b", lambda m: f"gate {words(int(m.group(1)))}", "gate label"),
    (r"\bT(\d)\b", lambda m: f"test {words(int(m.group(1)))}", "test label"),
    (r"\bSTEP-(\d)\b", lambda m: f"step {words(int(m.group(1)))}", "step label"),
    (
        r"\bE(\d)\.(\d)\b",
        lambda m: f"E {words(int(m.group(1)))} point {words(int(m.group(2)))}",
        "experiment label",
    ),
    (r"\bc1([a-z])\b", lambda m: f"C one {m.group(1).upper()}", "run id"),
    # Stated explicitly so the arm labels are handled on purpose rather than
    # by accident. v3/v4 become "vee three"; V0 and V+ stay as letters.
    (r"\bV0\b", "V zero", "arm label"),
    (r"\bV\+", "V plus", "arm label"),
    # --- trailing tidy ----------------------------------------------------
    (r"  +", " ", "double space"),
]

COMPILED = [(re.compile(p), r, d) for p, r, d in RULES]


def normalize(text: str, log=None):
    for rx, rep, desc in COMPILED:
        if log is not None:
            for m in rx.finditer(text):
                if desc == "double space":
                    continue
                lo, hi = max(0, m.start() - 45), min(len(text), m.end() + 45)
                log.append((desc, m.group(0), " ".join(text[lo:hi].split())))
        text = rx.sub(rep, text)
    return text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--report", action="store_true", help="list every substitution against scripts/ and exit"
    )
    a = ap.parse_args()

    src = pathlib.Path(__file__).resolve().parent / "scripts"
    files = sorted(src.glob("*.txt"))
    if not files:
        sys.exit("No scripts/ found. Run build-narration.py first.")

    log = []
    for f in files:
        body = re.sub(r"\[[^\]]*\]", "", f.read_text(encoding="utf-8"))
        normalize(body, log)

    if a.report:
        by_kind = {}
        for desc, hit, ctx in log:
            by_kind.setdefault(desc, []).append((hit, ctx))
        for desc in sorted(by_kind):
            items = by_kind[desc]
            print(f"\n{desc} — {len(items)} occurrence(s)")
            seen = set()
            for hit, ctx in items:
                if hit in seen:
                    continue
                seen.add(hit)
                print(f"  {hit!r}\n      …{ctx}…")
        print(f"\n{len(log)} substitutions total across {len(files)} chapters.")
    else:
        print(f"{len(log)} substitutions would fire. Use --report to inspect.")


if __name__ == "__main__":
    main()
