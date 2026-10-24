"""Fetching public monash.edu pages.

The crawler identifies itself (``MonashHubBot``, with the site's address) on
every request and reads ``robots.txt`` before the first page of a host. A
path the file disallows is not fetched, and is recorded as such.

www.monash.edu renders some pages client side, so a plain HTTP fetch of those
is a shell. The fetcher starts on httpx and, in ``auto`` mode, moves to a
browser engine the first time a page is refused, then stays there for the
rest of the run. The browser sends the same User-Agent. A 429 is not a reason
to change transport: it means slower, so the fetcher waits for as long as
``Retry-After`` says and tries the same way again.

The rate limit does not change with the transport. One request at a time, a
multi-second gap between them, and a hard cap on retries. The point is to read
a few dozen public pages a day, not to be fast.
"""
from __future__ import annotations

import logging
import urllib.robotparser
from dataclasses import dataclass
from urllib.parse import urljoin, urlsplit, urlunsplit

import httpx

from crawler.response import html_error, is_html, retry_after
from crawler.throttling.limiter import USER_AGENT, Throttle

log = logging.getLogger(__name__)

BROWSER_TRANSPORT = "playwright"
HTTP_TRANSPORT = "httpx"
AUTO_TRANSPORT = "auto"


@dataclass(slots=True)
class PageResult:
    url: str
    status: int | None
    html: str | None
    transport: str
    error: str | None = None
    #: Seconds the server asked us to wait, when it said.
    retry_after: float | None = None
    final_url: str | None = None

    @property
    def ok(self) -> bool:
        return self.status == 200 and bool(self.html)


def redirected_up(requested: str, final: str | None) -> bool:
    """True when a page now redirects to the section above it, or the home page.

    That is what Monash does with a page it has removed or merged, and the
    section page reads fine and is long enough, so storing it would quietly
    answer this seed's questions with a landing page. A page that moved
    sideways (``/old`` to ``/new/page``) is still followed. The host, a www
    prefix, a trailing slash or index.html, the query and case are ignored.
    """
    if not final:
        return False

    def path(url: str) -> str:
        return urlsplit(url).path.lower().removesuffix("index.html").rstrip("/")

    asked, landed = path(requested), path(final)
    return landed != asked and (landed == "" or asked.startswith(landed + "/"))


class Robots:
    """One ``robots.txt`` per host, read once, with the crawler's own name."""

    def __init__(self, fetch_text) -> None:
        self._fetch_text = fetch_text
        self._parsers: dict[str, urllib.robotparser.RobotFileParser | None] = {}

    def allowed(self, url: str) -> bool:
        parts = urlsplit(url)
        host = f"{parts.scheme}://{parts.netloc}"
        if host not in self._parsers:
            self._parsers[host] = self._load(host)
        parser = self._parsers[host]
        if parser is None:
            return False
        return parser.can_fetch(USER_AGENT.split("/")[0], url)

    def _load(self, host: str):
        parts = urlsplit(host)
        robots_url = urlunsplit((parts.scheme, parts.netloc, "/robots.txt", "", ""))
        try:
            status, text = self._fetch_text(robots_url)
        except Exception as exc:  # any failure at all is "could not read it"
            log.warning("%s: could not be read (%s); treating the host as closed", robots_url, exc)
            return None
        parser = urllib.robotparser.RobotFileParser()
        if status == 200:
            if text.lstrip().startswith("<"):
                log.warning("%s returned HTML instead of robots rules; treating host as closed",
                            robots_url)
                return None
            parser.parse(text.splitlines())
        elif status in (404, 410):
            parser.parse([])
        else:
            log.warning("%s answered HTTP %s; treating the host as closed", robots_url, status)
            return None
        return parser

    def denial_reason(self, url: str) -> str:
        parts = urlsplit(url)
        if self._parsers.get(f"{parts.scheme}://{parts.netloc}") is None:
            return "robots.txt unavailable - crawl permission unknown"
        return "disallowed by robots.txt"


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
        self._requested = transport
        self._mode = BROWSER_TRANSPORT if transport == BROWSER_TRANSPORT else HTTP_TRANSPORT
        self.robots = Robots(self._robots_text)
        self._client: httpx.Client | None = None
        self._playwright = None
        self._browser = None
        self._page = None

    # -- transports ---------------------------------------------------------

    def _http(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(
                timeout=self.timeout,
                follow_redirects=False,
                headers={
                    "User-Agent": USER_AGENT,
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "en-AU,en;q=0.9",
                },
            )
        return self._client

    def _robots_text(self, url: str) -> tuple[int, str]:
        self.throttle.wait()
        if self._mode == BROWSER_TRANSPORT:
            return self._robots_browser(url)
        response = self._http().get(url)
        if response.status_code == 403 and self._requested == AUTO_TRANSPORT:
            # The WAF that refuses httpx a page refuses it robots.txt too, and
            # that says nothing about the rules. Treating it as a closed host
            # stopped every monash.edu.my page from being read. Ask again the
            # way the pages would be read; a refusal there still closes it.
            log.warning("%s refused over httpx - reading it with the browser", url)
            self._mode = BROWSER_TRANSPORT
            self.throttle.wait()
            return self._robots_browser(url)
        return response.status_code, response.text

    def _robots_browser(self, url: str) -> tuple[int, str]:
        response = self._browser_page().goto(url, wait_until="domcontentloaded",
                                             timeout=self.timeout * 1000)
        if response is None:
            raise RuntimeError("no response")
        # The response body, not the page: Chromium wraps a text file in HTML.
        return response.status, response.text() if response.status == 200 else ""

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
        if not self.robots.allowed(url):
            reason = self.robots.denial_reason(url)
            log.info("%s: %s, not fetched", url, reason)
            return PageResult(url, None, None, self._mode, reason)
        last: PageResult | None = None
        for attempt in range(1, self.throttle.limit.max_attempts + 1):
            self.throttle.wait()
            result = self._fetch_once(url)
            if result.ok and redirected_up(url, result.final_url):
                # Keep the last copy and let a person update the seed.
                log.warning("%s redirected to %s, not stored", url, result.final_url)
                return PageResult(url, result.status, None, result.transport,
                                  f"redirected to {result.final_url}",
                                  final_url=result.final_url)
            if result.ok or result.status == 404:
                return result
            last = result
            if (result.status == 403 and self._mode == HTTP_TRANSPORT
                    and self._requested == AUTO_TRANSPORT):
                # Latch, and let the next attempt use the browser. Switching on
                # the *next* attempt means the crawl delay is never spent twice.
                log.warning("HTTP 403 on %s - switching to browser transport", url)
                self._mode = BROWSER_TRANSPORT
            if attempt < self.throttle.limit.max_attempts:
                self.throttle.backoff(attempt, at_least=result.retry_after or 0.0)
        return last or PageResult(url, None, None, self._mode, "no attempt made")

    def _fetch_once(self, url: str) -> PageResult:
        if self._mode == BROWSER_TRANSPORT:
            return self._fetch_browser(url)
        current = url
        try:
            for _ in range(6):
                with self._http().stream("GET", current) as response:
                    status = response.status_code
                    if response.is_redirect:
                        target = urljoin(current, response.headers.get("location", ""))
                        if not _allowed_redirect(url, target) or not self.robots.allowed(target):
                            return PageResult(url, status, None, HTTP_TRANSPORT,
                                              "redirect outside approved public pages")
                        current = target
                    elif status == 200:
                        if not is_html(response.headers.get("content-type", "")):
                            return PageResult(url, status, None, HTTP_TRANSPORT,
                                              "non-HTML response, kept as link only")
                        response.read()
                        html = response.text
                        error = html_error(html)
                        return PageResult(url, status, None if error else html, HTTP_TRANSPORT,
                                          error, final_url=current)
                    else:
                        return PageResult(url, status, None, HTTP_TRANSPORT, f"HTTP {status}",
                                          retry_after=retry_after(response.headers.get("retry-after")))
                self.throttle.wait()
        except httpx.HTTPError as exc:
            return PageResult(url, None, None, HTTP_TRANSPORT, f"{type(exc).__name__}: {exc}")
        return PageResult(url, None, None, HTTP_TRANSPORT, "too many redirects")

    def _fetch_browser(self, url: str) -> PageResult:
        try:
            page = self._browser_page()
            response = page.goto(url, wait_until="domcontentloaded", timeout=self.timeout * 1000)
        except Exception as exc:
            return PageResult(url, None, None, BROWSER_TRANSPORT, f"{type(exc).__name__}: {exc}")
        status = response.status if response else None
        if status != 200:
            header = response.headers.get("retry-after") if response else None
            return PageResult(url, status, None, BROWSER_TRANSPORT, f"HTTP {status}",
                              retry_after=_retry_after(header))
        if not _allowed_redirect(url, page.url):
            return PageResult(url, status, None, BROWSER_TRANSPORT,
                              "redirect outside approved pages")
        if not is_html(response.headers.get("content-type", "")):
            return PageResult(url, status, None, BROWSER_TRANSPORT, "non-HTML response")
        html = page.content()
        error = html_error(html)
        return PageResult(url, 200, None if error else html, BROWSER_TRANSPORT,
                          error, final_url=page.url)

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


def _retry_after(header: str | None) -> float | None:
    return retry_after(header)


def _allowed_redirect(source: str, target: str) -> bool:
    try:
        original, destination = urlsplit(source), urlsplit(target)
        hosts = {original.hostname}
        if original.hostname in {"www.monash.edu", "www.monash.edu.my"}:
            hosts = {"www.monash.edu", "www.monash.edu.my"}
        return (
            destination.scheme == "https" and destination.hostname in hosts
            and destination.port in (None, 443) and not destination.username
            and not destination.password
            and not destination.path.lower().endswith((".pdf", ".doc", ".docx", ".zip"))
        )
    except ValueError:
        return False
