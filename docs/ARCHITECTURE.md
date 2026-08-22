# Architecture

## The shape of it

```
                    Internet
                       │  HTTPS
              monashhub.secureview.tech
                       │
              nginx (already on the host)
                ├── /       → Nuxt SSR   (127.0.0.1:8101)
                └── /api/*  → FastAPI    (127.0.0.1:8100)
                                  │
                    ┌─────────────┴─────────────┐
                    │   monash-hub-internal     │   private Docker network
                    │                           │
                PostgreSQL 17            Crawler (on demand)
                 no published port        no published port
```

One FastAPI application, one PostgreSQL database, one Nuxt server. No message
broker, no Redis, no Elasticsearch, no model provider. Every one of those would
be a real cost and none of them buys anything the MVP needs: full-text search is
`tsvector`, fuzzy matching is `pg_trgm`, and the "AI" answers are templates over
parsed fields.

## Public and private

The rule the project runs on: **centralise what has to be shared, localise what
belongs to one person.**

| Data | Where | Why |
| --- | --- | --- |
| Handbook units | Central PostgreSQL | Crawl once, serve everyone |
| Official Monash pages | Central PostgreSQL | Same |
| Community posts and answers | Central PostgreSQL | Worthless unless shared and searchable |
| Personal Moodle session, grades, deadlines | Not stored — client side, later | No public value, real risk, and no reason to hold it |
| Lecture slides, recordings, PDFs | Never | We index; we are not a file mirror |

## The sync pipeline

Both crawlers run the same shape:

```
discover → fetch → normalise → hash → compare → parse → validate → persist → index
```

Two properties matter more than throughput:

1. **Unchanged content costs nothing.** `content_hash` is computed over the
   normalised record, not the raw page, so Handbook build ids and nav churn do
   not register as changes. If the hash matches, nothing is parsed, written or
   reindexed.
2. **A failure never destroys good data.** A fetch error, a parse error, or a
   suspiciously short text extraction leaves the previous row intact, marks the
   page `status='error'` and writes a `crawl_history` row. Silent overwriting is
   the failure mode we most want to avoid.

Refresh intervals are tiered by how fast the page actually moves: `dynamic`
twice a day (dates, deadlines), `medium` every two days (how-tos), `stable`
fortnightly (policy). See `crawler/sync/refresh.py`.

## Search

Three indexes, all in PostgreSQL:

- Generated `tsvector` columns on `units`, `official_pages`, `faq_entries` and
  `community_posts`, with GIN indexes. Generated columns cannot drift out of
  sync with their row the way a trigger or an application-side update can.
- Trigram GIN indexes on unit and page titles, for typos.
- An exact unit-code shortcut ahead of both, because someone typing `FIT2102`
  wants that unit and nothing else.

Results are **grouped by source**, never merged into one ranked list. A merged
list is exactly how a student's opinion ends up looking like a Handbook fact.

## The zero-AI router

`POST /api/v1/ask` runs four deterministic stages:

1. Extract unit codes with a regex (`FIT2102`, `fit 2102`, `FIT-2102`).
2. Classify intent against a bilingual keyword dictionary — longest match wins,
   with word boundaries for Latin keywords so `sc` does not fire inside
   `science`.
3. If there is a unit and a Handbook-backed intent, render the stored fields
   through a template.
4. Otherwise fall through: curated FAQ → official page search → community.

Subjective questions ("FIT2102 难不难") are detected and answered with the
published workload plus community threads. The system never produces a
difficulty score, because there is no honest way to compute one.

## Trust boundaries in the UI

Three badges, three colours, three labels — and the label is always present, so
the distinction survives for colour-blind readers and in plain text:

| Badge | Means |
| --- | --- |
| Official Handbook | A parsed Handbook field, with the Handbook link |
| Official source | Text extracted from a monash.edu page, with the link and check date |
| Community | A student wrote this. It is experience, not a rule |

Sponsored content, when it eventually exists, gets a fourth badge and its own
region. It will never affect the ranking of an academic or policy answer.

## Why a monolith

Two people are building this. A modular monolith with clear package boundaries
(`handbook`, `knowledge`, `search`, `community`) can be split later if there is
ever a reason. Splitting first would buy deployment complexity and nothing else.
