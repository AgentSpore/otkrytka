"""aiosqlite-backed store + orchestration for «Открытка».

Transactions (commit) are owned here per the connection passed in from the
router dependency. The service also owns the organizer-token guard (HTTP 403),
the lock guard (HTTP 409), the per-board card cap (HTTP 400), and server-side
image validation / re-encoding via Pillow.
"""

import io
import os
import secrets
import string
from urllib.parse import urlparse

import aiosqlite
from fastapi import HTTPException
from PIL import Image, UnidentifiedImageError

from ..core.config import get_settings

_SLUG_ALPHABET = string.ascii_lowercase + string.digits
_SLUG_LEN = 7
_SLUG_MAX_TRIES = 20
_CARDS_MAX = 100

# Server-side upload enforcement.
_ALLOWED_FORMATS = {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp"}
_MAX_IMAGE_DIM = 1600
_UPLOAD_PREFIX = "/uploads/"
_GIF_EXTS = (".gif", ".webp", ".png", ".jpg", ".jpeg")


def _gen_slug() -> str:
    return "".join(secrets.choice(_SLUG_ALPHABET) for _ in range(_SLUG_LEN))


def _gen_token() -> str:
    return secrets.token_urlsafe(24)


def _validate_gif_url(gif_url: str) -> None:
    """Reject anything that is not a plain http(s) image URL (blocks javascript:/data:)."""
    parsed = urlparse(gif_url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise HTTPException(status_code=400, detail="GIF link must be an http(s) URL")
    if not parsed.path.lower().endswith(_GIF_EXTS):
        raise HTTPException(status_code=400, detail="GIF link must point at an image file")


def _validate_image_path(image_path: str) -> None:
    """Only paths minted by our own upload endpoint are accepted as card images."""
    if not image_path.startswith(_UPLOAD_PREFIX) or "/" in image_path[len(_UPLOAD_PREFIX):]:
        raise HTTPException(status_code=400, detail="Unknown image reference")


def _check_token(board: aiosqlite.Row, organizer_token: str) -> None:
    """Constant-time compare of the organizer secret; 403 on mismatch."""
    if not secrets.compare_digest(board["organizer_token"], organizer_token):
        raise HTTPException(status_code=403, detail="Organizer token required")


# --- Row helpers -----------------------------------------------------------

async def _board_row(db: aiosqlite.Connection, slug: str) -> aiosqlite.Row:
    db.row_factory = aiosqlite.Row
    async with db.execute(
        "SELECT id, slug, title, recipient, cover, organizer_token, locked "
        "FROM boards WHERE slug = ? AND deleted_at IS NULL",
        (slug,),
    ) as cur:
        row = await cur.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Board not found")
    return row


async def _board_row_by_id(db: aiosqlite.Connection, board_id: int) -> aiosqlite.Row:
    # Filter soft-deleted rows so id-based mutations cannot resurrect a deleted
    # board via a guessable numeric id. restore_board clears deleted_at BEFORE
    # calling this, so it is unaffected.
    db.row_factory = aiosqlite.Row
    async with db.execute(
        "SELECT id, slug, title, recipient, cover, organizer_token, locked "
        "FROM boards WHERE id = ? AND deleted_at IS NULL",
        (board_id,),
    ) as cur:
        row = await cur.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Board not found")
    return row


async def _card_row(db: aiosqlite.Connection, card_id: int) -> aiosqlite.Row:
    db.row_factory = aiosqlite.Row
    async with db.execute(
        "SELECT id, board_id, author_name, text, image_path, gif_url, pinned "
        "FROM cards WHERE id = ?",
        (card_id,),
    ) as cur:
        row = await cur.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Card not found")
    return row


# --- Slug resolvers (for live-update broadcast) ----------------------------

async def slug_for_board_id(db: aiosqlite.Connection, board_id: int) -> str | None:
    db.row_factory = aiosqlite.Row
    async with db.execute("SELECT slug FROM boards WHERE id = ?", (board_id,)) as cur:
        row = await cur.fetchone()
    return row["slug"] if row else None


async def slug_for_card(db: aiosqlite.Connection, card_id: int) -> str | None:
    db.row_factory = aiosqlite.Row
    async with db.execute(
        "SELECT b.slug AS slug FROM boards b "
        "JOIN cards c ON c.board_id = b.id WHERE c.id = ?",
        (card_id,),
    ) as cur:
        row = await cur.fetchone()
    return row["slug"] if row else None


# --- Read assembly ---------------------------------------------------------

def _card_out(r: aiosqlite.Row) -> dict:
    return {
        "id": r["id"],
        "author_name": r["author_name"],
        "text": r["text"],
        "image_path": r["image_path"],
        "gif_url": r["gif_url"],
        "pinned": bool(r["pinned"]),
    }


async def _cards_out(db: aiosqlite.Connection, board_id: int) -> list[dict]:
    db.row_factory = aiosqlite.Row
    # Pinned cards first, then newest to oldest.
    async with db.execute(
        "SELECT id, board_id, author_name, text, image_path, gif_url, pinned "
        "FROM cards WHERE board_id = ? ORDER BY pinned DESC, id DESC",
        (board_id,),
    ) as cur:
        rows = await cur.fetchall()
    return [_card_out(r) for r in rows]


async def get_board(db: aiosqlite.Connection, slug: str) -> dict:
    board = await _board_row(db, slug)
    return {
        "id": board["id"],
        "slug": board["slug"],
        "title": board["title"],
        "recipient": board["recipient"],
        "cover": board["cover"],
        "locked": bool(board["locked"]),
        "cards": await _cards_out(db, board["id"]),
    }


# --- Board create / lock / soft-delete -------------------------------------

async def create_board(
    db: aiosqlite.Connection,
    title: str,
    recipient: str | None,
    cover: str | None,
) -> dict:
    token = _gen_token()
    for _ in range(_SLUG_MAX_TRIES):
        slug = _gen_slug()
        try:
            await db.execute(
                "INSERT INTO boards (slug, title, recipient, cover, organizer_token) "
                "VALUES (?, ?, ?, ?, ?)",
                (slug, title, recipient, cover or "", token),
            )
            await db.commit()
            # organizer_token is returned exactly once, to the creator.
            return {"slug": slug, "organizer_token": token}
        except aiosqlite.IntegrityError:
            await db.rollback()
            continue
    raise HTTPException(status_code=500, detail="Could not allocate a unique link")


async def lock_board(db: aiosqlite.Connection, board_id: int, organizer_token: str) -> dict:
    """Freeze the board so no further cards can be added (organizer only)."""
    board = await _board_row_by_id(db, board_id)
    _check_token(board, organizer_token)
    await db.execute("UPDATE boards SET locked = 1 WHERE id = ?", (board_id,))
    await db.commit()
    return await get_board(db, board["slug"])


async def delete_board(db: aiosqlite.Connection, board_id: int, organizer_token: str) -> None:
    """Soft-delete: hide the board but keep it so a delete can be undone."""
    board = await _board_row_by_id(db, board_id)
    _check_token(board, organizer_token)
    await db.execute(
        "UPDATE boards SET deleted_at = CURRENT_TIMESTAMP "
        "WHERE id = ? AND deleted_at IS NULL",
        (board_id,),
    )
    await db.commit()


async def restore_board(db: aiosqlite.Connection, board_id: int, organizer_token: str) -> dict:
    """Undo a soft-delete; returns the restored board (404 if unknown)."""
    db.row_factory = aiosqlite.Row
    async with db.execute(
        "SELECT organizer_token FROM boards WHERE id = ?", (board_id,)
    ) as cur:
        row = await cur.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Board not found")
    if not secrets.compare_digest(row["organizer_token"], organizer_token):
        raise HTTPException(status_code=403, detail="Organizer token required")
    await db.execute("UPDATE boards SET deleted_at = NULL WHERE id = ?", (board_id,))
    await db.commit()
    return await get_board(db, (await _board_row_by_id(db, board_id))["slug"])


# --- Cards -----------------------------------------------------------------

async def add_card(
    db: aiosqlite.Connection,
    slug: str,
    author_name: str,
    text: str | None,
    gif_url: str | None,
    image_path: str | None,
) -> dict:
    board = await _board_row(db, slug)
    if board["locked"]:
        raise HTTPException(status_code=409, detail="This card is closed for new wishes")

    # Strip here too: the direct-service path (and any non-schema caller) must not
    # store a whitespace-only author that only looks non-empty.
    clean_author = author_name.strip()
    if not clean_author:
        raise HTTPException(status_code=400, detail="Please add your name")

    clean_text = text.strip() if text else None
    clean_gif = gif_url.strip() if gif_url else None
    clean_image = image_path.strip() if image_path else None
    if not clean_text and not clean_gif and not clean_image:
        raise HTTPException(status_code=400, detail="Add some words, a photo or a GIF")
    if clean_gif:
        _validate_gif_url(clean_gif)
    if clean_image:
        _validate_image_path(clean_image)

    db.row_factory = aiosqlite.Row
    async with db.execute(
        "SELECT COUNT(*) AS n FROM cards WHERE board_id = ?", (board["id"],)
    ) as cur:
        agg = await cur.fetchone()
    if agg["n"] >= _CARDS_MAX:
        raise HTTPException(
            status_code=400, detail=f"A card can hold at most {_CARDS_MAX} wishes"
        )

    cur = await db.execute(
        "INSERT INTO cards (board_id, author_name, text, image_path, gif_url) "
        "VALUES (?, ?, ?, ?, ?)",
        (board["id"], clean_author, clean_text, clean_image, clean_gif),
    )
    await db.commit()
    return _card_out(await _card_row(db, cur.lastrowid))


async def pin_card(db: aiosqlite.Connection, card_id: int, organizer_token: str) -> dict:
    """Toggle a card's pinned flag (organizer only)."""
    card = await _card_row(db, card_id)
    board = await _board_row_by_id(db, card["board_id"])
    _check_token(board, organizer_token)
    new_pinned = 0 if card["pinned"] else 1
    await db.execute("UPDATE cards SET pinned = ? WHERE id = ?", (new_pinned, card_id))
    await db.commit()
    return _card_out(await _card_row(db, card_id))


async def delete_card(db: aiosqlite.Connection, card_id: int, organizer_token: str) -> None:
    """Hard-delete a card (organizer only)."""
    card = await _card_row(db, card_id)
    board = await _board_row_by_id(db, card["board_id"])
    _check_token(board, organizer_token)
    await db.execute("DELETE FROM cards WHERE id = ?", (card_id,))
    await db.commit()


# --- Image upload (local disk, Pillow validate + re-encode) ----------------

async def ensure_accepting_cards(db: aiosqlite.Connection, slug: str) -> None:
    """Guard the upload path with the same 404/409 as card-create.

    Called BEFORE any bytes hit disk so a locked or soft-deleted board never
    accumulates orphan files that no card will ever reference.
    """
    board = await _board_row(db, slug)  # 404 if missing or soft-deleted
    if board["locked"]:
        raise HTTPException(status_code=409, detail="This card is closed for new wishes")


def save_upload(data: bytes) -> str:
    """Validate + re-encode an uploaded image to local disk; return its URL path.

    Enforces the size cap (413) and the jpg/png/webp allowlist (415) on the
    server, independent of the client. Re-encoding through Pillow strips any
    embedded metadata and normalizes the file. Returns ``/uploads/<name><ext>``.
    """
    settings = get_settings()
    if len(data) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Image is too large")

    try:
        img = Image.open(io.BytesIO(data))
        img.load()
    except (UnidentifiedImageError, OSError) as exc:
        raise HTTPException(status_code=415, detail="Unsupported image type") from exc

    ext = _ALLOWED_FORMATS.get(img.format or "")
    if ext is None:
        raise HTTPException(
            status_code=415, detail="Only JPEG, PNG or WEBP images are allowed"
        )

    fmt = img.format
    if max(img.size) > _MAX_IMAGE_DIM:
        img.thumbnail((_MAX_IMAGE_DIM, _MAX_IMAGE_DIM))
    if fmt == "JPEG" and img.mode not in ("RGB", "L"):
        img = img.convert("RGB")

    os.makedirs(settings.upload_dir, exist_ok=True)
    filename = secrets.token_urlsafe(16) + ext
    save_kwargs = {"quality": 85, "optimize": True} if fmt == "JPEG" else {}
    img.save(os.path.join(settings.upload_dir, filename), format=fmt, **save_kwargs)
    return f"{_UPLOAD_PREFIX}{filename}"
