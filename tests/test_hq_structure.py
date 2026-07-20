"""Structural lint for the hq/ headquarters layout.

Enforces the invariants promised in hq/00-GENESIS/how-we-work.md: the five
areas exist with their READMEs, research topics carry legal states and no
terminal-state folder lingers, journey episodes are contiguously numbered and
indexed, post-split episodes record their reversal condition, the speckit
constitution symlink resolves into GENESIS (a dangling link would silently
fork the constitution via speckit's template re-copy), and relative markdown
links inside hq/ resolve.
"""

import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
HQ = REPO / "hq"

AREAS = ["00-GENESIS", "01-RESEARCH", "02-DESIGN", "03-IMPLEMENTATION", "04-JOURNEY"]
GENESIS_FILES = ["README.md", "vision.md", "constitution.md", "how-we-work.md"]
EPISODE_RE = re.compile(r"^\d{4}-[a-z0-9-]+\.md$")
NON_EPISODE = {"README.md", "TEMPLATE.md"}
LEGAL_STATES = {"active", "graduated", "abandoned"}
TERMINAL_STATES = {"graduated", "abandoned"}
# Episodes 0001-0044 are the split of the original JOURNEY.md and predate the
# Reversal-condition requirement; it binds from 0045 onward.
PRE_SPLIT_LAST = 44

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")


def episodes() -> list[Path]:
    return sorted(
        p for p in (HQ / "04-JOURNEY").iterdir() if p.is_file() and p.name not in NON_EPISODE
    )


def test_hq_areas_exist_with_readmes():
    assert (HQ / "README.md").is_file(), "missing hq/README.md"
    for area in AREAS:
        assert (HQ / area / "README.md").is_file(), f"missing hq/{area}/README.md"
    for name in GENESIS_FILES:
        assert (HQ / "00-GENESIS" / name).is_file(), f"missing hq/00-GENESIS/{name}"
    assert (HQ / "01-RESEARCH" / "TEMPLATE.md").is_file()
    assert (HQ / "04-JOURNEY" / "TEMPLATE.md").is_file()


def test_research_topics_have_legal_nonterminal_states():
    for topic in sorted((HQ / "01-RESEARCH").iterdir()):
        if not topic.is_dir():
            continue
        readme = topic / "README.md"
        assert readme.is_file(), f"{topic.name}: research topic without README.md"
        text = readme.read_text()
        assert text.lstrip().startswith("# "), f"{topic.name}: README lacks a title"
        assert "## Abstract" in text, f"{topic.name}: README lacks an Abstract section"
        m = re.search(r"^\*\*State:\*\* *(\S+)", text, re.MULTILINE)
        assert m, f"{topic.name}: README lacks a '**State:** ...' line"
        state = m.group(1)
        assert state in LEGAL_STATES, f"{topic.name}: illegal state {state!r}"
        assert state not in TERMINAL_STATES, (
            f"{topic.name}: state {state!r} is terminal but the folder lingers — "
            "/research-graduate removes the topic folder on every outcome"
        )


def test_journey_episodes_numbered_contiguously():
    names = [p.name for p in episodes()]
    bad = [n for n in names if not EPISODE_RE.match(n)]
    assert not bad, f"files in hq/04-JOURNEY that are not NNNN-slug.md episodes: {bad}"
    nums = [int(n[:4]) for n in names]
    assert len(nums) == len(set(nums)), f"duplicate episode numbers: {sorted(nums)}"
    assert sorted(nums) == list(range(1, len(nums) + 1)), (
        f"episode numbers not contiguous from 0001: {sorted(nums)}"
    )


def test_journey_episodes_are_indexed():
    index = (HQ / "04-JOURNEY" / "README.md").read_text()
    missing = [p.name for p in episodes() if p.name not in index]
    assert not missing, f"episodes missing from the hq/04-JOURNEY/README.md index: {missing}"


def test_post_split_episodes_record_reversal_condition():
    offenders = [
        p.name
        for p in episodes()
        if int(p.name[:4]) > PRE_SPLIT_LAST and "Reversal condition:" not in p.read_text()
    ]
    assert not offenders, (
        f"episodes without the required 'Reversal condition:' line: {offenders} "
        "(see hq/04-JOURNEY/TEMPLATE.md)"
    )


def test_constitution_symlink_resolves_to_genesis():
    link = REPO / ".specify" / "memory" / "constitution.md"
    assert link.is_symlink(), ".specify/memory/constitution.md must be a symlink into GENESIS"
    canonical = (HQ / "00-GENESIS" / "constitution.md").resolve()
    assert link.resolve() == canonical, f"symlink points at {link.resolve()}, not {canonical}"
    assert canonical.is_file(), "dangling symlink — speckit would re-copy its template over it"
    assert "# PRA Constitution" in canonical.read_text()


def test_hq_relative_links_resolve():
    broken = []
    for md in sorted(HQ.rglob("*.md")):
        for target in LINK_RE.findall(md.read_text()):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            path = target.split("#", 1)[0]
            if path and not (md.parent / path).exists():
                broken.append(f"{md.relative_to(REPO)} -> {target}")
    assert not broken, "broken relative markdown links inside hq/:\n" + "\n".join(broken)
