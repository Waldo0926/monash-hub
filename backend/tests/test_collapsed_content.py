"""Everything inside a collapsed section is read, question and answer.

Monash Malaysia's FAQ pages are graphite accordions: the question is the text
of a button, the answer a panel hidden by a stylesheet. Read as a list, the
student pass page kept the first paragraph of 15 answers and none of its 75
questions, and lost the lists inside the answers - "you fail to attend
classes for 3 or more consecutive days".
"""
from __future__ import annotations

from app.knowledge.cleaner import clean_page

GRAPHITE = """
<html><body><main><div class="content-inner__main">
<h1>Student pass</h1>
<p>Answers to the questions international students ask most about their student pass and visa.</p>
<ul class="graphite-accordion__list">
  <li class="graphite-accordion__item">
    <div><button aria-controls="a1" aria-expanded="false">Why am I getting an email notification?</button></div>
    <div id="a1" class="graphite-accordion__content" style="display:none">
      <p>The system will notify you via email if:</p>
      <ul><li>you fail to attend classes for 3 or more consecutive days</li>
          <li>your accumulated attendance is less than 80%</li></ul>
      <p>Contact the Student Pass team if you think this is wrong.</p>
    </div>
  </li>
  <li class="graphite-accordion__item">
    <div><button aria-controls="a2" aria-expanded="false">Undergraduate fees</button></div>
    <div id="a2" class="graphite-accordion__content" style="display:none">
      <table><tr><th>Year</th><th>Fee</th></tr><tr><td>2026</td><td>RM 45,000</td></tr></table>
    </div>
  </li>
</ul>
</div></main></body></html>
"""


def _blocks():
    return clean_page(GRAPHITE, url="https://www.monash.edu.my/student-pass")["blocks"]


def test_the_question_is_a_heading():
    headings = [b["text"] for b in _blocks() if b["type"] == "heading"]
    assert headings == ["Why am I getting an email notification?", "Undergraduate fees"]


def test_the_whole_answer_is_kept_in_order():
    blocks = _blocks()
    kinds = [b["type"] for b in blocks]
    assert kinds == ["paragraph", "heading", "paragraph", "list", "paragraph", "heading", "table"]
    items = ["".join(s["text"] for s in item) for item in blocks[3]["items"]]
    assert items == ["you fail to attend classes for 3 or more consecutive days",
                     "your accumulated attendance is less than 80%"]
    assert "Student Pass team" in blocks[4]["spans"][0]["text"]


def test_a_table_in_a_section_keeps_its_heading():
    blocks = _blocks()
    table = blocks.index(next(b for b in blocks if b["type"] == "table"))
    assert blocks[table - 1] == {**blocks[table - 1], "text": "Undergraduate fees"}
    assert blocks[table]["rows"] == [["2026", "RM 45,000"]]


def test_a_toggle_inside_a_heading_leaves_its_text_there():
    html = """<html><body><main><h1>Exchange</h1>
      <p>Everything you need to know before you go on exchange with Monash Abroad.</p>
      <h3><button aria-expanded="false">Who can apply?</button></h3>
      <div><p>Students with at least 48 credit points completed.</p></div>
    </main></body></html>"""
    blocks = clean_page(html, url="https://www.monash.edu/study-abroad")["blocks"]
    assert {"type": "heading", "text": "Who can apply?"}.items() <= blocks[1].items()


def test_two_paragraphs_in_a_list_item_stay_two_lines():
    html = """<html><body><main><h1>Printing</h1>
      <p>How to print on campus at the library and the computer labs, and what it costs.</p>
      <ul><li><p>Log in with your Monash ID.</p><p>Choose the printer.</p></li></ul>
    </main></body></html>"""
    blocks = clean_page(html, url="https://www.monash.edu.my/printing")["blocks"]
    item = "".join(s["text"] for s in blocks[-1]["items"][0])
    assert item == "Log in with your Monash ID.\nChoose the printer."


def test_a_list_deeper_inside_an_item_is_not_lost():
    html = """<html><body><main><h1>Documents</h1>
      <p>Bring these documents to the counter when you renew your student pass.</p>
      <ul><li>Bring:<div><ul><li>your passport</li><li>form IM12</li></ul></div></li></ul>
    </main></body></html>"""
    text = clean_page(html, url="https://www.monash.edu.my/docs")["clean_text"]
    assert "form IM12" in text and "your passport" in text
