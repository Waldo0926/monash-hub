"""Pure identity and URL boundaries for Malaysia programme evidence."""

from __future__ import annotations

import re
from urllib.parse import urlsplit, urlunsplit


def title_key(title: str | None) -> str:
    text = " ".join((title or "").split()).casefold().replace("&", " and ")
    text = re.sub(r"\s*\((?:phd|mphil|dhes)\)\s*$", "", text)
    text = re.sub(r"^(bachelor|master|doctor|diploma) in ", r"\1 of ", text)
    return " ".join(text.split())


def programme_url(value: str | None) -> str | None:
    """Only HTTPS Malaysia degree/pathway pages, never generic Apply/fee links."""
    if not isinstance(value, str):
        return None
    try:
        u = urlsplit(value)
        if u.scheme != "https" or u.netloc != "www.monash.edu.my" or u.query:
            return None
        parts = u.path.strip("/").split("/")
        if len(parts) < 4 or parts[:2] not in (
            ["study", "undergraduate"],
            ["study", "postgraduate-and-research"],
        ):
            return None
        if not re.match(
            r"^(?:bachelor|master|doctor|phd|mphil|postgraduate|graduate|diploma)", parts[-1]
        ):
            return None
        return urlunsplit((u.scheme, u.netloc, u.path.rstrip("/"), "", ""))
    except ValueError:
        return None
