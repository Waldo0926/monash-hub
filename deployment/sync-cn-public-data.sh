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
#   3. Compresses with xz and audits the dump locally before upload to guarantee
#      zero forbidden tables.
#   4. Uploads to DST_HOST:/tmp via parallel 1MB scp chunks (resilient to cross-border
#      packet loss), verifies SHA256 on DST_HOST, and restores inside a single atomic
#      transaction followed by ANALYZE.
#
# Usage:
#   deployment/sync-cn-public-data.sh
#   PARALLEL_CHUNKS=8 deployment/sync-cn-public-data.sh

set -euo pipefail

SRC_HOST="${SRC_HOST:-mcs21-vps}"
SRC_CONTAINER="${SRC_CONTAINER:-monash-hub-postgres-1}"
SRC_DB_USER="${SRC_DB_USER:-monashhub}"
SRC_DB_NAME="${SRC_DB_NAME:-monashhub}"

DST_HOST="${DST_HOST:-vps}"
DST_CONTAINER="${DST_CONTAINER:-monash-hub-cn-postgres-1}"
DST_DB_USER="${DST_DB_USER:-monashhub_cn}"
DST_DB_NAME="${DST_DB_NAME:-monashhub_cn}"

PARALLEL_CHUNKS="${PARALLEL_CHUNKS:-8}"
CHUNK_SIZE="${CHUNK_SIZE:-1m}"

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
LOCAL_DUMP="/tmp/monash-hub-cn-public-${STAMP}.sql.xz"
LOCAL_CHUNKS="/tmp/monash-hub-cn-chunks-${STAMP}"
REMOTE_CHUNKS="/tmp/monash-hub-cn-chunks-${STAMP}"
REMOTE_DUMP="/tmp/monash-hub-cn-public-${STAMP}.sql.xz"
REMOTE_SQL="/tmp/monash-hub-cn-restore-${STAMP}.sql"

cleanup() {
  rm -rf "$LOCAL_DUMP" "$LOCAL_CHUNKS"
  ssh -o BatchMode=yes "$DST_HOST" "rm -rf '$REMOTE_CHUNKS' '$REMOTE_DUMP' '$REMOTE_SQL'" >/dev/null 2>&1 || true
}
trap cleanup EXIT

TABLE_FLAGS=()
for tbl in "${PUBLIC_TABLES[@]}"; do
  TABLE_FLAGS+=(--table="public.${tbl}")
done

FORBIDDEN_REGEX="^(COPY|INSERT INTO) (public\.)?($(IFS='|'; echo "${FORBIDDEN_TABLES[*]}"))\\b"
TRUNCATE_LIST="$(IFS=,; echo "${PUBLIC_TABLES[*]}")"
IN_CLAUSE="$(printf "'%s'," "${PUBLIC_TABLES[@]}" | sed 's/,$//')"

echo "[1/4] Read-only pg_dump of ${#PUBLIC_TABLES[@]} public tables from ${SRC_HOST}:${SRC_CONTAINER} (xz compressed)..."
ssh -o BatchMode=yes "$SRC_HOST" \
  "docker exec ${SRC_CONTAINER} pg_dump -U ${SRC_DB_USER} -d ${SRC_DB_NAME} --data-only --no-owner --no-privileges ${TABLE_FLAGS[*]} | gzip -1" \
  | gzip -dc | xz -T0 -6 > "$LOCAL_DUMP"

DUMP_SIZE="$(du -h "$LOCAL_DUMP" | awk '{print $1}')"
EXPECTED_SHA="$(shasum -a 256 "$LOCAL_DUMP" | awk '{print $1}')"
echo "      Exported ${LOCAL_DUMP} (${DUMP_SIZE}, SHA256=${EXPECTED_SHA})"

echo "[2/4] Auditing dump locally to verify zero private/UGC tables are present..."
if xz -dc "$LOCAL_DUMP" | grep -qE "$FORBIDDEN_REGEX"; then
  echo "ERROR: Audit failed! Forbidden table detected in dump. Aborting." >&2
  exit 1
fi
echo "      Audit passed: only whitelisted public tables present."

echo "[3/4] Uploading ${DUMP_SIZE} to ${DST_HOST} in ${CHUNK_SIZE} parallel chunks (-P ${PARALLEL_CHUNKS})..."
mkdir -p "$LOCAL_CHUNKS"
split -b "$CHUNK_SIZE" -a 3 "$LOCAL_DUMP" "${LOCAL_CHUNKS}/part-"
TOTAL_CHUNKS="$(find "$LOCAL_CHUNKS" -maxdepth 1 -name 'part-*' | wc -l | tr -d ' ')"
ssh -o BatchMode=yes "$DST_HOST" "rm -rf '${REMOTE_CHUNKS}' && mkdir -p '${REMOTE_CHUNKS}'"

START_TS="$(date +%s)"
find "$LOCAL_CHUNKS" -maxdepth 1 -name 'part-*' | sort | xargs -n 1 -P "$PARALLEL_CHUNKS" bash -c '
  dst_host="$1"
  remote_dir="$2"
  f="$3"
  base="$(basename "$f")"
  for attempt in 1 2 3 4; do
    if scp -q -o BatchMode=yes -o ConnectTimeout=15 -o ServerAliveInterval=10 -o ServerAliveCountMax=3 "$f" "${dst_host}:${remote_dir}/${base}"; then
      exit 0
    fi
    sleep 2
  done
  echo "FAILED chunk: ${base}" >&2
  exit 1
' _ "$DST_HOST" "$REMOTE_CHUNKS"
END_TS="$(date +%s)"
echo "      Uploaded ${TOTAL_CHUNKS} chunks in $((END_TS - START_TS))s."

echo "[4/4] Verifying SHA256 and restoring into ${DST_HOST}:${DST_CONTAINER} atomically..."
ssh -o BatchMode=yes "$DST_HOST" "set -euo pipefail
DOCKER='docker'
docker ps >/dev/null 2>&1 || DOCKER='sudo docker'
cat '${REMOTE_CHUNKS}'/part-* > '${REMOTE_DUMP}'
rm -rf '${REMOTE_CHUNKS}'
GOT_SHA=\$(sha256sum '${REMOTE_DUMP}' | awk '{print \$1}')
if [ \"\$GOT_SHA\" != \"${EXPECTED_SHA}\" ]; then
  echo \"ERROR: SHA256 mismatch on target (\$GOT_SHA != ${EXPECTED_SHA})\" >&2
  exit 1
fi
{
  echo 'BEGIN;'
  echo \"SET LOCAL session_replication_role = 'replica';\"
  echo 'TRUNCATE TABLE ${TRUNCATE_LIST} RESTART IDENTITY CASCADE;'
  xz -dc '${REMOTE_DUMP}'
  echo 'COMMIT;'
  echo 'ANALYZE;'
} > '${REMOTE_SQL}'
\$DOCKER cp '${REMOTE_SQL}' '${DST_CONTAINER}:/tmp/cn-public-restore.sql'
\$DOCKER exec '${DST_CONTAINER}' psql -U '${DST_DB_USER}' -d '${DST_DB_NAME}' -v ON_ERROR_STOP=1 -f /tmp/cn-public-restore.sql >/dev/null
\$DOCKER exec '${DST_CONTAINER}' rm -f /tmp/cn-public-restore.sql
echo '      Restore complete. Target row counts:'
\$DOCKER exec '${DST_CONTAINER}' psql -U '${DST_DB_USER}' -d '${DST_DB_NAME}' -c \"SELECT relname AS table_name, n_live_tup AS est_rows FROM pg_stat_user_tables WHERE relname IN (${IN_CLAUSE}) ORDER BY relname;\"
"

echo "Done! Public read-only data synced cleanly to ${DST_HOST}."
