#!/usr/bin/env bash
# Repeatable, read-only public data sync from overseas PostgreSQL (mcs21-vps)
# to China mainland PostgreSQL (vps / monash-hub-cn).
#
# Safety guarantees:
#   1. Strictly READ-ONLY on SRC_HOST (mcs21-vps): executes only `pg_dump --data-only`
#      against an explicit whitelist of public business tables. Never modifies or
#      restarts anything on the overseas host.
#   2. Never exports users, auth/verification/throttle records, notifications,
#      community posts/answers/votes/bookmarks/reports, unit_reviews, search_terms,
#      crawl_history, source_change_events, avatars, tokens, secrets or .env files.
#   3. Transfers via local temp file + `scp` to `/tmp` on DST_HOST (no remote shell
#      piping of source code), then restores inside a single atomic transaction on
#      the target database followed by ANALYZE.
#
# Usage:
#   deployment/sync-cn-public-data.sh
#   SRC_HOST=mcs21-vps DST_HOST=vps deployment/sync-cn-public-data.sh

set -euo pipefail

SRC_HOST="${SRC_HOST:-mcs21-vps}"
SRC_CONTAINER="${SRC_CONTAINER:-monash-hub-postgres-1}"
SRC_DB_USER="${SRC_DB_USER:-monashhub}"
SRC_DB_NAME="${SRC_DB_NAME:-monashhub}"

DST_HOST="${DST_HOST:-vps}"
DST_CONTAINER="${DST_CONTAINER:-monash-hub-cn-postgres-1}"
DST_DB_USER="${DST_DB_USER:-monashhub_cn}"
DST_DB_NAME="${DST_DB_NAME:-monashhub_cn}"

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

echo "[1/4] Read-only pg_dump of ${#PUBLIC_TABLES[@]} public tables from ${SRC_HOST}:${SRC_CONTAINER}..."
ssh -o BatchMode=yes "$SRC_HOST" \
  "docker exec ${SRC_CONTAINER} pg_dump -U ${SRC_DB_USER} -d ${SRC_DB_NAME} --data-only --no-owner --no-privileges ${TABLE_FLAGS[*]}" \
  | gzip -c > "$LOCAL_DUMP"

DUMP_SIZE="$(du -h "$LOCAL_DUMP" | awk '{print $1}')"
echo "      Exported compressed dump: ${LOCAL_DUMP} (${DUMP_SIZE})"

echo "[2/4] Auditing dump to verify zero private/UGC tables are present..."
for bad in "${FORBIDDEN_TABLES[@]}"; do
  if gzip -dc "$LOCAL_DUMP" | grep -qE "^(COPY|INSERT INTO) (public\.)?${bad}\b"; then
    echo "ERROR: Audit failed! Forbidden table '${bad}' detected in dump. Aborting." >&2
    exit 1
  fi
done
echo "      Audit passed: only whitelisted public tables present."

echo "[3/4] Uploading dump to ${DST_HOST}:${REMOTE_DUMP}..."
scp -q "$LOCAL_DUMP" "${DST_HOST}:${REMOTE_DUMP}"

TRUNCATE_LIST="$(IFS=,; echo "${PUBLIC_TABLES[*]}")"
IN_CLAUSE="$(printf "'%s'," "${PUBLIC_TABLES[@]}" | sed 's/,$//')"

echo "[4/4] Restoring into ${DST_HOST}:${DST_CONTAINER} inside a single atomic transaction..."
ssh -o BatchMode=yes "$DST_HOST" \
  "set -euo pipefail; { echo 'BEGIN;'; echo \"SET LOCAL session_replication_role = 'replica';\"; echo 'TRUNCATE TABLE ${TRUNCATE_LIST} RESTART IDENTITY CASCADE;'; gzip -dc '${REMOTE_DUMP}'; echo 'COMMIT;'; echo 'ANALYZE;'; } > '${REMOTE_SQL}'; docker cp '${REMOTE_SQL}' '${DST_CONTAINER}:/tmp/cn-public-restore.sql'; docker exec '${DST_CONTAINER}' psql -U '${DST_DB_USER}' -d '${DST_DB_NAME}' -v ON_ERROR_STOP=1 -f /tmp/cn-public-restore.sql >/dev/null; docker exec '${DST_CONTAINER}' rm -f /tmp/cn-public-restore.sql; echo '      Restore complete. Target row counts:'; docker exec '${DST_CONTAINER}' psql -U '${DST_DB_USER}' -d '${DST_DB_NAME}' -c \"SELECT relname AS table_name, n_live_tup AS est_rows FROM pg_stat_user_tables WHERE relname IN (${IN_CLAUSE}) ORDER BY relname;\""

echo "Done! Public read-only data synced cleanly to ${DST_HOST}."
