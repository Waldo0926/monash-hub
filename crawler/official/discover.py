"""Walk Monash's student sites to find official pages worth indexing.

    python -m crawler.official.discover --site my     --out /out/discover_my.json
    python -m crawler.official.discover --site myfac  --out /out/discover_fac.json
    python -m crawler.official.discover --site abroad --out /out/discover_ab.json
    python -m crawler.official.discover --site au     --out /out/discover.json --max 900
    python -m crawler.official.discover --site extra  --out /out/extra.json

This is how ``seeds_coverage.py`` was built, and how to rebuild it when Monash
reorganises a site. It is a discovery pass, not a crawl: breadth-first from a
few hub pages, following only links inside each site's student section, one
request at a time through the same throttled fetcher as the crawler. What it
writes is a list of candidates - address, title, text length, content hash,
headings - for ``crawler.official.coverage`` to filter into seeds. Nothing is
stored in the database.

``--site extra`` fetches ``coverage.EXTRA`` - pages found by searching rather
than by walking (course and campus transfer, faculty FAQs) - without following
their links.

Exchange: the walk stops at Monash's program search. One page per partner
university is monash-abroad-tracker's data; the Hub keeps the rules.
"""
from __future__ import annotations

import argparse
import json
import logging
import re
from collections import deque
from urllib.parse import urldefrag, urljoin, urlparse

from app.knowledge.cleaner import clean_page
from bs4 import BeautifulSoup

from crawler.official.coverage import EXTRA
from crawler.official.fetch import OfficialFetcher
from crawler.throttling.limiter import RateLimit, Throttle

log = logging.getLogger("crawler.official.discover")

AU, MY = "www.monash.edu", "www.monash.edu.my"

SITES: dict[str, dict] = {
    "au": {
        "hosts": (AU,),
        "hubs": [f"https://{AU}/students/{p}" for p in (
            "admin", "admin/graduations", "admin/enrolments", "admin/assessments",
            "admin/fees", "admin/dates", "admin/policies", "admin/timetables",
            "study-success", "study-success/academic-progress", "support/international",
            "support/connect", "support/misconduct", "support/complaints",
            "unsatisfactory-progress", "support",
        )],
        "prefixes": ("/students/admin", "/students/study-success", "/students/support",
                     "/students/final-year", "/students/unsatisfactory-progress",
                     "/students/new"),
    },
    "my": {
        "hosts": (MY,),
        "hubs": [f"https://{MY}/{p}" for p in (
            "student-services", "student-services/student-admin",
            "student-services/international-students",
            "student-services/student-admin/examinations-results",
            "student-services/support-services",
            "study/apply/application-form/fee-payment-methods", "study/apply",
        )],
        "prefixes": ("/student-services", "/study/apply", "/study/fees", "/study/scholarships"),
    },
    # The schools' own current-student pages: course rules, FAQs on transfer,
    # completion and special consideration that the central site leaves to them.
    "myfac": {
        "hosts": (MY,),
        "hubs": [f"https://{MY}/{p}" for p in (
            "business/current", "it/current-students", "science/current",
            "science/current/undergraduate", "engineering/current-students",
            "pharmacy/current-students", "sass/current", "sass/current/undergraduate",
            "medicine/current-students", "accommodation", "its",
        )],
        "prefixes": ("/business/current", "/it/current", "/science/current",
                     "/engineering/current", "/pharmacy/current", "/sass/current",
                     "/medicine/current", "/accommodation", "/its"),
        "max_slashes": 6,
    },
    "abroad": {
        "hosts": (AU, MY),
        "hubs": [
            f"https://{AU}/study-abroad/overseas",
            f"https://{AU}/study-abroad/outbound",
            f"https://{AU}/study-abroad/overseas/other-programs/global-summer-winter-programs",
            f"https://{MY}/study-abroad/outbound",
            f"https://{MY}/study-abroad/outbound/exchange-program",
            f"https://{MY}/study-abroad/outbound/short-term-programs",
            f"https://{MY}/study-abroad/outbound/costs-and-funding",
            f"https://{MY}/study-abroad/outbound/faqs-about-going-on-exchange",
            f"https://{MY}/study-abroad/outbound/Semester-in-Australia",
            f"https://{MY}/study-abroad/outbound/intercampus-exchange",
        ],
        "prefixes": ("/study-abroad/overseas", "/study-abroad/outbound"),
        # Partner programs, except Monash's own campus in Prato.
        "skip": re.compile(r"/program-search(?!/[^/]*prato)", re.IGNORECASE),
    },
}

# Never worth following: page fragments, files, and things that are not pages.
SKIP = re.compile(r"/accordion|/__data/|\.pdf$|\.docx?$|/news|/events|/_|/tabs?/|/print",
                  re.IGNORECASE)


def normalise(url: str) -> str:
    url = urldefrag(url)[0].split("?")[0].rstrip("/")
    host = urlparse(url).netloc
    if host in ("monash.edu", "monash.edu.my"):
        url = url.replace(f"://{host}", f"://www.{host}", 1)
    return url


def _wanted(site: dict, url: str) -> bool:
    parsed = urlparse(url)
    if parsed.netloc not in site["hosts"] or SKIP.search(parsed.path):
        return False
    if (skip := site.get("skip")) and skip.search(parsed.path):
        return False
    if parsed.path.count("/") > site.get("max_slashes", 99):
        return False
    return parsed.path.lower().startswith(tuple(p.lower() for p in site["prefixes"]))


def _describe(url: str, html: str, depth: int) -> tuple[dict, list[str]]:
    cleaned = clean_page(html, url=url)
    text = cleaned["clean_text"] or ""
    main = BeautifulSoup(html, "html.parser").find("main")
    anchors = (main or BeautifulSoup(html, "html.parser")).find_all("a", href=True)
    links = sorted({normalise(urljoin(url, a["href"])) for a in anchors})
    return {
        "url": url, "status": 200, "depth": depth, "title": cleaned["title"],
        "len": len(text), "hash": cleaned["content_hash"], "head": text[:300],
    }, links


def discover(site_name: str, *, max_pages: int, max_depth: int, out: str,
             min_interval: float) -> list[dict]:
    found: list[dict] = []
    with OfficialFetcher(Throttle(RateLimit(min_interval=min_interval))) as fetcher:
        if site_name == "extra":
            for url, overrides in EXTRA.items():
                result = fetcher.fetch(url)
                if result.ok:
                    page, _ = _describe(url, result.html, 0)
                    found.append({**page, "keep": True, "prio": 1, **overrides})
                else:
                    found.append({"url": url, "status": result.status})
            _save(found, out)
            return found

        site = SITES[site_name]
        seen = {normalise(h) for h in site["hubs"]}
        queue = deque((normalise(h), 0) for h in site["hubs"])
        while queue and len(found) < max_pages:
            url, depth = queue.popleft()
            result = fetcher.fetch(url)
            if not result.ok:
                found.append({"url": url, "status": result.status, "depth": depth})
                continue
            page, links = _describe(url, result.html, depth)
            found.append(page)
            for link in links:
                if link not in seen and depth < max_depth and _wanted(site, link):
                    seen.add(link)
                    queue.append((link, depth + 1))
            log.info("%4d found, %4d queued, d%d %6d chars %s",
                     len(found), len(queue), depth, page["len"], url)
            if len(found) % 20 == 0:
                _save(found, out)
    _save(found, out)
    return found


def _save(found: list[dict], out: str) -> None:
    with open(out, "w", encoding="utf-8") as handle:
        json.dump(found, handle, ensure_ascii=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Find official student pages to index")
    parser.add_argument("--site", required=True, choices=[*SITES, "extra"])
    parser.add_argument("--out", required=True)
    parser.add_argument("--max", type=int, default=600, help="stop after this many pages")
    parser.add_argument("--depth", type=int, default=4)
    parser.add_argument("--min-interval", type=float, default=3.0)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    found = discover(args.site, max_pages=args.max, max_depth=args.depth, out=args.out,
                     min_interval=max(args.min_interval, 2.0))
    log.info("done: %d pages", len(found))


if __name__ == "__main__":
    main()
