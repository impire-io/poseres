"""The one deprecation mechanism (feature 035, Doc 0008).

Internal module: the *policy* is public, the helper is maintainer
tooling. Unused by every existing mode — dead code for the frozen
baseline. The notice format is a single uniform sentence so the
SC-005 guarantee (every deprecated element names its replacement and
removal horizon) is a one-place property.
"""

from __future__ import annotations

import functools
import warnings
from collections.abc import Callable

__all__ = ["deprecated", "notice_sentence"]


def notice_sentence(element: str, replacement: str, removal: str) -> str:
    return f"{element} is deprecated and may be removed in {removal}; use {replacement}."


def deprecated(*, replacement: str, removal: str) -> Callable:
    """Mark a public callable deprecated per the Doc 0008 policy.

    ``replacement``: the dotted path to use instead (non-empty).
    ``removal``: the earliest release that may remove it (``"vX.Y"``).
    """
    if not replacement or not removal:
        raise ValueError("deprecated() requires non-empty replacement and removal")

    def wrap(func: Callable) -> Callable:
        sentence = notice_sentence(f"{func.__module__}.{func.__qualname__}", replacement, removal)

        @functools.wraps(func)
        def inner(*args, **kwargs):
            warnings.warn(sentence, DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)

        inner.__deprecated__ = sentence
        return inner

    return wrap
