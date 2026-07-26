"""Pose Resolution Architecture (PRA).

A single in-memory, batched, deterministic core (PRA-01) plus the validation
harness (PRA-02) that runs the acceptance suite T1-T6 and the investigatory
T-SCALE.

Determinism (FR-010, SC-007, PRA-01 §7.1) requires a fixed float-accumulation
order. We pin every BLAS backend to a single thread *before* numpy is imported
anywhere in the process, so reductions are byte-stable across runs on one
machine. This module is imported before any ``pra`` submodule pulls in numpy.

The public surface is declared in ``tests/contract/surface_inventory.py``
and documented in ``hq/02-DESIGN/0008-public-api-versioning.md`` (feature
035). ``Config`` and ``Engine`` are re-exported lazily (PEP 562) so that
``import pra`` stays exactly as light as before the v1.0 freeze.
"""

import os as _os

# Pin BLAS threading before numpy is first imported (PRA-01 §7.1, research R3).
for _var in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "NUMEXPR_NUM_THREADS",
):
    _os.environ.setdefault(_var, "1")

__all__ = ["__version__", "Config", "Engine"]


def _load_version() -> str:
    from importlib.metadata import PackageNotFoundError, version

    try:
        return version("poseres")
    except PackageNotFoundError:  # source tree without an installed dist
        return "0.0.0+uninstalled"


__version__ = _load_version()

_LAZY = {"Config": ("pra.config", "Config"), "Engine": ("pra.core.engine", "Engine")}


def __getattr__(name: str):
    if name in _LAZY:
        from importlib import import_module

        module_path, attr = _LAZY[name]
        return getattr(import_module(module_path), attr)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
