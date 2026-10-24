"""A table on Monash Hub reads the way it does on monash.edu.

Merged cells used to be flattened: a rowspan left every row below it one
column short, so its cells slid left under the wrong heading, and a second
header row was dropped. A cell with two paragraphs became one run-on line.
"""
from __future__ import annotations

from app.knowledge.cleaner import clean_page


def _table(inner: str) -> dict:
    html = f"<html><body><main><h1>Fees</h1><table>{inner}</table></main></body></html>"
    blocks = clean_page(html, url="https://example.invalid/fees")["blocks"]
    return next(b for b in blocks if b["type"] == "table")


def test_a_rowspan_keeps_the_rows_below_it_in_their_columns():
    table = _table("""
      <thead><tr><th>Level</th><th>Year</th><th>Fee</th></tr></thead>
      <tbody>
        <tr><td rowspan="2">Undergraduate</td><td>2026</td><td>RM 45,000</td></tr>
        <tr><td>2027</td><td>RM 47,000</td></tr>
        <tr><td>Postgraduate</td><td>2026</td><td>RM 52,000</td></tr>
      </tbody>""")
    assert table["rows"] == [
        ["Undergraduate", "2026", "RM 45,000"],
        ["", "2027", "RM 47,000"],
        ["Postgraduate", "2026", "RM 52,000"],
    ]
    assert table["merged"] == [["body", 0, 0, 2, 1]]


def test_a_colspan_is_recorded_as_one_cell():
    table = _table("""
      <tr><th>Item</th><th>Amount</th><th>Due</th></tr>
      <tr><td colspan="2">Payable on enrolment</td><td>Week 1</td></tr>""")
    assert table["columns"] == ["Item", "Amount", "Due"]
    assert table["rows"] == [["Payable on enrolment", "", "Week 1"]]
    assert table["merged"] == [["body", 0, 0, 1, 2]]


def test_a_rowspan_in_the_last_column_still_covers_it():
    table = _table("""
      <tr><th>A</th><th>B</th></tr>
      <tr><td>1</td><td rowspan="2">same</td></tr>
      <tr><td>2</td></tr>""")
    assert table["rows"] == [["1", "same"], ["2", ""]]


def test_a_second_header_row_is_kept():
    table = _table("""
      <thead>
        <tr><th rowspan="2">Unit</th><th colspan="2">Fee</th></tr>
        <tr><th>Domestic</th><th>International</th></tr>
      </thead>
      <tbody><tr><td>FIT1045</td><td>1,200</td><td>4,800</td></tr></tbody>""")
    assert table["columns"] == ["Unit", "Fee", ""]
    assert table["head"] == [["", "Domestic", "International"]]
    assert table["merged"] == [["head", 0, 0, 2, 1], ["head", 0, 1, 1, 2]]


def test_a_cell_keeps_its_own_line_breaks():
    table = _table("""
      <tr><th>Service</th><th>How</th></tr>
      <tr><td>Printing</td><td><p>Log in with your Monash ID.</p><p>Top up at the library.</p></td></tr>
      <tr><td>Wi-Fi</td><td>eduroam<br>Monash Guest</td></tr>""")
    assert table["rows"][0][1] == "Log in with your Monash ID.\nTop up at the library."
    assert table["rows"][1][1] == "eduroam\nMonash Guest"


def test_a_plain_table_has_no_merges():
    table = _table("<tr><th>A</th></tr><tr><td>1</td></tr>")
    assert "merged" not in table and "head" not in table
