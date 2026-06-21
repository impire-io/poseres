"""Pose Resolution Architecture (PRA).

A single in-memory, batched, deterministic core (PRA-01) plus the validation
harness (PRA-02) that runs the acceptance suite T1-T6 and the investigatory
T-SCALE.

Determinism (FR-010, SC-007, PRA-01 §7.1) requires a fixed float-accumulation
order. We pin every BLAS backend to a single thread *before* numpy is imported
anywhere in the process, so reductions are byte-stable across runs on one
machine. This module is imported before any ``pra`` submodule pulls in numpy.
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

__all__ = ["__version__"]
__version__ = "0.1.0"
