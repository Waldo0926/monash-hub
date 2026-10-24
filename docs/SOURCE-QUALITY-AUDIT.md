# Official-source quality audit — 25 October 2026

## Scope and evidence

Baseline: `061eb8fb3abefae8b66f9055d8545f93fac8493d`. This review inspected the
crawler, parsers, source registry, translation handling and guide renderer.
It sampled public Monash Australia, Monash Malaysia, Policy Bank and Handbook
sources. It is not a whole-site crawl or a production database audit.

The registry started with 746 URLs: 365 Malaysia, 273 Australia and 108 shared.
The change adds 13 reviewed HTML sources: five Policy Bank directories and eight
Malaysia introduction/admission/study-options pages. The resulting registry is
759 URLs (373 Malaysia, 273 Australia, 113 shared), without duplicate URLs/slugs.
Registration does not establish that a source has been fetched successfully.

Official entry points checked:

- [Malaysia homepage](https://www.monash.edu.my/),
  [welcome](https://www.monash.edu.my/about/welcome),
  [reputation](https://www.monash.edu.my/about/top-university-in-malaysia),
  [entry requirements](https://www.monash.edu.my/study/entry-requirements),
  its academic, English and age guidance, and undergraduate/postgraduate indexes.
- [Malaysia exchange guidance](https://www.monash.edu.my/study-abroad/outbound/exchange-program):
  eligibility, dates and faculty planning links are separate from Handbook rules.
- [Education Policy Bank](https://www.monash.edu/policy-bank/policies-and-procedures/academic/education),
  research, graduate research, governance and IT policy directories. These HTML
  directories link to the authoritative policy documents; their bodies are not
  mirrored. Education lists separate versions by effective date, so a generic
  "latest policy" answer without teaching-period context is unsafe.
- The 2026 and 2027 Handbook pages for FIT3155, FIT2102, FIT2109, FIT3143 and
  C2001: all ten fetched and parsed successfully over HTTP in this session.
  FIT3155's published hurdle metadata differs between years; C2001 has five
  top-level structure groups in 2026 and six in 2027. Group counts alone do not
  establish a student's graduation requirements or applicability to an intake.
- The Handbook index reported 6,137 total academic items for 2026 and 6,284 for
  2027. These are combined unit/course/area counts from a five-result probe,
  not counts of units, stored records or a verified complete inventory.

## REA observations and limits

REA 6.7.0 was run through its version-pinned CLI, without changing global Codex
configuration. Dedicated unsigned-in Chrome profiles were observed on loopback
CDP ports. REA recorded an access-error shell for the Handbook and a challenge
shell for the Malaysia exchange page; those browser observations did not expose
the official content. A separate HTTP client could read the Handbook and its
search endpoint. Three real public responses (2026/2027 FIT3155 plus the 2027
index probe) were retained as a local HAR for REA's offline network inspection.

Public official pages were also checked through the available web reader. That
reader's success is not evidence that the production crawler can fetch them.
In the local HTTP audit, both official-site robots endpoints answered 403; the
new audit stopped before fetching the six Malaysia and five Policy Bank entry
pages. It must report that coverage as unknown, not absent or complete.
Raw captures and page bodies remain outside Git.

## Implemented changes

| Defect or gap | Resulting behaviour |
| --- | --- |
| Link changed but title/body words stayed identical | Hash includes normalised structured blocks and link targets, so policy replacements are detected |
| Policy and course-map links disappeared inside tables | Table blocks carry a labelled link index; rendering and unofficial translation preserve those targets |
| HTTP 200 challenge, sign-in or error shells could be indexed | Recognised shells fail; last valid stored content is retained by the existing persistence path |
| Non-HTML responses treated as page content | HTTP fetchers inspect MIME type before reading a successful response body; documents remain links |
| Relative links resolved against an obsolete pre-redirect path | Official fetch results expose the effective URL, used by extraction and discovery |
| Official HTTP redirects followed arbitrary destinations | Redirects are bounded to approved public Monash hosts and checked against target robots rules |
| Robots 403/429 or HTML shell interpreted as an empty allow-all file | Such hosts close for the run, with permission reported as unknown; 404/410 remain absent-file responses |
| Handbook fetcher ignored Retry-After and lost final HTTP status | Both numeric and HTTP-date hints are honoured within the existing pause cap; status remains available |
| Handbook JSON identity could differ from the requested code/year | Unit, course and area parsers reject mismatches, keeping data from different years separate |
| Exact script-attribute regex broke on harmless markup changes | JSON extraction tolerates attribute order/nonce changes and rejects malformed object shapes |
| Truncated/repeated/wrong-year search pages looked like discovery success | Discovery fails visibly on incomplete pages, unstable totals, repetition and malformed/wrong-year items |
| Existing discovery omitted Policy Bank and Malaysia admissions/introduction sections | Explicit bounded discovery profiles cover those sections; candidates still require review |
| No repeatable, database-free coverage receipt | `crawler.official.audit` reports registry counts, inspected/unchecked entries, failures and outgoing link dispositions |

## Running and accepting the change

Run the audit before promoting newly discovered sources:

```bash
PYTHONPATH=backend python -m crawler.official.audit --inventory-only --out /tmp/seed-inventory.json
PYTHONPATH=backend python -m crawler.official.audit --site my-study --out /tmp/malaysia-audit.json
PYTHONPATH=backend python -m crawler.official.audit --site policies --out /tmp/policy-audit.json
```

Inspect `pages`, `entry_pages_unchecked`, `outcomes` and `link_dispositions`.
`review-candidate` does not mean missing authoritative policy: it may be a
landing page, another content pipeline, or a page that should stay unindexed.
The audit never follows or downloads candidate/document links or writes the DB.

After review and deployment through the normal PR/main workflow:

1. Register the updated seed list with `deployment/crawl.sh official --register`.
2. Refresh due pages; an extractor rollout can use `deployment/crawl.sh official --all`
   to re-extract stored content with version 7. This is hundreds of sequential
   requests and can take over an hour; watch failures and preserve old data.
3. Review translations against their new hashes before re-stamping them. Follow
   `docs/CRAWLING.md`; hash invalidation must not silently imply human review.
4. Verify the deployed revision, crawl outcomes, policy-table links in original
   and translated views, and source/freshness labels. This review does not claim
   a merge, deployment, production recrawl or current production data.

## Remaining work requiring evidence

- Audit stored rows against complete year-specific Handbook inventories and
  successful crawl receipts. A small live sample cannot establish completeness.
- Add explicit policy authority/effective-from/effective-until/supersession
  metadata and query filters before attempting policy conflict resolution.
- Review campus applicability at the document/section level. A policy directory
  labelled shared does not make every document or exception global.
- Inspect malformed merged tables, nested lists, interactive decision trees and
  script-only pages with representative fixtures before changing their parsers.
- Extend the reviewed-source map to additional faculties, admissions, scholarships,
  accessibility and campus services using audit candidates and real user queries.
  Do not automatically promote every link or indexed URL into the knowledge base.

## Validation receipt

- Backend suite against an isolated PostgreSQL 17: 1,253 passed. Subsequent
  targeted source/parser/translation checks after the final guards: 149 passed,
  23 database-dependent cases skipped in that targeted run (covered by the full
  database suite before those guard-only changes).
- Frontend typecheck, 48 unit tests and production build passed.
- Ruff and whitespace checks passed.
- Ten live Handbook pages parsed successfully; two year-specific index probes
  returned the expected year and an integer total.
- REA offline HAR inspection completed with three records, evidence
  `ev_b1afea5eea5441b407066d537e90ef053492fd1d64fd1c17ffac23b463c1624a`.
  This establishes retained response evidence, not a full website inventory.
