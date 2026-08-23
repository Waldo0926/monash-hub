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

## Accounts

Nickname, email, password. No real name, no student ID — the roadmap is explicit
that registration friction is what leaves a forum empty, and a student forum
does not need to know who anyone is.

Both registration and password reset are gated on a six-digit code sent to the
address. That is what makes an account recoverable at all: without a verified
address, a forgotten password is a lost account. Only an HMAC of the code is
stored, bound to the address, with a ten-minute expiry and five attempts.

Two things the endpoints deliberately do not reveal:

- **Whether an address has an account.** Requesting a code always returns the
  same body, and a registration code is simply not sent to an address that is
  already registered. "That email is taken" is reported only after a valid code
  proves the requester controls the address.
- **Which part of a sign-in was wrong.** Unknown email and wrong password return
  the same 401 with the same message.

Sessions are JWTs carrying the account's `token_version`. A password reset bumps
that column, which invalidates every token already issued — sign-out-everywhere
without a session table to delete from.

## Notifications

One flat table. A notification copies the actor's nickname, the post title and a
short excerpt at the moment it is written, rather than joining at read time.
That costs a little duplication and buys two things: the list is a single
indexed read, and it still reads correctly after the post is edited or hidden.

They are written when someone answers your question, and when your answer is
marked helpful. Answering your own post notifies nobody.

The header badge polls `/notifications/unread-count` once a minute and pauses
while the tab is hidden. A WebSocket for a number that changes a few times a day
would mean a live connection per open tab for the whole session.

## Interface languages

English, 简体中文, 日本語 and 한국어, switched from the header, remembered in a
cookie, resolved during SSR so the server and the browser render the same
markup.

There is no i18n library: `frontend/i18n/index.ts` is four plain objects and a
`translate()` that substitutes `{name}` placeholders, wired to `$t` by a plugin.
The app has no plural rules worth the dependency and formats its one date by
hand in UTC.

**Only the interface is translated.** Handbook fields, official Monash page text
and anything a student wrote stay in the language they were written in. Those
are quotations from a source, and silently translating a quotation is how a
platform ends up asserting something the official page never said.

## Does it hold up as it fills?

Measured on a generated forum of 2,000 accounts, 20,000 posts, 60,000 answers
and 40,000 notifications — considerably more than a first year is likely to
bring — on one PostgreSQL container:

| Query | p50 | p95 |
| --- | --- | --- |
| Community feed, recent | 0.22 ms | 0.69 ms |
| Community feed, by category | 0.26 ms | 0.30 ms |
| Unit thread feed | 0.23 ms | 0.29 ms |
| Community full-text search | 0.28 ms | 0.35 ms |
| Answers for one post | 0.20 ms | 0.24 ms |
| Unread notification count | 0.18 ms | 0.23 ms |
| Notification list | 0.15 ms | 0.23 ms |
| Sign-in lookup | 0.13 ms | 0.15 ms |

The whole database was 59 MB. Nothing here is close to needing a cache.

Three things make that true, and they are the ones to protect:

- **Composite indexes matching the orderings the feed actually offers** —
  `(is_hidden, is_pinned, updated_at)`, and the same with `category` and
  `unit_code` in front. Without them every community page load is a sequential
  scan plus a sort.
- **Counters updated atomically.** `answer_count`, `vote_count` and `view_count`
  are `UPDATE ... SET x = x + 1`, not read-modify-write. Two people opening a
  thread at the same moment would otherwise each read the same number and write
  it back, losing one.
- **No N+1 in the list endpoints.** Tags and authors are eager-loaded; a feed of
  twenty posts is a fixed handful of queries, not twenty-one.

## Why a monolith

Two people are building this. A modular monolith with clear package boundaries
(`handbook`, `knowledge`, `search`, `community`) can be split later if there is
ever a reason. Splitting first would buy deployment complexity and nothing else.
