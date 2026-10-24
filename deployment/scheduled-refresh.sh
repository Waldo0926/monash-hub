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
# One lock for both crawls: they share the crawler container's CPU budget and
# the same upstream, and neither is urgent enough to run beside the other.
#
# Translation runs after the crawl lock is released, under a lock of its own
# (shared with translate.sh). The first Japanese and Korean fill takes hours,
# and while it held the crawl lock the 02:26 Handbook refresh saw it and
# skipped itself, leaving the week's crawl undone.
set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-/opt/monash-hub/repo}"
STATE_DIR="${STATE_DIR:-/opt/monash-hub/state}"
COMPOSE=(docker compose -p monash-hub)
mkdir -p "$STATE_DIR"
cd "$PROJECT_DIR"

# The engine is whatever .env says (TRANSLATE_ENGINE, default the offline
# model). It matters: a page that changes is translated again here, and the
# offline model would put back what the chat model had just replaced.
engine="$(sed -n 's/^TRANSLATE_ENGINE=//p' .env 2>/dev/null | tail -1)"
# Every language the site offers. Each pass only sends what changed since the
# last one (it skips any target whose English hash it has already translated),
# so after the first fill this is minutes, not hours.
locales="$(sed -n 's/^TRANSLATE_LOCALES=//p' .env 2>/dev/null | tail -1)"
locales="${locales:-zh ja ko}"

# Two strings at a time. Zhipu's free tier answers glm-4.5-flash two at a
# time: measured from the VPS, 40 requests two in flight all came back, and
# with three or four in flight 17 to 19 of them were refused with 429.
workers="$(sed -n 's/^TRANSLATE_WORKERS=//p' .env 2>/dev/null | tail -1)"

# One failed pass (a provider that stops answering, one language the engine
# cannot do) is logged and the next one still runs, as does the reindex.
translate() {
  docker compose -f docker-compose.yml -f deployment/translate-resources.yml -p monash-hub \
    run --rm crawler python -m crawler.translate.run --fields all \
    --engine "${engine:-argos}" --workers "${workers:-2}" "$@" \
    || echo "translation pass failed: $*"
}

# A step that fails is remembered, not fatal: a unit crawl that could not read
# the Handbook index used to end the script there, so degrees, the search
# reindex and the week's translation were all skipped with it. The exit
# status still says something failed, so systemd shows the run as failed.
failed=0

exec 9>"$STATE_DIR/scheduled-refresh.lock"
if ! flock -n 9; then
  echo "another scheduled refresh is running; skipping this one"
  exit 0
fi

case "${1:-}" in
  official)
    # Only pages whose tier says they are due, so running this often costs a
    # handful of requests, not the whole seed list.
    "${COMPOSE[@]}" run --rm crawler python -m crawler.official.run || failed=1
    ;;

  handbook)
    # Units crawled in the last six days are skipped, so a run interrupted by
    # a deploy or a reboot resumes rather than starting over next week.
    "${COMPOSE[@]}" run --rm crawler \
      python -m crawler.handbook.run --all --skip-fresh 144 --min-interval 2 || failed=1
    "${COMPOSE[@]}" run --rm crawler \
      python -m crawler.handbook.run_courses --all --skip-fresh 144 --min-interval 2 || failed=1
    ;;
  *)
    echo "usage: $0 {official|handbook}" >&2
    exit 2
    ;;
esac

# Is next year's Handbook out? One request. When it first is, say so once -
# loading a new year and switching to it is a decision for a person, and the
# faculties' course maps for that year are already up months before.
if [[ "${1}" == official ]]; then
  answer="$("${COMPOSE[@]}" run --rm crawler python -m crawler.handbook.next_year 2>/dev/null | tail -1 || true)"
  if [[ "$answer" == published* ]]; then
    year="$(awk '{print $2}' <<<"$answer")"
    marker="$STATE_DIR/handbook-$year-published"
    if [[ ! -f "$marker" ]]; then
      touch "$marker"
      echo "the $year Handbook is now published: $answer"
      "${COMPOSE[@]}" exec -T api python -m app.core.notify \
        "Monash Hub: the $year Handbook is published" \
        "handbook.monash.edu now lists $year ($answer). Load it with
deployment/crawl.sh handbook --all --year $year (and run_courses), then switch
CURRENT_ACADEMIC_YEAR when it is complete. See docs/DEPLOYMENT.md." || true
    fi
  fi
fi

# A refreshed page keeps its translations, but search reads the flattened copy.
"${COMPOSE[@]}" run --rm crawler python -m app.search.reindex_zh

# The crawl is done; let the other refresh have the upstream.
flock -u 9
exec 9>&-

exec 8>"$STATE_DIR/translate.lock"
if [[ "$1" == official ]]; then
  # Every six hours, so a refresh that finds a pass running leaves its pages
  # to the next one rather than queueing behind it.
  if ! flock -n 8; then
    echo "a translation pass is running; changed pages wait for the next refresh"
    exit "$failed"
  fi
  # A page that changed keeps its old translation, flagged stale, until it
  # is translated again. Only changed or new pages are sent, and a person's
  # translation still wins on read.
  for locale in $locales; do
    translate --locale "$locale" --targets official
  done
else
  # Weekly, so it waits its turn instead of skipping a week. Nothing
  # translated the new Handbook English before this, so a unit Monash
  # rewrote stayed in English until somebody ran translate.sh by hand.
  # Stored sentences are reused; only the ones that changed reach the engine.
  flock 8
  for locale in $locales; do
    translate --locale "$locale" --targets units
    translate --locale "$locale" --targets curriculum
  done
fi
"${COMPOSE[@]}" run --rm crawler python -m app.search.reindex_zh
exit "$failed"
