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
    assert tier(f"{MY}/library/services-facilities/printing") == "stable"
    assert tier(f"{AU}/policy-bank/policies-and-procedures/academic") == "stable"
