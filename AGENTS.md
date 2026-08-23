# AGENTS.md

Rules for anyone writing code in this repository, human or otherwise. They come
from the product roadmap and they are not stylistic preferences — each one is
here because breaking it costs money, trust, or someone else's server.

## Do not

- **Do not add an LLM.** No OpenAI, Anthropic, or any other model SDK. No
  pgvector, no embeddings, no RAG. That is Stage 7, after there are real users
  and a reason to pay for it. Every question the MVP answers is a database
  lookup or a template.
- **Do not merge official data and community content.** Handbook fields,
  official Monash pages and student posts stay in separate tables and are
  labelled differently everywhere they appear. There is no shared `answers`
  table, and there never will be.
- **Do not crawl monash.edu indiscriminately.** The seed list is curated by
  hand. It grows from real search queries after public beta, not because
  crawling more is easy.
- **Do not mirror files.** Text, structured fields, links and metadata only.
  No images, no videos, no lecture recordings, no PDFs into the database.
- **Do not touch the other projects on the VPS.** The FYP secure file platform
  and the Monash Abroad Tracker share that host. Different compose project,
  different network, different volumes, different nginx server block.
- **Do not commit secrets or data.** No `.env`, no keys, no database dumps, no
  crawled HTML. `.env.example` is the only environment file in Git.
- **Do not develop on the server.** The VPS checks out `main` and deploys it.
  Test locally, open a PR, merge, deploy.
- **Do not expose PostgreSQL.** It has no published port and lives on an
  internal Docker network.
- **Do not copy third-party code with an incompatible licence.** Implement it,
  and record where an idea came from.
- **Do not translate source content.** The interface has four languages; the
  Handbook fields, official page text and student posts inside it have one — the
  one they were written in. Translating a quotation silently turns someone
  else's statement into ours.
- **Do not read the counters and write them back.** `answer_count`,
  `vote_count`, `view_count`: `UPDATE ... SET x = x + 1`, always. A
  read-modify-write loses one of two concurrent updates.

## Do

- **Keep the parser pure.** `app/handbook/parser.py` takes HTML and returns
  dicts. No network, no database. That is what makes it testable against saved
  fixtures, and the fixtures are what stop a Handbook redesign from silently
  corrupting real data.
- **Never overwrite good data with a failure.** A fetch error or a parse error
  keeps the last valid row, records the failure in `crawl_history`, and shouts.
  A gap in today's crawl is recoverable; a blanked unit record is not.
- **Hash before you write.** If `content_hash` is unchanged, skip the parse,
  skip the write, skip the reindex. Most of a healthy crawl should be skips.
- **Rate limit every fetcher.** One request at a time, seconds between them,
  exponential backoff, a retry cap. The floor is not configurable away.
- **Say when you last checked.** Any official value shown to a student carries
  its source link and its check date.
- **Keep account endpoints uninformative.** Requesting a code, signing in and
  resetting a password must not reveal whether an address has an account. The
  wording on screen has to match, or the UI undoes the precaution.
- **Index the ordering, not just the filter.** A new community sort or filter
  needs a composite index that matches it, or it is a sequential scan the day
  the forum gets busy.
- **State uncertainty as uncertainty.** "The Handbook does not list an exam" is
  true. "There is no exam" is not ours to say. `has_exam` is nullable for
  exactly this reason.
- **Design mobile-first and accessible.** 44px touch targets, visible focus
  rings, real headings, no horizontal page overflow, and colour never as the
  only signal.
- **Design every state.** Loading, empty, error, stale and permission-denied are
  part of the feature, not a follow-up ticket.

## Workflow

- `main` is the only deployable branch. The VPS tracks it and deploys on merge.
- Branches are `feat/*`, `fix/*` or `chore/*`, merged by pull request.
- CI must pass: ruff, the migration drift check, backend tests, frontend build.
- Schema changes come with an Alembic migration in the same commit.
- New parser behaviour comes with a fixture test in the same commit.

## Where things live

| I want to change… | Look in |
| --- | --- |
| How a Handbook field is read | `backend/app/handbook/parser.py` |
| What is stored, and how versioning works | `backend/app/models/`, `backend/app/handbook/repository.py` |
| Which official pages are indexed | `crawler/official/seeds.py` |
| How a question is routed | `backend/app/search/keywords.py`, `backend/app/search/router.py` |
| Search ranking | `backend/app/search/service.py` |
| Curated FAQ answers | `backend/app/knowledge/faq_seed.py` |
| Rate limits and retries | `crawler/throttling/limiter.py` |
| Colours, spacing, type | `frontend/assets/css/tokens.css` |
| Interface translations | `frontend/i18n/index.ts` |
| Registration and reset rules | `backend/app/api/v1/auth.py`, `backend/app/core/verification.py` |
| What sends a notification | `backend/app/community/notifications.py` |
| Production topology | `docker-compose.yml`, `deployment/` |
