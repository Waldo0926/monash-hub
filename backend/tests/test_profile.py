"""Your own profile, and the avatar upload.

The upload is the first thing on this platform that lets a stranger put a file
on our disk, so most of these tests are about what it refuses.
"""
from __future__ import annotations

import io

import pytest
from app.core import avatars
from app.core.security import hash_password
from app.models.user import User
from PIL import Image


@pytest.fixture
def account(db):
    user = User(
        email="waldo@example.com", nickname="Waldo",
        password_hash=hash_password("Correct-Horse-9"), is_active=True,
    )
    db.add(user)
    db.commit()
    return user


@pytest.fixture
def signed_in(client, account):
    token = client.post(
        "/api/v1/auth/signin",
        json={"email": "waldo@example.com", "password": "Correct-Horse-9"},
    ).json()["token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def avatar_dir(tmp_path, monkeypatch):
    from app.core.config import get_settings

    settings = get_settings()
    monkeypatch.setattr(settings, "avatar_dir", str(tmp_path), raising=False)
    return tmp_path


def _png(size=(400, 300), colour=(200, 30, 30)) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", size, colour).save(buffer, format="PNG")
    return buffer.getvalue()


# --- what the store refuses ----------------------------------------------

def test_a_file_that_is_not_an_image_is_refused(avatar_dir):
    """Including SVG, which Pillow cannot open - and which is a script."""
    for data in (
        b"<svg xmlns='http://www.w3.org/2000/svg'><script>alert(1)</script></svg>",
        b"not an image at all",
        b"\x89PNG\r\n\x1a\n truncated",
    ):
        with pytest.raises(avatars.AvatarError):
            avatars.store(data, user_id=1)


def test_an_empty_upload_is_refused(avatar_dir):
    with pytest.raises(avatars.AvatarError):
        avatars.store(b"", user_id=1)


def test_an_oversized_upload_is_refused_before_it_is_decoded(avatar_dir):
    with pytest.raises(avatars.AvatarError, match="4MB"):
        avatars.store(b"\x00" * (avatars.MAX_BYTES + 1), user_id=1)


# --- what it stores -------------------------------------------------------

def test_the_stored_file_is_one_we_produced(avatar_dir):
    """Re-encoding is what makes an uploaded file safe to serve back."""
    name = avatars.store(_png(), user_id=7)
    written = (avatar_dir / name).read_bytes()

    assert name.startswith("7-") and name.endswith(".webp")
    with Image.open(io.BytesIO(written)) as image:
        assert image.format == "WEBP"
    # And it is not the bytes that came in.
    assert written != _png()


def test_a_rectangle_is_centre_cropped_to_a_square(avatar_dir):
    name = avatars.store(_png(size=(1000, 400)), user_id=1)
    with Image.open(avatar_dir / name) as image:
        assert image.width == image.height


def test_a_large_image_is_shrunk(avatar_dir):
    name = avatars.store(_png(size=(2000, 2000)), user_id=1)
    with Image.open(avatar_dir / name) as image:
        assert max(image.size) == avatars.SIZE


def test_each_upload_gets_its_own_name(avatar_dir):
    """A reused name would let a cache keep showing the picture you replaced."""
    first = avatars.store(_png(), user_id=1)
    second = avatars.store(_png(), user_id=1)
    assert first != second


def test_remove_ignores_a_name_that_could_escape_the_directory(avatar_dir):
    outside = avatar_dir.parent / "keep-me"
    outside.write_text("not an avatar")
    avatars.remove("../keep-me")
    assert outside.exists(), "a path separator must never reach unlink()"


# --- the endpoints --------------------------------------------------------

def test_a_profile_is_only_ever_your_own(client):
    """There is no endpoint that takes a user id, so nothing to enumerate."""
    assert client.get("/api/v1/profile").status_code == 401


def test_the_profile_reports_what_you_have_written(client, signed_in, avatar_dir):
    body = client.get("/api/v1/profile", headers=signed_in).json()
    assert body["nickname"] == "Waldo"
    assert body["avatar_url"] is None
    assert body["counts"] == {"posts": 0, "answers": 0, "bookmarks": 0}
    assert body["joined_at"]


def test_uploading_and_then_removing_a_picture(client, signed_in, avatar_dir):
    upload = client.post(
        "/api/v1/profile/avatar",
        headers=signed_in,
        files={"file": ("me.png", _png(), "image/png")},
    )
    assert upload.status_code == 200
    url = upload.json()["avatar_url"]
    assert url.startswith("/avatars/") and url.endswith(".webp")
    assert len(list(avatar_dir.iterdir())) == 1

    cleared = client.delete("/api/v1/profile/avatar", headers=signed_in)
    assert cleared.json()["avatar_url"] is None
    assert list(avatar_dir.iterdir()) == [], "the file goes with the record"


def test_replacing_a_picture_does_not_leave_the_old_one_behind(
    client, signed_in, avatar_dir
):
    for _ in range(3):
        client.post(
            "/api/v1/profile/avatar",
            headers=signed_in,
            files={"file": ("me.png", _png(), "image/png")},
        )
    assert len(list(avatar_dir.iterdir())) == 1


def test_a_rejected_upload_says_why(client, signed_in, avatar_dir):
    response = client.post(
        "/api/v1/profile/avatar",
        headers=signed_in,
        files={"file": ("x.svg", b"<svg/>", "image/svg+xml")},
    )
    assert response.status_code == 400
    assert "image" in response.json()["detail"].lower()


def test_the_nickname_is_checked_the_way_registration_checks_it(client, signed_in):
    """A name that could not be registered must not be reachable by editing."""
    response = client.patch("/api/v1/profile", headers=signed_in, json={"nickname": "a"})
    assert response.status_code == 400


def test_a_taken_nickname_is_refused(client, signed_in, db):
    db.add(User(email="other@example.com", nickname="Taken",
                password_hash=hash_password("Correct-Horse-9"), is_active=True))
    db.commit()
    response = client.patch("/api/v1/profile", headers=signed_in, json={"nickname": "taken"})
    assert response.status_code == 409


def test_changing_your_own_nickname_to_its_current_value_is_fine(client, signed_in):
    response = client.patch("/api/v1/profile", headers=signed_in, json={"nickname": "Waldo"})
    assert response.status_code == 200


def test_an_empty_bio_removes_it(client, signed_in):
    client.patch("/api/v1/profile", headers=signed_in, json={"bio": "Third year, Malaysia."})
    assert client.get("/api/v1/profile", headers=signed_in).json()["bio"] == "Third year, Malaysia."

    client.patch("/api/v1/profile", headers=signed_in, json={"bio": "   "})
    assert client.get("/api/v1/profile", headers=signed_in).json()["bio"] is None


def test_activity_starts_empty_and_never_401s_for_a_new_account(client, signed_in):
    body = client.get("/api/v1/profile/activity", headers=signed_in).json()
    assert body == {"posts": [], "answered": [], "bookmarks": []}
