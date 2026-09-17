"""Which units a translation pass actually touches.

No database or model here - just the selection logic that used to force every
`--fields all` run to walk the whole catalogue even when only one Handbook
page, like FIT1008's mid-year republish, needed re-translating.
"""
from __future__ import annotations

import pytest

from crawler.translate.run import _select_codes

CATALOGUE = ["FIT1008", "FIT1045", "FIT1055", "FIT2102"]


def test_no_units_filter_returns_everything():
    assert _select_codes(CATALOGUE, None, limit=0) == CATALOGUE


def test_limit_only_applies_without_a_units_filter():
    assert _select_codes(CATALOGUE, None, limit=2) == ["FIT1008", "FIT1045"]


def test_units_filter_scopes_to_the_given_codes():
    assert _select_codes(CATALOGUE, ["FIT1008"], limit=0) == ["FIT1008"]


def test_units_filter_is_case_insensitive_and_trims_whitespace():
    assert _select_codes(CATALOGUE, [" fit1008 ", "fit1055"], limit=0) == [
        "FIT1008", "FIT1055",
    ]


def test_units_filter_ignores_limit():
    """--limit is a full-catalogue safety valve; a --units list is already
    exactly what was asked for, so it is not silently truncated."""
    assert _select_codes(CATALOGUE, ["FIT1008", "FIT1055"], limit=1) == [
        "FIT1008", "FIT1055",
    ]


def test_an_unknown_unit_code_fails_loudly():
    with pytest.raises(ValueError, match="FIT9999"):
        _select_codes(CATALOGUE, ["FIT1008", "FIT9999"], limit=0)
