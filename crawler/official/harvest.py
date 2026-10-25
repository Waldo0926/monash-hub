"""Read official pages on one machine and store them from another.

    # Where the site answers - a member's own computer:
    python -m crawler.official.harvest --host www.monash.edu.my --out my.jsonl.gz
    # Copy the file to the server (scp), then there:
    deployment/crawl.sh official-harvest /opt/monash-hub/harvest/my.jsonl.gz

Since 2026-10-25 Monash Malaysia's site answers the server's address with 403,
in the browser as well as over HTTP, while a student's own computer reads every
page normally. Getting past that refusal is not ours to do; reading the pages
where they are served, at the same pace and with the same robots rules, is.

This side only fetches: one JSON line per seed page - the address, what came
back and the raw HTML - written as it goes, so a stopped run resumes. Nothing
is cleaned here. The server cleans and stores each page with its own code, the
same path a crawl there takes (``crawler.official.run --harvest``), so a page
read on a laptop is stored exactly as one read on the server would be.
"""
from __future__ import annotations

import argparse
import gzip
import json
import logging
import os
from datetime import UTC, datetime, timedelta
from urllib.parse import urlparse

from crawler.official.fetch import OfficialFetcher, PageResult
from crawler.official.seeds import SEEDS, Seed
from crawler.throttling.limiter import RateLimit, Throttle

log = logging.getLogger("crawler.official.harvest")

#: A page read longer ago than this is not stored as if it were read today.
MAX_AGE = timedelta(days=3)


def _records(path: str) -> list[dict]:
    """Every whole line in a harvest file. A run stopped mid-write leaves a
    torn last line, or a torn gzip member; what came before it still counts."""
    if not os.path.exists(path):
        return []
    opener = gzip.open if path.endswith(".gz") else open
    records = []
    try:
        with opener(path, "rt", encoding="utf-8") as handle:
            for line in handle:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    break
    except (EOFError, gzip.BadGzipFile):
        pass
    return records


def seeds_on(host: str) -> list[Seed]:
    return [s for s in SEEDS if urlparse(s.url).netloc == host and not s.sign_in]


def harvest(host: str, out: str, *, min_interval: float, transport: str = "auto",
            fetcher: OfficialFetcher | None = None) -> dict[str, int]:
    """Fetch every seed page on ``host`` into ``out``; resumes from what is there."""
    done = {record["url"] for record in _records(out)}
    seeds = [s for s in seeds_on(host) if s.url not in done]
    log.info("%s: %d pages to read, %d already read", host, len(seeds), len(done))
    summary = {"ok": 0, "failed": 0}
    fetcher = fetcher or OfficialFetcher(Throttle(RateLimit(min_interval=min_interval)),
                                         transport=transport)
    opener = gzip.open if out.endswith(".gz") else open
    with fetcher, opener(out, "at", encoding="utf-8") as handle:
        for index, seed in enumerate(seeds, start=1):
            result = fetcher.fetch(seed.url)
            handle.write(json.dumps({
                "url": seed.url, "status": result.status, "html": result.html,
                "transport": result.transport, "error": result.error,
                "final_url": result.final_url,
                "fetched_at": datetime.now(UTC).isoformat(),
            }, ensure_ascii=False) + "\n")
            handle.flush()
            summary["ok" if result.ok else "failed"] += 1
            if not result.ok:
                log.warning("%s: %s", seed.url, result.error)
            if index % 20 == 0:
                log.info("%d/%d read, %s", index, len(seeds), summary)
    log.info("%s: done, %s", host, summary)
    return summary


class HarvestedFetcher:
    """Answers ``fetch`` from a harvest file instead of the network.

    Stands in for ``OfficialFetcher`` in ``crawler.official.run``. A page
    missing from the file, or read more than ``MAX_AGE`` ago, is not among
    ``urls`` and the run leaves it alone.
    """

    def __init__(self, path: str, *, now: datetime | None = None) -> None:
        now = now or datetime.now(UTC)
        self._pages: dict[str, dict] = {}
        stale = 0
        for record in _records(path):
            if now - datetime.fromisoformat(record["fetched_at"]) > MAX_AGE:
                stale += 1
                continue
            self._pages[record["url"]] = record  # the last read of a page wins
        if stale:
            log.warning("%d pages in %s were read more than %s ago and are skipped",
                        stale, path, MAX_AGE)

    @property
    def urls(self) -> set[str]:
        return set(self._pages)

    def fetch(self, url: str) -> PageResult:
        record = self._pages[url]
        return PageResult(url, record["status"], record["html"],
                          f"relayed-{record['transport']}", record["error"],
                          final_url=record["final_url"])

    def __enter__(self) -> HarvestedFetcher:
        return self

    def __exit__(self, *exc_info: object) -> None:
        pass


def main() -> None:
    parser = argparse.ArgumentParser(description="Read official seed pages for another machine")
    parser.add_argument("--host", required=True, help="e.g. www.monash.edu.my")
    parser.add_argument("--out", required=True, help=".jsonl or .jsonl.gz; resumed if it exists")
    parser.add_argument("--transport", default="auto", choices=["auto", "httpx", "playwright"])
    parser.add_argument("--min-interval", type=float, default=3.0)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    harvest(args.host, args.out, min_interval=max(args.min_interval, 2.0),
            transport=args.transport)


if __name__ == "__main__":
    main()
