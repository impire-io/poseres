# Phase 1 Data Model: API Stability & v1.0

No runtime data model changes. The entities are documentation/test
data structures.

## SurfaceEntry (in `tests/contract/surface_inventory.py`)

| Field | Type | Meaning |
|---|---|---|
| `path` | str | dotted import path (`pra.config.Config`) or CLI entry name (`pra-validate`) |
| `kind` | enum str | `class` \| `function` \| `protocol` \| `dataclass` \| `cli` \| `constant` \| `subject-family` |
| `family` | enum str | `world-body` \| `anatomy` \| `drive` \| `persistence` \| `run` \| `operational` |
| `params` | tuple[str, ...] \| None | for callables: required positional-or-keyword parameter names the promise covers |
| `doc` | str | pointer into Doc 0008 / the design doc that documents it |

Validation rules (enforced by the guard test):
- `path` resolves by import (or entry-point lookup for `cli`).
- live object matches `kind`; for callables, every declared `params`
  name is present in the live signature.
- every entry's name appears in Doc 0008, and Doc 0008 names no
  public element absent from the inventory (bidirectional agreement).

## DeprecationRecord (message format, `pra/_deprecation.py`)

| Field | Meaning |
|---|---|
| element | the deprecated name (auto-derived from the wrapped object) |
| replacement | what to use instead (required, non-empty) |
| removal | earliest release that may remove it (required, `"vX.Y"` form) |

Emitted as one `DeprecationWarning` sentence:
`"{element} is deprecated and may be removed in {removal}; use {replacement}."`
State transitions: public → deprecated (minor release, changelog entry)
→ removed (major release only, or documented urgent exception).

## Release

| Field | Meaning |
|---|---|
| version | `1.0.0` in `pyproject.toml` (single source; `pra.__version__` reads it) |
| tag | annotated signed `v1.0.0` on merged main |
| changelog | `CHANGELOG.md` entry stating the promise, linking Doc 0008 |
| gate evidence | the all-green gate on the tagged commit |
