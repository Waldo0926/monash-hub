#!/usr/bin/env bash
# One-time repair pass for the 2026 Handbook requisite parser change.
#
# The deployment launches this in the background because a rate-limited crawl
# of every Handbook unit takes several hours. A lock prevents overlapping
# passes, and marker files make the first pass force a reparse while later
# retries skip rows successfully refreshed in the preceding 24 hours.
set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-/opt/monash-hub/repo}"
STATE_DIR="${STATE_DIR:-/opt/monash-hub/state}"
VERSION="20260915-text-requisites-v1"
DONE="$STATE_DIR/handbook-requisites-$VERSION.done"
STARTED="$STATE_DIR/handbook-requisites-$VERSION.started"
LOCK="$STATE_DIR/handbook-requisites-$VERSION.lock"
COMPOSE=(docker compose -p monash-hub)

mkdir -p "$STATE_DIR"
exec 9>"$LOCK"
if ! flock -n 9; then
  echo "another requisite refresh is already running"
  exit 0
fi
if [[ -f "$DONE" ]]; then
  echo "requisite refresh $VERSION already completed"
  exit 0
fi

cd "$PROJECT_DIR"
echo "==> $(date -u +%FT%TZ) refreshing MTH2051 first"
"${COMPOSE[@]}" run --rm crawler \
  python -m crawler.handbook.run --units MTH2051 --year 2026 --min-interval 1

if [[ -f "$STARTED" ]]; then
  echo "==> resuming the full 2026 Handbook refresh; recent successful rows are skipped"
  fresh=(--skip-fresh 24)
else
  echo "==> starting the full 2026 Handbook refresh so every unit is reparsed"
  touch "$STARTED"
  fresh=()
fi

"${COMPOSE[@]}" run --rm crawler \
  python -m crawler.handbook.run --all --year 2026 --min-interval 3 "${fresh[@]}"

touch "$DONE"
echo "==> $(date -u +%FT%TZ) requisite refresh $VERSION completed"
