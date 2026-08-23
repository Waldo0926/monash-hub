# Crawling policy

## What we fetch

Two sources, both public, both small:

- **handbook.monash.edu** — unit pages, 20 fixture units to start. The page is a
  Next.js app, so the authoritative content is the JSON in `__NEXT_DATA__`. We
  parse that rather than scraping rendered HTML: it is the same data the page
  renders, and a visual redesign does not break the parser.
- **www.monash.edu / www.monash.edu.my** — 40 hand-picked student-facing pages,
  listed in `crawler/official/seeds.py`. Every URL in that list returned HTTP
  200 when it was compiled.

We do not crawl the whole site, follow arbitrary links, or download images,
video, PDFs or any other binary.

## Backfilling a whole year

```bash
deployment/crawl.sh handbook --all --min-interval 1.5
```

Five thousand units at a second and a half apart is around three hours, so it is
run detached and watched through the log, not in a terminal someone has to keep
open. It is resumable: `--skip-fresh 24` drops anything already crawled today,
so a run that dies partway can simply be started again.

This is a one-off. Afterwards the same units cost almost nothing to re-check,
because an unchanged page is a hash comparison and no write.

## Rate limits

Set in `crawler/throttling/limiter.py` and applied to every request:

| Control | Default |
| --- | --- |
| Concurrency | 1 — strictly sequential |
| Minimum interval | 3s (Handbook), 4s (official pages) |
| Jitter | up to 1.5s extra |
| Attempts per URL | 3 |
| Backoff | 5s, doubling, capped at 120s |

The command-line floor is 1s for the Handbook and 2s for official pages, so a
flag cannot turn the crawler into a load test. A full official crawl of 40 pages
takes about four minutes and happens at most twice a day for the pages that
change fastest.

## Skipping work

Every page is hashed after extraction. If the hash is unchanged there is no
parse, no write and no reindex — and the run still records a `crawl_history`
row, so a healthy no-op is visibly different from a crawler that never started.

Pages carry a refresh tier. A stable policy page is re-read fortnightly; a
census-date page twice a day. Anything not due is not requested at all.

## The WAF, and why the crawler carries a browser

`www.monash.edu` sits behind a WAF that scores the HTTP *client*, not the
address. Measured from two different machines within the same minute: `curl` and
`httpx` got `403`, a headless browser sending the same user agent got `200`.
Changing headers does not help; neither does changing hosts.

So `crawler/official/fetch.py` starts on `httpx` and latches to a browser
transport the first time it is refused, keeping it for the rest of the run
rather than paying a failed request per page. The rate limit is identical either
way — the browser is there because the site needs a real rendering engine to
serve a page, not to fetch faster or to hide anything. `handbook.monash.edu`
serves `httpx` normally and never needs it.

A `403` is therefore not evidence that anything is broken.

## Failure handling

| Case | What happens |
| --- | --- |
| Network error / timeout | Retry with backoff, then record `failed`, keep the last good row |
| HTTP 404 | Recorded immediately, not retried — a missing page is an answer |
| HTTP 403 / 429 | Latch to the browser transport, back off, retry |
| Parse error | Keep the last valid record, log it loudly, record `failed` |
| Extraction under 200 characters | Treated as a template change, not as deleted content — keep the last valid version |

## What never enters the repository

Crawled HTML, page dumps, database dumps, images, PDFs. `backend/tests/fixtures`
holds three trimmed Handbook payloads for parser tests and one synthetic
official page written by hand — that is all.
