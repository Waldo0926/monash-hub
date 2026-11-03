# Handbook unit comparison: evidence and limits

Related: #262. Updated 2026-11-03; implementation is a PR until reviewed and deployed.

## Existing behavior and fixes

The unit comparison already supports explicit year pairs, nested prerequisites/corequisites/prohibitions, campuses/periods, assessment weights, nullable exam flags, source links and check dates. Missing years are not inferred to mean discontinued units. AND/OR reordering retains equivalent rules without flattening nesting.

Two additional defects are fixed:

1. Changing a selector after a comparison used to relabel the completed result without reloading its data. Results now retain their requested code and years, mark edited inputs as pending, prevent overlapping submissions and reject an API snapshot whose code/year differs from the request.
2. The API always serializes missing relationship collections as `[]`; the UI therefore could not prove that an old empty record came from an explicit empty source. Collection comparison now needs nonempty rendered data or explicit source coverage before calling empty lists unchanged, added or removed. Legacy records remain unknown until the normal parser refresh supplies evidence.

The parser stores boolean collection-source proof in the normalized UnitVersion JSON, never raw HTML. Coverage metadata is excluded from semantic content hashing. An unchanged-content refresh may enrich only this metadata on the matching version; it does not rewrite child records, invalidate translations or emit a policy-change event. No schema migration or production backfill is part of this PR.

## Acceptance checklist

- Explicit years and API identity checks; no silent fallback for missing editions.
- Added/removed/changed/unchanged/unavailable distinguish absent data from explicit empty source collections.
- English/Chinese wording, original Handbook links and check dates retained.
- Synthetic parser, persistence/API and desktop/phone regression coverage added.
- A unit edition does not replace degree rules for the student's commencement year. The comparison links to the existing course map, which selects degree rules from the plan start year separately from each unit's teaching year.
- This unit page does not compare degree/AOS requirements that it does not model. No eligibility, credit mapping or AI policy interpretation is added.

## Rollout boundary

Ruff, typecheck, unit tests and build run locally. PostgreSQL-specific API/persistence and the full disposable browser stack run in CI; skipped local tests are not passes. Production deployment, naturally refreshed coverage metadata and live affected-flow checks remain necessary before closing #262. Existing old snapshots fail closed, without a forced recrawl, data deletion or new scheduler.
