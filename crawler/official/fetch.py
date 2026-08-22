"""Fetching public monash.edu pages.

www.monash.edu is behind a WAF that scores the HTTP *client*, not the address:
plain httpx gets 403 where a real browser engine gets 200, from the same machine
in the same minute. So this fetcher starts on httpx and latches to a browser
engine the first time it is refused, then keeps using it for the rest of the run
rather than paying a failed request per page.

The rate limit does not change with the transport. One request at a time, a
multi-second gap between them, and a hard cap on retries - the point is to read
a few dozen public pages a day, not to be fast.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

import httpx

from crawler.throttling.limiter import Throttle

log = logging.getLogger(__name__)

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
)
BROWSER_TRANSPORT = "playwright"
HTTP_TRANSPORT = "httpx"


@dataclass(slots=True)
class PageResult:
    url: str
    status: int | None
    html: str | None
    transport: str
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.status == 200 and bool(self.html)


class OfficialFetcher:
    """Auto-switching fetcher. Use as a context manager."""

    def __init__(
        self,
        throttle: Throttle | None = None,
        *,
        transport: str = "auto",
        timeout: float = 45.0,
    ) -> None:
        self.throttle = throttle or Throttle()
        self.timeout = timeout
        self._mode = transport
        self._client: httpx.Client | None = None
        self._playwright = None
        self._browser = None
        self._page = None

    # -- transports ---------------------------------------------------------

    def _http(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(
                timeout=self.timeout,
                follow_redirects=True,
                headers={
                    "User-Agent": USER_AGENT,
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "en-AU,en;q=0.9",
                },
            )
        return self._client

    def _browser_page(self):
        if self._page is None:
            from playwright.sync_api import sync_playwright

            log.info("starting browser transport")
            self._playwright = sync_playwright().start()
            self._browser = self._playwright.chromium.launch()
            context = self._browser.new_context(user_agent=USER_AGENT, locale="en-AU")
            self._page = context.new_page()
            # Nothing here needs images or fonts, and not requesting them is
            # both faster and lighter on the origin.
            self._page.route(
                "**/*",
                lambda route: route.abort()
                if route.request.resource_type in {"image", "media", "font"}
                else route.continue_(),
            )
        return self._page

    # -- fetching -----------------------------------------------------------

    def fetch(self, url: str) -> PageResult:
        last: PageResult | None = None
        for attempt in range(1, self.throttle.limit.max_attempts + 1):
            self.throttle.wait()
            result = self._fetch_once(url)
            if result.ok or result.status == 404:
                return result
            last = result
            if result.status in (403, 429) and self._mode != BROWSER_TRANSPORT:
                # Latch, and let the next attempt use the browser. Switching on
                # the *next* attempt means the crawl delay is never spent twice.
                log.warning("HTTP %s on %s - switching to browser transport", result.status, url)
                self._mode = BROWSER_TRANSPORT
            if attempt < self.throttle.limit.max_attempts:
                self.throttle.backoff(attempt)
        return last or PageResult(url, None, None, self._mode, "no attempt made")

    def _fetch_once(self, url: str) -> PageResult:
        if self._mode == BROWSER_TRANSPORT:
            return self._fetch_browser(url)
        try:
            response = self._http().get(url)
        except httpx.HTTPError as exc:
            return PageResult(url, None, None, HTTP_TRANSPORT, f"{type(exc).__name__}: {exc}")
        if response.status_code == 200:
            return PageResult(url, 200, response.text, HTTP_TRANSPORT)
        return PageResult(url, response.status_code, None, HTTP_TRANSPORT,
                          f"HTTP {response.status_code}")

    def _fetch_browser(self, url: str) -> PageResult:
        try:
            page = self._browser_page()
            response = page.goto(url, wait_until="domcontentloaded", timeout=self.timeout * 1000)
        except Exception as exc:
            return PageResult(url, None, None, BROWSER_TRANSPORT, f"{type(exc).__name__}: {exc}")
        status = response.status if response else None
        if status != 200:
            return PageResult(url, status, None, BROWSER_TRANSPORT, f"HTTP {status}")
        return PageResult(url, 200, page.content(), BROWSER_TRANSPORT)

    # -- lifecycle ----------------------------------------------------------

    def close(self) -> None:
        if self._client is not None:
            self._client.close()
        if self._browser is not None:
            self._browser.close()
        if self._playwright is not None:
            self._playwright.stop()

    def __enter__(self) -> OfficialFetcher:
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()

    @property
    def transport(self) -> str:
        return self._mode
