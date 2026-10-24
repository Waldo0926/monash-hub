"""Text on a page that is not the page: consent banners and widget placeholders."""
from __future__ import annotations

from app.knowledge.cleaner import clean_page

URL = "https://www.monash.edu/law/current-students/home/international-opportunities"
BANNER = (
    '<div class="consent-bar"><p>We use cookies to improve your experience. '
    'By continuing you agree to our cookie policy.</p></div>'
)


def test_a_page_that_is_only_a_title_stays_empty_instead_of_reading_the_banner():
    html = (
        "<html><body>" + BANNER
        + '<main><div class="content-inner__main"><h1>International opportunities</h1>'
        "</div></main></body></html>"
    )
    page = clean_page(html, url=URL)
    assert page["title"] == "International opportunities"
    assert "cookies" not in page["clean_text"]


def test_a_cookie_notice_inside_the_article_is_dropped_but_a_sentence_about_cookies_is_not():
    html = (
        '<html><body><main><p>We use cookies to remember your sign-in.</p>'
        "<p>" + "Real guidance for students about enrolment. " * 8 + "</p>"
        "<p>Clear your browser cookies if Moodle will not load, then sign in again.</p>"
        "</main></body></html>"
    )
    text = clean_page(html, url=URL)["clean_text"]
    assert "remember your sign-in" not in text
    assert "Clear your browser cookies" in text


def test_the_sign_in_widget_placeholder_is_not_content():
    html = (
        "<html><body><main><p>Content cannot be accessed</p>"
        "<p>" + "Key dates for each teaching period are listed below. " * 6 + "</p>"
        "</main></body></html>"
    )
    text = clean_page(html, url="https://www.monash.edu/students/dates")["clean_text"]
    assert "cannot be accessed" not in text
    assert text.startswith("Key dates")


def test_with_no_article_at_all_the_body_is_still_read():
    html = "<html><body><p>" + "A page with no main element at all. " * 8 + "</p></body></html>"
    assert "no main element" in clean_page(html, url=URL)["clean_text"]
