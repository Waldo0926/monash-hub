#!/usr/bin/env bash
#
# The scheduled refreshes, run by the systemd timers in deployment/systemd/.
#
#   deployment/scheduled-refresh.sh official   # seed pages that are due, then reindex
#   deployment/scheduled-refresh.sh handbook   # every unit and degree, weekly
#
# Nothing refreshed on its own before this: crawl.sh said the first crawls were
# meant to be watched, and by late September every official page had last been
# checked on 30 August - census and fee dates included - while the site told
# readers when each was "last checked". The refresh tiers in
# crawler/sync/refresh.py (12 hours for dates, 2 days, 14 days) only mean
# something if something asks what is due.
#
# One lock for both: they share the crawler container's CPU budget and the same
# upstream, and neither is urgent enough to run beside the other.
set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-/opt/monash-hub/repo}"
STATE_DIR="${STATE_DIR:-/opt/monash-hub/state}"
COMPOSE=(docker compose -p monash-hub)
mkdir -p "$STATE_DIR"
cd "$PROJECT_DIR"

exec 9>"$STATE_DIR/scheduled-refresh.lock"
if ! flock -n 9; then
  echo "another scheduled refresh is running; skipping this one"
  exit 0
fi

case "${1:-}" in
  official)
    # Only pages whose tier says they are due, so running this often costs a
    # handful of requests, not the whole seed list.
    "${COMPOSE[@]}" run --rm crawler python -m crawler.official.run
    ;;
  handbook)
    # Units crawled in the last six days are skipped, so a run interrupted by
    # a deploy or a reboot resumes rather than starting over next week.
    "${COMPOSE[@]}" run --rm crawler \
      python -m crawler.handbook.run --all --skip-fresh 144 --min-interval 2
    "${COMPOSE[@]}" run --rm crawler \
      python -m crawler.handbook.run_courses --all --skip-fresh 144 --min-interval 2
    ;;
  *)
    echo "usage: $0 {official|handbook}" >&2
    exit 2
    ;;
esac

# A refreshed page keeps its translations, but search reads the flattened copy.
"${COMPOSE[@]}" run --rm crawler python -m app.search.reindex_zh
