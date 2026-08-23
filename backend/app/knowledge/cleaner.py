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
import re
import unicodedata
from typing import Any

from bs4 import BeautifulSoup, NavigableString, Tag

# Bumped when the extraction itself changes. It goes into the content hash, so
# the next crawl re-writes every page instead of reporting "unchanged" and
# leaving the old shape in the database forever.
EXTRACTOR_VERSION = 3

DROP_TAGS = ("script", "style", "noscript", "svg", "iframe", "form", "button")

# Template plumbing that renders as a sentence. Monash ships an unconfigured
# share widget on many pages and it comes through the extractor as a paragraph
# reading "Social Media Share Bar: Not Configured", which then goes on to be
# indexed, translated and shown to a student as if it were content.
JUNK_TEXT = re.compile(
    r"^\s*(?:social media share bar\s*:?\s*not configured|not configured|"
    r"skip to (?:content|main content)|back to top)\s*$",
    re.IGNORECASE,
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
    # The same content as the desktop tabs beside it. See the module docstring.
    ".desktop-hidden",
    # A search widget, not content: it extracts to "Search / Top FAQs / Chat".
    ".monash-faq-help-panel",
    ".visuallyhidden",
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
    return bool(href) and not href.startswith(("#", "javascript:"))


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


def _table_rows(rows: list[Tag]) -> list[list[str]]:
    """Cells as plain strings, with ``colspan`` expanded into blank neighbours.

    Merged cells are rare here and only ever appear in a totals row, so the
    simple expansion keeps every row the same width without the block format
    having to carry a span for each cell.
    """
    out = []
    for row in rows:
        cells: list[str] = []
        for cell in row.find_all(["td", "th"], recursive=False):
            try:
                span = max(1, int(str(cell.get("colspan", 1)).strip()))
            except (TypeError, ValueError):
                span = 1
            cells.append(_flat(cell))
            cells.extend([""] * (span - 1))
        if any(cells):
            out.append(cells)
    return out


def _table_block(table: Tag) -> dict[str, Any] | None:
    caption = table.find("caption")
    head = table.find("thead")
    body = table.find("tbody")
    foot = table.find("tfoot")

    header_rows = _table_rows(head.find_all("tr")) if head else []
    columns = header_rows[0] if header_rows else []

    container = body or table
    body_rows = _table_rows(
        [tr for tr in container.find_all("tr") if tr.find_parent(["thead", "tfoot"]) is None]
    )
    if not head and body_rows:
        # No <thead>: if the first row is all <th>, it is the header anyway.
        first = container.find("tr")
        if first is not None and first.find("td") is None and first.find("th") is not None:
            columns, body_rows = body_rows[0], body_rows[1:]

    foot_rows = _table_rows(foot.find_all("tr")) if foot else []

    if not body_rows and not columns:
        return None

    width = max(len(columns), *(len(r) for r in body_rows + foot_rows), 0)
    block: dict[str, Any] = {
        "type": "table",
        "columns": columns + [""] * (width - len(columns)),
        "rows": [r + [""] * (width - len(r)) for r in body_rows],
    }
    if caption:
        text = _flat(caption)
        if text:
            block["caption"] = text
    if foot_rows:
        block["foot"] = [r + [""] * (width - len(r)) for r in foot_rows]
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
                if text and node.name in CONTAINERS:
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
            elif name in ("ul", "ol"):
                block = _list_block(child)
                if block:
                    blocks.append(block)
                for nested in child.select("li > ul, li > ol"):
                    nested_block = _list_block(nested)
                    if nested_block:
                        blocks.append(nested_block)
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
        return f"t:{block.get('caption', '')}:{block['columns']}:{block['rows']}"
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
            marker = "1." if block["ordered"] else "•"
            lines.extend(f"{marker} {rich_to_text(item)}" for item in block["items"])
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
            if JUNK_TEXT.match(text):
                continue
        elif block.get("type") == "heading" and JUNK_TEXT.match(block.get("text") or ""):
            continue
        kept.append(block)
    return kept


def clean_page(html: str, *, url: str) -> dict:
    """Return ``{title, headings, blocks, clean_text, summary, content_hash}``."""
    soup = BeautifulSoup(html, "lxml")

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

    body = None
    for selector in CONTENT_SELECTORS:
        found = soup.select_one(selector)
        if found and len(found.get_text(strip=True)) > 200:
            body = found
            break
    if body is None:
        body = soup.body or soup

    # Before the outline and the search text are derived from them, so all
    # three agree about what is on the page.
    blocks = _drop_junk(_extract_blocks(body))
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
        "content_hash": content_hash(title, clean_text),
    }


def _first_meaningful_paragraph(blocks: list[dict[str, Any]]) -> str | None:
    for block in blocks:
        if block["type"] != "paragraph":
            continue
        text = rich_to_text(block["spans"])
        if len(text) >= 80:
            return WS_RE.sub(" ", text)[:600]
    return None


def content_hash(title: str, clean_text: str) -> str:
    """Hash the extracted content, so template churn does not read as a change.

    ``EXTRACTOR_VERSION`` is part of the input on purpose: when the extraction
    changes, every page has to look changed, or the crawl reports "unchanged"
    against text produced by code that no longer exists.
    """
    payload = f"{EXTRACTOR_VERSION}\n{title.strip()}\n{clean_text.strip()}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
