"""The official-page fetcher says who it is, asks first, and slows down when told.

No network: the HTTP and browser transports are replaced by a script of
answers, and robots.txt by a string.
"""
from __future__ import annotations

from crawler.official.fetch import (
    AUTO_TRANSPORT,
    BROWSER_TRANSPORT,
    HTTP_TRANSPORT,
    OfficialFetcher,
    PageResult,
)
from crawler.throttling.limiter import USER_AGENT, RateLimit, Throttle


class Scripted(OfficialFetcher):
    """Answers in order, and remembers which transport each one was asked on."""

    def __init__(self, answers, robots="", robots_status=200, **kwargs):
        limit = RateLimit(min_interval=0, jitter=0, backoff_base=0, backoff_max=0, max_attempts=3)
        super().__init__(Throttle(limit), **kwargs)
        self.answers = list(answers)
        self.robots_text = robots
        self.robots_status = robots_status
        self.asked: list[tuple[str, str]] = []
        self.pauses: list[float] = []
        self.throttle.backoff = lambda attempt, at_least=0.0: self.pauses.append(at_least)

    def _robots_text(self, url):
        if isinstance(self.robots_status, Exception):
            raise self.robots_status
        return self.robots_status, self.robots_text

    def _fetch_once(self, url):
        self.asked.append((self._mode, url))
        status, retry_after = self.answers.pop(0)
        html = "<html>page</html>" if status == 200 else None
        return PageResult(url, status, html, self._mode, None if status == 200 else f"HTTP {status}",
                          retry_after=retry_after)


def test_the_crawler_names_itself_on_both_sources():
    from crawler.handbook.fetch import USER_AGENT as handbook_agent
    from crawler.official import fetch as official

    assert handbook_agent == USER_AGENT
    assert official.USER_AGENT == USER_AGENT
    assert USER_AGENT.startswith("MonashHubBot/") and "monashhub.secureview.tech" in USER_AGENT


def test_a_path_robots_disallows_is_not_fetched():
    robots = "User-agent: *\nDisallow: /students/private/\n"
    fetcher = Scripted([(200, None)], robots=robots)
    result = fetcher.fetch("https://www.monash.edu/students/private/page")
    assert result.status is None and "robots" in (result.error or "")
    assert fetcher.asked == []
    assert fetcher.fetch("https://www.monash.edu/students/public").ok


def test_a_rule_for_this_bot_by_name_wins_over_the_general_one():
    robots = "User-agent: *\nDisallow: /\n\nUser-agent: MonashHubBot\nAllow: /\n"
    fetcher = Scripted([(200, None)], robots=robots)
    assert fetcher.fetch("https://www.monash.edu/students/page").ok


def test_a_missing_robots_file_means_no_rules_and_an_unreadable_one_means_closed():
    assert Scripted([(200, None)], robots_status=404).fetch("https://a.example/x").ok
    closed = Scripted([(200, None)], robots_status=503).fetch("https://b.example/x")
    assert closed.status is None and "permission unknown" in closed.error
    broken = Scripted([(200, None)], robots_status=OSError("reset")).fetch("https://c.example/x")
    assert broken.status is None


def test_a_429_means_slower_on_the_same_transport():
    fetcher = Scripted([(429, 90.0), (200, None)], transport=AUTO_TRANSPORT)
    assert fetcher.fetch("https://www.monash.edu/students/page").ok
    assert [mode for mode, _ in fetcher.asked] == [HTTP_TRANSPORT, HTTP_TRANSPORT]
    assert fetcher.pauses == [90.0]


def test_a_403_in_auto_mode_reads_that_page_with_the_browser_and_no_wait():
    fetcher = Scripted([(403, None), (200, None), (200, None)], transport=AUTO_TRANSPORT)
    assert fetcher.fetch("https://www.monash.edu/students/one").ok
    assert fetcher.fetch("https://www.monash.edu/students/two").ok
    # One refusal is that page: the next one is asked over httpx again.
    assert [mode for mode, _ in fetcher.asked] == [HTTP_TRANSPORT, BROWSER_TRANSPORT, HTTP_TRANSPORT]
    assert fetcher.pauses == []


def test_a_host_that_refuses_every_page_latches_to_the_browser():
    answers = [(403, None), (200, None)] * 3 + [(200, None)]
    fetcher = Scripted(answers, transport=AUTO_TRANSPORT)
    for n in range(4):
        assert fetcher.fetch(f"https://www.monash.edu.my/page-{n}").ok
    assert [mode for mode, _ in fetcher.asked][-1] == BROWSER_TRANSPORT
    assert fetcher.transport == BROWSER_TRANSPORT


def test_a_page_the_browser_is_refused_too_is_not_asked_a_third_time():
    fetcher = Scripted([(403, None), (403, None), (200, None)], transport=AUTO_TRANSPORT)
    assert fetcher.fetch("https://www.monash.edu.my/exams").status == 403
    assert len(fetcher.asked) == 2


def test_a_link_to_a_file_is_not_retried():
    class Download(Scripted):
        def _fetch_once(self, url):
            self.asked.append((self._mode, url))
            return PageResult(url, None, None, BROWSER_TRANSPORT,
                              "Error: Page.goto: Download is starting")

    fetcher = Download([], transport=BROWSER_TRANSPORT)
    assert not fetcher.fetch("https://www.monash.edu.my/form").ok
    assert len(fetcher.asked) == 1


def test_an_explicit_transport_is_kept_whatever_the_server_says():
    fetcher = Scripted([(403, None), (403, None), (403, None)], transport=HTTP_TRANSPORT)
    result = fetcher.fetch("https://www.monash.edu/students/page")
    assert result.status == 403
    assert {mode for mode, _ in fetcher.asked} == {HTTP_TRANSPORT}
