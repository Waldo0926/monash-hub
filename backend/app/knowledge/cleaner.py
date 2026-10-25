"""Reduce an official Monash page to searchable text plus structure.

We keep the title, the heading outline, a short summary, an ordered list of
content blocks and a flat text rendering of them - and nothing else. No images,
no stylesheets, no PDFs, no attachments. The Hub links back to the source for
anything richer, which keeps disk cost flat and keeps us an index rather than a
copy of someone else's site.

**Blocks, not one long string.** The first version of this kept only
``clean_text``, produced by asking BeautifulSoup for the text of the body with a
newline between nodes. That is fine until you look at a real page: Monash writes
"All grades, *including fail grades* and *grades from any repeated units*" with
three ``<strong>`` tags in it, so the reader got five lines where there was one
sentence, and the GPA worked example - a six column table - arrived as sixty
loose numbers in a column. The page was legible to a search index and to nobody
else.

So the extractor walks the document instead and emits typed blocks: headings,
paragraphs, lists and tables. ``clean_text`` is still produced, derived from
those blocks, because the search vector wants a flat string. It is no longer
what anybody reads.

Two Monash-specific shapes are worth knowing about, because both of them cost
us before they were handled:

* **Tabbed sections are in the HTML twice** - once as desktop tabs
  (``.tabs.mobile-hidden``) and again as a mobile accordion
  (``.accordion.desktop-hidden``), with identical content. Indexing both
  duplicated every tabbed page. We keep the tab version and drop the accordion.
* **A tab label carries meaning.** On the GPA page the two tabs are "Australia"
  and "Malaysia", and the Malaysian numbers are genuinely different. Dropping
  the labels would splice two different grading scales into one list, so each
  panel becomes a heading with its label as the text.
"""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from typing import Any
from urllib.parse import urljoin, urlsplit

from bs4 import BeautifulSoup, Comment, NavigableString, Tag

# Bumped when the extraction itself changes. It goes into the content hash, so
# the next crawl re-writes every page instead of reporting "unchanged" and
# leaving the old shape in the database forever.
EXTRACTOR_VERSION = 7

DROP_TAGS = (
    "script", "style", "noscript", "svg", "iframe", "form", "button",
    "input", "label", "option", "select", "textarea",
)

# Template plumbing that renders as a sentence. Monash ships an unconfigured
# share widget on many pages and it comes through the extractor as a paragraph
# reading "Social Media Share Bar: Not Configured", which then goes on to be
# indexed, translated and shown to a student as if it were content.
JUNK_TEXT = re.compile(
    r"^\s*(?:social media share bar\s*:?\s*not configured|not configured|"
    r"skip to (?:content|main content)|back to top|"
    # Interactive controls from accordions and decision trees. They are useful
    # on monash.edu, but without the original JavaScript they appeared here as
    # standalone body paragraphs such as "View / Close / ▾".
    r"view|close|go back|choose a topic|select a topic|"
    r"what would you like help with\??|no banners found|▾|"
    # A sign-in widget's placeholder. It sits above the real text of
    # students/admin, /dates, /timetables and the other hubs, and reads to a
    # student as if the page were locked.
    r"content cannot be accessed\.?|"
    # The CMS's own note to whoever writes the page. It reached the results
    # legend as the description of five grades, and was then translated.
    r"need description)\s*$",
    re.IGNORECASE,
)
# A consent banner that no selector caught: short, and about cookies.
COOKIE_NOTICE = re.compile(
    r"^\s*(?=.{0,400}$)(?:this (?:web)?site |we )uses? cookies\b", re.IGNORECASE | re.DOTALL
)
# Monash templates wrap the real content in these; dropping them stops every
# page from hashing differently just because a nav item changed.
DROP_SELECTORS = (
    "header",
    "footer",
    "nav",
    "[role=navigation]",
    "[role=banner]",
    "[role=contentinfo]",
    ".breadcrumb",
    ".breadcrumbs",
    ".skip-link",
    ".cookie",
    "#onetrust-consent-sdk",
    "[id*=cookie-banner]",
    "[class*=cookie-banner]",
    "[class*=cookie-notice]",
    "[class*=cookie-consent]",
    "[id*=cookie-consent]",
    # The same content as the desktop tabs beside it. See the module docstring.
    ".desktop-hidden",
    # A search widget, not content: it extracts to "Search / Top FAQs / Chat".
    ".monash-faq-help-panel",
    ".visuallyhidden",
    # Nested accordions put "View" inside the heading and a hidden
    # "View / Close" pair beside the panel. The heading itself is content; the
    # toggle controls are not.
    ".accTitle__toggle-wrapper",
    ".nested-accordion__expand-text",
    ".nested-accordion__collapse_text",
    # Selectric mirrors a <select> as another list, so keeping it duplicates all
    # options. Decision-tree forms cannot work in the read-only guide copy and
    # the page already links to the official interactive original.
    ".selectric-wrapper",
    ".sq_question_wrapper",
)
# Most specific first: monash.edu's <main> also contains the left-hand section
# nav and the page furniture, and .content-inner__main is the article itself.
CONTENT_SELECTORS = (
    ".content-inner__main",
    "main",
    "[role=main]",
    "#main-content",
    "article",
    ".content-main",
)

CONTAINERS = {"div", "section", "article", "main", "figure", "aside", "span"}
HEADINGS = ("h2", "h3", "h4", "h5", "h6")

WS_RE = re.compile(r"[ \t\xa0​]+")
BLANK_RE = re.compile(r"\n{3,}")
SLUG_STRIP_RE = re.compile(r"[^a-z0-9]+")


# --- inline text ----------------------------------------------------------
#
# A "rich" value is a list of spans, each carrying its text plus whether it was
# emphasised and where it linked. Keeping the link is the point: the official
# pages are mostly signposts to other pages, and an extractor that flattens
# "see the Web Enrolment System" into unclickable words has thrown away the
# useful half of the sentence.

def _clean(text: str) -> str:
    return WS_RE.sub(" ", unicodedata.normalize("NFKC", text))


def _is_linkable(href: str) -> bool:
    """Anchors to nowhere are noise; ``#/`` in particular is a Monash JS hook."""
    return bool(href) and not href.startswith("#")


def _absolute_links(value: Any, base: str) -> Any:
    """Resolve every span's link against the page it came from, http(s) only.

    The pages link to each other relatively, and a relative link shown on the
    Hub pointed at the Hub's own domain. Anything that is not a web address
    once resolved (``javascript:`` in any spelling, ``data:``, ``mailto:``)
    is dropped rather than handed to a browser.
    """
    if isinstance(value, list):
        return [_absolute_links(item, base) for item in value]
    if isinstance(value, dict):
        out = {k: _absolute_links(v, base) for k, v in value.items() if k != "url"}
        url = value.get("url")
        if isinstance(url, str):
            resolved = urljoin(base, url.strip())
            if urlsplit(resolved).scheme in ("http", "https"):
                out["url"] = resolved
        return out
    return value


def _rich(node: Tag) -> list[dict[str, Any]]:
    """Flatten a node's inline content into spans, merging matching neighbours."""
    spans: list[dict[str, Any]] = []

    def push(text: str, bold: bool, url: str | None) -> None:
        text = _clean(text)
        if not text:
            return
        if spans and spans[-1].get("bold", False) == bold and spans[-1].get("url") == url:
            spans[-1]["text"] += text
            return
        span: dict[str, Any] = {"text": text}
        if bold:
            span["bold"] = True
        if url:
            span["url"] = url
        spans.append(span)

    def walk(current: Tag, bold: bool, url: str | None) -> None:
        for child in current.children:
            if isinstance(child, NavigableString):
                push(str(child), bold, url)
            elif isinstance(child, Tag):
                if child.name == "br":
                    push("\n", bold, url)
                elif child.name in ("p", "div") and spans:
                    # Two paragraphs in one list item ran together as one.
                    push("\n", bold, url)
                    walk(child, bold, url)
                elif child.name in ("ul", "ol"):
                    continue  # a nested list is a block of its own
                elif child.name in ("strong", "b"):
                    walk(child, True, url)
                elif child.name == "a":
                    href = (child.get("href") or "").strip()
                    walk(child, bold, href if _is_linkable(href) else url)
                else:
                    walk(child, bold, url)

    walk(node, False, None)

    while spans and not spans[-1]["text"].strip():
        spans.pop()
    while spans and not spans[0]["text"].strip():
        spans.pop(0)
    if spans:
        spans[0]["text"] = spans[0]["text"].lstrip()
        spans[-1]["text"] = spans[-1]["text"].rstrip()
    return [s for s in spans if s["text"]]


def rich_to_text(spans: list[dict[str, Any]]) -> str:
    return "".join(span["text"] for span in spans).strip()


def _flat(node: Tag) -> str:
    """Plain text of a node, for table cells and headings."""
    return _clean(node.get_text(" ", strip=True)).strip()


# --- block extraction -----------------------------------------------------

def _slug(text: str, taken: set[str]) -> str:
    base = SLUG_STRIP_RE.sub("-", text.lower()).strip("-")[:60] or "section"
    candidate, n = base, 2
    while candidate in taken:
        candidate, n = f"{base}-{n}", n + 1
    taken.add(candidate)
    return candidate


def _span(cell: Tag, attribute: str) -> int:
    try:
        return max(1, min(int(str(cell.get(attribute, 1)).strip()), 50))
    except (TypeError, ValueError):
        return 1


#: Inside a cell these start a new line: a cell holding two paragraphs or a
#: short list is two lines on monash.edu, not one run-on sentence.
_CELL_BREAKS = ("p", "li", "div", "h2", "h3", "h4", "h5", "h6", "dt", "dd")


def _cell_text(cell: Tag) -> str:
    """A cell's text, keeping the line breaks the cell itself has."""
    for br in cell.find_all("br"):
        br.replace_with("\n")
    for part in cell.find_all(_CELL_BREAKS):
        part.insert_before("\n")
        part.insert_after("\n")
    lines = (_clean(line).strip() for line in cell.get_text(" ").split("\n"))
    return "\n".join(line for line in lines if line)


def _skip_covered(cells: list[str], below: dict[int, int]) -> bool:
    """Leave blanks where a cell from a row above reaches into this one."""
    covered = False
    while below.get(len(cells), 0) > 0:
        below[len(cells)] -= 1
        cells.append("")
        covered = True
    return covered


def _table_rows(rows: list[Tag]) -> tuple[list[list[str]], list[list[int]]]:
    """Cells as plain strings on a regular grid, and the merged cells.

    A cell that spans columns or rows keeps its text in its first position and
    leaves blanks in the positions it covers, so every row is the same width
    and a cell's column is its index. The merges come back as
    ``[row, column, rowspan, colspan]`` so the page can draw them as merged.
    Without the rows a ``rowspan`` covers, every cell below it moved one
    column to the left - a fee under the wrong year.
    """
    out: list[list[str]] = []
    merged: list[list[int]] = []
    below: dict[int, int] = {}  # column -> rows a cell above still covers
    for row in rows:
        cells: list[str] = []
        covered = False
        starts: list[list[int]] = []

        for cell in row.find_all(["td", "th"], recursive=False):
            covered |= _skip_covered(cells, below)
            colspan, rowspan = _span(cell, "colspan"), _span(cell, "rowspan")
            if colspan > 1 or rowspan > 1:
                starts.append([len(out), len(cells), rowspan, colspan])
            if rowspan > 1:
                for column in range(len(cells), len(cells) + colspan):
                    below[column] = rowspan - 1
            cells.append(_cell_text(cell))
            cells.extend([""] * (colspan - 1))
        # Columns past the last cell that a cell above still covers.
        for column in sorted(c for c, left in below.items() if left > 0 and c >= len(cells)):
            cells.extend([""] * (column - len(cells)))
            covered |= _skip_covered(cells, below)
        if any(cells) or covered:
            out.append(cells)
            merged.extend(starts)
    return out, merged


def _table_block(table: Tag) -> dict[str, Any] | None:
    caption = table.find("caption")
    head = table.find("thead")
    body = table.find("tbody")
    foot = table.find("tfoot")

    header_rows, head_merged = _table_rows(head.find_all("tr")) if head else ([], [])

    container = body or table
    body_rows, body_merged = _table_rows(
        [tr for tr in container.find_all("tr") if tr.find_parent(["thead", "tfoot"]) is None]
    )
    if not head and body_rows:
        # No <thead>: if the first row is all <th>, it is the header anyway.
        first = container.find("tr")
        if first is not None and first.find("td") is None and first.find("th") is not None:
            header_rows, body_rows = body_rows[:1], body_rows[1:]
            head_merged = [m for m in body_merged if m[0] == 0]
            body_merged = [[r - 1, *rest] for r, *rest in body_merged if r > 0]

    foot_rows, foot_merged = _table_rows(foot.find_all("tr")) if foot else ([], [])
    columns = header_rows[0] if header_rows else []

    if not body_rows and not columns:
        return None

    width = max(len(columns), *(len(r) for r in header_rows + body_rows + foot_rows), 0)

    def pad(rows: list[list[str]]) -> list[list[str]]:
        return [r + [""] * (width - len(r)) for r in rows]

    block: dict[str, Any] = {
        "type": "table",
        "columns": columns + [""] * (width - len(columns)),
        "rows": pad(body_rows),
    }
    # A second header row ("Domestic | International" under "Fee") used to be
    # dropped. It is kept apart so ``columns`` still means the first one.
    if len(header_rows) > 1:
        block["head"] = pad(header_rows[1:])
    merged = (
        [["head", *m] for m in head_merged]
        + [["body", *m] for m in body_merged]
        + [["foot", *m] for m in foot_merged]
    )
    if merged:
        block["merged"] = merged
    if caption:
        text = _flat(caption)
        if text:
            block["caption"] = text
    if foot_rows:
        block["foot"] = pad(foot_rows)
    # Policy Bank publishes document addresses inside tables, often labelled
    # only "[PDF]". Keep a labelled link index alongside the original cells;
    # links are text/metadata only, never requests for the documents themselves.
    links = []
    for row in table.find_all("tr"):
        label = _flat(row)
        for anchor in row.find_all("a", href=True):
            href = anchor["href"].strip()
            if _is_linkable(href):
                spans = [{"text": label, "url": href}]
                if spans not in links:
                    links.append(spans)
    if links:
        block["links"] = links
    return block


def _list_block(node: Tag) -> dict[str, Any] | None:
    items = []
    for item in node.find_all("li", recursive=False):
        spans = _rich(item)
        if spans:
            items.append(spans)
    if not items:
        return None
    return {"type": "list", "ordered": node.name == "ol", "items": items}


def _list_blocks(node: Tag, depth: int = 0) -> list[dict[str, Any]]:
    """A list and the lists inside its items, in reading order.

    A list inside an item used to come out after the whole outer list, so
    Monash Malaysia's work rules read "restaurants, petrol kiosks..." under
    the last rule instead of under "only in these places". The outer list is
    cut after the item and goes on below the inner one: ``start`` keeps the
    numbering of an ordered list, ``depth`` says how far in a list sits.
    """
    ordered = node.name == "ol"
    out: list[dict[str, Any]] = []
    run: list[list[dict[str, Any]]] = []
    done = 0

    def flush() -> None:
        nonlocal done
        if not run:
            return
        block: dict[str, Any] = {"type": "list", "ordered": ordered, "items": list(run)}
        if ordered and done:
            block["start"] = done + 1
        if depth:
            block["depth"] = depth
        out.append(block)
        done += len(run)
        run.clear()

    for item in node.find_all("li", recursive=False):
        spans = _rich(item)
        if spans:
            run.append(spans)
        inner = [lst for lst in item.find_all(["ul", "ol"]) if lst.find_parent("li") is item]
        if inner:
            flush()
            for lst in inner:
                out.extend(_list_blocks(lst, depth + 1))
    flush()
    return out


def _has_loose_text(node: Tag) -> bool:
    """A list with text outside its items: ``<ul><p>April ceremony</p><li>...``."""
    return any(
        (isinstance(child, Tag) and child.name != "li" and child.get_text(strip=True))
        or (isinstance(child, NavigableString) and not isinstance(child, Comment)
            and _clean(str(child)).strip())
        for child in node.children
    )


def _list_runs(node: Tag, add_paragraph) -> list[dict[str, Any]]:
    """The items of a list with the text between them kept, in order.

    Monash's graduation FAQ writes one ``<ul>`` per question with a paragraph
    before each group of items ("April 2026 ceremony in Malaysia, you'll get
    tickets in total:"). Only the ``<li>`` were read, so the items lost the
    ceremony they belong to.
    """
    out: list[dict[str, Any]] = []
    run: list[list[dict[str, Any]]] = []

    def flush() -> None:
        if run:
            out.append({"type": "list", "ordered": node.name == "ol", "items": list(run)})
            run.clear()

    for child in node.children:
        if isinstance(child, Tag) and child.name == "li":
            spans = _rich(child)
            if spans:
                run.append(spans)
        elif isinstance(child, Tag):
            spans = _rich(child)
            if spans and rich_to_text(spans):
                flush()
                out.append({"type": "paragraph", "spans": spans})
        elif isinstance(child, NavigableString) and not isinstance(child, Comment):
            text = _clean(str(child)).strip()
            if text:
                flush()
                out.append({"type": "paragraph", "spans": [{"text": text}]})
    flush()
    return out


def _is_tab_group(node: Tag) -> bool:
    classes = set(node.get("class") or [])
    return "tabs" in classes and node.select_one(".tabs__target") is not None


def _tab_panels(node: Tag) -> list[tuple[str, Tag]]:
    """Pair each tab label with the panel it controls, in document order."""
    labels: dict[str, str] = {}
    for link in node.select(".tabs__link"):
        target = link.get("aria-controls") or (link.get("href") or "").lstrip("#")
        text = _flat(link)
        if target and text:
            labels[target] = text

    panels = [
        (labels.get(panel.get("id") or "", ""), panel) for panel in node.select(".tabs__target")
    ]
    return [(label, panel) for label, panel in panels if label]


def _extract_blocks(body: Tag) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    slugs: set[str] = set()

    def add_heading(text: str, level: int, *, variant: str | None = None) -> None:
        text = _clean(text).strip()
        if not text:
            return
        block: dict[str, Any] = {
            "type": "heading",
            "level": min(max(level, 2), 4),
            "text": text,
            "id": _slug(text, slugs),
        }
        if variant:
            block["variant"] = variant
        blocks.append(block)

    def add_paragraph(spans: list[dict[str, Any]]) -> None:
        if spans and rich_to_text(spans):
            blocks.append({"type": "paragraph", "spans": spans})

    def walk(node: Tag) -> None:
        for child in node.children:
            if isinstance(child, NavigableString):
                text = _clean(str(child)).strip()
                if text and (node.name in CONTAINERS or node.name == "li"):
                    add_paragraph([{"text": text}])
                continue
            if not isinstance(child, Tag):
                continue

            name = child.name
            if name == "h1":
                continue  # the page title, already carried separately
            if name in HEADINGS:
                add_heading(_flat(child), int(name[1]))
            elif name in ("p", "blockquote"):
                add_paragraph(_rich(child))
            elif name in ("ul", "ol") and _holds_sections(child):
                for item in child.find_all("li", recursive=False):
                    walk(item)
            elif name in ("ul", "ol"):
                # A list item holding a table is a section, not a bullet. The
                # results legend keeps three years of grading tables inside one
                # <ul>, and flattening those items put a whole table - headers,
                # codes, mark ranges - into a single run of text with no row
                # left in it. Lift them out before the item is flattened.
                lifted = [t.extract() for t in child.find_all("table")]
                if _has_loose_text(child):
                    blocks.extend(_list_runs(child, add_paragraph))
                    # Any depth: "li > div > ul" was a list nobody saw.
                    for nested in child.select("li ul, li ol"):
                        nested_block = _list_block(nested)
                        if nested_block:
                            blocks.append(nested_block)
                else:
                    blocks.extend(_list_blocks(child))
                for lifted_table in lifted:
                    lifted_block = _table_block(lifted_table)
                    if lifted_block:
                        blocks.append(lifted_block)
            elif name == "table":
                block = _table_block(child)
                if block:
                    blocks.append(block)
            elif name == "dl":
                for term in child.find_all(["dt", "dd"], recursive=False):
                    spans = _rich(term)
                    if not spans:
                        continue
                    if term.name == "dt":
                        add_heading(rich_to_text(spans), 4)
                    else:
                        add_paragraph(spans)
            elif _is_tab_group(child):
                for label, panel in _tab_panels(child):
                    add_heading(label, 2, variant="tab")
                    walk(panel)
            elif name in CONTAINERS or name in ("li", "tr", "td", "th"):
                walk(child)
            else:
                add_paragraph(_rich(child))

    walk(body)
    return _dedupe(blocks)


def _block_key(block: dict[str, Any]) -> str | None:
    if block["type"] == "paragraph":
        text = rich_to_text(block["spans"])
        # Short lines ("Delivery times are:") legitimately repeat.
        return f"p:{text}" if len(text) >= 60 else None
    if block["type"] == "table":
        return "t:" + json.dumps(block, sort_keys=True, ensure_ascii=False)
    if block["type"] == "list":
        return f"l:{[rich_to_text(i) for i in block['items']]}"
    return None


def _dedupe(blocks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Drop a block that repeats one already emitted.

    Monash's own templates do this - the same paragraph inside both a tab and
    its accordion twin - and a page that says everything twice reads as broken
    even when every word of it is correct.
    """
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for block in blocks:
        key = _block_key(block)
        if key is not None:
            if key in seen:
                continue
            seen.add(key)
        out.append(block)
    return out


# --- text rendering -------------------------------------------------------

def blocks_to_text(blocks: list[dict[str, Any]]) -> str:
    """Flatten blocks back to plain text, for the search vector and summaries."""
    lines: list[str] = []
    for block in blocks:
        kind = block["type"]
        if kind == "heading":
            lines.extend(["", block["text"], ""])
        elif kind == "paragraph":
            lines.append(rich_to_text(block["spans"]))
        elif kind == "list":
            indent = "  " * block.get("depth", 0)
            for number, item in enumerate(block["items"], block.get("start", 1)):
                marker = f"{number}." if block["ordered"] else "•"
                lines.append(f"{indent}{marker} {rich_to_text(item)}")
        elif kind == "table":
            if block.get("caption"):
                lines.append(block["caption"])
            columns = [c for c in block["columns"] if c]
            if columns:
                lines.append(" | ".join(columns))
            for row in block["rows"] + block.get("foot", []):
                lines.append(" | ".join(c for c in row if c))
        lines.append("")
    return BLANK_RE.sub("\n\n", "\n".join(lines)).strip()


def _drop_junk(blocks: list[dict]) -> list[dict]:
    """Remove blocks that are template plumbing rather than content."""
    kept = []
    for block in blocks:
        if block.get("type") == "paragraph":
            text = "".join(span.get("text", "") for span in block.get("spans") or [])
            if JUNK_TEXT.match(text) or COOKIE_NOTICE.match(text):
                continue
        elif block.get("type") == "heading":
            text = block.get("text") or ""
            if JUNK_TEXT.match(text):
                continue
            # The nested-accordion toggle is normally removed by its class, but
            # this also repairs older/variant templates where it was already
            # flattened into the heading text.
            cleaned = re.sub(r"\s+(?:View|Close)\s*$", "", text, flags=re.IGNORECASE)
            if cleaned != text:
                block = {**block, "text": cleaned}
        elif block.get("type") == "list":
            items = [rich_to_text(item) for item in block.get("items") or []]
            # A JavaScript-enhanced select is emitted twice by the source page:
            # once as <option>s and once as a Selectric <ul>. Neither is useful
            # without the form, and rendering the latter as a real content list
            # is especially misleading.
            if items and JUNK_TEXT.match(items[0]) and all(len(item) <= 80 for item in items):
                continue
        kept.append(block)

    # Heading text may have lost a trailing toggle word above; rebuild anchors
    # so the outline and the actual heading still point at the same id.
    taken: set[str] = set()
    for block in kept:
        if block.get("type") == "heading":
            block["id"] = _slug(block.get("text") or "", taken)
    return kept


def _accordion_questions(soup: BeautifulSoup) -> None:
    """Turn each accordion toggle into the heading it is.

    The question of a collapsed Q&A is the text of a ``<button>`` that opens
    the answer, and buttons are dropped as page controls - so the student pass
    page kept 75 answers and not one of the questions they answer ("Can I work
    while studying?"). A toggle inside a heading leaves its text in the
    heading; one on its own becomes a heading. The answers were never the
    problem: they are in the HTML, collapsed only by a stylesheet.
    """
    for button in soup.select("button[aria-controls], button[aria-expanded]"):
        text = _clean(button.get_text(" ", strip=True)).strip()
        if not text or JUNK_TEXT.match(text):
            continue
        if button.find_parent(list(HEADINGS)):
            button.replace_with(text)
            continue
        heading = soup.new_tag("h4")
        heading.string = text
        button.replace_with(heading)


def _holds_sections(node: Tag) -> bool:
    """A list used as a page layout - an accordion of questions - not a list.

    Read as bullets, each item was flattened to its first paragraph and lost
    its heading, its other paragraphs, its own lists and the tables in it.
    """
    if any("accordion" in c for c in node.get("class") or []):
        return True
    return any(
        item.find(list(HEADINGS)) is not None
        for item in node.find_all("li", recursive=False)
    )


def clean_page(html: str, *, url: str) -> dict:
    """Return ``{title, headings, blocks, clean_text, summary, content_hash}``."""
    soup = BeautifulSoup(html, "lxml")

    # HTML comments first. BeautifulSoup's get_text() returns Comment nodes
    # along with real text, and Monash's CMS leaves a lot of them: a fees page
    # arrived with "endnoindex", "@@ WIP @@", "Micro Banner: Do Not Display",
    # "/.call-to-action__wrapper" and "Remove below on 1.1.9 release" as
    # paragraphs, which were then indexed, translated and shown to a student.
    for comment in soup.find_all(string=lambda node: isinstance(node, Comment)):
        comment.extract()

    _accordion_questions(soup)
    for tag in soup(list(DROP_TAGS)):
        tag.decompose()
    for selector in DROP_SELECTORS:
        for tag in soup.select(selector):
            tag.decompose()

    title = ""
    if soup.title and soup.title.string:
        title = soup.title.string.strip()
    h1 = soup.find("h1")
    if h1:
        heading_text = h1.get_text(" ", strip=True)
        if heading_text:
            title = heading_text
    title = re.sub(r"\s*\|\s*Monash University\s*$", "", title).strip()
    title = re.sub(r"\s*-\s*Current students\s*$", "", title).strip()

    # The most specific selector with real text in it. A page whose article is
    # only a title keeps its short article: falling back to the whole body made
    # 314 near-empty pages read "We use cookies to improve your experience".
    matched = [found for selector in CONTENT_SELECTORS if (found := soup.select_one(selector))]
    body = next((found for found in matched if len(found.get_text(strip=True)) > 200), None)
    if body is None:
        body = matched[0] if matched else soup.body or soup

    # Before the outline and the search text are derived from them, so all
    # three agree about what is on the page.
    blocks = _absolute_links(_drop_junk(_extract_blocks(body)), url)
    headings = [
        {"level": b["level"], "text": b["text"], "id": b["id"]}
        for b in blocks
        if b["type"] == "heading"
    ]
    clean_text = blocks_to_text(blocks)
    summary = _first_meaningful_paragraph(blocks) or clean_text[:400] or None

    return {
        "title": title or url,
        "headings": headings,
        "blocks": blocks,
        "clean_text": clean_text,
        "summary": summary,
        "content_hash": content_hash(title, clean_text, blocks=blocks),
    }


def _first_meaningful_paragraph(blocks: list[dict[str, Any]]) -> str | None:
    for block in blocks:
        if block["type"] != "paragraph":
            continue
        text = rich_to_text(block["spans"])
        if len(text) >= 80:
            return WS_RE.sub(" ", text)[:600]
    return None


def content_hash(title: str, clean_text: str, *, blocks: list[dict] | None = None) -> str:
    """Hash the extracted content, so template churn does not read as a change.

    ``EXTRACTOR_VERSION`` is part of the input on purpose: when the extraction
    changes, every page has to look changed, or the crawl reports "unchanged"
    against text produced by code that no longer exists.
    """
    payload = f"{EXTRACTOR_VERSION}\n{title.strip()}\n{clean_text.strip()}"
    if blocks is not None:
        payload += "\n" + json.dumps(blocks, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
