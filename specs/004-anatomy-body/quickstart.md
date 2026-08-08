# Quickstart: Anatomy and Body

## 1. Mount the world through a body (byte-identical)

```python
from pra.anatomy.body import Body, WorldSensor, WorldActuator
from pra.config import Config
from pra.core.engine import Engine
from pra.world.event_source import SensorimotorWorld


def body_factory(cfg, rng):
    world = SensorimotorWorld(cfg, rng)
    return Body(world, sensors=[WorldSensor(world)], actuators=[WorldActuator(world)])


summary = Engine(Config(), world_factory=body_factory).run(1)
# byte-identical to Engine(Config()).run(1)
```

## 2. Grow the body mid-run (tools)

```python
from pra.anatomy.body import ConstantSensor

body.register_sensor(ConstantSensor("thermo", [0.5, -0.5]))  # queued
# ... takes effect at the next consolidation cycle: obs_dim += 2,
# every frame's encoder/decoder resized (learned weights preserved).
```

## 3. Verify

```bash
./.venv/bin/pytest tests/unit/test_body_composition.py tests/unit/test_frame_resize.py \
  tests/contract/test_anatomy_contract.py tests/integration/test_anatomy_growth.py -q
./.venv/bin/ruff format --check . && ./.venv/bin/ruff check . && ./.venv/bin/pytest -q
```

## 4. Scenario → check map

| Spec scenario | Verify |
|---|---|
| US1 composition/routing/byte-identity | `test_body_composition.py`, `test_anatomy_growth.py::test_world_through_body_is_byte_identical` |
| US2 growth without forgetting | `test_frame_resize.py`, `test_anatomy_growth.py::test_midrun_growth*` |
| US3 baseline untouched | `test_anatomy_growth.py::test_baseline_unchanged` |
| Edge cases (widths, duplicates, last-part, deferral) | `test_body_composition.py`, `test_anatomy_growth.py` |
