"""Synthetic upstream failures must not look like current authoritative data."""
from __future__ import annotations

import json
from datetime import UTC, datetime

import httpx
import pytest
from app.handbook.course_parser import parse_aos_page, parse_course_page
from app.handbook.parser import ParseError, extract_next_data, parse_unit_page
from app.knowledge.cleaner import clean_page

from crawler.handbook.fetch import HandbookFetcher
from crawler.official.audit import audit, inventory, link_inventory
from crawler.official.discover import SITES, _wanted
from crawler.official.fetch import OfficialFetcher, PageResult, Robots
from crawler.response import html_error, retry_after
from crawler.throttling.limiter import RateLimit, Throttle


def throttle():
    return Throttle(RateLimit(min_interval=0, jitter=0, backoff_base=0, backoff_max=0))


def html(payload):
    return '<script nonce="x" type="application/json" id="__NEXT_DATA__">' + json.dumps(payload) + '</script>'


@pytest.mark.parametrize("parser,kind,field,code", [
    (parse_unit_page, "units", "unit_code", "FIT3155"),
    (parse_course_page, "courses", "course_code", "C2001"),
    (parse_aos_page, "aos", "code", "ALGSW11"),
])
def test_wrong_year_and_wrong_identity_are_parse_failures(parser, kind, field, code):
    content = {field: code, "implementation_year": "2026", "title": "Example"}
    source = html({"props": {"pageProps": {"pageContent": content}}})
    assert parser(source, f"https://handbook.monash.edu/2026/{kind}/{code}")["academic_year"] == 2026
    with pytest.raises(ParseError, match="identity"):
        parser(source, f"https://handbook.monash.edu/2027/{kind}/{code}")
    with pytest.raises(ParseError, match="identity"):
        parser(source, f"https://handbook.monash.edu/2026/{kind}/OTHER1000")


def test_next_data_attribute_order_is_irrelevant_and_non_objects_are_rejected():
    assert extract_next_data(html({"props": {}})) == {"props": {}}
    with pytest.raises(ParseError, match="not an object"):
        extract_next_data(html([]))
    with pytest.raises(ParseError, match="not an object"):
        extract_next_data(html({"props": {"pageProps": []}}))


def test_same_words_with_a_replaced_document_address_change_the_hash():
    source = '<main><p>Read the <a href="/old">Assessment Policy</a>.</p></main>'
    before = clean_page(source, url="https://www.monash.edu/policies")
    after = clean_page(source.replace('/old', '/new'), url="https://www.monash.edu/policies")
    assert before["clean_text"] == after["clean_text"]
    assert before["content_hash"] != after["content_hash"]


def test_policy_table_document_links_keep_the_policy_name_and_effective_date():
    source = '''<main><table><tr><td>Assessment procedure (from 27 July 2026)</td>
      <td><a href="https://publicpolicydms.monash.edu/doc/123">[PDF]</a></td></tr></table></main>'''
    table = clean_page(source, url="https://www.monash.edu/policy-bank")["blocks"][0]
    assert table["links"][0][0]["url"].endswith("/123")
    assert "from 27 July 2026" in table["links"][0][0]["text"]
    assert link_inventory(source, "https://www.monash.edu/policy-bank")[0]["disposition"] == "document-link-only"


def test_translated_policy_table_links_keep_their_targets():
    from app.knowledge.translations import Translation, translate_blocks

    source = '<main><table><tr><td>Assessment policy</td><td><a href="/document">PDF</a></td></tr></table></main>'
    blocks = clean_page(source, url="https://www.monash.edu/policy-bank")["blocks"]
    label = blocks[0]["links"][0][0]["text"]
    tr = Translation("zh")
    tr.strings[label] = "考核政策 PDF"
    translated = translate_blocks(blocks, tr)
    assert translated[0]["links"][0][0] == {"text": "考核政策 PDF", "url": "https://www.monash.edu/document"}
    assert blocks[0]["links"][0][0]["text"] == label


@pytest.mark.parametrize("status,text", [(403, ""), (429, ""), (503, ""), (200, "<html>challenge</html>")])
def test_unreadable_robots_is_closed(status, text):
    assert not Robots(lambda _: (status, text)).allowed("https://www.monash.edu/students/x")


@pytest.mark.parametrize("source", [
    '<title>Just a moment...</title><div>Wait for access</div>',
    '<title>ERROR: The request could not be satisfied</title>',
    '<title>Page not found</title>',
    '<title>Sign in</title><input type="password">',
])
def test_error_shells_are_not_content(source):
    assert html_error(source)
    assert not html_error('<title>Access policy</title><main>Sign in to WES to enrol.</main>')


def test_retry_after_dates_and_untrusted_numeric_values():
    now = datetime(2026, 10, 25, 0, 0, tzinfo=UTC)
    assert retry_after("Sun, 25 Oct 2026 00:01:00 GMT", now=now) == 60
    assert retry_after("30") == 30
    assert retry_after("-1") == 0
    assert retry_after("nan") is None
    assert retry_after("inf") is None


def test_official_redirects_resolve_links_at_the_actual_page():
    asked = []

    def respond(request):
        asked.append(request.url.path)
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nAllow: /\n")
        if request.url.path == "/old":
            return httpx.Response(302, headers={"Location": "/new/page"})
        return httpx.Response(200, headers={"Content-Type": "text/html"},
                              text='<main><p><a href="child">Rules</a></p></main>')

    with OfficialFetcher(throttle(), transport="httpx") as fetcher:
        fetcher._client = httpx.Client(transport=httpx.MockTransport(respond))
        result = fetcher.fetch("https://www.monash.edu/old")
    assert result.ok and result.final_url == "https://www.monash.edu/new/page"
    block = clean_page(result.html, url=result.final_url)["blocks"][0]
    assert block["spans"][0]["url"] == "https://www.monash.edu/new/child"
    assert asked == ["/robots.txt", "/old", "/new/page"]


def test_non_html_bodies_are_never_read_and_foreign_redirects_are_not_followed():
    class Unreadable(httpx.SyncByteStream):
        def __iter__(self):
            raise AssertionError("binary must remain a link")

    def respond(request):
        if request.url.path == "/robots.txt":
            return httpx.Response(404)
        if request.url.path == "/foreign":
            return httpx.Response(302, headers={"Location": "https://unrelated.example/login"})
        return httpx.Response(200, headers={"Content-Type": "application/pdf"}, stream=Unreadable())

    with OfficialFetcher(throttle(), transport="httpx") as fetcher:
        fetcher._client = httpx.Client(transport=httpx.MockTransport(respond))
        assert not fetcher.fetch("https://www.monash.edu/document").ok
        assert "redirect" in fetcher.fetch("https://www.monash.edu/foreign").error


def test_handbook_retry_after_is_honoured_and_last_http_status_survives():
    def respond(request):
        if request.url.path == "/robots.txt":
            return httpx.Response(404)
        return httpx.Response(429, headers={"Retry-After": "35"})

    with HandbookFetcher(throttle()) as fetcher:
        fetcher._client.close()
        fetcher._client = httpx.Client(transport=httpx.MockTransport(respond))
        pauses = []
        fetcher.throttle.backoff = lambda attempt, at_least=0: pauses.append(at_least)
        result = fetcher.fetch("https://handbook.monash.edu/2026/units/FIT3155")
    assert result.status == 429 and not result.ok and pauses == [35, 35]


def test_audit_is_bounded_and_does_not_promote_links_to_fetches():
    class FakeFetcher:
        def __init__(self):
            self.asked = []

        def fetch(self, url):
            self.asked.append(url)
            return PageResult(url, 200, '<main><p>' + 'Example information. ' * 20 +
                              '</p><a href="/new-guidance">New guidance</a></main>', "fake")

    fetcher = FakeFetcher()
    report = audit("my-study", fetcher, max_pages=1)
    assert len(fetcher.asked) == 1
    assert report["entry_pages_unchecked"]
    assert report["pages"][0]["links"][0]["disposition"] == "review-candidate"
    assert not inventory()["duplicate_urls"] and not inventory()["duplicate_slugs"]
    assert _wanted(SITES["policies"], "https://www.monash.edu/policy-bank/policies-and-procedures/academic/education")
    assert not _wanted(SITES["my-study"], "https://www.monash.edu.my/study/entry-requirements-unrelated/x")
    assert _wanted(SITES["myfac"], "https://www.monash.edu.my/it/current-students/Course-Offered")
    assert _wanted(SITES["myfac"], "https://www.monash.edu.my/pharmacy/current-students/guide")
