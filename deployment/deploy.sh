#!/usr/bin/env bash
#
# Deploy Monash Hub on the VPS.
#
#   /opt/monash-hub/repo/deployment/deploy.sh
#
# Pulls main, rebuilds, migrates, restarts. Safe to re-run. It never touches
# any other compose project on the host.
set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-/opt/monash-hub/repo}"
BACKUP_DIR="${BACKUP_DIR:-/opt/monash-hub/backups}"
COMPOSE=(docker compose -p monash-hub)

cd "$PROJECT_DIR"

if [[ ! -f .env ]]; then
  echo "error: $PROJECT_DIR/.env is missing. Copy .env.example and fill it in." >&2
  exit 1
fi

echo "==> Backing up the database before anything else"
mkdir -p "$BACKUP_DIR"
if "${COMPOSE[@]}" ps --status running --services 2>/dev/null | grep -qx postgres; then
  stamp="$(date -u +%Y%m%dT%H%M%SZ)"
  # Read the two values needed rather than sourcing the file. .env is a Compose
  # env file, not a shell script: Compose is happy with EMAIL_FROM_NAME=Monash
  # Hub, and `.` is not.
  db_user="$(sed -n 's/^POSTGRES_USER=//p' .env | tail -1)"
  db_name="$(sed -n 's/^POSTGRES_DB=//p' .env | tail -1)"
  "${COMPOSE[@]}" exec -T postgres \
    pg_dump -U "${db_user:-monashhub}" "${db_name:-monashhub}" \
    | gzip > "$BACKUP_DIR/monashhub-$stamp.sql.gz"
  echo "    saved $BACKUP_DIR/monashhub-$stamp.sql.gz"
  # Keep a fortnight of daily backups; the dataset is small and re-crawlable.
  find "$BACKUP_DIR" -name 'monashhub-*.sql.gz' -mtime +14 -delete
else
  echo "    postgres is not running yet - first deploy, nothing to back up"
fi

echo "==> Fetching main"
git fetch --prune origin
git checkout main
git reset --hard origin/main
echo "    now at $(git rev-parse --short HEAD) - $(git log -1 --pretty=%s)"

echo "==> Building images"
# --profile tools is not optional here: crawler and migrate live behind it, and
# without it a deploy silently ships yesterday's crawler.
"${COMPOSE[@]}" --profile tools build

echo "==> Running migrations"
"${COMPOSE[@]}" run --rm migrate

echo "==> Seeding curated content"
# Human-reviewed translations and curated FAQ entries ship with the code. They
# are idempotent upserts, so every deploy must apply them; otherwise a release
# can contain the corrected wording while production keeps an older machine
# translation indefinitely.
"${COMPOSE[@]}" run --rm crawler python -m app.knowledge.seed

echo "==> Refreshing the Chinese search index"
# Seeding can add or correct Chinese unit and guide titles. Display reads the
# translation table directly, while full-text search reads the flattened,
# indexed copy, so the two must move together on every deploy.
"${COMPOSE[@]}" run --rm crawler python -m app.search.reindex_zh

echo "==> Starting services"
# Deliberately not --remove-orphans. A crawl started with `compose run` is a
# container Compose does not consider part of the active profile, so a deploy
# would kill a backfill that has been running for hours. Tidying up genuinely
# stale containers is worth less than that.
"${COMPOSE[@]}" up -d

echo "==> Waiting for the API to report healthy"
api_port="$(sed -n 's/^API_PORT=//p' .env | tail -1)"
api_port="${api_port:-8100}"
for attempt in $(seq 1 30); do
  if curl -fsS "http://127.0.0.1:${api_port}/api/health" >/dev/null 2>&1; then
    echo "    API healthy after ${attempt}0s at most"
    break
  fi
  if [[ $attempt -eq 30 ]]; then
    echo "error: API did not become healthy. Recent logs:" >&2
    "${COMPOSE[@]}" logs --tail 50 api >&2
    exit 1
  fi
  sleep 2
done

# This release fixes a class of Handbook pages whose prerequisites exist only
# in Rules / Enrolment Rule prose. Existing database rows have to be reparsed;
# merely deploying the new parser cannot reconstruct data it never stored.
# MTH2051 is refreshed first, then the whole 2026 Handbook runs rate-limited in
# the background. The helper is locked and version-marked, so later deploys do
# not start another full pass.
requisite_version="20260915-text-requisites-v1"
requisite_done="/opt/monash-hub/state/handbook-requisites-$requisite_version.done"
if [[ ! -f "$requisite_done" ]]; then
  log_dir="/opt/monash-hub/logs"
  mkdir -p "$log_dir"
  requisite_log="$log_dir/handbook-requisites-$requisite_version.log"
  nohup bash "$PROJECT_DIR/deployment/refresh-handbook-requisites.sh" \
    >"$requisite_log" 2>&1 < /dev/null &
  echo "==> Started one-time Handbook requisite refresh (pid $!, log: $requisite_log)"
fi

echo "==> Done"
curl -fsS "http://127.0.0.1:${api_port}/api/health"; echo
