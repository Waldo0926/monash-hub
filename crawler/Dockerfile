# Crawler image: the API code plus a browser engine.
#
# www.monash.edu refuses plain HTTP clients, so the official-page crawler needs
# a real browser. The API image stays slim by keeping that dependency here - the
# web service should not be carrying 400MB of Chromium it never uses.
#
# Same Python as the API image, so the backend code the crawler imports runs
# on the version CI tests. Playwright installs its own Chromium below, so the
# playwright pin in crawler/requirements.txt does not wait for a prebuilt image.
FROM python:3.14-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

WORKDIR /srv

COPY backend/requirements.txt /srv/backend/requirements.txt
COPY crawler/requirements.txt /srv/crawler/requirements.txt
RUN pip install --no-cache-dir -r /srv/backend/requirements.txt \
 && pip install --no-cache-dir -r /srv/crawler/requirements.txt

# Chromium and the system libraries it needs, for exactly the playwright
# version pinned above. Only Chromium: the crawler never uses Firefox or WebKit.
RUN playwright install --with-deps chromium \
 && rm -rf /var/lib/apt/lists/*

# Translation models, baked in rather than downloaded per run: a `compose run`
# container is thrown away each time, so otherwise every batch would re-fetch a
# hundred megabytes before it could start.
ARG TRANSLATION_LOCALES="zh ja ko"
RUN TRANSLATION_LOCALES="$TRANSLATION_LOCALES" python - <<'PY'
import os
import argostranslate.package as package

package.update_package_index()
available = package.get_available_packages()
for locale in os.environ.get("TRANSLATION_LOCALES", "zh").split():
    match = [p for p in available if p.from_code == "en" and p.to_code == locale]
    if not match:
        raise SystemExit(f"no en->{locale} package in the Argos index")
    print(f"installing en->{locale}")
    package.install_from_path(match[0].download())
PY

COPY backend /srv/backend
COPY crawler /srv/crawler

ENV PYTHONPATH=/srv/backend:/srv

# The crawler has no listening port and is never reachable from the internet.
# It is started on demand, not as a long-running service.
CMD ["python", "-m", "crawler.handbook.run", "--fixtures"]
