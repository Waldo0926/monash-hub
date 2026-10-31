"""Read-only, bounded source coverage audit; never writes the application database.

    python -m crawler.official.audit --site my-study --out /out/my-study-audit.json
    python -m crawler.official.audit --site policies --out /out/policy-audit.json
    python -m crawler.official.audit --inventory-only --out /out/seed-inventory.json

Only curated entry pages are fetched. Outgoing links become review candidates,
not crawl targets or new seeds. PDF documents remain labelled links. Counts are
relative to the inspected entries, never a claim of whole-site completeness.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urljoin, urlsplit

from app.knowledge.cleaner import clean_page
from bs4 import BeautifulSoup

from crawler.official.discover import SITES, normalise
from crawler.official.fetch import OfficialFetcher
from crawler.official.seeds import SEEDS
from crawler.throttling.limiter import RateLimit, Throttle

OFFICIAL_HOSTS = {"www.monash.edu", "www.monash.edu.my"}
FILE_SUFFIXES = (".pdf", ".doc", ".docx", ".xlsx", ".zip", ".pptx", ".mp4", ".jpg", ".png")


def inventory() -> dict:
    """Registered is deliberately distinct from fetched, current, or complete."""
    return {
        "registered": len(SEEDS),
        "by_campus": dict(Counter(s.applies_to for s in SEEDS)),
        "by_category": dict(Counter(s.category for s in SEEDS)),
        "duplicate_urls": [u for u, n in Counter(s.url for s in SEEDS).items() if n > 1],
        "duplicate_slugs": [s for s, n in Counter(s.slug for s in SEEDS).items() if n > 1],
    }


def link_inventory(html: str, base_url: str) -> list[dict]:
    """Keep source context and label for every link without fetching its target."""
    known = {normalise(s.url) for s in SEEDS}
    soup = BeautifulSoup(html, "lxml")
    body = soup.select_one(".content-inner__main") or soup.find("main") or soup
    links: list[dict] = []
    seen = set()
    for anchor in body.find_all("a", href=True):
        href = anchor["href"].strip()
        if not href or href.startswith("#"):
            continue
        url = urljoin(base_url, href)
        parts = urlsplit(url)
        if parts.scheme not in {"http", "https"}:
            continue
        label = anchor.get_text(" ", strip=True)
        context = anchor.find_parent("tr")
        label = context.get_text(" ", strip=True) if context else label
        key = (url, label)
        if key in seen:
            continue
        seen.add(key)
        if (parts.hostname == "publicpolicydms.monash.edu"
                or parts.path.lower().endswith(FILE_SUFFIXES)):
            disposition = "document-link-only"
        elif normalise(url) in known:
            disposition = "registered"
        elif parts.hostname == "handbook.monash.edu":
            disposition = "handbook-separate-pipeline"
        elif parts.hostname in OFFICIAL_HOSTS:
            disposition = "review-candidate"
        else:
            disposition = "external-link-only"
        links.append({"url": url, "label": label, "disposition": disposition,
                      "discovered_on": base_url})
    return links


def audit(site_name: str, fetcher: OfficialFetcher, *, max_pages: int = 20) -> dict:
    entries = list(dict.fromkeys(SITES[site_name]["hubs"]))
    selected = entries[:max_pages]
    pages = []
    for url in selected:
        result = fetcher.fetch(url)
        page = {"url": url, "status": result.status, "transport": result.transport,
                "final_url": result.final_url or url}
        if not result.ok:
            page.update(outcome="failed", error=result.error)
        else:
            base = result.final_url or url
            cleaned = clean_page(result.html, url=base)
            length = len(cleaned["clean_text"])
            page.update(outcome="extracted" if length >= 200 else "short-extraction",
                        title=cleaned["title"], text_length=length,
                        content_hash=cleaned["content_hash"],
                        links=link_inventory(result.html, base))
        pages.append(page)
    return {
        "site": site_name,
        "checked_at": datetime.now(UTC).isoformat(),
        "inventory": inventory(),
        "entry_pages_total": len(entries),
        "entry_pages_checked": len(pages),
        "entry_pages_unchecked": entries[len(selected):],
        "outcomes": dict(Counter(p["outcome"] for p in pages)),
        "link_dispositions": dict(Counter(
            link["disposition"] for page in pages for link in page.get("links", [])
        )),
        "pages": pages,
        "limitations": [
            "Only selected curated entry pages were inspected; linked targets were not fetched.",
            "Registered pages have not necessarily been fetched or checked successfully.",
            "PDF/policy bodies, sign-in content and whole-site completeness are unverified.",
            "Campus labels describe directory audiences, not each linked document's applicability.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--site", choices=list(SITES), default="my-study")
    parser.add_argument("--inventory-only", action="store_true")
    parser.add_argument("--max-pages", type=int, default=20)
    parser.add_argument("--min-interval", type=float, default=4.0)
    parser.add_argument("--transport", choices=["auto", "httpx", "playwright"], default="auto")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.max_pages < 1:
        parser.error("--max-pages must be positive")
    if args.inventory_only:
        report = {"inventory": inventory(), "network_requested": False}
    else:
        throttle = Throttle(RateLimit(min_interval=max(2.0, args.min_interval)))
        with OfficialFetcher(throttle, transport=args.transport) as fetcher:
            report = audit(args.site, fetcher, max_pages=args.max_pages)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
