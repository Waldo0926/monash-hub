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
# Measured on the eight-core VPS: `short` is about ten minutes, `all` about an
# hour and a half. Both are resumable - a unit whose English has not changed
# since it was last translated at the same `--fields` is skipped - so an
# interrupted pass is restarted by running the same command again.
#
# The pass gets more cores than a crawl does; see translate-resources.yml for
# what it is set to and why. TRANSLATE_CPUS overrides it.
set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-/opt/monash-hub/repo}"
cd "$PROJECT_DIR"
COMPOSE=(docker compose -f docker-compose.yml -f deployment/translate-resources.yml -p monash-hub)

locale="${1:-zh}"
fields="${2:-short}"
shift 2 2>/dev/null || true

"${COMPOSE[@]}" run --rm crawler \
  python -m crawler.translate.run --locale "$locale" --fields "$fields" "$@"

if [[ "$locale" == "zh" ]]; then
  # A translation is visible immediately on its page, but search reads the
  # indexed copy on units and guides. Refresh it here so a successful Chinese
  # translation pass can never leave search one version behind.
  "${COMPOSE[@]}" run --rm crawler python -m app.search.reindex_zh
fi
