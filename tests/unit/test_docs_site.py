"""The docs site cannot silently rot (feature 036, FR-006).

The site under ``docs/`` single-sources its heavyweight content: the deploy
workflow (``.github/workflows/docs.yml``) copies ``GETTING-STARTED.md``,
``hq/02-DESIGN/0*.md`` and ``explainer/index.html`` into the assembled site
at build time. That scheme rots silently if a source moves, so this module
checks — with no network and no Jekyll — that:

- every file the workflow's copy step reads exists in the repository, and
  the workflow still contains each copy command the site relies on;
- every relative link in the committed ``docs/`` pages resolves, either to a
  committed file or to one the workflow provides at build time;
- every ``header_pages`` navigation entry in ``docs/_config.yml`` resolves
  the same way;
- every GitHub ``blob``/``tree`` link into this repository points at a path
  that exists at that location in the tree;
- the README links the deployed site (the roadmap's exit criterion).

The resolver's own failure mode is demonstrated, not assumed
(``test_guard_rejects_missing_references``).
"""

import posixpath
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DOCS = REPO / "docs"
WORKFLOW = REPO / ".github" / "workflows" / "docs.yml"

# The workflow's copy list, mirrored (exact command substrings). If the
# assemble step changes, this map and the workflow must move together.
COPY_COMMANDS = {
    "cp GETTING-STARTED.md docs/getting-started.md",
    "cp hq/02-DESIGN/0*.md docs/design/",
    "cp explainer/index.html docs/explainer/index.html",
}
# Site-root-relative paths that exist only in the assembled site, mapped to
# the repo files the workflow copies them from.
BUILD_PROVIDED = {
    "getting-started.md": "GETTING-STARTED.md",
    "explainer": "explainer/index.html",
    "explainer/index.html": "explainer/index.html",
}
DESIGN_SITE_DIR = "design"
DESIGN_SOURCE_DIR = "hq/02-DESIGN"

LINK_RE = re.compile(r"\]\(([^)\s]+)\)")
GITHUB_RE = re.compile(r"https://github\.com/impire-io/poseres/(?:blob|tree)/main/([^)#\s]+)")
PAGES_URL = "https://impire-io.github.io/poseres/"


def committed_pages() -> list[Path]:
    pages = sorted(DOCS.rglob("*.md"))
    assert pages, "no committed pages under docs/"
    return pages


def site_target_resolves(target: str) -> bool:
    """True iff a site-root-relative path exists committed under docs/ or is
    provided by the workflow's build-time copies."""
    target = target.rstrip("/")
    if (DOCS / target).is_file():
        return True
    if target in BUILD_PROVIDED:
        return (REPO / BUILD_PROVIDED[target]).is_file()
    head, _, name = target.partition("/")
    if head == DESIGN_SITE_DIR and name:
        return (REPO / DESIGN_SOURCE_DIR / name).is_file()
    return False


def test_workflow_copy_sources_exist():
    text = WORKFLOW.read_text()
    for command in COPY_COMMANDS:
        assert command in text, f"docs.yml lost its copy step: {command!r}"
        source = command.split()[1]
        if "*" in source:
            assert list(REPO.glob(source)), f"workflow copy glob matches nothing: {source}"
        else:
            assert (REPO / source).is_file(), f"workflow copy source missing: {source}"


def test_workflow_trigger_paths_exist():
    text = WORKFLOW.read_text()
    for token in re.findall(r'-\s+"([^"*]+?)(?:/\*\*)?"', text):
        assert (REPO / token).exists(), f"docs.yml trigger path missing from repo: {token}"


def test_relative_links_in_committed_pages_resolve():
    for page in committed_pages():
        base = page.parent.relative_to(DOCS).as_posix()
        for link in LINK_RE.findall(page.read_text()):
            if link.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target = posixpath.normpath(posixpath.join("" if base == "." else base, link))
            target = target.split("#", 1)[0]
            assert site_target_resolves(target), (
                f"{page.relative_to(REPO)} links {link!r} -> {target!r}, "
                "which neither exists under docs/ nor is copied in by docs.yml"
            )


def test_github_links_point_at_existing_paths():
    for page in committed_pages():
        for repo_path in GITHUB_RE.findall(page.read_text()):
            assert (REPO / repo_path).exists(), (
                f"{page.relative_to(REPO)} links a GitHub path absent from the tree: {repo_path}"
            )


def test_nav_entries_resolve():
    config = (DOCS / "_config.yml").read_text()
    block = config.split("header_pages:", 1)
    assert len(block) == 2, "docs/_config.yml lost its header_pages navigation"
    entries = re.findall(r"^\s+-\s+(\S+)", block[1], flags=re.MULTILINE)
    assert entries, "header_pages is empty"
    for entry in entries:
        assert site_target_resolves(entry), f"nav entry does not resolve: {entry}"


def test_design_index_links_every_design_doc():
    index = (DOCS / DESIGN_SITE_DIR / "index.md").read_text()
    docs = sorted(p.name for p in (REPO / DESIGN_SOURCE_DIR).glob("0*.md"))
    assert docs, "no design docs found to deploy"
    for name in docs:
        assert f"({name})" in index, (
            f"docs/design/index.md misses a row for {name} — the glob deploys it, "
            "the reading order must link it"
        )


def test_readme_links_the_deployed_site():
    assert PAGES_URL in (REPO / "README.md").read_text(), (
        "README.md must link the deployed docs site (roadmap exit criterion)"
    )


def test_guard_rejects_missing_references():
    # The resolver must discriminate, not rubber-stamp: unknown pages, absent
    # design docs, and repo paths that left the tree all read as failures.
    assert not site_target_resolves("no-such-page.md")
    assert not site_target_resolves("design/0999-never-written.md")
    assert not (REPO / "hq/02-DESIGN/0999-never-written.md").exists()
