# Crawling policy

## What we fetch

Two source families, both public:

- **handbook.monash.edu**: unit, course and area-of-study pages, every published
  unit of a Handbook year. The page is a
  Next.js app, so the authoritative content is the JSON in `__NEXT_DATA__`. We
  parse that rather than scraping rendered HTML: it is the same data the page
  renders, and a visual redesign does not break the parser.
- **www.monash.edu / www.monash.edu.my**: curated student-facing pages. The
  hand-picked ones are listed in `crawler/official/seeds.py`, and the long
  tail of the student sites, Malaysia first, in `crawler/official/seeds_coverage.py`.
  Policy Bank HTML directories retain labelled document links without mirroring
  their bodies. Registration alone does not prove a URL is currently readable.

We do not crawl the whole site, follow arbitrary links, or download images,
video, PDFs or any other binary.

## Who is asking

Every request, over `httpx` or the browser, carries the same user agent, set in
`crawler/throttling/limiter.py`:

```text
MonashHubBot/0.1 (+https://monashhub.secureview.tech; student information index)
```

Before the first page of a host, both page fetchers read that host's
`robots.txt` once and checks each URL against it under the name `MonashHubBot`.
A disallowed page is not requested and is recorded as such. If `robots.txt`
cannot be read at all, or answers with a server error, the host is treated as
closed for that run. Only 404/410 mean no robots file. A 401/403, 429, redirect,
or HTML challenge instead means crawl permission is unknown; the page is not
requested. Robots requests use the same throttle as page requests.

The one exception is a 403 to `httpx` on an official site in `auto` mode. The
WAF refuses the HTTP client whatever it asks for, so the official fetcher asks
for `robots.txt` once more with the browser, the same way it would read the
pages, and goes by that answer. A refusal there still closes the host.

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
| Concurrency | 1, strictly sequential |
| Minimum interval | 3s (Handbook), 4s (official pages) |
| Jitter | up to 1.5s extra |
| Attempts per URL | 3 |
| Backoff | 5s, doubling, capped at 120s |

The command-line floor is 1s for the Handbook and 2s for official pages, so a
flag cannot turn the crawler into a load test. The registry contains hundreds of
official pages; a forced full refresh can take over an hour. Prefer due-only
refreshes and inspect the outcome counts rather than assuming a run is complete.

## Skipping work

Every page is hashed after extraction. Official-page hashes include structured
blocks and link targets, so replacing a policy link without changing its label
still triggers an update. If the hash is unchanged there is no content write
or reindex, and the run still records a `crawl_history`
row, so a healthy no-op is visibly different from a crawler that never started.

Pages carry a refresh tier. A stable policy page is re-read fortnightly; a
census-date page twice a day. Anything not due is not requested at all.

## The WAF, and why the crawler carries a browser

Both official sites can return WAF/challenge pages. Previous observations found
a browser could read pages that HTTP clients could not; this is not guaranteed
across hosts, locations or dates. The October 2026 local audit saw inaccessible
robots files on both sites, so those crawls correctly stopped before page fetches.

So `crawler/official/fetch.py` starts on `httpx` and latches to a browser
transport the first time it is refused, keeping it for the rest of the run
rather than paying a failed request per page. The rate limit is identical either
way. The browser is there because the site needs a real rendering engine to
serve a page, not to fetch faster or to hide anything. `handbook.monash.edu`
serves `httpx` normally and never needs it.

A browser does not establish that a page is readable: recognised challenge,
sign-in, soft-404 and access-error shells are failures even when they return 200.

## Failure handling

| Case | What happens |
| --- | --- |
| Network error / timeout | Retry with backoff, then record `failed`, keep the last good row |
| Handbook index page fails | Retried like a unit page. Only after the last attempt does the run stop, since without the index it does not know what to crawl |
| HTTP 404 | Recorded immediately, not retried. A missing page is an answer |
| HTTP 404 on the Handbook, past the withdrawal cap | Recorded `failed`, the row stays active. One run marks at most 25 units, degrees or areas of study inactive (or 2% of its targets if that is more); `--max-withdrawals` raises it after a person has checked |
| HTTP 403 | Latch to the browser transport, back off, retry |
| HTTP 429 | Stay on the same transport, wait as long as `Retry-After` says (up to 10 minutes), retry |
| Official page redirected to the section above it, or the home page | Not stored, not retried. Recorded `failed` with the address it went to; the last good copy stays up until the seed is updated. A page that moved sideways is still followed |
| Parse error | Keep the last valid record, log it loudly, record `failed` |
| Wrong Handbook code/year | Parse failure; never substitute another item's data |
| Partial, repeated or wrong-year Handbook index | Fail discovery instead of returning an apparently complete list |
| Non-HTML body | Do not ingest it; keep document links on their source pages |
| Extraction under 200 characters | Treated as a template change, not as deleted content. Keep the last valid version |
| 30 Handbook targets fail in a row | The run stops with `UpstreamDown` and the job is recorded `failed`. Not used for official pages, which span several hosts |
| Browser page crashes | Close it and open a new one on the next fetch, at most twice a run |
| systemd stops the run (SIGTERM) | The job is recorded `failed`. A job of the same kind still `running` after 12 hours is closed as failed when the next run starts |

A failed official page keeps being served from its last good copy, with the
date it was last read. Only a 404 or 410 takes it off the site. The failure is
in `official_pages.fetch_error`, and the page is retried on the next run.

After each scheduled run, `python -m crawler.sync.alert <job types>` prints
what needs a person: a failed run, one still marked running, or more than 5%
of targets (and at least five) failed. `scheduled-refresh.sh` mails that to
`ALERT_EMAIL`, at most once a day for each kind. `/api/health` has the last run
of each kind under `data.crawls` and `data.handbook_overdue`.

## What never enters the repository

Crawled HTML, page dumps, database dumps, images, PDFs, raw HAR/CDP evidence.
`backend/tests/fixtures` and synthetic test builders exercise upstream shapes
without redistributing full source pages.

## Auditing coverage without a database

```bash
PYTHONPATH=backend python -m crawler.official.audit --inventory-only --out /tmp/inventory.json
PYTHONPATH=backend python -m crawler.official.audit --site my-study --out /tmp/malaysia.json
PYTHONPATH=backend python -m crawler.official.audit --site policies --out /tmp/policies.json
```

The audit fetches only the chosen curated entry pages, with robots checks and
the normal rate limit. It records unchecked entries, failed fetches, registered
links, review candidates and document links; it does not fetch outgoing links
or write the database. Counts describe this bounded inspection, not the entire
Monash website. See [the October audit](SOURCE-QUALITY-AUDIT.md) for findings,
REA limitations and rollout verification.


## After the extractor changes

`EXTRACTOR_VERSION` is part of the content hash, so bumping it is what makes the
next crawl re-extract instead of skipping. Two things have to follow it:

```bash
deployment/crawl.sh official --all     # re-extract with the new version
deployment/crawl.sh seed               # re-stamp the hand-written translations
deployment/translate.sh zh short       # re-translate against the new text
```

The seed step matters: a hand-written translation is stored against the hash of
the English it was made from, so after a re-extraction every seeded page would
otherwise show "this may be out of date" about text Monash never touched.

## Translating what has been crawled

```bash
deployment/translate.sh zh short   # titles and closed-list values - minutes
deployment/translate.sh zh all     # adds overviews and outcomes - about 30 min
```

Same shape as a crawl: sequential, idempotent, and keyed on the source hash, so
a unit whose English has not moved is skipped. It writes only rows marked
`provenance='machine'`; a hand-written translation for the same target always
wins on read.

The models are baked into the crawler image (`TRANSLATION_LOCALES` build arg)
rather than downloaded per run, because a `compose run` container is discarded
each time and would otherwise re-fetch a hundred megabytes before starting.
