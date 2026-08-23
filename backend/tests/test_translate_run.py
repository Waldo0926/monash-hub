"""Splitting the unit list so several translators can run at once."""
from __future__ import annotations

import argparse

import pytest

from crawler.translate.run import _shard


def test_a_shard_is_parsed():
    assert _shard("0/1") == (0, 1)
    assert _shard("3/4") == (3, 4)


@pytest.mark.parametrize("value", ["4/4", "-1/4", "1/0", "one/two", "3", ""])
def test_a_shard_that_would_skip_units_is_refused(value):
    """Off by one here means units silently never translated."""
    with pytest.raises(argparse.ArgumentTypeError):
        _shard(value)


def test_every_unit_lands_in_exactly_one_shard():
    codes = [f"UNIT{i:04d}" for i in range(97)]  # a prime, so nothing divides evenly
    seen: list[str] = []
    for index in range(4):
        seen += codes[index::4]
    assert sorted(seen) == codes
    assert len(seen) == len(set(seen))
