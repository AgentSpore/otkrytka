"""Image upload endpoint: accept a valid jpg, reject wrong type + oversize."""

import io
import os

import pytest
from PIL import Image

from otkrytka.core.config import get_settings


def _jpeg_bytes(size=(64, 64), color=(200, 120, 90)) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", size, color).save(buf, format="JPEG")
    return buf.getvalue()


async def _make_board(client):
    return (await client.post("/api/v1/boards", json={"title": "Открытка"})).json()["slug"]


@pytest.mark.asyncio
async def test_upload_accepts_jpeg(client):
    slug = await _make_board(client)
    res = await client.post(
        f"/api/v1/boards/{slug}/upload",
        files={"file": ("photo.jpg", _jpeg_bytes(), "image/jpeg")},
    )
    assert res.status_code == 200
    path = res.json()["image_path"]
    assert path.startswith("/uploads/")
    assert path.endswith(".jpg")


@pytest.mark.asyncio
async def test_upload_rejects_wrong_type(client):
    slug = await _make_board(client)
    res = await client.post(
        f"/api/v1/boards/{slug}/upload",
        files={"file": ("note.txt", b"this is not an image", "text/plain")},
    )
    assert res.status_code == 415


@pytest.mark.asyncio
async def test_upload_rejects_oversize(client):
    slug = await _make_board(client)
    max_bytes = get_settings().max_upload_mb * 1024 * 1024
    payload = b"\xff\xd8\xff" + b"0" * (max_bytes + 10)
    res = await client.post(
        f"/api/v1/boards/{slug}/upload",
        files={"file": ("huge.jpg", payload, "image/jpeg")},
    )
    assert res.status_code == 413


@pytest.mark.asyncio
async def test_upload_reencodes_and_shrinks_large_image(client):
    slug = await _make_board(client)
    # 2400px wide should be thumbnailed down to the 1600px cap on the server.
    big = _jpeg_bytes(size=(2400, 1200))
    res = await client.post(
        f"/api/v1/boards/{slug}/upload",
        files={"file": ("big.jpg", big, "image/jpeg")},
    )
    assert res.status_code == 200
    filename = res.json()["image_path"].removeprefix("/uploads/")
    stored = os.path.join(get_settings().upload_dir, filename)
    with Image.open(stored) as im:
        assert max(im.size) <= 1600


@pytest.mark.asyncio
async def test_upload_on_unknown_board_is_404(client):
    res = await client.post(
        "/api/v1/boards/nope000/upload",
        files={"file": ("photo.jpg", _jpeg_bytes(), "image/jpeg")},
    )
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_upload_to_locked_board_rejected_without_writing_file(client):
    created = (await client.post("/api/v1/boards", json={"title": "Открытка"})).json()
    slug, token = created["slug"], created["organizer_token"]
    board = (await client.get(f"/api/v1/boards/{slug}")).json()
    await client.patch(f"/api/v1/boards/{board['id']}/lock", json={"organizer_token": token})

    upload_dir = get_settings().upload_dir
    before = set(os.listdir(upload_dir)) if os.path.isdir(upload_dir) else set()

    res = await client.post(
        f"/api/v1/boards/{slug}/upload",
        files={"file": ("photo.jpg", _jpeg_bytes(), "image/jpeg")},
    )
    assert res.status_code == 409
    after = set(os.listdir(upload_dir)) if os.path.isdir(upload_dir) else set()
    # No orphan file should have been written for the rejected upload.
    assert after == before
