# Monash Hub

An independent student information platform for Monash: structured 2026 Handbook
unit data, an index of the official Monash pages students actually have to look
up, and a public, searchable community — in one place.

**Production:** https://monashhub.secureview.tech

> Monash Hub is not affiliated with or endorsed by Monash University. Confirm
> anything that matters through the Monash website, Handbook, Moodle or WES.

## What this version is

No generative AI, no API tokens, no vector database. The MVP answers questions
the way they should be answered — by reading a field we already parsed and
linking back to the source:

- **Handbook** — units, offerings, assessment, requisites, learning outcomes and
  workload, parsed from the Handbook's own JSON and stored per academic year.
- **Official knowledge** — 40 curated monash.edu pages kept as clean text with a
  content hash, a source link and the date we last checked.
- **Zero-AI answers** — a unit-code regex, a bilingual keyword dictionary and a
  deterministic router turn "FIT2102 有没有考试？" into the assessment table.
- **Community** — posts, answers, tags, votes, reports and moderation, visually
  separated from official data everywhere it appears, with notifications when
  someone answers your question.
- **Accounts** — nickname, email, password. Registration and password reset are
  both gated on a code sent to the address; nothing asks for a real name or a
  student ID.
- **Four interface languages** — English, 简体中文, 日本語, 한국어, switched from
  the header. Handbook and official text stays in its source language.

Adding an LLM is Stage 7, after there are real users. The product has to work
without one.

## Layout

```
backend/     FastAPI app, SQLAlchemy models, Alembic migrations, tests
  app/handbook/    Handbook parser (pure functions) and persistence
  app/knowledge/   Official page cleaner, FAQ seed data
  app/search/      Keyword dictionary, unified search, zero-AI router
  app/community/   (models live in app/models/community.py)
crawler/     Fetchers, rate limiting and crawl bookkeeping
frontend/    Nuxt 4 SSR web app with its own design tokens
deployment/  nginx site, deploy and crawl scripts
docs/        Architecture, deployment and crawling notes
```

## Running it locally

You need Docker, Python 3.12 and Node 22.

```bash
cp .env.example .env      # then set POSTGRES_PASSWORD and SECRET_KEY
docker compose -p monash-hub up -d postgres
docker compose -p monash-hub run --rm migrate
```

Backend:

```bash
cd backend
uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python -r requirements-dev.txt
export DATABASE_URL='postgresql+psycopg://monashhub:<password>@localhost:5432/monashhub'
.venv/bin/uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
NUXT_API_BASE=http://localhost:8000/api NUXT_PUBLIC_API_BASE=http://localhost:8000/api npm run dev
```

Load some data:

```bash
docker compose -p monash-hub run --rm crawler python -m crawler.handbook.run --fixtures
docker compose -p monash-hub run --rm crawler python -m crawler.official.run --all
docker compose -p monash-hub run --rm crawler python -m app.knowledge.seed
```

## Tests

```bash
createdb monashhub_test   # or: docker compose -p monash-hub exec postgres createdb -U monashhub monashhub_test
cd backend
export TEST_DATABASE_URL='postgresql+psycopg://monashhub:<password>@localhost:5432/monashhub_test'
.venv/bin/pytest
```

Parser, keyword and cleaner tests run without a database. API tests need
PostgreSQL and skip themselves when `TEST_DATABASE_URL` is unset.

Point it at a **separate database** from the one you develop against — the suite
drops every table it created when it finishes, and pointing it at your dev
database means losing your local data.

## API

`https://monashhub.secureview.tech/api/docs` — or locally, `/api/docs`.

| Endpoint | Purpose |
| --- | --- |
| `GET /api/health` | Liveness plus row counts and the last crawl |
| `GET /api/v1/units` | Unit search and filters |
| `GET /api/v1/units/{code}` | Unit detail |
| `GET /api/v1/units/{code}/assessment` | Assessment only |
| `GET /api/v1/units/{code}/requisites` | Requisites only |
| `GET /api/v1/units/{code}/offerings` | Offerings only |
| `POST /api/v1/ask` | Zero-AI question router |
| `GET /api/v1/search` | Unified search, grouped by source |
| `GET /api/v1/official/search` | Official page full-text search |
| `GET /api/v1/guides` · `/guides/{slug}` | Official guide index and detail |
| `GET/POST /api/v1/community/posts` | Community |
| `POST /api/v1/community/reports` | Reporting |
| `POST /api/v1/auth/verification-code` | Send a registration or reset code |
| `POST /api/v1/auth/signup` · `/signin` | Accounts |
| `POST /api/v1/auth/password-reset` | Recovery, signs other devices out |
| `GET /api/v1/notifications` | Your notifications and unread count |

## Contributing

`main` is the only deployable branch and the VPS tracks it. Work on
`feat/*`, `fix/*` or `chore/*` and merge through a pull request. CI runs lint,
the migration drift check, the backend tests and a frontend build.

Never commit `.env`, a database dump, crawled HTML, or anything else in
`.gitignore`.

## Docs

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — how the pieces fit and why
- [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) — the VPS setup, step by step
- [docs/CRAWLING.md](docs/CRAWLING.md) — crawl policy, rate limits and the WAF
- [docs/ROADMAP-STATUS.md](docs/ROADMAP-STATUS.md) — what is done and what is next
- [AGENTS.md](AGENTS.md) — rules for anyone (or anything) writing code here
