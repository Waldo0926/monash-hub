"""Enumerate every unit the Handbook publishes for a year.

The Handbook's own search page calls a JSON endpoint to list results; this uses
the same one rather than guessing unit codes or walking links. It pages at 100 -
larger sizes are refused - and keeps only results whose URI is under
``/<year>/units/``, because the same index also carries courses and areas of
study.

Discovery is one request per hundred units, so a full year costs about sixty
requests. That is the cheap half of a full crawl; fetching the pages is the
part that takes hours, which is why the runner does it politely and resumably.
"""
from __future__ import annotations

import logging

import httpx

from crawler.throttling.limiter import Throttle

log = logging.getLogger(__name__)

SEARCH_URL = "https://handbook.monash.edu/api/search/search-all"
PAGE_SIZE = 100
SITE_ID = "monash-prod-pres"


class DiscoveryError(RuntimeError):
    """The index could not be read, so we do not know what to crawl."""


def discover_unit_codes(year: int, throttle: Throttle | None = None) -> list[str]:
    """Return every unit code published for ``year``, in Handbook order."""
    throttle = throttle or Throttle()
    codes: list[str] = []
    seen: set[str] = set()
    prefix = f"/{year}/units/"
    offset = 0
    total: int | None = None

    with httpx.Client(timeout=45.0, headers={"User-Agent": _user_agent()}) as client:
        while total is None or offset < total:
            throttle.wait()
            params = {
                "query": "",
                "searchType": "advanced",
                "siteId": SITE_ID,
                "siteYear": str(year),
                "from": offset,
                "size": PAGE_SIZE,
            }
            try:
                response = client.get(SEARCH_URL, params=params)
                response.raise_for_status()
                payload = response.json()["data"]
            except (httpx.HTTPError, KeyError, ValueError) as exc:
                raise DiscoveryError(f"unit index unreadable at offset {offset}: {exc}") from exc

            results = payload.get("results") or []
            if total is None:
                total = int(payload.get("total") or 0)
                log.info("Handbook %s index reports %d entries", year, total)
            if not results:
                break

            for item in results:
                uri = item.get("uri") or ""
                if not uri.startswith(prefix):
                    continue
                code = (item.get("code") or uri.rsplit("/", 1)[-1]).strip().upper()
                if code and code not in seen:
                    seen.add(code)
                    codes.append(code)

            offset += len(results)
            log.debug("discovered %d units after %d entries", len(codes), offset)

    log.info("discovered %d units for %s", len(codes), year)
    if not codes:
        raise DiscoveryError(f"no units found for {year} - the index shape may have changed")
    return codes


def _user_agent() -> str:
    from crawler.handbook.fetch import USER_AGENT

    return USER_AGENT
