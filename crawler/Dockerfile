# Crawler image: the API code plus a browser engine.
#
# www.monash.edu refuses plain HTTP clients, so the official-page crawler needs
# a real browser. The API image stays slim by keeping that dependency here - the
# web service should not be carrying 400MB of Chromium it never uses.
FROM mcr.microsoft.com/playwright/python:v1.56.0-noble

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_BREAK_SYSTEM_PACKAGES=1

WORKDIR /srv

COPY backend/requirements.txt /srv/backend/requirements.txt
COPY crawler/requirements.txt /srv/crawler/requirements.txt
RUN pip install --no-cache-dir -r /srv/backend/requirements.txt \
 && pip install --no-cache-dir -r /srv/crawler/requirements.txt

COPY backend /srv/backend
COPY crawler /srv/crawler

ENV PYTHONPATH=/srv/backend:/srv

# The crawler has no listening port and is never reachable from the internet.
# It is started on demand, not as a long-running service.
CMD ["python", "-m", "crawler.handbook.run", "--fixtures"]
