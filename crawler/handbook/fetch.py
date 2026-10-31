"""Fetch Handbook unit pages.

handbook.monash.edu serves plain HTTP clients without complaint, so this is
httpx and nothing heavier. The parser reads the embedded JSON, so we ask for the
page exactly as a reader would and take what comes back.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

import httpx

from crawler.official.fetch import Robots
from crawler.response import html_error, is_html, retry_after
from crawler.throttling.limiter import USER_AGENT, Throttle

log = logging.getLogger(__name__)

__all__ = ["USER_AGENT", "FetchResult", "HandbookFetcher"]


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
            follow_redirects=False,
            headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"},
        )
        self.robots = Robots(self._robots_text)

    def _robots_text(self, url: str) -> tuple[int, str]:
        self.throttle.wait()
        response = self._client.get(url)
        return response.status_code, response.text

    def fetch(self, url: str) -> FetchResult:
        if not self.robots.allowed(url):
            return FetchResult(url, None, None, self.robots.denial_reason(url))
        last_error: str | None = None
        last_status: int | None = None
        for attempt in range(1, self.throttle.limit.max_attempts + 1):
            self.throttle.wait()
            pause = 0.0
            try:
                with self._client.stream("GET", url) as response:
                    last_status = response.status_code
                    if response.status_code == 200:
                        if not is_html(response.headers.get("content-type", "")):
                            return FetchResult(url, 200, None, "non-HTML response")
                        response.read()
                        if error := html_error(response.text):
                            return FetchResult(url, 200, None, error)
                        return FetchResult(url=url, status=200, html=response.text)
                    if response.status_code == 404:
                        return FetchResult(url=url, status=404, html=None, error="not found")
                    if response.is_redirect:
                        return FetchResult(url, response.status_code, None,
                                           "unexpected Handbook item redirect")
                    last_error = f"HTTP {response.status_code}"
                    pause = retry_after(response.headers.get("retry-after")) or 0.0
            except httpx.HTTPError as exc:
                last_error = f"{type(exc).__name__}: {exc}"
                log.warning("fetch failed (%s): %s", url, last_error)
            if attempt < self.throttle.limit.max_attempts:
                self.throttle.backoff(attempt, at_least=pause)
        return FetchResult(url=url, status=last_status, html=None, error=last_error)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> HandbookFetcher:
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()
