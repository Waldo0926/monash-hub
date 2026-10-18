#!/usr/bin/env bash
#
# Smoke-check a running Monash Hub.
#
#   deployment/smoke.sh --base https://monashhub.secureview.tech [--commit <sha>]
#   deployment/smoke.sh --api http://127.0.0.1:8100 --web http://127.0.0.1:8101 [--commit <sha>]
#
# "The API answers /api/health" is not the same as "the site works". This asks
# what a visitor would: does the home page render, in English and in Chinese;
# does a unit page render with its data; does search answer; is the sitemap
# there; is a wrong URL a 404 rather than a 500. With --commit it also checks
# that what is running is the commit that was meant to be deployed, which is
# the one thing a green health check cannot say.
#
# Reads only. Data checks are skipped on an empty database (a first deploy).
# Exits 1 at the first failed check, with the response that failed it.
set -euo pipefail

API=""
WEB=""
EXPECTED_COMMIT=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --base) API="$2"; WEB="$2"; shift 2 ;;
    --api) API="$2"; shift 2 ;;
    --web) WEB="$2"; shift 2 ;;
    --commit) EXPECTED_COMMIT="$2"; shift 2 ;;
    *) echo "usage: $0 (--base URL | --api URL --web URL) [--commit SHA]" >&2; exit 2 ;;
  esac
done
if [[ -z "$API" || -z "$WEB" ]]; then
  echo "usage: $0 (--base URL | --api URL --web URL) [--commit SHA]" >&2
  exit 2
fi
API="${API%/}"
WEB="${WEB%/}"

BODY="$(mktemp)"
trap 'rm -f "$BODY"' EXIT
STATUS=""
failed=0

# fetch URL [curl args...]: body in $BODY, HTTP status in $STATUS. Transport
# errors count as status 000 so the check that follows reports them.
fetch() {
  local url="$1"; shift
  STATUS="$(curl -sS -o "$BODY" -w '%{http_code}' --max-time 30 \
    -H 'User-Agent: monash-hub-smoke' "$@" "$url" 2>>"$BODY" || true)"
}

pass() { echo "  ok    $1"; }
fail() {
  echo "  FAIL  $1" >&2
  echo "        status $STATUS, body starts: $(head -c 300 "$BODY" | tr '\n' ' ')" >&2
  failed=1
}

# json EXPR: evaluate a Python expression over the parsed body as `d`.
json() { python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); print(eval(sys.argv[2]))' "$BODY" "$1" 2>/dev/null; }

echo "Smoke-checking api=$API web=$WEB"

# --- API ------------------------------------------------------------------------
fetch "$API/api/health"
if [[ "$STATUS" == 200 && "$(json 'd["status"]')" == "ok" ]]; then
  pass "/api/health answers"
else
  fail "/api/health answers"; exit 1
fi
units="$(json 'd["data"]["units"]')"; units="${units:-0}"
pages="$(json 'd["data"]["official_pages_ok"]')"; pages="${pages:-0}"
commit="$(json 'd.get("commit") or ""')"
echo "        units=$units official_pages=$pages commit=${commit:-unknown}"

if [[ -n "$EXPECTED_COMMIT" ]]; then
  if [[ "$commit" == "$EXPECTED_COMMIT" ]]; then
    pass "running commit is $EXPECTED_COMMIT"
  else
    fail "running commit is $EXPECTED_COMMIT (health reports '${commit:-nothing}')"
  fi
fi

if [[ "$units" -gt 0 ]]; then
  fetch "$API/api/v1/units?limit=1"
  code="$(json 'd["results"][0].get("code") or d["results"][0].get("unit_code")')"
  if [[ "$STATUS" == 200 && -n "$code" ]]; then
    pass "unit search returns a unit ($code)"
  else
    fail "unit search returns a unit"; code=""
  fi

  fetch "$API/api/v1/units/$code/tree"
  if [[ -n "$code" && "$STATUS" == 200 ]]; then pass "unit tree answers for $code"; else fail "unit tree answers for $code"; fi
else
  echo "  skip  unit checks: the database has no units yet"
  code=""
fi

if [[ -n "$code" ]]; then
  # The exact-code shortcut: a unit the API just listed must be findable.
  fetch "$API/api/v1/search?q=$code"
  if [[ "$STATUS" == 200 && "$(json 'sum(g["total"] for g in d["groups"]) > 0')" == "True" ]]; then
    pass "search for $code finds it"
  else
    fail "search for $code finds it"
  fi
fi

# --- Web --------------------------------------------------------------------------
fetch "$WEB/"
if [[ "$STATUS" == 200 ]] && grep -q 'Monash Hub' "$BODY" && grep -Eq '<html[^>]*lang="en"' "$BODY"; then
  pass "home page renders in English"
else
  fail "home page renders in English"
fi

fetch "$WEB/" -H 'Cookie: mh_locale=zh'
if [[ "$STATUS" == 200 ]] && grep -Eq '<html[^>]*lang="zh-Hans"' "$BODY"; then
  pass "home page renders in Chinese for the zh cookie"
else
  fail "home page renders in Chinese for the zh cookie"
fi

if [[ -n "$code" ]]; then
  fetch "$WEB/units/$code"
  if [[ "$STATUS" == 200 ]] && grep -q "$code" "$BODY"; then
    pass "unit page /units/$code renders"
  else
    fail "unit page /units/$code renders"
  fi
fi

fetch "$WEB/units/ZZZ9999"
if [[ "$STATUS" == 404 ]]; then pass "a unit that does not exist is a 404"; else fail "a unit that does not exist is a 404"; fi

fetch "$WEB/no-such-page-smoke"
if [[ "$STATUS" == 404 ]]; then pass "a path that does not exist is a 404"; else fail "a path that does not exist is a 404"; fi

fetch "$WEB/robots.txt"
if [[ "$STATUS" == 200 ]] && grep -q '^Sitemap:' "$BODY"; then pass "robots.txt names the sitemap"; else fail "robots.txt names the sitemap"; fi

fetch "$WEB/sitemap.xml"
locs="$(grep -o '<loc>' "$BODY" | wc -l | tr -d ' ')"
if [[ "$STATUS" == 200 ]] && grep -q '<urlset' "$BODY" && { [[ "$units" -eq 0 ]] || [[ "$locs" -gt 0 ]]; }; then
  pass "sitemap.xml lists $locs URLs"
else
  fail "sitemap.xml lists URLs"
fi

if [[ $failed -ne 0 ]]; then
  echo "Smoke check failed." >&2
  exit 1
fi
echo "Smoke check passed."
