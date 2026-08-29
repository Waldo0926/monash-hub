#!/usr/bin/env bash
#
# Run a crawl on the VPS.
#
#   deployment/crawl.sh handbook            # the 20 fixture units
#   deployment/crawl.sh handbook FIT2102    # specific units
#   deployment/crawl.sh handbook --all --min-interval 1.5   # every 2026 unit
#   deployment/crawl.sh official            # only seed pages that are due
#   deployment/crawl.sh official --all      # every seed page, ignoring intervals
#   deployment/crawl.sh seed                # curated FAQ rows
#   deployment/crawl.sh reindex-zh          # make the stored Chinese searchable
#   deployment/crawl.sh reindex-zh --stats  # coverage only, writes nothing
#
# Crawls are one-shot containers, not services. Nothing here runs on a timer
# yet: the first production crawls are meant to be watched.
set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-/opt/monash-hub/repo}"
cd "$PROJECT_DIR"
COMPOSE=(docker compose -p monash-hub)

target="${1:-}"; shift || true

case "$target" in
  handbook)
    if [[ $# -eq 0 ]]; then
      "${COMPOSE[@]}" run --rm crawler python -m crawler.handbook.run --fixtures
    elif [[ $1 == -* ]]; then
      # Flags go straight through, so --all and --skip-fresh work from here.
      "${COMPOSE[@]}" run --rm crawler python -m crawler.handbook.run "$@"
    else
      "${COMPOSE[@]}" run --rm crawler python -m crawler.handbook.run --units "$(IFS=,; echo "$*")"
    fi
    ;;
  official)
    "${COMPOSE[@]}" run --rm crawler python -m crawler.official.run "$@"
    ;;
  seed)
    "${COMPOSE[@]}" run --rm crawler python -m app.knowledge.seed
    ;;
  reindex-zh)
    # Copies the stored Chinese onto the rows search queries. Idempotent, and it
    # only writes rows whose text changed - run it after a crawl and after a
    # translation batch. See docs/DEPLOYMENT.md.
    "${COMPOSE[@]}" run --rm crawler python -m app.search.reindex_zh "$@"
    ;;
  *)
    echo "usage: $0 {handbook|official|seed|reindex-zh} [args]" >&2
    exit 2
    ;;
esac
