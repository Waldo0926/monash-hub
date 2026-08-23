# AGENTS.md

Rules for anyone writing code in this repository, human or otherwise. They come
from the product roadmap and they are not stylistic preferences — each one is
here because breaking it costs money, trust, or someone else's server.

## Do not

- **Do not add an LLM to the answer path.** No OpenAI, Anthropic, or any other
  model SDK behind a request. No pgvector, no embeddings, no RAG. That is Stage
  7, after there are real users and a reason to pay for it. **Every question the
  product answers is still a database lookup or a template**, and that sentence
  is the rule - not "no third-party service ever appears in the repository".

  There is exactly one exception, and it is shaped so the sentence above stays
  true: `app/knowledge/translate_units.py` calls a translation service
  **offline, in batches, run by hand**, and writes rows into
  `content_translations` — the same table a person writes into. Nothing calls it
  during a request. If it is deleted tomorrow, every page still renders; the
  Chinese on unit descriptions is simply not there.

  Four conditions keep it honest, and a change that weakens any of them is not
  a refactor:

  1. **It only touches unit descriptions.** Overview, teaching approach,
     workload, learning outcomes. Not official pages, not the FAQ, not anything
     a student wrote. The pages that decide an enrolment, a fee or a visa are
     translated by a person.
  2. **The glossary is not negotiable.** `app/knowledge/glossary.py` holds the
     terms the service is not allowed an opinion about, starting with the pair
     it always gets backwards — at Monash a *unit* is a subject and a *course*
     is the degree. Output that renders one of them wrongly is **discarded, not
     stored**.
  3. **The page says it is machine translated**, in different words and a
     different colour from a human translation. `method` on the row is what
     drives that, and it must never be set to `human` by a machine.
  4. **A failure leaves English.** Every path out of a failed translation ends
     with the unit keeping its source text. A gap is recoverable; a confident
     wrong sentence about census dates is not.
- **Do not merge official data and community content.** Handbook fields,
  official Monash pages and student posts stay in separate tables and are
  labelled differently everywhere they appear. There is no shared `answers`
  table, and there never will be.
- **Do not crawl monash.edu indiscriminately.** The seed list is curated by
  hand. It grows from real search queries after public beta, not because
  crawling more is easy.
- **Do not mirror files.** Text, structured fields, links and metadata only.
  No images, no videos, no lecture recordings, no PDFs into the database.
  Structure *is* text: headings, lists and tables are extracted as typed blocks
  (`app/knowledge/cleaner.py`) because a table flattened into a column of loose
  numbers is not a cheaper copy of the page, it is a broken one. Screenshotting
  a page to preserve its layout is still mirroring, and still out.
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
- **Do not translate source content *silently*.** This rule used to be an
  outright ban, and the reason for the ban still stands: translating a quotation
  without saying so turns someone else's statement into ours. What changed is
  that a Chinese-reading student was being handed English on the pages that
  decide their enrolment, and "read it in the original" is not a neutral default
  for them. So translation is now allowed under four conditions, all of which
  are enforced in code:

  1. **A person writes it.** No model, no translation API. Translations live in
     `backend/app/knowledge/translations_seed.py`, in the repository, where they
     can be read in a diff.
  2. **A missing translation stays in English.** Never approximate, never fill
     the gap. `app/knowledge/translations.py` falls back to the source on every
     miss, and that is the feature, not a limitation of it.
  3. **It is labelled on screen.** `TranslationNotice.vue` says it is unofficial
     and links to the original. A reader must never be able to mistake our
     Chinese for something Monash published.
  4. **It expires.** Every translation is stored against the content hash of the
     English it was made from. When the source changes, the hash stops matching
     and the page says the translation may be out of date, rather than
     continuing to speak for text that has changed underneath it.

  Student posts are still never translated: they are somebody's own words in a
  forum, and there is no version of that which is ours to rewrite.

  Handbook *field values* - campus, teaching period, attendance mode, assessment
  type - are a separate case handled by `frontend/i18n/handbook-terms.ts`. Those
  come from closed lists a few dozen entries long, so they are translated by
  exact lookup at display time and the stored value is never touched.
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
| Chinese for Handbook field values | `frontend/i18n/handbook-terms.ts` |
| Chinese for official page and unit prose | `backend/app/knowledge/translations_seed.py` |
| Terms machine translation may not touch | `backend/app/knowledge/glossary.py` |
| The batch translation run | `backend/app/knowledge/translate_units.py` |
| How an official page is turned into blocks | `backend/app/knowledge/cleaner.py` |
| How a guide page renders | `frontend/components/PageBlocks.vue` |
| Registration and reset rules | `backend/app/api/v1/auth.py`, `backend/app/core/verification.py` |
| What sends a notification | `backend/app/community/notifications.py` |
| Production topology | `docker-compose.yml`, `deployment/` |
