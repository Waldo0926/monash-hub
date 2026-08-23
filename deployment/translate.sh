#!/usr/bin/env bash
#
# Machine-translate the stored content.
#
#   deployment/translate.sh zh short     # titles and the enumerable values
#   deployment/translate.sh zh all       # adds overviews, outcomes, workload
#   deployment/translate.sh ja short
#
# Everything it writes is marked as machine-written. A hand-written translation
# for the same target always wins on read, so this can be re-run safely and
# translating a page properly later simply takes over.
#
# `short` is minutes; `all` is roughly half an hour for a full year of units.
# Both are resumable - a unit whose English has not changed is skipped.
set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-/opt/monash-hub/repo}"
cd "$PROJECT_DIR"
COMPOSE=(docker compose -p monash-hub)

locale="${1:-zh}"
fields="${2:-short}"
shift 2 2>/dev/null || true

"${COMPOSE[@]}" run --rm crawler \
  python -m crawler.translate.run --locale "$locale" --fields "$fields" "$@"
