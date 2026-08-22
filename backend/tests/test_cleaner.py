"""The official-page cleaner keeps text and structure, and drops the chrome."""
from __future__ import annotations

from app.knowledge.cleaner import clean_page, content_hash


def test_extracts_title_headings_and_body(official_html):
    result = clean_page(official_html("sample-guide"), url="https://example.invalid/guide")
    assert result["title"] == "Applying for special consideration"
    assert [h["text"] for h in result["headings"]] == ["Who can apply", "How to apply"]
    assert "outside your control" in result["clean_text"]


def test_navigation_and_scripts_are_dropped(official_html):
    result = clean_page(official_html("sample-guide"), url="https://example.invalid/guide")
    assert "Skip to content" not in result["clean_text"]
    assert "Copyright Monash" not in result["clean_text"]
    assert "analytics" not in result["clean_text"]


def test_summary_prefers_a_real_paragraph(official_html):
    result = clean_page(official_html("sample-guide"), url="https://example.invalid/guide")
    assert result["summary"].startswith("Special consideration is for short-term")


def test_hash_ignores_navigation_churn(official_html):
    original = official_html("sample-guide")
    reskinned = original.replace("Study</a>", "Studies</a>").replace(
        "Copyright Monash 2026", "Copyright Monash 2027"
    )
    assert clean_page(original, url="u")["content_hash"] == clean_page(reskinned, url="u")[
        "content_hash"
    ]


def test_hash_changes_when_the_content_changes(official_html):
    original = official_html("sample-guide")
    edited = original.replace("two university working days", "five university working days")
    assert clean_page(original, url="u")["content_hash"] != clean_page(edited, url="u")[
        "content_hash"
    ]


def test_content_hash_is_whitespace_insensitive():
    assert content_hash("Title", "body text") == content_hash("  Title ", "body text\n")
