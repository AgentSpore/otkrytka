"""Backend hardening regressions: upload byte-cap + decompression-bomb + EXIF
strip, atomic card-cap under concurrency, add-after-lock, WAL + busy_timeout,
file unlink on delete, cross-board image binding, path-traversal-safe unlink,
and oEmbed 404 on an unknown slug.
"""

import asyncio
import io
import os
import struct
import zlib

import aiosqlite
import pytest
from fastapi import HTTPException
from PIL import Image

from otkrytka.api.boards import _UPLOAD_CHUNK, _read_capped
from otkrytka.core.config import get_settings
from otkrytka.core.db import init_db
from otkrytka.core.limits import BodySizeLimitMiddleware
from otkrytka.services import board_service


# --- helpers -------------------------------------------------------------------

def _jpeg_bytes(size=(64, 64), color=(200, 120, 90)) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", size, color).save(buf, format="JPEG")
    return buf.getvalue()


def _png_with_declared_size(width: int, height: int) -> bytes:
    """A minimal PNG whose IHDR declares (width, height) with a valid CRC but
    almost no pixel data — Pillow reads the huge size from the header on open()
    without decoding, which is exactly what the decompression-bomb guard checks.
    """
    sig = b"\x89PNG\r\n\x1a\n"
    ihdr_data = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)  # 8-bit RGB
    ihdr = (
        struct.pack(">I", len(ihdr_data))
        + b"IHDR"
        + ihdr_data
        + struct.pack(">I", zlib.crc32(b"IHDR" + ihdr_data) & 0xFFFFFFFF)
    )
    iend = struct.pack(">I", 0) + b"IEND" + struct.pack(">I", zlib.crc32(b"IEND") & 0xFFFFFFFF)
    return sig + ihdr + iend


async def _make_board(client, title="Открытка"):
    body = (await client.post("/api/v1/boards", json={"title": title})).json()
    return body["slug"], body["organizer_token"]


async def _board_id(client, slug):
    return (await client.get(f"/api/v1/boards/{slug}")).json()["id"]


async def _upload(client, slug):
    return await client.post(
        f"/api/v1/boards/{slug}/upload",
        files={"file": ("photo.jpg", _jpeg_bytes(), "image/jpeg")},
    )


# --- 1. upload byte-cap streaming + decompression bomb -------------------------

@pytest.mark.asyncio
async def test_oversized_upload_rejected_413(client):
    slug, _ = await _make_board(client)
    max_bytes = get_settings().max_upload_mb * 1024 * 1024
    payload = b"\xff\xd8\xff" + b"0" * (max_bytes + 5_000)
    res = await client.post(
        f"/api/v1/boards/{slug}/upload",
        files={"file": ("huge.jpg", payload, "image/jpeg")},
    )
    assert res.status_code == 413
    assert res.json()["detail"]["code"] == "image_too_large"


@pytest.mark.asyncio
async def test_read_capped_stops_before_buffering_whole_stream():
    """The capped reader never buffers past cap + one chunk (no unbounded read)."""
    cap = 100 * 1024

    class _BigFile:
        def __init__(self):
            self.served = 0

        async def read(self, n):
            # Endless stream: a broken reader would spin forever / OOM.
            self.served += n
            return b"x" * n

    f = _BigFile()
    with pytest.raises(HTTPException) as exc:
        await _read_capped(f, cap)
    assert exc.value.status_code == 413
    assert f.served <= cap + _UPLOAD_CHUNK


@pytest.mark.asyncio
async def test_decompression_bomb_rejected(client):
    slug, _ = await _make_board(client)
    # ~4.4 gigapixel declared in a few dozen bytes: rejected on the header, no OOM.
    bomb = _png_with_declared_size(66_000, 66_000)
    res = await client.post(
        f"/api/v1/boards/{slug}/upload",
        files={"file": ("bomb.png", bomb, "image/png")},
    )
    assert res.status_code == 413
    assert res.json()["detail"]["code"] == "image_too_large"


# --- 2. EXIF orientation applied + stripped ------------------------------------

@pytest.mark.asyncio
async def test_exif_rotated_jpeg_is_transposed_and_stripped(client):
    slug, _ = await _make_board(client)
    # A 40x20 image tagged orientation=6 (rotate 90 CW) should come out 20x40
    # with no EXIF block in the stored file.
    base = Image.new("RGB", (40, 20), (10, 200, 90))
    exif = base.getexif()
    exif[0x0112] = 6  # Orientation tag
    buf = io.BytesIO()
    base.save(buf, format="JPEG", exif=exif)

    res = await client.post(
        f"/api/v1/boards/{slug}/upload",
        files={"file": ("rot.jpg", buf.getvalue(), "image/jpeg")},
    )
    assert res.status_code == 200
    stored = os.path.join(
        get_settings().upload_dir, res.json()["image_path"].removeprefix("/uploads/")
    )
    with Image.open(stored) as im:
        assert im.size == (20, 40)  # transposed
        assert not dict(im.getexif())  # EXIF stripped on re-encode


# --- 3. atomic card cap under concurrency + add-after-lock ----------------------

@pytest.mark.asyncio
async def test_concurrent_adds_never_exceed_cap(client):
    slug, _ = await _make_board(client)
    # Fill to five below the cap, then fire many concurrent adds for the last slots.
    for i in range(95):
        r = await client.post(
            f"/api/v1/boards/{slug}/cards",
            json={"author_name": f"G{i}", "text": "!"},
        )
        assert r.status_code == 200

    async def add(i):
        return await client.post(
            f"/api/v1/boards/{slug}/cards",
            json={"author_name": f"C{i}", "text": "!"},
        )

    results = await asyncio.gather(*(add(i) for i in range(30)))
    ok = [r for r in results if r.status_code == 200]
    full = [r for r in results if r.status_code == 400]
    assert len(ok) == 5  # exactly the 5 remaining slots
    assert all(r.json()["detail"]["code"] == "board_full" for r in full)

    body = (await client.get(f"/api/v1/boards/{slug}")).json()
    assert len(body["cards"]) == 100  # never overbooked


@pytest.mark.asyncio
async def test_add_after_lock_is_409(client):
    slug, token = await _make_board(client)
    bid = await _board_id(client, slug)
    await client.patch(f"/api/v1/boards/{bid}/lock", json={"organizer_token": token})
    res = await client.post(
        f"/api/v1/boards/{slug}/cards", json={"author_name": "Поздно", "text": "!"}
    )
    assert res.status_code == 409
    assert res.json()["detail"]["code"] == "board_locked"


# --- 4. WAL + busy_timeout -----------------------------------------------------

@pytest.mark.asyncio
async def test_wal_and_busy_timeout_on_fresh_connection():
    await init_db()
    settings = get_settings()
    async with aiosqlite.connect(settings.db_path, isolation_level=None) as db:
        await db.execute("PRAGMA busy_timeout = 5000")
        async with db.execute("PRAGMA journal_mode") as cur:
            jm = (await cur.fetchone())[0]
        async with db.execute("PRAGMA busy_timeout") as cur:
            bt = (await cur.fetchone())[0]
    assert jm.lower() == "wal"
    assert bt > 0


# --- 5. delete unlinks files ---------------------------------------------------

@pytest.mark.asyncio
async def test_delete_card_unlinks_file(client):
    slug, token = await _make_board(client)
    image_path = (await _upload(client, slug)).json()["image_path"]
    stored = os.path.join(get_settings().upload_dir, image_path.removeprefix("/uploads/"))
    assert os.path.exists(stored)
    card = (await client.post(
        f"/api/v1/boards/{slug}/cards",
        json={"author_name": "Лев", "image_path": image_path},
    )).json()

    await client.request(
        "DELETE", f"/api/v1/cards/{card['id']}", json={"organizer_token": token}
    )
    assert not os.path.exists(stored)


@pytest.mark.asyncio
async def test_delete_board_unlinks_files(client):
    slug, token = await _make_board(client)
    image_path = (await _upload(client, slug)).json()["image_path"]
    stored = os.path.join(get_settings().upload_dir, image_path.removeprefix("/uploads/"))
    await client.post(
        f"/api/v1/boards/{slug}/cards",
        json={"author_name": "Лев", "image_path": image_path},
    )
    assert os.path.exists(stored)

    bid = await _board_id(client, slug)
    res = await client.request(
        "DELETE", f"/api/v1/boards/{bid}", json={"organizer_token": token}
    )
    assert res.status_code == 204
    assert not os.path.exists(stored)  # public file purged on delete


# --- 6. cross-board image binding (422) ----------------------------------------

@pytest.mark.asyncio
async def test_image_path_from_another_board_rejected(client):
    slug_a, _ = await _make_board(client, title="A")
    slug_b, _ = await _make_board(client, title="B")
    # File minted for board A, attached to board B -> 422.
    image_path = (await _upload(client, slug_a)).json()["image_path"]
    res = await client.post(
        f"/api/v1/boards/{slug_b}/cards",
        json={"author_name": "X", "image_path": image_path},
    )
    assert res.status_code == 422
    assert res.json()["detail"]["code"] == "image_wrong_board"


# --- 7. path-traversal-safe unlink ---------------------------------------------

def test_upload_basename_rejects_traversal():
    assert board_service._upload_basename("/uploads/../x") is None
    assert board_service._upload_basename("/uploads/a/b") is None
    assert board_service._upload_basename("/uploads/") is None
    assert board_service._upload_basename("/etc/passwd") is None
    assert board_service._upload_basename("/uploads/ok123.jpg") == "ok123.jpg"


def test_safe_unlink_never_escapes_uploads_dir(monkeypatch, tmp_path):
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()
    outside = tmp_path / "secret.txt"
    outside.write_text("do not delete")

    settings = get_settings()
    monkeypatch.setattr(settings, "upload_dir", str(upload_dir))

    # Every traversal attempt must be a no-op; the outside file survives.
    for evil in (
        "/uploads/../secret.txt",
        "/uploads/../../secret.txt",
        "/uploads/a/b",
        "/etc/passwd",
    ):
        board_service._safe_unlink(evil)
    assert outside.exists()

    # A legitimate bare name inside the uploads dir IS unlinked.
    victim = upload_dir / "gone.jpg"
    victim.write_bytes(b"x")
    board_service._safe_unlink("/uploads/gone.jpg")
    assert not victim.exists()


# --- 8. oEmbed unknown slug -> 404 ---------------------------------------------

@pytest.mark.asyncio
async def test_oembed_unknown_slug_is_404(client, monkeypatch):
    canon = "https://otkrytka.agentspore.com"
    monkeypatch.setattr(get_settings(), "canonical_base_url", canon)
    # Well-formed card URL on our host, but the slug does not exist.
    res = await client.get(f"/oembed?url={canon}/c/zzz9999&format=json")
    assert res.status_code == 404


# --- CRIT 1: real ASGI body-size cap (aborts before full spool) ----------------

@pytest.mark.asyncio
async def test_body_size_middleware_aborts_before_full_spool():
    """The middleware raises 413 mid-stream, so the parser never spools the rest.

    A downstream app draining the body must observe FEWER chunks than were sent,
    proving the oversized body was cut off before being fully received/spooled.
    """
    max_bytes = 1000
    consumed = {"chunks": 0}

    async def fake_app(scope, receive, send):
        while True:
            msg = await receive()  # raises _BodyTooLarge once the cap is crossed
            consumed["chunks"] += 1
            if not msg.get("more_body"):
                break

    mw = BodySizeLimitMiddleware(fake_app, max_upload_bytes=max_bytes)
    cap = mw.upload_max
    chunk = b"x" * (cap // 2 + 1)  # three of these overflow the cap
    parts = [
        {"type": "http.request", "body": chunk, "more_body": True},
        {"type": "http.request", "body": chunk, "more_body": True},
        {"type": "http.request", "body": chunk, "more_body": True},
        {"type": "http.request", "body": b"", "more_body": False},
    ]
    it = iter(parts)

    async def receive():
        return next(it)

    sent = []

    async def send(message):
        sent.append(message)

    scope = {
        "type": "http",
        "method": "POST",
        "path": "/api/v1/boards/abc1234/upload",
        "headers": [],
    }
    await mw(scope, receive, send)

    starts = [m for m in sent if m["type"] == "http.response.start"]
    assert starts and starts[0]["status"] == 413
    assert consumed["chunks"] < 4  # aborted before draining the whole body


@pytest.mark.asyncio
async def test_body_size_middleware_content_length_fast_path():
    async def fake_app(scope, receive, send):  # must never be reached
        raise AssertionError("app should not run for an over-length declared body")

    mw = BodySizeLimitMiddleware(fake_app, max_upload_bytes=1000)
    scope = {
        "type": "http",
        "method": "POST",
        "path": "/api/v1/boards/abc1234/upload",
        "headers": [(b"content-length", str(mw.upload_max + 1).encode())],
    }
    sent = []

    async def send(message):
        sent.append(message)

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    await mw(scope, receive, send)
    assert any(m["type"] == "http.response.start" and m["status"] == 413 for m in sent)


# --- CRIT 2: shared image_path survives a sibling delete -----------------------

@pytest.mark.asyncio
async def test_delete_card_keeps_shared_image(client):
    slug, token = await _make_board(client)
    image_path = (await _upload(client, slug)).json()["image_path"]
    stored = os.path.join(get_settings().upload_dir, image_path.removeprefix("/uploads/"))

    # Two cards reference the SAME uploaded file.
    c1 = (await client.post(
        f"/api/v1/boards/{slug}/cards",
        json={"author_name": "A", "image_path": image_path},
    )).json()
    await client.post(
        f"/api/v1/boards/{slug}/cards",
        json={"author_name": "B", "image_path": image_path},
    )
    assert os.path.exists(stored)

    # Deleting one must NOT orphan the other card's image.
    await client.request(
        "DELETE", f"/api/v1/cards/{c1['id']}", json={"organizer_token": token}
    )
    assert os.path.exists(stored)  # sibling still references it
    body = (await client.get(f"/api/v1/boards/{slug}")).json()
    assert [c["image_path"] for c in body["cards"]] == [image_path]


# --- W6: bomb guard mid-band (my explicit check) + just-under acceptance --------

@pytest.mark.asyncio
async def test_bomb_midband_rejected_by_explicit_check(client):
    slug, _ = await _make_board(client)
    # 6500*6500 = 42.25 MP: over _MAX_PIXELS (40 MP) but under Pillow's 2x error
    # band, so it must be rejected by OUR explicit header check, not Pillow's.
    assert board_service._MAX_PIXELS < 6500 * 6500 < 2 * board_service._MAX_PIXELS
    bomb = _png_with_declared_size(6500, 6500)
    res = await client.post(
        f"/api/v1/boards/{slug}/upload",
        files={"file": ("mid.png", bomb, "image/png")},
    )
    assert res.status_code == 413
    assert res.json()["detail"]["code"] == "image_too_large"


@pytest.mark.asyncio
async def test_large_image_just_under_pixel_cap_accepted(client):
    slug, _ = await _make_board(client)
    # 6200*6200 = 38.44 MP < 40 MP: a real (solid-color, tiny compressed) image
    # just under the cap is accepted and thumbnailed down to the 1600px bound.
    assert 6200 * 6200 < board_service._MAX_PIXELS
    buf = io.BytesIO()
    Image.new("RGB", (6200, 6200), (30, 120, 200)).save(buf, format="PNG")
    res = await client.post(
        f"/api/v1/boards/{slug}/upload",
        files={"file": ("big.png", buf.getvalue(), "image/png")},
    )
    assert res.status_code == 200
    stored = os.path.join(
        get_settings().upload_dir, res.json()["image_path"].removeprefix("/uploads/")
    )
    with Image.open(stored) as im:
        assert max(im.size) <= 1600


# --- TOCTOU: concurrent delete_card + add_card never dangles a file ------------

@pytest.mark.asyncio
async def test_delete_and_add_race_no_dangling_file(client):
    """delete_card(A) racing add_card(B, same image) must never leave a surviving
    card pointing at a deleted file: either B is rejected (file unlinked, no card
    refs it) or B commits first (delete sees the sibling and keeps the file)."""
    slug, token = await _make_board(client)
    image_path = (await _upload(client, slug)).json()["image_path"]
    stored = os.path.join(get_settings().upload_dir, image_path.removeprefix("/uploads/"))
    a = (await client.post(
        f"/api/v1/boards/{slug}/cards",
        json={"author_name": "A", "image_path": image_path},
    )).json()

    async def do_delete():
        return await client.request(
            "DELETE", f"/api/v1/cards/{a['id']}", json={"organizer_token": token}
        )

    async def do_add():
        return await client.post(
            f"/api/v1/boards/{slug}/cards",
            json={"author_name": "B", "image_path": image_path},
        )

    await asyncio.gather(do_delete(), do_add())

    body = (await client.get(f"/api/v1/boards/{slug}")).json()
    # INVARIANT: every surviving card's image file must exist on disk.
    for c in body["cards"]:
        if c["image_path"]:
            path = os.path.join(
                get_settings().upload_dir, c["image_path"].removeprefix("/uploads/")
            )
            assert os.path.exists(path), f"card {c['id']} points at a missing file"
    # If no card survived referencing it, the file must have been unlinked.
    if not any(c["image_path"] == image_path for c in body["cards"]):
        assert not os.path.exists(stored)


# --- App-wide default cap on non-upload JSON routes ----------------------------

@pytest.mark.asyncio
async def test_oversized_json_body_rejected_413(client):
    # A > 64 KB JSON body on POST /boards is rejected by the middleware before
    # routing/validation (the field cap would 422 a valid-shape body far smaller).
    huge = "x" * (70 * 1024)
    res = await client.post("/api/v1/boards", json={"title": huge})
    assert res.status_code == 413
    assert res.json()["detail"]["code"] == "request_too_large"
