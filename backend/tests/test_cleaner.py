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


# --- structured blocks ----------------------------------------------------
#
# The fixture is a trimmed copy of the real GPA page, because that page is where
# the flat extractor was most obviously wrong: it turned a six column worked
# example into sixty loose numbers and printed the whole tabbed half of the page
# twice.

from app.knowledge.cleaner import blocks_to_text, rich_to_text  # noqa: E402


def _blocks(official_html, kind: str, name: str = "gpa-tabbed"):
    result = clean_page(official_html(name), url="https://example.invalid/gpa")
    return [b for b in result["blocks"] if b["type"] == kind]


def test_a_sentence_broken_up_by_inline_tags_stays_one_paragraph(official_html):
    paragraphs = [rich_to_text(b["spans"]) for b in _blocks(official_html, "paragraph")]
    sentence = next(p for p in paragraphs if p.startswith("For example, your grades"))
    # Three <strong> tags mid-sentence used to make this five separate lines.
    assert "are given a numerical value" in sentence
    assert "\n" not in sentence


def test_emphasis_and_links_survive_as_spans(official_html):
    lists = _blocks(official_html, "list")
    items = [i for block in lists for i in block["items"]]

    estimate = next(i for i in items if "online calculator below" in rich_to_text(i))
    assert any(s["text"] == "estimate" and s.get("bold") for s in estimate)

    wes = next(i for i in items if "Web Enrolment System" in rich_to_text(i))
    assert any(s.get("url", "").startswith("https://my.monash.edu") for s in wes)


def test_a_table_comes_back_as_a_table(official_html):
    tables = _blocks(official_html, "table")
    example = next(t for t in tables if t["columns"][0] == "Unit")

    assert example["caption"].startswith("An example of how a weighted GPA")
    assert example["columns"] == [
        "Unit", "Mark", "Grade", "Grade value", "Unit credit points",
        "Weighted GPA unit score",
    ]
    assert example["rows"][0] == ["MON1001", "63", "C", "2.0", "6", "12.0"]
    # An empty mark stays an empty cell rather than shifting the row left.
    assert example["rows"][2] == ["MON2002", "", "WN (withdrawn fail)", "0.0", "6", "0.0"]
    # colspan=4 in the totals row is expanded, so every row is the same width.
    assert example["foot"] == [["Total", "", "", "", "78", "229.8"]]
    assert all(len(row) == 6 for row in example["rows"] + example["foot"])


def test_ordered_and_unordered_lists_are_told_apart(official_html):
    lists = _blocks(official_html, "list")
    steps = next(b for b in lists if "Calculate to three decimal places." in
                 [rich_to_text(i) for i in b["items"]])
    assert steps["ordered"] is True
    assert any(b["ordered"] is False for b in lists)


def test_tab_labels_become_headings(official_html):
    """The GPA page's two tabs are two different grading scales, not one."""
    headings = _blocks(official_html, "heading")
    tabs = [h for h in headings if h.get("variant") == "tab"]
    assert [h["text"] for h in tabs] == ["Australia", "Malaysia"]


def test_the_mobile_accordion_twin_is_not_indexed_twice(official_html):
    result = clean_page(official_html("gpa-tabbed"), url="u")
    assert result["clean_text"].count("we need to assign each grade a value") == 1
    assert [h["text"] for h in result["headings"]].count("Methodology") == 1


def test_page_furniture_is_still_dropped(official_html):
    result = clean_page(official_html("gpa-tabbed"), url="u")
    for noise in ("Skip to content", "Copyright Monash", "Top FAQs", "You are here"):
        assert noise not in result["clean_text"], noise


def test_every_heading_has_a_unique_anchor(official_html):
    headings = _blocks(official_html, "heading")
    ids = [h["id"] for h in headings]
    assert all(ids)
    assert len(ids) == len(set(ids))


def test_clean_text_is_derived_from_the_blocks(official_html):
    result = clean_page(official_html("gpa-tabbed"), url="u")
    assert result["clean_text"] == blocks_to_text(result["blocks"])
    # And the table survives the flattening as rows, not as a column of numbers.
    assert "MON1001 | 63 | C | 2.0 | 6 | 12.0" in result["clean_text"]


def test_changing_the_extractor_invalidates_every_stored_hash(official_html):
    """Otherwise a crawl reports 'unchanged' and the old shape never gets fixed."""
    from app.knowledge import cleaner

    original = clean_page(official_html("gpa-tabbed"), url="u")["content_hash"]
    bumped = cleaner.EXTRACTOR_VERSION + 1
    try:
        cleaner.EXTRACTOR_VERSION = bumped
        assert clean_page(official_html("gpa-tabbed"), url="u")["content_hash"] != original
    finally:
        cleaner.EXTRACTOR_VERSION = bumped - 1


def test_template_plumbing_is_not_content(official_html):
    """Monash ships an unconfigured share widget that extracts as a sentence.

    Left in, it is indexed, translated and shown to a student as if the page
    said it.
    """
    html = official_html("sample-guide").replace(
        "<h1>", "<p>Social Media Share Bar: Not Configured</p><h1>"
    )
    result = clean_page(html, url="https://example.invalid/guide")

    assert "Not Configured" not in result["clean_text"]
    assert not any("Not Configured" in str(block) for block in result["blocks"])


def test_html_comments_are_not_page_text():
    """BeautifulSoup hands Comment nodes back from get_text().

    Monash's CMS leaves plenty of them - a real fees page arrived carrying
    "endnoindex", "@@ WIP @@" and "/.call-to-action__wrapper" as paragraphs,
    which were then indexed, translated and shown to a student as content.
    """
    html = """
    <html><body><main>
      <h1>Fees and payments</h1>
      <!-- endnoindex -->
      <!-- @@ WIP @@ -->
      <p>Find out when and how to pay your fees, and plan your payments.</p>
      <!-- /.call-to-action__wrapper -->
      <!-- Feature Box 1: Show -->
      <p>Use the fee calculator to work out your course fees for the year ahead.</p>
    </main></body></html>
    """
    result = clean_page(html, url="https://example.invalid/fees")

    rendered = str(result["blocks"]) + (result["clean_text"] or "")
    for leak in ("endnoindex", "WIP", "call-to-action", "Feature Box"):
        assert leak not in rendered
    assert "plan your payments" in result["clean_text"]
