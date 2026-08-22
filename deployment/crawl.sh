#!/usr/bin/env bash
#
# Run a crawl on the VPS.
#
#   deployment/crawl.sh handbook            # the 20 fixture units
#   deployment/crawl.sh handbook FIT2102    # specific units
#   deployment/crawl.sh official            # only seed pages that are due
#   deployment/crawl.sh official --all      # every seed page, ignoring intervals
#   deployment/crawl.sh seed                # curated FAQ rows
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
    if [[ $# -gt 0 ]]; then
      "${COMPOSE[@]}" run --rm crawler python -m crawler.handbook.run --units "$(IFS=,; echo "$*")"
    else
      "${COMPOSE[@]}" run --rm crawler python -m crawler.handbook.run --fixtures
    fi
    ;;
  official)
    "${COMPOSE[@]}" run --rm crawler python -m crawler.official.run "$@"
    ;;
  seed)
    "${COMPOSE[@]}" run --rm crawler python -m app.knowledge.seed
    ;;
  *)
    echo "usage: $0 {handbook|official|seed} [args]" >&2
    exit 2
    ;;
esac
