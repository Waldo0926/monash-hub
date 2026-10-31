"""An incomplete index must fail visibly rather than masquerading as a full year."""
from __future__ import annotations

import httpx
import pytest

from crawler.handbook import discover
from crawler.throttling.limiter import RateLimit, Throttle


def run(monkeypatch, pages):
    answers = iter(pages)
    client = httpx.Client(transport=httpx.MockTransport(lambda _: httpx.Response(200, json={"data": next(answers)})))
    monkeypatch.setattr(discover.httpx, "Client", lambda **_: client)
    throttle = Throttle(RateLimit(min_interval=0, jitter=0))
    return discover.discover_unit_codes(2026, throttle)


def item(code="FIT3155", year=2026):
    return {"uri": f"/{year}/units/{code}", "code": code}


def test_full_inventory_can_span_pages_and_include_other_item_kinds(monkeypatch):
    assert run(monkeypatch, [
        {"total": 3, "results": [item(), {"uri": "/2026/courses/C2001", "code": "C2001"}]},
        {"total": 3, "results": [item("FIT2102")]},
    ]) == ["FIT3155", "FIT2102"]


@pytest.mark.parametrize("pages", [
    [{"total": 2, "results": [item()]}, {"total": 2, "results": []}],
    [{"total": 2, "results": [item()]}, {"total": 2, "results": [item()]}],
    [{"total": 2, "results": [item()]}, {"total": 3, "results": [item("FIT2102")]}],
    [{"total": 1, "results": [item(year=2027)]}],
    [{"results": [item()]}],
    [{"total": 1, "results": {"unexpected": "shape"}}],
    [{"total": 1, "results": [None]}],
])
def test_incomplete_repeated_wrong_year_and_malformed_inventories_fail(monkeypatch, pages):
    with pytest.raises(discover.DiscoveryError):
        run(monkeypatch, pages)
