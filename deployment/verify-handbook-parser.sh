#!/usr/bin/env bash
#
# Re-fetch two units whose Handbook pages exposed parser bugs in September
# 2026, assert the live API now parses them correctly, and start the full
# 2026 requisite audit if it has not completed.
#
#   /opt/monash-hub/repo/deployment/verify-handbook-parser.sh
#
# This used to run inside deploy.sh on every deploy. It is a repair for one
# year's data and a regression check that the parser's unit tests now cover
# (backend/tests/test_handbook_parser.py), so it is a tool to run by hand
# after a parser change, not a gate every release has to pass.
set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-/opt/monash-hub/repo}"
COMPOSE=(docker compose -p monash-hub)
YEAR="${HANDBOOK_YEAR:-2026}"

cd "$PROJECT_DIR"
api_port="$(sed -n 's/^API_PORT=//p' .env | tail -1)"
api_port="${api_port:-8100}"

# MTH2051: the parser gap that dropped MTH2010 from its prerequisites.
echo "==> Refreshing and verifying MTH2051 prerequisite data"
"${COMPOSE[@]}" run --rm crawler \
  python -m crawler.handbook.run --units MTH2051 --year "$YEAR" --min-interval 1 --fail-on-errors \
  || echo "warning: could not refresh MTH2051 from the Handbook; checking the stored data" >&2
mth2051_tree="$(curl -fsS \
  "http://127.0.0.1:${api_port}/api/v1/units/MTH2051/tree?direction=upstream&depth=1&campus=Malaysia")"
if ! grep -q '"MTH2010"' <<<"$mth2051_tree"; then
  echo "error: MTH2051's live prerequisite graph still lacks MTH2010" >&2
  echo "$mth2051_tree" >&2
  exit 1
fi
echo "    MTH2051 prerequisite graph verified"

# FIT1055: the enrolment_rules metadata leak that made the unit prohibit itself.
echo "==> Refreshing and verifying FIT1055 prerequisite data"
"${COMPOSE[@]}" run --rm crawler \
  python -m crawler.handbook.run --units FIT1055 --year "$YEAR" --min-interval 1 --fail-on-errors \
  || echo "warning: could not refresh FIT1055 from the Handbook; checking the stored data" >&2
fit1055_requisites="$(curl -fsS \
  "http://127.0.0.1:${api_port}/api/v1/units/FIT1055/requisites")"
# "unit_code": "FIT1055" always appears in this payload; only a requisite
# item's own "code" field naming FIT1055 is the self-reference bug.
if grep -Eq '"code": *"FIT1055"' <<<"$fit1055_requisites"; then
  echo "error: FIT1055 still lists itself as a requisite/prohibition" >&2
  echo "$fit1055_requisites" >&2
  exit 1
fi
echo "    FIT1055 prerequisite graph verified"

# The full pass over every unit, rate limited and therefore hours long, runs
# in the background. The helper is locked, versioned and resumable, and
# writes its done marker only after a clean pass; it knows its own version.
log_dir="/opt/monash-hub/logs"
mkdir -p "$log_dir"
requisite_log="$log_dir/handbook-requisites-$(date -u +%Y%m%d).log"
nohup bash "$PROJECT_DIR/deployment/refresh-handbook-requisites.sh" \
  >"$requisite_log" 2>&1 < /dev/null &
echo "==> Full $YEAR Handbook requisite audit started or confirmed done (pid $!, log: $requisite_log)"
