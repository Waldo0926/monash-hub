"""Reduce an official Monash page to searchable text plus structure.

We keep the title, the heading outline, a short summary and the body text - and
nothing else. No images, no stylesheets, no PDFs, no attachments. The Hub links
back to the source for anything richer, which keeps disk cost flat and keeps us
an index rather than a copy of someone else's site.
"""
from __future__ import annotations

import hashlib
import re

from bs4 import BeautifulSoup

DROP_TAGS = ("script", "style", "noscript", "svg", "iframe", "form", "button")
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
)
CONTENT_SELECTORS = ("main", "[role=main]", "#main-content", "article", ".content-main")

WS_RE = re.compile(r"[ \t\xa0]+")
BLANK_RE = re.compile(r"\n{3,}")


def _text_of(node) -> str:
    text = node.get_text("\n", strip=True)
    text = WS_RE.sub(" ", text)
    return BLANK_RE.sub("\n\n", text).strip()


def clean_page(html: str, *, url: str) -> dict:
    """Return ``{title, headings, clean_text, summary, content_hash}``."""
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

    body = None
    for selector in CONTENT_SELECTORS:
        found = soup.select_one(selector)
        if found and len(found.get_text(strip=True)) > 200:
            body = found
            break
    if body is None:
        body = soup.body or soup

    headings = []
    for level in ("h2", "h3"):
        for tag in body.find_all(level):
            label = tag.get_text(" ", strip=True)
            if label:
                headings.append({"level": int(level[1]), "text": label})

    clean_text = _text_of(body)
    summary = _first_meaningful_paragraph(body) or clean_text[:400] or None

    return {
        "title": title or url,
        "headings": headings,
        "clean_text": clean_text,
        "summary": summary,
        "content_hash": content_hash(title, clean_text),
    }


def _first_meaningful_paragraph(body) -> str | None:
    for paragraph in body.find_all("p"):
        text = paragraph.get_text(" ", strip=True)
        if len(text) >= 80:
            return WS_RE.sub(" ", text)[:600]
    return None


def content_hash(title: str, clean_text: str) -> str:
    """Hash the extracted content, so template churn does not read as a change."""
    payload = f"{title.strip()}\n{clean_text.strip()}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
