"""Storing a profile picture.

This is the first thing on the platform a stranger can put on our disk, and the
rules follow from that rather than from what is convenient.

**We never store the bytes we were given.** The upload is decoded with Pillow
and re-encoded as WebP, so what lands on disk is a file this process produced.
That kills the whole class of files that are a valid image *and* something else
- the polyglots that get served back under our own domain. A file we cannot
decode is refused, which also rejects SVG, the one image format that is a
script.

**It is capped before it is decoded.** A decompression bomb is a small file that
becomes an enormous bitmap, so the pixel count is checked from the header before
any pixels are allocated.

**The filename is ours and carries a random component.** Not the uploaded name -
that is attacker-controlled and full of `../`. The random part means a changed
avatar gets a new URL, so a stale cache cannot show the old one and an old URL
handed around does not keep working forever.

The file is written to a directory nginx serves directly. The API never reads it
back: a request for an avatar should not wake Python up.
"""
from __future__ import annotations

import contextlib
import io
import secrets
from pathlib import Path

from PIL import Image, UnidentifiedImageError

from app.core.config import get_settings

# Displayed at 96px at the largest, so 256 covers a 2x screen with room spare.
SIZE = 256
# Before decoding. A photo straight off a phone is under this; anything larger
# is not a profile picture.
MAX_BYTES = 4 * 1024 * 1024
# Pillow's own bomb guard is generous. A 40 megapixel source is already far more
# than a 256px square needs.
MAX_PIXELS = 40_000_000
QUALITY = 82


class AvatarError(ValueError):
    """The upload is not something we are willing to store."""


def _target_dir() -> Path:
    directory = Path(get_settings().avatar_dir)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def store(data: bytes, user_id: int) -> str:
    """Decode, square, shrink, re-encode. Returns the file name to record.

    Raises :class:`AvatarError` for anything that is not a decodable image.
    """
    if not data:
        raise AvatarError("The file is empty.")
    if len(data) > MAX_BYTES:
        raise AvatarError("That image is larger than 4MB.")

    try:
        with Image.open(io.BytesIO(data)) as probe:
            width, height = probe.size
            if width * height > MAX_PIXELS:
                raise AvatarError("That image has too many pixels to process.")
            # Some formats only reveal breakage on load, which is the point of
            # doing it here rather than trusting the header.
            probe.load()
            image = probe.convert("RGB")
    except AvatarError:
        raise
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        # Includes SVG, which Pillow cannot open - and which is a script.
        raise AvatarError("That file is not an image we can read.") from exc

    image = _square(image)
    image.thumbnail((SIZE, SIZE), Image.LANCZOS)

    buffer = io.BytesIO()
    image.save(buffer, format="WEBP", quality=QUALITY, method=4)

    # The user id makes the file identifiable when looking at the directory; the
    # random half is what stops a new avatar reusing the old URL.
    name = f"{user_id}-{secrets.token_hex(8)}.webp"
    (_target_dir() / name).write_bytes(buffer.getvalue())
    return name


def _square(image: Image.Image) -> Image.Image:
    """Centre crop, because a circle mask over a portrait cuts off a face."""
    width, height = image.size
    if width == height:
        return image
    side = min(width, height)
    left = (width - side) // 2
    top = (height - side) // 2
    return image.crop((left, top, left + side, top + side))


def remove(name: str | None) -> None:
    """Delete a stored avatar, ignoring one that is already gone.

    Called when the avatar is replaced, so the directory does not accumulate
    every picture the user has ever had.
    """
    if not name:
        return
    # The name always comes from our own column, but a path separator in it
    # would still write outside the directory, so it is checked rather than
    # trusted.
    if "/" in name or "\\" in name or name.startswith("."):
        return
    # A file we cannot delete is a tidiness problem, not a request failure.
    with contextlib.suppress(OSError):
        (_target_dir() / name).unlink(missing_ok=True)


def url_for(name: str | None) -> str | None:
    if not name:
        return None
    prefix = get_settings().avatar_url_prefix.rstrip("/")
    return f"{prefix}/{name}"
