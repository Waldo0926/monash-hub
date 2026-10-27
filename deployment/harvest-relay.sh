#!/usr/bin/env bash
#
# Read the due official pages on a machine Monash answers and store them on the
# server. For a home machine, with OFFICIAL_FETCH=harvest set on the server.
#
#   SERVER=my-vps deployment/harvest-relay.sh
#
# Run daily by deployment/systemd/monash-hub-harvest.timer, settings in
# /etc/monash-hub-harvest.env (see the service file). For each host:
#
#   1. ask the server which pages are due (crawl.sh official-due)
#   2. read only those, with the same fetcher and robots rules as the server
#   3. copy the file over and store it (crawl.sh official-harvest)
#
# The server keeps the refresh tiers, so this asks Monash for what a crawl on
# the server would have asked for, not every page every day. A host whose read
# or store fails is retried the next day; the server mails once nothing has
# been stored for OFFICIAL_HARVEST_MAX_HOURS.
set -euo pipefail

SERVER="${SERVER:?SERVER must be the ssh host of the Monash Hub server}"
SERVER_REPO="${SERVER_REPO:-/opt/monash-hub/repo}"
SERVER_DIR="${SERVER_DIR:-/opt/monash-hub/harvest}"
WORK_DIR="${WORK_DIR:-/data/monash-hub-harvest}"
REPO_DIR="${REPO_DIR:-$WORK_DIR/repo}"
VENV="${VENV:-$WORK_DIR/venv}"
HOSTS="${HOSTS:-www.monash.edu www.monash.edu.my}"
KEEP_DAYS="${KEEP_DAYS:-7}"
export PLAYWRIGHT_BROWSERS_PATH="${PLAYWRIGHT_BROWSERS_PATH:-$WORK_DIR/ms-playwright}"

mkdir -p "$WORK_DIR/out"
exec 9>"$WORK_DIR/relay.lock"
if ! flock -n 9; then
  echo "a harvest is already running; skipping this one"
  exit 0
fi

# The seed list has to be the server's, or slugs it asks for are unknown here.
git -C "$REPO_DIR" pull -q --ff-only
cd "$REPO_DIR"

# Only what the harvest imports, at the versions the server pins. The
# translation model in crawler/requirements.txt is not needed to read pages.
"$VENV/bin/pip" install -q \
  $(grep -E '^(beautifulsoup4|lxml|httpx)==' backend/requirements.txt) \
  $(grep -E '^playwright==' crawler/requirements.txt)
"$VENV/bin/python" -m playwright install chromium

stamp="$(date +%F)"
failed=0

relay() {
  local host="$1" slugs file
  slugs="$(ssh "$SERVER" "$SERVER_REPO/deployment/crawl.sh official-due $host" | tail -1)"
  if [[ -z "$slugs" ]]; then
    echo "$host: nothing is due"
    return 0
  fi
  echo "$host: $(tr ',' '\n' <<<"$slugs" | wc -l) pages due"
  file="$WORK_DIR/out/$host-$stamp.jsonl.gz"
  # Resumes the file if today's run was stopped part way.
  "$VENV/bin/python" -m crawler.official.harvest --host "$host" --out "$file" --slugs "$slugs"
  ssh "$SERVER" "mkdir -p $SERVER_DIR"
  scp -q "$file" "$SERVER:$SERVER_DIR/"
  ssh "$SERVER" "$SERVER_REPO/deployment/crawl.sh official-harvest $SERVER_DIR/$(basename "$file")"
  echo "$host: stored"
}

# One host each: the throttle is per host, and the two sites do not share one.
pids=()
for host in $HOSTS; do
  relay "$host" > >(sed -u "s/^/[$host] /") 2>&1 &
  pids+=("$!")
done
for pid in "${pids[@]}"; do
  wait "$pid" || failed=1
done

find "$WORK_DIR/out" -name '*.jsonl.gz' -mtime +"$KEEP_DAYS" -delete
ssh "$SERVER" "find $SERVER_DIR -name '*.jsonl.gz' -mtime +$KEEP_DAYS -delete" || true
exit "$failed"
