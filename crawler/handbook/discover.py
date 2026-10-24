"""Enumerate what the Handbook publishes for a year.

The Handbook's own search page calls a JSON endpoint to list results; this uses
the same one rather than guessing unit codes or walking links. It pages at 100 -
larger sizes are refused - and filters by the prefix of the
URI, because one index carries units, courses and areas of study together.

Discovery is one request per hundred units, so a full year costs about sixty
requests. That is the cheap half of a full crawl; fetching the pages is the
part that takes hours, which is why the runner does it politely and resumably.
"""
from __future__ import annotations

import logging

import httpx

from crawler.response import retry_after
from crawler.throttling.limiter import Throttle

log = logging.getLogger(__name__)

SEARCH_URL = "https://handbook.monash.edu/api/search/search-all"
PAGE_SIZE = 100
SITE_ID = "monash-prod-pres"


class DiscoveryError(RuntimeError):
    """The index could not be read, so we do not know what to crawl."""


def discover_unit_codes(year: int, throttle: Throttle | None = None) -> list[str]:
    """Return every unit code published for ``year``, in Handbook order."""
    return _discover(year, "units", throttle)


def discover_course_codes(year: int, throttle: Throttle | None = None) -> list[str]:
    """Return every course code published for ``year`` - C2001 and its 502 peers."""
    return _discover(year, "courses", throttle)


def discover_aos_codes(year: int, throttle: Throttle | None = None) -> list[str]:
    """Return every area-of-study code - the majors, minors and specialisations."""
    return _discover(year, "aos", throttle)


def _discover(year: int, kind: str, throttle: Throttle | None = None,
              *, transport: httpx.BaseTransport | None = None) -> list[str]:
    """One walk of the index, keeping the entries under ``/<year>/<kind>/``.

    The index is one list of everything the Handbook publishes, so the three
    entry points above differ only in which prefix they keep. Walking it three
    times costs three times sixty requests, which is still the cheap half of a
    crawl.
    """
    throttle = throttle or Throttle()
    codes: list[str] = []
    seen: set[str] = set()
    prefix = f"/{year}/{kind}/"
    offset = 0
    total: int | None = None
    seen_pages: set[tuple[str, ...]] = set()

    with httpx.Client(timeout=45.0, headers={"User-Agent": _user_agent()},
                      transport=transport) as client:
        while total is None or offset < total:
            payload = _index_page(client, throttle, year, offset)
            if not isinstance(payload, dict) or not isinstance(payload.get("results"), list):
                raise DiscoveryError(f"index shape changed at offset {offset}")
            reported_total = payload.get("total")
            if (isinstance(reported_total, bool) or not isinstance(reported_total, int)
                    or reported_total < 0):
                raise DiscoveryError(f"invalid index total at offset {offset}")
            results = payload["results"]
            if total is None:
                total = reported_total
                log.info("Handbook %s index reports %d entries", year, total)
            elif reported_total != total:
                raise DiscoveryError("index total changed during discovery; retry the inventory")
            if not results:
                if offset < total:
                    raise DiscoveryError(f"incomplete index: stopped at {offset} of {total}")
                break
            if offset + len(results) > total:
                raise DiscoveryError("index returned more entries than its reported total")

            if any(not isinstance(item, dict) or not isinstance(item.get("uri"), str)
                   or not item["uri"].startswith(f"/{year}/") for item in results):
                raise DiscoveryError(f"index returned a malformed or wrong-year item at {offset}")
            page_identity = tuple(item["uri"] for item in results)
            if page_identity in seen_pages:
                raise DiscoveryError(f"index repeated a page at offset {offset}")
            seen_pages.add(page_identity)

            for item in results:
                uri = item.get("uri") or ""
                if not uri.startswith(prefix):
                    continue
                code = (item.get("code") or uri.rsplit("/", 1)[-1]).strip().upper()
                # M6011 is listed as "M6011 M6019": one page, two codes. A code
                # with a space makes a URL nobody can link to, so keep the first.
                code = code.split()[0] if code else code
                if code and code not in seen:
                    seen.add(code)
                    codes.append(code)

            offset += len(results)
            log.debug("discovered %d %s after %d entries", len(codes), kind, offset)

    log.info("discovered %d %s for %s", len(codes), kind, year)
    if not codes:
        raise DiscoveryError(f"no {kind} found for {year} - the index shape may have changed")
    return codes


def _index_page(client: httpx.Client, throttle: Throttle, year: int, offset: int):
    """One page of the index, tried as often as a unit page is.

    A walk is about sixty pages, three walks a week. Giving up on the first
    timeout threw away the whole weekly crawl - units, degrees, and the
    translation pass that follows them - over one slow answer. Only reading
    the page is retried; a page that reads but has the wrong shape is checked
    by the caller and still ends discovery.
    """
    params = {
        "query": "",
        "searchType": "advanced",
        "siteId": SITE_ID,
        "siteYear": str(year),
        "from": offset,
        "size": PAGE_SIZE,
    }
    attempts = throttle.limit.max_attempts
    error: Exception | None = None
    for attempt in range(1, attempts + 1):
        throttle.wait()
        pause = 0.0
        try:
            response = client.get(SEARCH_URL, params=params)
            pause = retry_after(response.headers.get("retry-after")) or 0.0
            response.raise_for_status()
            return response.json()["data"]
        except (httpx.HTTPError, KeyError, ValueError) as exc:
            error = exc
            log.warning("index page at offset %d failed (%s)", offset, exc)
        if attempt < attempts:
            throttle.backoff(attempt, at_least=pause)
    raise DiscoveryError(
        f"index unreadable at offset {offset} after {attempts} attempts: {error}"
    ) from error


def _user_agent() -> str:
    from crawler.handbook.fetch import USER_AGENT

    return USER_AGENT
