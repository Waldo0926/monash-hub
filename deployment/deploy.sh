#!/usr/bin/env bash
#
# Deploy Monash Hub on the VPS.
#
#   /opt/monash-hub/repo/deployment/deploy.sh            # latest origin/main
#   /opt/monash-hub/repo/deployment/deploy.sh <sha>      # that commit of main
#
# Checks out the commit, rebuilds, migrates, restarts, and puts the previous
# images back if the new API never reports healthy. Safe to re-run. It never
# touches any other compose project on the host.
#
# GitHub Actions passes the commit its CI run tested. Under the SSH forced
# command in docs/AUTOMATED-DEPLOYMENT.md the argument arrives in
# SSH_ORIGINAL_COMMAND rather than in $1, so both are read. Only a commit on
# origin/main is accepted: a dispatch from another branch deploys nothing.
set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-/opt/monash-hub/repo}"
BACKUP_DIR="${BACKUP_DIR:-/opt/monash-hub/backups}"
COMPOSE=(docker compose -p monash-hub)

cd "$PROJECT_DIR"

if [[ ! -f .env ]]; then
  echo "error: $PROJECT_DIR/.env is missing. Copy .env.example and fill it in." >&2
  exit 1
fi

# --- which commit ---------------------------------------------------------------
# Bash reads a script as it runs, so the checkout below must not happen under
# the feet of this process: the first invocation only moves the checkout and
# then re-executes the script that came with it, with --at marking that.
if [[ "${1:-}" != "--at" ]]; then
  sha_from_ssh="$(sed -nE 's/.*\b([0-9a-f]{40})\b.*/\1/p' <<<"${SSH_ORIGINAL_COMMAND:-}")"
  DEPLOY_SHA="${DEPLOY_SHA:-${1:-$sha_from_ssh}}"

  echo "==> Fetching origin"
  git fetch --prune origin
  if [[ -z "$DEPLOY_SHA" ]]; then
    DEPLOY_SHA="$(git rev-parse origin/main)"
  elif ! git merge-base --is-ancestor "$DEPLOY_SHA" origin/main; then
    echo "error: $DEPLOY_SHA is not on origin/main; only reviewed commits are deployed" >&2
    exit 1
  fi
  git checkout -q --detach "$DEPLOY_SHA"
  echo "    now at $(git rev-parse --short HEAD) - $(git log -1 --pretty=%s)"
  exec "$PROJECT_DIR/deployment/deploy.sh" --at "$DEPLOY_SHA"
fi
DEPLOY_SHA="$2"

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

echo "==> Keeping the running images as the fallback"
# Compose names a built image <project>-<service>. The tag that is running
# now becomes :previous, so a release whose API never comes up can be undone
# without a rebuild. The database is already backed up above; a migration is
# not undone here, only the containers.
for service in api web crawler migrate; do
  if docker image inspect "monash-hub-$service:latest" >/dev/null 2>&1; then
    docker tag "monash-hub-$service:latest" "monash-hub-$service:previous"
  fi
done

rollback() {
  echo "==> Putting the previous images back" >&2
  local restored=0
  for service in api web; do
    if docker image inspect "monash-hub-$service:previous" >/dev/null 2>&1; then
      docker tag "monash-hub-$service:previous" "monash-hub-$service:latest"
      restored=1
    fi
  done
  if [[ $restored -eq 1 ]]; then
    "${COMPOSE[@]}" up -d --no-build api web
    echo "    previous images are running again; the database keeps this release's migrations" >&2
  else
    echo "    no previous images to go back to (first deploy)" >&2
  fi
}

echo "==> Building images"
# --profile tools is not optional here: crawler and migrate live behind it, and
# without it a deploy silently ships yesterday's crawler.
"${COMPOSE[@]}" --profile tools build

echo "==> Running migrations"
"${COMPOSE[@]}" run --rm migrate

echo "==> Registering the official page list"
# Writes new seed pages (and retires dropped ones) without fetching anything,
# so the FAQ seeded next can link to a page added in this release. The pages
# themselves are fetched by the scheduled refresh.
"${COMPOSE[@]}" run --rm crawler python -m crawler.official.run --register

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
    rollback
    exit 1
  fi
  sleep 2
done

# One-off data repairs do not live here. A deploy must not depend on the
# Handbook answering, nor on two particular units looking a particular way:
# both happened, and the 2027 rollover would have failed every deploy. See
# deployment/verify-handbook-parser.sh for the repairs that used to run here.

echo "==> Done: $(git rev-parse --short HEAD) is live"
curl -fsS "http://127.0.0.1:${api_port}/api/health"; echo
