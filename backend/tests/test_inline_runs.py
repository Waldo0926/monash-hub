"""Text that sits side by side in a <div> is one paragraph.

On 2026-10-25 the misconduct page showed its coloured tiles as seven broken
lines ("impartial and fair to" / "all parties" / ...), and the IT re-enrolment
page split "Check the <a>handbook</a> for units on offer" into three lines and
lost the link. Both are inline content written straight into a container:
tiles with a <br> to wrap the line, and <li> with no list around them.
"""
from __future__ import annotations

from app.knowledge.cleaner import clean_page

URL = "https://www.monash.edu/students/support/misconduct/about-scc"


def _blocks(body: str) -> list[dict]:
    html = f"<html><body><main><h1>Title</h1>{body}</main></body></html>"
    return clean_page(html, url=URL)["blocks"]


def _texts(blocks: list[dict]) -> list[str]:
    return ["".join(s["text"] for s in b["spans"]) for b in blocks if b["type"] == "paragraph"]


def test_a_tile_with_a_line_wrap_is_one_line():
    blocks = _blocks(
        "<p>We aim to deal with allegations with these key qualities:</p>"
        '<div class="row"><div class="col-xs-12 col-md-4" style="font-weight:bold">'
        "impartial and fair to<br>all parties</div>"
        '<div class="col-xs-12 col-md-4">responsive to complex and<br>sensitive issues</div>'
        '<div class="col-xs-12 col-md-4">handled in a timely manner</div></div>'
    )
    assert _texts(blocks)[1:] == [
        "impartial and fair to all parties",
        "responsive to complex and sensitive issues",
        "handled in a timely manner",
    ]


def test_a_line_break_between_lines_is_kept():
    blocks = _blocks("<div>Building 1<br>Clayton campus</div><div>Phone:<br>1800 666 274</div>"
                     "<div>Description:-<br>myDIDeA was built for</div>")
    assert _texts(blocks) == ["Building 1\nClayton campus", "Phone:\n1800 666 274",
                              "Description:-\nmyDIDeA was built for"]


def test_lettered_lines_keep_their_breaks():
    """MED5101 on monash.edu.my lists its options as a) b) c) on lines of their own."""
    blocks = _blocks(
        "<p>You can spend it on a) writing up the publication arising from your research,"
        "<br>b) continuing that research towards a publication, or<br>c) working on a new "
        "research project.</p><p>a)An option to submit preferences<br>b)A first-in option"
        "<br>(ii) or a third</p>"
    )
    assert _texts(blocks) == [
        "You can spend it on a) writing up the publication arising from your research,\n"
        "b) continuing that research towards a publication, or\n"
        "c) working on a new research project.",
        "a)An option to submit preferences\nb)A first-in option\n(ii) or a third",
    ]


def test_a_link_in_the_middle_of_a_sentence_stays_in_it():
    blocks = _blocks(
        '<div><h3>Before you enrol</h3>Read the <a href="https://handbook.monash.edu/">'
        "handbook</a> and your <strong>course map</strong> first.</div>"
    )
    paragraph = next(b for b in blocks if b["type"] == "paragraph")
    assert "".join(s["text"] for s in paragraph["spans"]) == \
        "Read the handbook and your course map first."
    assert {"text": "handbook", "url": "https://handbook.monash.edu/"} in paragraph["spans"]
    assert {"text": "course map", "bold": True} in paragraph["spans"]


def test_list_items_with_no_list_around_them_become_a_list():
    blocks = _blocks(
        '<div id="content_container_136975_136975"><h3>Choose your units</h3>'
        '<li>Check the&nbsp;<a href="https://handbook.monash.edu/">handbook</a> '
        "for units on offer and choose your units.</li>\n"
        "<li>Enrol in WES.</li><p>Then check your timetable.</p></div>"
    )
    kinds = [b["type"] for b in blocks]
    assert kinds == ["heading", "list", "paragraph"]
    items = blocks[1]["items"]
    assert ["".join(s["text"] for s in item) for item in items] == [
        "Check the handbook for units on offer and choose your units.",
        "Enrol in WES.",
    ]
    assert {"text": "handbook", "url": "https://handbook.monash.edu/"} in items[0]


def test_text_on_either_side_of_a_block_stays_apart():
    blocks = _blocks("<div>Before the table<table><tr><td>a</td><td>b</td></tr></table>after it</div>")
    assert _texts(blocks) == ["Before the table", "after it"]
