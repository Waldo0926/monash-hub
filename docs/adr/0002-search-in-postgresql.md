# 0002. Search in PostgreSQL, not a search engine

Status: Accepted (written down 2026-10, for a decision made earlier)

## Context

The site has to find units by code, title and content, official guides by
topic, and forum posts by text, in English and in Chinese, with typos. The
usual answer is Elasticsearch or Meilisearch. Either is another service to
run, back up and keep in sync with the database.

## Decision

Three indexes, all in PostgreSQL:

- generated `tsvector` columns with GIN indexes on `units`, `official_pages`,
  `faq_entries` and `community_posts`;
- trigram (`pg_trgm`) indexes on unit and page titles, for typos;
- an exact unit-code shortcut ahead of both.

Chinese titles are indexed through a flattened copy that is rebuilt on every
deploy (`app.search.reindex_zh`), because PostgreSQL's parser does not
segment Chinese.

Results are grouped by source (Handbook, degrees, official guides, FAQ,
community) and never merged into one ranked list.

## Consequences

- Generated columns cannot drift from their row. There is no indexing queue
  to fall behind and no second store to restore after an outage.
- Ranking is simpler than a search engine's. For a catalogue of a few
  thousand units and a few hundred pages that has not mattered.
- The Chinese index is a deploy-time step that must stay in `deploy.sh`.
  Forgetting it means a corrected Chinese title shows on the page but is not
  found by search.
- Grouping by source is a product decision as much as a technical one: a
  merged list is how a student's opinion ends up looking like a Handbook
  fact.

## Revisit when

The corpus grows past what one PostgreSQL can index comfortably, or ranking
quality becomes the main complaint. Check `EXPLAIN ANALYZE` on the search
queries before reaching for a new service.
