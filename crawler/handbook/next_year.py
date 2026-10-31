"""Has next year's Handbook been published yet?

Monash publishes the next Handbook around October, while faculties post the
next year's course maps earlier - in September 2026 the IT, Engineering,
Education and Arts 2027 maps were up and handbook.monash.edu/2027 still
answered every page with a 404. Course maps show the order to take units in;
prerequisites, offerings and assessment exist only in the Handbook. So next
year's data is loaded when the Handbook appears, and this is how we find out
that it has: one request to the same index discovery reads, asking whether it
lists anything for the year.

    python -m crawler.handbook.next_year           # the year after the current one
    python -m crawler.handbook.next_year --year 2027

Prints ``published <year> <entries>`` or ``not-published <year>``; the exit
status is 0 either way, so a scheduled run is not marked failed by the answer.
"""
from __future__ import annotations

import argparse
import logging

import httpx
from app.core.config import get_settings

from crawler.handbook.discover import SEARCH_URL, SITE_ID, _user_agent

log = logging.getLogger("crawler.handbook.next_year")


def published_entries(year: int) -> int:
    """How many entries the Handbook index lists for ``year``; 0 when none."""
    params = {"query": "", "searchType": "advanced", "siteId": SITE_ID,
              "siteYear": str(year), "from": 0, "size": 5}
    with httpx.Client(timeout=45.0, headers={"User-Agent": _user_agent()}) as client:
        response = client.get(SEARCH_URL, params=params)
        response.raise_for_status()
        data = response.json()["data"]
    # The index is only trusted about a year if what it returns is that year:
    # an empty year could otherwise be answered with the current one's entries.
    results = [r for r in data.get("results") or []
               if (r.get("uri") or "").startswith(f"/{year}/")]
    return int(data.get("total") or 0) if results else 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--year", type=int, default=None)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    year = args.year or get_settings().current_academic_year + 1
    try:
        entries = published_entries(year)
    except (httpx.HTTPError, KeyError, ValueError) as exc:
        log.warning("could not read the %s Handbook index: %s", year, exc)
        print(f"unknown {year}")
        return
    if entries:
        log.warning("the %s Handbook is published (%d entries)", year, entries)
        print(f"published {year} {entries}")
    else:
        print(f"not-published {year}")


if __name__ == "__main__":
    main()
