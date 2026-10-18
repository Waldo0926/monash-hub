# 0003. Direct answers from templates, no language model

Status: Accepted (written down 2026-10, for a decision made earlier)

## Context

Students ask the same questions in slightly different words: when is the
census date, what are the prerequisites for FIT2102, how do I apply for
special consideration. A language model would answer all of them fluently,
and would also invent a census date now and then. The project has no budget
for model calls and no appetite for a confident wrong answer about an
academic rule.

## Decision

`POST /api/v1/ask` is deterministic. It extracts unit codes with a regex,
classifies intent against a bilingual keyword dictionary, renders stored
Handbook fields through a template when it has both, and otherwise falls
through to curated FAQ, official page search and the community. The Ask
button on every page talks to the same endpoint. No model is called and
there is no API key to configure.

Subjective questions ("is FIT2102 hard") get the published workload and the
community threads, never a difficulty score.

## Consequences

- Every answer traces to a stored field, a curated FAQ entry or a page the
  crawler fetched, and the page shows which. Nothing is made up.
- Coverage is only as wide as the keyword dictionary. A question phrased in
  a way nobody anticipated falls through to search, which is the honest
  outcome.
- Zero cost per question, no rate limit from a provider, nothing to leak.
- When a model is added later, this router stays in front of it: the model
  may rephrase, it does not get to answer from its own memory.

## Revisit when

There is a measured set of real questions the router cannot route and a
model that can be run for free on the box. Even then the template path stays
for anything the Handbook answers directly.
