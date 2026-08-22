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
  # shellcheck disable=SC1091
  set -a; . ./.env; set +a
  "${COMPOSE[@]}" exec -T postgres \
    pg_dump -U "${POSTGRES_USER:-monashhub}" "${POSTGRES_DB:-monashhub}" \
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
"${COMPOSE[@]}" build

echo "==> Running migrations"
"${COMPOSE[@]}" run --rm migrate

echo "==> Starting services"
"${COMPOSE[@]}" up -d --remove-orphans

echo "==> Waiting for the API to report healthy"
for attempt in $(seq 1 30); do
  if curl -fsS "http://127.0.0.1:${API_PORT:-8100}/api/health" >/dev/null 2>&1; then
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

echo "==> Done"
curl -fsS "http://127.0.0.1:${API_PORT:-8100}/api/health"; echo
