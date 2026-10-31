# AGENTS.md

Repository rules for human and automated contributors. The project handles official-source data, student-generated content, authentication, and production deployment, so changes must preserve source boundaries, privacy, and reproducibility.

## Do not

- **Do not merge official data and community content.** Handbook fields, official Monash pages and student posts remain separate data types and are labelled differently in the UI.
- **Do not crawl monash.edu indiscriminately.** Official-page seeds are curated. Expand coverage deliberately and respect rate limits and upstream availability.
- **Do not mirror files.** Store structured fields, text, links and metadata only. Do not ingest images, videos, lecture recordings, PDFs or other binary copies of third-party material.
- **Do not commit secrets or production data.** No `.env`, credentials, private keys, database dumps, raw crawl output or user exports. `.env.example` is the only environment file intended for Git.
- **Do not modify unrelated services on a shared production host.** Monash Hub must remain isolated by its own Compose project, network, volumes and reverse-proxy configuration.
- **Do not develop on the production server.** Develop and test on a branch, merge through a Pull Request, then deploy the reviewed `main` branch.
- **Do not expose PostgreSQL publicly.** It belongs on the internal container network and has no published database port.
- **Do not copy third-party code under an incompatible licence.** Reimplement ideas when necessary and preserve attribution where required.
- **Do not translate source content silently.** Translations must be clearly marked as unofficial, preserve a link to the original source, record provenance, and fail back to the original language when a trustworthy translation is unavailable.
- **Do not let machine translation decide high-impact terminology.** Terms such as `census date`, `hurdle`, `WAM`, `credit points`, `intermission` and `prohibition` are protected through the glossary/closed-list translation layer.
- **Do not use read-modify-write for counters.** `answer_count`, `vote_count` and `view_count` must use atomic database updates.

## Do

- **Keep parsers pure.** Handbook parsers accept HTML and return normalised Python dictionaries without network or database access. Tests use small synthetic fixtures that exercise upstream page shapes without redistributing full page snapshots.
- **Never overwrite good data with a failed crawl.** Fetch or parse failures keep the last valid record and are recorded separately.
- **Hash before writing.** Unchanged normalised content should not cause a database rewrite or reindex.
- **Rate-limit every fetcher.** Fetch sequentially, keep a non-zero delay floor, cap retries and use backoff.
- **Show provenance and freshness.** Official information displayed to a student should retain its source link and last-checked date.
- **Keep account endpoints uninformative.** Registration, sign-in and password-reset responses must not reveal whether an email address already has an account.
- **Index for the actual query pattern.** New community sorts and filters should have indexes that match their filtering and ordering behaviour.
- **State uncertainty as uncertainty.** “The Handbook does not list an exam” is different from “there is no exam”. Preserve nullable/unknown states where the source is silent.
- **Design mobile-first and accessibly.** Use visible focus states, real headings, usable touch targets and redundant signals beyond colour.
- **Design loading, empty, error, stale and permission-denied states as part of each feature.**

## Translation rules

1. Human-reviewed and machine translations are stored with provenance and surfaced as unofficial translations.
2. Protected terminology and closed-list Handbook values are handled by exact lookup before free-form translation.
3. A missing or invalid translation stays in the source language instead of being approximated.
4. Translation UI links back to the original source.
5. Whole-field translations are associated with source hashes so upstream changes can be surfaced as stale.
6. Student community posts are not automatically translated.

## Workflow

- `main` is the production branch.
- Feature work uses `feat/*`, `fix/*` or `chore/*` branches and is merged by Pull Request.
- CI must pass linting, migration drift checks, backend tests and the frontend build.
- Schema changes include an Alembic migration in the same change.
- Parser behaviour changes include or update a synthetic fixture test.
- Production credentials are injected through environment variables or GitHub environment secrets; they never belong in the repository.

## Where things live

| I want to change… | Look in |
| --- | --- |
| Handbook unit parsing | `backend/app/handbook/parser.py` |
| Course / area-of-study parsing | `backend/app/handbook/course_parser.py` |
| Models and persistence | `backend/app/models/`, `backend/app/handbook/repository.py` |
| Official-page seeds | `crawler/official/seeds.py` |
| Search routing and ranking | `backend/app/search/` |
| Curated FAQ data | `backend/app/knowledge/faq_seed.py` |
| Official-page extraction | `backend/app/knowledge/cleaner.py` |
| Translation mechanics / glossary | `backend/app/knowledge/translations.py`, `backend/app/knowledge/glossary.py` |
| Interface translations | `frontend/i18n/` |
| Guide rendering | `frontend/components/PageBlocks.vue` |
| Authentication and verification | `backend/app/api/v1/auth.py`, `backend/app/core/verification.py` |
| Community notifications | `backend/app/community/notifications.py` |
| Deployment topology | `docker-compose.yml`, `deployment/` |

## Public-repository boundary

The public repository may contain source code, synthetic fixtures, example configuration and deployment templates. It must not contain private user data, credentials, database contents, customer data, raw production crawl output, or unrelated infrastructure details.
