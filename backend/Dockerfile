# API image. Also used by the crawler service, which runs the same code with a
# different command - see crawler/Dockerfile for the browser-enabled variant.
FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /srv

COPY backend/requirements.txt /srv/backend/requirements.txt
RUN pip install --no-cache-dir -r /srv/backend/requirements.txt

COPY backend /srv/backend
COPY crawler /srv/crawler

# Both packages are importable: the crawler reads the parsers and models that
# live in the backend app.
ENV PYTHONPATH=/srv/backend:/srv

WORKDIR /srv/backend

# Runs unprivileged. Nothing here needs to write to the image.
RUN useradd --system --create-home --uid 10001 monashhub && chown -R monashhub /srv
USER monashhub

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=4).status == 200 else 1)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*"]
