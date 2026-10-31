"""Reading a whole site from its sitemap, less what is not for students."""
from __future__ import annotations

from crawler.official import discover
from crawler.official.coverage import tier

MY = "https://www.monash.edu.my"
AU = "https://www.monash.edu"


class Sitemaps:
    def __init__(self, files):
        self.files = files
        self.asked = []

    def text_file(self, url):
        self.asked.append(url)
        return (200, self.files[url]) if url in self.files else (404, "")


def urlset(*urls):
    locs = "".join(f"<url><loc>{u}</loc></url>" for u in urls)
    return f'<?xml version="1.0"?><urlset>{locs}</urlset>'


def test_the_malaysia_sitemap_keeps_student_pages_and_drops_news_files_and_campaigns():
    fetcher = Sitemaps({f"{MY}/sitemap.xml": urlset(
        f"{MY}/its/our-services/students/printing-services",
        f"{MY}/library/services-facilities/printing",
        f"{MY}/finance/sst-info",
        f"{MY}/finance/sst-info/",
        f"{MY}/pages/latest/articles/2017/some-story",
        f"{MY}/news-and-events/2026/open-day",
        f"{MY}/alumni/graduates/someone",
        f"{MY}/openday3",
        f"{MY}/finance/fees/guide.pdf",
        f"{MY}/library/print",
        "https://elsewhere.example/finance",
    )})
    assert discover.sitemap_urls(fetcher, "my-all") == [
        f"{MY}/its/our-services/students/printing-services",
        f"{MY}/library/services-facilities/printing",
        f"{MY}/finance/sst-info",
    ]


def test_faculty_sitemaps_only_give_their_current_student_pages_and_indexes_are_followed():
    child = f"{AU}/business/sitemap-1.xml"
    fetcher = Sitemaps({
        f"{AU}/business/sitemap.xml":
            f'<?xml version="1.0"?><sitemapindex><sitemap><loc>{child}</loc></sitemap>'
            "</sitemapindex>",
        child: urlset(
            f"{AU}/business/current-students/course-transfers",
            f"{AU}/business/research/centre",
            f"{AU}/business/current-students/news/today",
        ),
        f"{AU}/students/sitemap.xml": urlset(f"{AU}/students/admin/fees",
                                             f"{AU}/students/admin/fees?x=1"),
    })
    assert discover.sitemap_urls(fetcher, "au-students") == [
        f"{AU}/students/admin/fees",
        f"{AU}/business/current-students/course-transfers",
    ]
    assert child in fetcher.asked


def test_a_missing_sitemap_is_skipped_not_fatal():
    assert discover.sitemap_urls(Sitemaps({}), "my-all") == []


def test_the_print_view_is_skipped_but_printing_pages_are_not():
    assert discover.SKIP.search("/students/admin/print")
    assert not discover.SKIP.search("/its/our-services/students/printing-services")


def test_only_semester_pages_and_dates_are_checked_often():
    assert tier(f"{MY}/student-services/student-admin/principal-dates") == "dynamic"
    assert tier(f"{MY}/finance/encumbrance") == "medium"
    assert tier(f"{AU}/students/admin/fees/payment-options") == "medium"
    assert tier(f"{MY}/ugfees") == tier(f"{MY}/pgfees") == "medium"
    assert tier(f"{MY}/ugfees-archive") == "stable"
    assert tier(f"{MY}/library/services-facilities/printing") == "stable"
    assert tier(f"{AU}/policy-bank/policies-and-procedures/academic") == "stable"


def test_search_verification_tracking_and_404_addresses_are_not_read():
    fetcher = Sitemaps({f"{MY}/sitemap.xml": urlset(
        f"{MY}/search",
        f"{MY}/it/archive/search",
        f"{MY}/google1a2b3c4d5e.html",
        f"{MY}/robots2.txt",
        f"{MY}/sitemap.xml",
        f"{MY}/analytics/google-tag-manager2",
        f"{MY}/student-services/feedback",
        f"{MY}/page-not-found",
        f"{MY}/medicine/login",
        f"{MY}/pharmacy/archive/he/programme",
        f"{MY}/study-abroad/outbound/Semester-in-Australia",
        f"{MY}/study-abroad/outbound/semester-in-australia/",
        f"{MY}/student-services/student-admin",
    )})
    assert discover.sitemap_urls(fetcher, "my-all") == [
        f"{MY}/study-abroad/outbound/Semester-in-Australia",
        f"{MY}/student-services/student-admin",
    ]


class Result:
    def __init__(self, status, error):
        self.status, self.error = status, error


def test_a_200_that_was_not_a_page_is_recorded_as_a_failure():
    row = discover._failure(f"{MY}/guide", Result(200, "not HTML: application/pdf"), 1)
    assert row["status"] is None and row["http"] == 200
    assert discover._failure(f"{MY}/gone", Result(404, "HTTP 404"), 1)["status"] == 404


def test_the_page_not_found_page_is_a_soft_404():
    from crawler.response import html_error

    for title in ("Page Not Found | Monash University Malaysia", "404 - Monash University",
                  "page not found"):
        assert html_error(f"<html><title>{title}</title><p>x</p></html>") == "upstream soft 404"
    assert html_error("<html><title>Lost and found | Monash</title></html>") is None
