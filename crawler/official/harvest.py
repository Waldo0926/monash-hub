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
import zlib
from collections.abc import Iterable, Iterator
from datetime import UTC, datetime, timedelta
from urllib.parse import urlparse

from crawler.official.fetch import OfficialFetcher, PageResult
from crawler.official.seeds import SEEDS, Seed
from crawler.throttling.limiter import RateLimit, Throttle

log = logging.getLogger("crawler.official.harvest")

#: A page read longer ago than this is not stored as if it were read today.
MAX_AGE = timedelta(days=3)


GZIP_MAGIC = b"\x1f\x8b\x08"


RECORD_KEYS = {"url", "status", "html", "transport", "error", "final_url", "fetched_at"}

#: Decompressed bytes taken at a time: one page's HTML runs to 2.5 MB.
STEP = 1 << 20


def _starts_record(data: memoryview, at: int) -> bool:
    """Whether a gzip member of this file starts at ``at``: the header bytes
    can occur inside compressed data by chance, a record cannot."""
    try:
        head = zlib.decompressobj(wbits=31).decompress(data[at:at + 4096], 16)
    except zlib.error:
        return False
    return head.startswith(b'{"url"')


def _gzip_lines(data: bytes) -> Iterator[bytes]:
    """Each line of every gzip member, as far as each member goes.

    A run stopped mid-write tears the member it was writing, and the next run
    appends a new one. ``gzip.open`` raises at the tear and loses the rest.
    Worse, a decoder carried past a tear reads the next member as more of the
    torn one, often without an error: its literal bytes come out right and its
    back-references point into the wrong text, so whole lines can come out as
    valid JSON with the wrong fields. So a member is never read across a
    place where another member visibly starts; a torn one is read as far as
    it goes, and reading starts again there. Lines that are not whole records
    are dropped by the caller.
    """
    cuts = []
    at = data.find(GZIP_MAGIC)
    while at != -1:
        cuts.append(at)
        at = data.find(GZIP_MAGIC, at + 1)
    cuts.append(len(data))
    view = memoryview(data)
    first = 0
    while first < len(cuts) - 1:
        reader = zlib.decompressobj(wbits=31)
        piece, end, pending = first, None, bytearray()
        try:
            while piece < len(cuts) - 1 and end is None:
                if piece > first and _starts_record(view, cuts[piece]):
                    break  # torn before here: this is the next member
                chunk = view[cuts[piece]:cuts[piece + 1]]
                while not reader.eof:
                    out = reader.decompress(chunk, STEP)
                    chunk = reader.unconsumed_tail
                    if not out and not chunk:
                        break
                    pending += out
                    *lines, rest = pending.split(b"\n")
                    yield from lines
                    pending = bytearray(rest)
                piece += 1
                if reader.eof:
                    end = cuts[piece] - len(reader.unused_data)
        except zlib.error:
            pass
        if end is None:
            first = max(piece, first + 1)  # torn: go on at the next member
        else:
            if pending:
                yield bytes(pending)
            first = next((k for k in range(first + 1, len(cuts)) if cuts[k] >= end),
                         len(cuts) - 1)


def _records(path: str) -> Iterator[dict]:
    """Every whole line in a harvest file, one at a time: a full harvest holds
    gigabytes of HTML, more than the crawler container may use. A run stopped
    mid-write leaves a torn last line, or a torn gzip member; every whole line
    around it still counts."""
    if not os.path.exists(path):
        return
    with open(path, "rb") as handle:
        if path.endswith(".gz"):
            lines: Iterable[bytes] = _gzip_lines(handle.read())
        else:
            lines = handle
        for line in lines:
            try:
                record = json.loads(line)
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
            if isinstance(record, dict) and record.keys() >= RECORD_KEYS:
                yield record


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
    with fetcher, open(out, "ab") as handle:
        for index, seed in enumerate(seeds, start=1):
            result = fetcher.fetch(seed.url)
            line = json.dumps({
                "url": seed.url, "status": result.status, "html": result.html,
                "transport": result.transport, "error": result.error,
                "final_url": result.final_url,
                "fetched_at": datetime.now(UTC).isoformat(),
            }, ensure_ascii=False).encode("utf-8") + b"\n"
            # One gzip member per page: a run stopped mid-write loses only
            # the page it was writing.
            handle.write(gzip.compress(line) if out.endswith(".gz") else line)
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
        # Each record is kept compressed until it is fetched: 723 pages held
        # as parsed records took more than the crawler's 2 GB.
        self._pages: dict[str, bytes] = {}
        stale = 0
        for record in _records(path):
            if now - datetime.fromisoformat(record["fetched_at"]) > MAX_AGE:
                stale += 1
                continue
            # The last read of a page wins.
            self._pages[record["url"]] = zlib.compress(json.dumps(record).encode("utf-8"))
        if stale:
            log.warning("%d pages in %s were read more than %s ago and are skipped",
                        stale, path, MAX_AGE)

    @property
    def urls(self) -> set[str]:
        return set(self._pages)

    def fetch(self, url: str) -> PageResult:
        record = json.loads(zlib.decompress(self._pages[url]))
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
