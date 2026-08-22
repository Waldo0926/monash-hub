"""Fetch Handbook unit pages.

handbook.monash.edu serves plain HTTP clients without complaint, so this is
httpx and nothing heavier. The parser reads the embedded JSON, so we ask for the
page exactly as a reader would and take what comes back.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

import httpx

from crawler.throttling.limiter import Throttle

log = logging.getLogger(__name__)

USER_AGENT = (
    "MonashHubBot/0.1 (+https://monashhub.secureview.tech; student information index)"
)


@dataclass(slots=True)
class FetchResult:
    url: str
    status: int | None
    html: str | None
    error: str | None = None
    transport: str = "httpx"

    @property
    def ok(self) -> bool:
        return self.status == 200 and bool(self.html)


class HandbookFetcher:
    def __init__(self, throttle: Throttle | None = None, timeout: float = 30.0) -> None:
        self.throttle = throttle or Throttle()
        self._client = httpx.Client(
            timeout=timeout,
            follow_redirects=True,
            headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"},
        )

    def fetch(self, url: str) -> FetchResult:
        last_error: str | None = None
        for attempt in range(1, self.throttle.limit.max_attempts + 1):
            self.throttle.wait()
            try:
                response = self._client.get(url)
            except httpx.HTTPError as exc:
                last_error = f"{type(exc).__name__}: {exc}"
                log.warning("fetch failed (%s): %s", url, last_error)
            else:
                if response.status_code == 200:
                    return FetchResult(url=url, status=200, html=response.text)
                if response.status_code == 404:
                    # A missing unit is an answer, not a failure to retry.
                    return FetchResult(url=url, status=404, html=None, error="not found")
                last_error = f"HTTP {response.status_code}"
                log.warning("fetch returned %s for %s", response.status_code, url)
            if attempt < self.throttle.limit.max_attempts:
                self.throttle.backoff(attempt)
        return FetchResult(url=url, status=None, html=None, error=last_error)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> HandbookFetcher:
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()
