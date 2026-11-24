#!/usr/bin/env bash
# Repeatable, read-only public data sync from overseas PostgreSQL (mcs21-vps)
# to China mainland PostgreSQL (vps / monash-hub-cn).
#
# Safety guarantees:
#   1. Strictly READ-ONLY on SRC_HOST (mcs21-vps): executes only `pg_dump --data-only`
#      against an explicit whitelist of 18 public business tables. Never modifies or
#      restarts anything on the overseas host.
#   2. Never exports users, auth/verification/throttle records, notifications,
#      community posts/answers/votes/bookmarks/reports, unit_reviews, search_terms,
#      crawl_history, source_change_events, avatars, tokens, secrets or .env files.
#   3. Audits the exported dump before restore to guarantee zero forbidden tables.
#   4. Restores inside a single atomic transaction on DST_HOST followed by ANALYZE.
#
# Transfer modes:
#   TRANSFER_MODE=direct (default): uses temporary SSH agent forwarding (`ssh -A`)
#     from DST_HOST directly to SRC_HOST (cloud-to-cloud, no keys stored on DST_HOST).
#   TRANSFER_MODE=local: dumps to local /tmp and uploads to DST_HOST:/tmp via scp.
#
# Usage:
#   deployment/sync-cn-public-data.sh
#   TRANSFER_MODE=local deployment/sync-cn-public-data.sh

set -euo pipefail

SRC_HOST="${SRC_HOST:-mcs21-vps}"
SRC_CONTAINER="${SRC_CONTAINER:-monash-hub-postgres-1}"
SRC_DB_USER="${SRC_DB_USER:-monashhub}"
SRC_DB_NAME="${SRC_DB_NAME:-monashhub}"

DST_HOST="${DST_HOST:-vps}"
DST_CONTAINER="${DST_CONTAINER:-monash-hub-cn-postgres-1}"
DST_DB_USER="${DST_DB_USER:-monashhub_cn}"
DST_DB_NAME="${DST_DB_NAME:-monashhub_cn}"

TRANSFER_MODE="${TRANSFER_MODE:-direct}"

# Explicit whitelist of public read-only tables (ordered parent -> child).
PUBLIC_TABLES=(
  official_sources
  official_pages
  official_page_versions
  faq_entries
  units
  unit_versions
  unit_offerings
  unit_assessments
  unit_requisite_groups
  unit_requisite_items
  unit_learning_outcomes
  unit_activities
  courses
  areas_of_study
  curriculum_containers
  curriculum_items
  content_translations
  crawl_jobs
)

# Forbidden tables that must NEVER appear in the whitelist or dump.
FORBIDDEN_TABLES=(
  users
  email_verification_codes
  notifications
  auth_throttle
  community_tags
  community_post_tags
  community_posts
  community_answers
  community_votes
  community_bookmarks
  community_reports
  unit_reviews
  search_terms
  crawl_history
  source_change_events
  alembic_version
)

for tbl in "${PUBLIC_TABLES[@]}"; do
  for bad in "${FORBIDDEN_TABLES[@]}"; do
    if [[ "$tbl" == "$bad" ]]; then
      echo "ERROR: Forbidden table '$tbl' found in PUBLIC_TABLES whitelist. Aborting." >&2
      exit 1
    fi
  done
done

STAMP="$(date +%Y%m%d-%H%M%S)"
LOCAL_DUMP="/tmp/monash-hub-cn-public-${STAMP}.sql.gz"
REMOTE_DUMP="/tmp/monash-hub-cn-public-${STAMP}.sql.gz"
REMOTE_SQL="/tmp/monash-hub-cn-restore-${STAMP}.sql"

cleanup() {
  rm -f "$LOCAL_DUMP"
  ssh -o BatchMode=yes "$DST_HOST" "rm -f '$REMOTE_DUMP' '$REMOTE_SQL'" >/dev/null 2>&1 || true
}
trap cleanup EXIT

TABLE_FLAGS=()
for tbl in "${PUBLIC_TABLES[@]}"; do
  TABLE_FLAGS+=(--table="public.${tbl}")
done

FORBIDDEN_REGEX="^(COPY|INSERT INTO) (public\.)?($(IFS='|'; echo "${FORBIDDEN_TABLES[*]}"))\\b"
TRUNCATE_LIST="$(IFS=,; echo "${PUBLIC_TABLES[*]}")"
IN_CLAUSE="$(printf "'%s'," "${PUBLIC_TABLES[@]}" | sed 's/,$//')"

if [[ "$TRANSFER_MODE" == "direct" ]]; then
  SRC_RESOLVED_HOST="$(ssh -G "$SRC_HOST" | awk '/^hostname / {print $2; exit}')"
  SRC_RESOLVED_USER="$(ssh -G "$SRC_HOST" | awk '/^user / {print $2; exit}')"
  SRC_RESOLVED_PORT="$(ssh -G "$SRC_HOST" | awk '/^port / {print $2; exit}')"
  echo "[1/3] Direct cloud-to-cloud read-only pg_dump (${#PUBLIC_TABLES[@]} public tables) from ${SRC_RESOLVED_USER}@${SRC_RESOLVED_HOST}:${SRC_RESOLVED_PORT} -> ${DST_HOST}..."
  ssh -A -o BatchMode=yes "$DST_HOST" \
    "set -euo pipefail; ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new -p '${SRC_RESOLVED_PORT}' '${SRC_RESOLVED_USER}@${SRC_RESOLVED_HOST}' \"docker exec ${SRC_CONTAINER} pg_dump -U ${SRC_DB_USER} -d ${SRC_DB_NAME} --data-only --no-owner --no-privileges ${TABLE_FLAGS[*]}\" | gzip -c > '${REMOTE_DUMP}'; ls -lh '${REMOTE_DUMP}'"

  echo "[2/3] Auditing dump on ${DST_HOST} to verify zero private/UGC tables are present..."
  ssh -o BatchMode=yes "$DST_HOST" \
    "set -euo pipefail; if gzip -dc '${REMOTE_DUMP}' | grep -qE '${FORBIDDEN_REGEX}'; then echo 'ERROR: Forbidden table detected in dump!' >&2; exit 1; fi; echo '      Audit passed: only whitelisted public tables present.'"
else
  echo "[1/3] Read-only pg_dump of ${#PUBLIC_TABLES[@]} public tables from ${SRC_HOST}:${SRC_CONTAINER} to local temp..."
  ssh -o BatchMode=yes "$SRC_HOST" \
    "docker exec ${SRC_CONTAINER} pg_dump -U ${SRC_DB_USER} -d ${SRC_DB_NAME} --data-only --no-owner --no-privileges ${TABLE_FLAGS[*]}" \
    | gzip -c > "$LOCAL_DUMP"
  ls -lh "$LOCAL_DUMP"

  echo "[2/3] Auditing dump locally and uploading to ${DST_HOST}:${REMOTE_DUMP}..."
  if gzip -dc "$LOCAL_DUMP" | grep -qE "$FORBIDDEN_REGEX"; then
    echo "ERROR: Audit failed! Forbidden table detected in dump. Aborting." >&2
    exit 1
  fi
  echo "      Audit passed: only whitelisted public tables present."
  scp -q "$LOCAL_DUMP" "${DST_HOST}:${REMOTE_DUMP}"
fi

echo "[3/3] Restoring into ${DST_HOST}:${DST_CONTAINER} inside a single atomic transaction..."
ssh -o BatchMode=yes "$DST_HOST" \
  "set -euo pipefail; DOCKER='docker'; docker ps >/dev/null 2>&1 || DOCKER='sudo docker'; { echo 'BEGIN;'; echo \"SET LOCAL session_replication_role = 'replica';\"; echo 'TRUNCATE TABLE ${TRUNCATE_LIST} RESTART IDENTITY CASCADE;'; gzip -dc '${REMOTE_DUMP}'; echo 'COMMIT;'; echo 'ANALYZE;'; } > '${REMOTE_SQL}'; \$DOCKER cp '${REMOTE_SQL}' '${DST_CONTAINER}:/tmp/cn-public-restore.sql'; \$DOCKER exec '${DST_CONTAINER}' psql -U '${DST_DB_USER}' -d '${DST_DB_NAME}' -v ON_ERROR_STOP=1 -f /tmp/cn-public-restore.sql >/dev/null; \$DOCKER exec '${DST_CONTAINER}' rm -f /tmp/cn-public-restore.sql; echo '      Restore complete. Target row counts:'; \$DOCKER exec '${DST_CONTAINER}' psql -U '${DST_DB_USER}' -d '${DST_DB_NAME}' -c \"SELECT relname AS table_name, n_live_tup AS est_rows FROM pg_stat_user_tables WHERE relname IN (${IN_CLAUSE}) ORDER BY relname;\""

echo "Done! Public read-only data synced cleanly to ${DST_HOST}."
