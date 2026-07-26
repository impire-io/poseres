# Quickstart: living with the v1.0 surface

## As a user (build a world against the frozen seam)

```python
from pra import Config, Engine, __version__
from pra.world.ladder import make_world  # public: world seam

cfg = Config(world="shifting", shift_after_steps=6760)
summary = Engine(cfg, world_factory=make_world).run(seed=1)
```

Everything you may rely on is listed in
`hq/02-DESIGN/0008-public-api-versioning.md`. If a name isn't there,
it's internal: it may move in any release. Upgrading within v1.x never
breaks the listed surface — the release gate itself enforces it.

## As the maintainer (deprecate something)

```python
from pra._deprecation import deprecated

@deprecated(replacement="pra.new_thing", removal="v2.0")
def old_thing(...): ...
```

Then: changelog entry in the same release; removal no earlier than the
next major, and only if the deprecation shipped at least one minor
release earlier.

## As the maintainer (cut the release)

1. Merge the feature; gate green on main (all tests, zero skips).
2. `pyproject.toml` version → `1.0.0` (already part of this feature).
3. `git tag -s v1.0.0 -m "v1.0.0 — the public surface freezes"` and push the tag.
4. Verify: `pip install .` in a fresh venv → `python -c "import pra; print(pra.__version__)"` prints `1.0.0`.
