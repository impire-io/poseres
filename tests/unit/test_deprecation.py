"""The deprecation notice contract (feature 035, SC-005)."""

from __future__ import annotations

import warnings

import pytest

from pra._deprecation import deprecated, notice_sentence


def test_notice_names_element_replacement_and_removal() -> None:
    @deprecated(replacement="pra.new_thing", removal="v2.0")
    def old_thing() -> int:
        return 41

    with pytest.warns(DeprecationWarning) as caught:
        assert old_thing() == 41
    assert len(caught) == 1
    message = str(caught[0].message)
    assert message == notice_sentence(
        f"{old_thing.__module__}.{old_thing.__qualname__}", "pra.new_thing", "v2.0"
    )
    assert "pra.new_thing" in message and "v2.0" in message


def test_wrapped_function_keeps_identity_and_records_sentence() -> None:
    @deprecated(replacement="pra.other", removal="v2.0")
    def venerable(x: int) -> int:
        return x * 2

    assert venerable.__name__ == "venerable"
    assert venerable.__deprecated__.endswith("use pra.other.")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        assert venerable(4) == 8


def test_empty_fields_are_refused() -> None:
    with pytest.raises(ValueError):
        deprecated(replacement="", removal="v2.0")
    with pytest.raises(ValueError):
        deprecated(replacement="pra.x", removal="")
