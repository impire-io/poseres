"""The surface guard (feature 035): the v1 public promise, enforced.

Contract: specs/035-api-stability-v1/contracts/public-surface.md.
A release in which a public element vanished or changed shape without
following the Doc 0008 policy fails here, not in a user's project.
"""

from __future__ import annotations

import dataclasses
import inspect
import re
import tomllib
from importlib import import_module, metadata
from pathlib import Path

import pytest

from tests.contract.surface_inventory import SURFACE, SurfaceEntry

REPO = Path(__file__).resolve().parents[2]
DOC = REPO / "hq" / "02-DESIGN" / "0008-public-api-versioning.md"
PYPROJECT = REPO / "pyproject.toml"


def _resolve(path: str):
    parts = path.split(".")
    for split in range(len(parts), 0, -1):
        module_path = ".".join(parts[:split])
        try:
            obj = import_module(module_path)
        except ModuleNotFoundError:
            continue
        for attr in parts[split:]:
            obj = getattr(obj, attr)
        return obj
    raise ModuleNotFoundError(path)


def _kind_of(obj) -> str:
    if inspect.isclass(obj):
        if getattr(obj, "_is_protocol", False):
            return "protocol"
        if dataclasses.is_dataclass(obj):
            return "dataclass"
        return "class"
    if inspect.isfunction(obj) or inspect.isbuiltin(obj):
        return "function"
    return "constant"


def _check_entry(entry: SurfaceEntry) -> None:
    """The guard for one entry; raises AssertionError on any break."""
    if entry.kind == "cli":
        scripts = tomllib.loads(PYPROJECT.read_text())["project"]["scripts"]
        assert entry.path in scripts, f"CLI entry point {entry.path!r} missing from pyproject"
        module_path, func = scripts[entry.path].split(":")
        assert callable(getattr(import_module(module_path), func))
        return
    if entry.kind == "subject-family":
        return  # documented space; presence checked by the doc-agreement test
    obj = _resolve(entry.path)
    live_kind = _kind_of(obj)
    assert live_kind == entry.kind, f"{entry.path}: declared {entry.kind}, live {live_kind}"
    if entry.params is not None:
        target = obj.__init__ if inspect.isclass(obj) else obj
        live = [p.name for p in inspect.signature(target).parameters.values() if p.name != "self"]
        missing = [name for name in entry.params if name not in live]
        assert not missing, f"{entry.path}: promised params missing: {missing}"


@pytest.mark.parametrize("entry", SURFACE, ids=lambda entry: entry.path)
def test_public_element_holds_its_promise(entry: SurfaceEntry) -> None:
    _check_entry(entry)


def _doc_claimed_names() -> set[str]:
    """Backticked surface tokens inside Doc 0008's 'The public surface' section."""
    text = DOC.read_text()
    match = re.search(
        r"^## The public surface\b.*?(?=^## (?!The public surface)|\Z)",
        text,
        re.DOTALL | re.MULTILINE,
    )
    assert match, "Doc 0008 must contain a '## The public surface' section"
    return {
        token
        for token in re.findall(r"`([^`]+)`", match.group(0))
        if token.startswith(("pra.", "pra-"))
    }


def test_doc_and_inventory_agree_bidirectionally() -> None:
    inventory = {entry.path for entry in SURFACE}
    documented = _doc_claimed_names()
    undocumented = sorted(inventory - documented)
    unpromised = sorted(documented - inventory)
    assert not undocumented, f"in inventory but not in Doc 0008: {undocumented}"
    assert not unpromised, f"Doc 0008 claims elements not in the inventory: {unpromised}"


def test_version_single_sources_from_pyproject() -> None:
    pyproject_version = tomllib.loads(PYPROJECT.read_text())["project"]["version"]
    import pra

    assert pra.__version__ == pyproject_version
    assert metadata.version("poseres") == pyproject_version


def test_quickstart_names_are_public() -> None:
    """The quickstart's imports are exactly public surface (spec T009)."""
    from pra import Config, Engine, __version__
    from pra.world.ladder import make_world

    assert callable(make_world) and inspect.isclass(Engine)
    assert dataclasses.is_dataclass(Config) and isinstance(__version__, str)


def test_guard_catches_a_removed_symbol() -> None:
    """Negative control: the guard must FAIL on a vanished element."""
    mutated = dataclasses.replace(SURFACE[0], path=SURFACE[0].path + "_this_symbol_does_not_exist")
    with pytest.raises((AssertionError, AttributeError, ModuleNotFoundError)):
        _check_entry(mutated)


def test_guard_catches_a_renamed_parameter() -> None:
    """Negative control: the guard must FAIL on a broken signature."""
    entry = next(e for e in SURFACE if e.path == "pra.world.ladder.make_world")
    mutated = dataclasses.replace(entry, params=("config", "rng_renamed_away"))
    with pytest.raises(AssertionError, match="promised params missing"):
        _check_entry(mutated)
