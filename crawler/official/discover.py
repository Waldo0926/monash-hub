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
import html
import json
import logging
import os
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
            # The Finance office's own section: fee statements, instalment
            # plans, EPF withdrawal, SST, e-invoicing and the encumbrance rules.
            # Nothing under it had been indexed.
            "finance",
        )],
        "prefixes": ("/student-services", "/study/apply", "/study/fees", "/study/scholarships",
                     "/finance"),
    },
    "my-study": {
        "hosts": (MY,),
        "hubs": [f"https://{MY}/{p}" for p in (
            "about/welcome", "about/top-university-in-malaysia",
            "study/entry-requirements", "study/undergraduate", "study/postgraduate-and-research",
            "student-services/financial-assistance",
        )],
        "prefixes": ("/about/welcome", "/about/top-university-in-malaysia",
                     "/study/entry-requirements", "/study/undergraduate",
                     "/study/postgraduate-and-research", "/student-services/financial-assistance"),
    },
    "policies": {
        "hosts": (AU,),
        "hubs": [f"https://{AU}/policy-bank/policies-and-procedures/{p}" for p in (
            "academic/education", "academic/research", "academic/graduate-education",
            "management/governance", "management/its",
        )],
        "prefixes": ("/policy-bank/policies-and-procedures/",),
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
            # /accommodation now redirects here, and the library's own pages
            # (hours, borrowing, study spaces) were never walked.
            "student-life/accommodation", "library",
        )],
        "prefixes": ("/business/current", "/it/current-students", "/science/current",
                     "/engineering/current-students", "/pharmacy/current-students",
                     "/sass/current", "/medicine/current-students", "/accommodation", "/its",
                     "/student-life", "/library"),
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

# Faculties outside the IT, Business, Engineering and Science sitemaps keep their
# current-student pages under their own sections; these are walked.
SITES["aufac"] = {
    "hosts": (AU,),
    "hubs": [f"https://{AU}/{p}/current-students" for p in (
        "arts", "law", "medicine", "pharm", "mada", "education",
    )],
    "prefixes": tuple(f"/{p}/current-students" for p in (
        "arts", "law", "medicine", "pharm", "mada", "education",
    )),
}

#: Sites read from their own sitemaps rather than walked: every address they
#: list, less what is not for students. Walking from a few hubs found the
#: section front pages and some of what they link to; the sitemap is the whole
#: site, including pages no menu points at.
NOT_FOR_STUDENTS = re.compile(
    r"(^|/)(news|news-and-events|events?|latest|articles|alumni|staff|people|profiles?|"
    r"timeline|media|featured-items|__data|seaco|education-training-academy)(/|$)|"
    r"^/(openday|intake|apday|pg-|peak-)|"
    # Files and pages the sitemaps list that are not guidance: the site search,
    # verification files, the 404 page, sign-in and feedback forms, tracking.
    r"(^|/)(search|feedback|page-not-found|login|log-in|analytics|archive)(/|$)|"
    r"google-tag-manager|/google[0-9a-f]*\.html$|/robots\d*\.txt$|sitemap[^/]*\.xml$|"
    r"\.(pdf|docx?|xlsx?|pptx?|zip|jpe?g|png|gif|mp4)$",
    re.IGNORECASE,
)
LOC = re.compile(r"<loc>\s*(.*?)\s*</loc>", re.DOTALL)
SITEMAPS: dict[str, dict] = {
    "my-all": {
        "sitemaps": [f"https://{MY}/sitemap.xml"],
        "hosts": (MY,),
        "include": None,
    },
    "au-students": {
        "sitemaps": [f"https://{AU}/{p}/sitemap.xml" for p in (
            "students", "admissions", "it", "business", "engineering", "science",
        )],
        "hosts": (AU,),
        # The faculty sitemaps are the faculties' whole sites; only their
        # current-student sections are for this index.
        "include": re.compile(r"^/(students|admissions)(/|$)|^/[a-z-]+/current-students(/|$)",
                              re.IGNORECASE),
    },
}


def sitemap_urls(fetcher: OfficialFetcher, name: str) -> list[str]:
    """Every page a site's sitemaps list that is for students, in sitemap order."""
    spec = SITEMAPS[name]
    queue = list(spec["sitemaps"])
    seen_maps: set[str] = set()
    urls: list[str] = []
    seen: set[str] = set()
    while queue:
        sitemap = queue.pop(0)
        if sitemap in seen_maps:
            continue
        seen_maps.add(sitemap)
        status, text = fetcher.text_file(sitemap)
        if status != 200 or "<loc>" not in text:
            log.warning("%s: HTTP %s, no sitemap read", sitemap, status)
            continue
        locs = [html.unescape(loc.strip()) for loc in LOC.findall(text)]
        if "<sitemapindex" in text:
            queue += locs
            continue
        for loc in locs:
            url = normalise(loc)
            path = urlparse(url).path
            # One address however the sitemap capitalises it: Monash serves
            # /Semester-in-Australia and /semester-in-australia as one page.
            if (urlparse(url).netloc not in spec["hosts"] or url.lower() in seen
                    or NOT_FOR_STUDENTS.search(path) or SKIP.search(path)
                    or (spec["include"] and not spec["include"].search(path))):
                continue
            seen.add(url.lower())
            urls.append(url)
        log.info("%s: %d addresses kept so far", sitemap, len(urls))
    return urls


def discover_sitemap(name: str, *, max_pages: int, out: str, min_interval: float) -> list[dict]:
    """Read every page a sitemap lists, once. Resumes from ``out`` if it exists."""
    found: list[dict] = []
    if os.path.exists(out):
        with open(out, encoding="utf-8") as handle:
            found = json.load(handle)
    done = {page["url"] for page in found}
    with OfficialFetcher(Throttle(RateLimit(min_interval=min_interval))) as fetcher:
        urls = [u for u in sitemap_urls(fetcher, name) if u not in done][:max_pages]
        log.info("%s: %d pages to read, %d already read", name, len(urls), len(done))
        for index, url in enumerate(urls, start=1):
            result = fetcher.fetch(url)
            if result.ok:
                page, _ = _describe(result.final_url or url, result.html, 1)
                found.append({**page, "url": url})
            else:
                found.append(_failure(url, result, 1))
            if index % 20 == 0:
                _save(found, out)
                log.info("%d/%d read", index, len(urls))
    _save(found, out)
    return found


# Never worth following: page fragments, files, and things that are not pages.
# "/print" is the print view of a page; "/printing" is how to print on campus,
# and matching both kept every printing page out of the index.
SKIP = re.compile(r"/accordion|/__data/|\.pdf$|\.docx?$|/news|/events|/_|/tabs?/|/print(/|$)",
                  re.IGNORECASE)


def normalise(url: str) -> str:
    url = urldefrag(url)[0].split("?")[0].rstrip("/")
    host = urlparse(url).netloc
    if host in ("monash.edu", "monash.edu.my"):
        url = url.replace(f"://{host}", f"://www.{host}", 1)
    return url


def _wanted(site: dict, url: str) -> bool:
    parsed = urlparse(url)
    if (parsed.scheme != "https" or parsed.netloc not in site["hosts"]
            or SKIP.search(parsed.path)):
        return False
    if (skip := site.get("skip")) and skip.search(parsed.path):
        return False
    if parsed.path.count("/") > site.get("max_slashes", 99):
        return False
    path = parsed.path.lower().rstrip("/")
    return any(path == p.lower().rstrip("/") or path.startswith(p.lower().rstrip("/") + "/")
               for p in site["prefixes"])


def _failure(url: str, result, depth: int) -> dict:
    """A page that was not read. A 200 that was not a page - a PDF, a soft 404,
    a redirect off the approved sites - is a failure too, not a 200 row."""
    status = None if result.status == 200 else result.status
    return {"url": url, "status": status, "http": result.status, "depth": depth,
            "error": result.error}


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
                    page, _ = _describe(result.final_url or url, result.html, 0)
                    found.append({**page, "keep": True, "prio": 1, **overrides})
                else:
                    found.append(_failure(url, result, 0))
            _save(found, out)
            return found

        site = SITES[site_name]
        seen = {normalise(h).lower() for h in site["hubs"]}
        queue = deque((normalise(h), 0) for h in site["hubs"])
        while queue and len(found) < max_pages:
            url, depth = queue.popleft()
            result = fetcher.fetch(url)
            if not result.ok:
                found.append(_failure(url, result, depth))
                continue
            page, links = _describe(result.final_url or url, result.html, depth)
            found.append(page)
            for link in links:
                if link.lower() not in seen and depth < max_depth and _wanted(site, link):
                    seen.add(link.lower())
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
    parser.add_argument("--site", required=True, choices=[*SITES, *SITEMAPS, "extra"])
    parser.add_argument("--out", required=True)
    parser.add_argument("--max", type=int, default=600, help="stop after this many pages")
    parser.add_argument("--depth", type=int, default=4)
    parser.add_argument("--min-interval", type=float, default=3.0)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    interval = max(args.min_interval, 2.0)
    if args.site in SITEMAPS:
        found = discover_sitemap(args.site, max_pages=args.max, out=args.out,
                                 min_interval=interval)
    else:
        found = discover(args.site, max_pages=args.max, max_depth=args.depth, out=args.out,
                         min_interval=interval)
    log.info("done: %d pages", len(found))


if __name__ == "__main__":
    main()
