# 0001. One FastAPI app, one PostgreSQL, one Nuxt server

Status: Accepted (written down 2026-10, for a decision made earlier)

## Context

Two people build and run Monash Hub on one VPS that already hosts other
services. The product is a read-mostly site: Handbook data crawled once and
served to everyone, official pages refreshed on a schedule, and a student
forum that is small by any server's standards.

## Decision

A modular monolith. The backend is one FastAPI application with package
boundaries (`handbook`, `knowledge`, `search`, `community`, `plan`) and one
PostgreSQL 17 database. The frontend is one Nuxt server. The crawler runs the
same backend image with a different command, on demand. No message broker, no
Redis, no object store, no separate search service.

## Consequences

- One Compose project, one deploy script, one place to look when something
  is wrong. `deployment/deploy.sh` backs up, migrates, seeds and restarts the
  whole thing in a few minutes.
- A bug in the crawler can take the API down with it if it runs away, so the
  crawler container has a CPU and memory limit and never runs unattended on
  the same box without one.
- Measured on a generated forum many times the expected size, every list
  query answered in under a millisecond (`docs/ARCHITECTURE.md`, "Does it
  hold up as it fills?"). Nothing here needs a cache.
- Splitting later is possible along the package boundaries. Splitting first
  would have bought deployment complexity and nothing else.

## Revisit when

A second machine is needed for capacity, or a component needs a release
cadence of its own. Neither has happened.
