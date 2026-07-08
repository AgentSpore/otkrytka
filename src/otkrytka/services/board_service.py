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
import warnings
from urllib.parse import urlparse

import aiosqlite
from fastapi import HTTPException
from loguru import logger
from PIL import Image, ImageOps, UnidentifiedImageError

from ..core.config import get_settings

_SLUG_ALPHABET = string.ascii_lowercase + string.digits
_SLUG_LEN = 7
_SLUG_MAX_TRIES = 20
_CARDS_MAX = 100
# Per-board upload cap: files uploaded but never attached to a card are only
# reclaimed when the board is deleted, so bound the orphan pile per board. Set
# above _CARDS_MAX to tolerate re-picks (upload, change your mind, upload again)
# without blocking a legitimate contributor.
_UPLOADS_MAX = 300

# Server-side upload enforcement.
_ALLOWED_FORMATS = {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp"}
_MAX_IMAGE_DIM = 1600
# Hard cap on decoded pixel count (decompression-bomb guard): a small highly
# compressed file can declare huge dimensions that blow up on decode. 40 MP is
# well above any legitimate phone photo. Checked from the header BEFORE decode.
_MAX_PIXELS = 40_000_000
_UPLOAD_PREFIX = "/uploads/"
_GIF_EXTS = (".gif", ".webp", ".png", ".jpg", ".jpeg")

# Make Pillow itself refuse an oversized decode as a second line of defense; the
# explicit header check below is primary (rejects before any decode).
Image.MAX_IMAGE_PIXELS = _MAX_PIXELS


def api_error(status_code: int, code: str, message: str) -> HTTPException:
    """Build an HTTPException carrying a stable machine-readable ``code`` so the
    RU frontend can localize the message instead of showing raw English.

    The response body is ``{"detail": {"code": ..., "message": ...}}`` — ONE
    consistent mechanism across every participant-facing state/validation error.
    """
    return HTTPException(status_code=status_code, detail={"code": code, "message": message})


def _gen_slug() -> str:
    return "".join(secrets.choice(_SLUG_ALPHABET) for _ in range(_SLUG_LEN))


def _gen_token() -> str:
    return secrets.token_urlsafe(24)


def _validate_gif_url(gif_url: str) -> None:
    """Reject anything that is not a plain http(s) image URL (blocks javascript:/data:)."""
    parsed = urlparse(gif_url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise api_error(400, "gif_url_invalid", "GIF link must be an http(s) URL")
    if not parsed.path.lower().endswith(_GIF_EXTS):
        raise api_error(400, "gif_url_not_image", "GIF link must point at an image file")


def _validate_image_path(image_path: str) -> None:
    """Only paths minted by our own upload endpoint are accepted as card images."""
    if not image_path.startswith(_UPLOAD_PREFIX) or "/" in image_path[len(_UPLOAD_PREFIX):]:
        raise api_error(400, "image_ref_invalid", "Unknown image reference")


def _upload_basename(image_path: str) -> str | None:
    """Return the bare ``<name>`` from a well-formed ``/uploads/<name>`` path, or
    ``None`` if the path is not a bare single-segment upload reference.

    Path-traversal safety: any ``/``, ``\\`` or ``..`` in the name -> ``None``,
    so callers can only ever address a file directly inside the uploads dir.
    """
    if not image_path or not image_path.startswith(_UPLOAD_PREFIX):
        return None
    name = image_path[len(_UPLOAD_PREFIX):]
    if not name or "/" in name or "\\" in name or ".." in name:
        return None
    if os.path.basename(name) != name:
        return None
    return name


def _safe_unlink(image_path: str | None) -> None:
    """Best-effort delete of an uploaded file, confined to the uploads dir.

    Never unlinks outside the uploads dir: the stored path must be a bare
    ``/uploads/<name>`` (validated by ``_upload_basename``) and the resolved
    target must still live under the uploads dir.
    """
    if not image_path:
        return
    name = _upload_basename(image_path)
    if name is None:
        return
    upload_dir = os.path.realpath(get_settings().upload_dir)
    full = os.path.realpath(os.path.join(upload_dir, name))
    if os.path.commonpath([upload_dir, full]) != upload_dir:
        return
    try:
        os.remove(full)
    except FileNotFoundError:
        pass  # already gone -> nothing to reclaim, not an anomaly
    except OSError as exc:
        # A public /uploads file that failed to delete keeps serving deleted
        # content; surface it (loguru brace-style lazy args, no f-string).
        logger.warning("Failed to unlink upload file {}: {}", full, exc)


def _check_token(board: aiosqlite.Row, organizer_token: str) -> None:
    """Constant-time compare of the organizer secret; 403 on mismatch."""
    if not secrets.compare_digest(board["organizer_token"], organizer_token):
        raise api_error(403, "organizer_token_required", "Organizer token required")


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
        raise api_error(404, "board_not_found", "Board not found")
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
        raise api_error(404, "board_not_found", "Board not found")
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
        raise api_error(404, "card_not_found", "Card not found")
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
    raise api_error(500, "slug_unavailable", "Could not allocate a unique link")


async def lock_board(db: aiosqlite.Connection, board_id: int, organizer_token: str) -> dict:
    """Freeze the board so no further cards can be added (organizer only)."""
    board = await _board_row_by_id(db, board_id)
    _check_token(board, organizer_token)
    await db.execute("UPDATE boards SET locked = 1 WHERE id = ?", (board_id,))
    await db.commit()
    return await get_board(db, board["slug"])


async def delete_board(db: aiosqlite.Connection, board_id: int, organizer_token: str) -> None:
    """Soft-delete the board (reversible) AND purge its uploaded files (not).

    The row is soft-deleted so ``restore_board`` can bring back the text of every
    wish, but the uploaded image files are unlinked immediately: ``/uploads`` is a
    public static mount that would otherwise keep serving a deleted card's photos
    forever. Restore therefore recovers text but not photos — an intentional
    privacy-over-reversibility trade-off for the image files.
    """
    board = await _board_row_by_id(db, board_id)
    _check_token(board, organizer_token)
    # Read the file list, soft-delete the board and drop its upload rows inside ONE
    # BEGIN IMMEDIATE, serialized against _insert_card_atomic: a concurrent upload
    # either commits first (its row is in `names` and gets unlinked) or blocks then
    # sees deleted_at set (add_card 404s / binding 422s). Files are unlinked only
    # AFTER commit.
    db.row_factory = aiosqlite.Row
    await db.execute("BEGIN IMMEDIATE")
    try:
        async with db.execute(
            "SELECT filename FROM uploads WHERE board_id = ?", (board_id,)
        ) as cur:
            names = [r["filename"] for r in await cur.fetchall()]
        await db.execute(
            "UPDATE boards SET deleted_at = CURRENT_TIMESTAMP "
            "WHERE id = ? AND deleted_at IS NULL",
            (board_id,),
        )
        await db.execute("DELETE FROM uploads WHERE board_id = ?", (board_id,))
        await db.execute("COMMIT")
    except BaseException:
        await db.execute("ROLLBACK")
        raise
    for name in names:
        _safe_unlink(f"{_UPLOAD_PREFIX}{name}")


async def restore_board(db: aiosqlite.Connection, board_id: int, organizer_token: str) -> dict:
    """Undo a soft-delete; returns the restored board (404 if unknown)."""
    db.row_factory = aiosqlite.Row
    async with db.execute(
        "SELECT organizer_token FROM boards WHERE id = ?", (board_id,)
    ) as cur:
        row = await cur.fetchone()
    if row is None:
        raise api_error(404, "board_not_found", "Board not found")
    if not secrets.compare_digest(row["organizer_token"], organizer_token):
        raise api_error(403, "organizer_token_required", "Organizer token required")
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
        raise api_error(409, "board_locked", "This card is closed for new wishes")

    # Strip here too: the direct-service path (and any non-schema caller) must not
    # store a whitespace-only author that only looks non-empty.
    clean_author = author_name.strip()
    if not clean_author:
        raise api_error(400, "author_required", "Please add your name")

    clean_text = text.strip() if text else None
    clean_gif = gif_url.strip() if gif_url else None
    clean_image = image_path.strip() if image_path else None
    if not clean_text and not clean_gif and not clean_image:
        raise api_error(400, "content_required", "Add some words, a photo or a GIF")
    if clean_gif:
        _validate_gif_url(clean_gif)
    if clean_image:
        _validate_image_path(clean_image)  # cheap format/traversal pre-check (400)

    card_id = await _insert_card_atomic(
        db, board["id"], clean_author, clean_text, clean_image, clean_gif
    )
    return _card_out(await _card_row(db, card_id))


async def _insert_card_atomic(
    db: aiosqlite.Connection,
    board_id: int,
    author: str,
    text: str | None,
    image_path: str | None,
    gif_url: str | None,
) -> int:
    """Recheck lock + card cap + upload binding and INSERT inside a single
    ``BEGIN IMMEDIATE`` so two concurrent posts can never overbook the cap or land
    after a lock, and a card can never be inserted referencing a file that a
    concurrent ``delete_card`` is about to unlink.

    ``BEGIN IMMEDIATE`` takes the write lock up front, serializing writers against
    each other AND against ``_delete_card_atomic``; the connection's
    ``busy_timeout`` makes a competitor wait rather than fail. The upload-binding
    check MUST live here (not before the transaction) so that a delete which drops
    the uploads row commits-then-blocks this insert into a 422 instead of leaving
    the new card pointing at a just-deleted file.
    """
    db.row_factory = aiosqlite.Row
    await db.execute("BEGIN IMMEDIATE")
    try:
        async with db.execute(
            "SELECT locked FROM boards WHERE id = ? AND deleted_at IS NULL", (board_id,)
        ) as cur:
            brow = await cur.fetchone()
        if brow is None:
            raise api_error(404, "board_not_found", "Board not found")
        if brow["locked"]:
            raise api_error(409, "board_locked", "This card is closed for new wishes")
        async with db.execute(
            "SELECT COUNT(*) AS n FROM cards WHERE board_id = ?", (board_id,)
        ) as cur:
            if (await cur.fetchone())["n"] >= _CARDS_MAX:
                # 400 (not 409) to preserve the existing client contract for the cap.
                raise api_error(400, "board_full", f"A card can hold at most {_CARDS_MAX} wishes")
        if image_path is not None:
            name = _upload_basename(image_path)
            if name is None:
                raise api_error(422, "image_wrong_board", "Image was not uploaded for this card")
            async with db.execute(
                "SELECT 1 FROM uploads WHERE filename = ? AND board_id = ?", (name, board_id)
            ) as cur:
                if await cur.fetchone() is None:
                    raise api_error(422, "image_wrong_board", "Image was not uploaded for this card")
        ins = await db.execute(
            "INSERT INTO cards (board_id, author_name, text, image_path, gif_url) "
            "VALUES (?, ?, ?, ?, ?)",
            (board_id, author, text, image_path, gif_url),
        )
        await db.execute("COMMIT")
        return ins.lastrowid
    except BaseException:
        await db.execute("ROLLBACK")
        raise


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
    """Hard-delete a card (organizer only) and unlink its uploaded file (if any).

    The delete is irreversible, so removing the backing file reclaims disk and
    stops ``/uploads/<name>`` from serving a wish the organizer deleted — but ONLY
    when no OTHER live card still references the same file (two cards can share
    one uploaded image), else the sibling's image would be orphaned.
    """
    card = await _card_row(db, card_id)
    board = await _board_row_by_id(db, card["board_id"])
    _check_token(board, organizer_token)
    image_path = card["image_path"]
    # The sibling-check + card DELETE + uploads-row DELETE run in ONE
    # BEGIN IMMEDIATE, serialized against _insert_card_atomic, so a concurrent
    # add_card cannot insert a new card referencing this file between the check
    # and the unlink. Unlink happens AFTER commit and only when no sibling refs it.
    shared = await _delete_card_atomic(db, card_id, image_path)
    if not shared:
        _safe_unlink(image_path)


async def _delete_card_atomic(
    db: aiosqlite.Connection, card_id: int, image_path: str | None
) -> bool:
    """Delete the card and (if its file is unreferenced) its uploads row, atomically.

    Returns whether another live card still references ``image_path`` — the caller
    unlinks the file only when this is ``False``.
    """
    db.row_factory = aiosqlite.Row
    await db.execute("BEGIN IMMEDIATE")
    try:
        shared = False
        if image_path:
            async with db.execute(
                "SELECT 1 FROM cards WHERE image_path = ? AND id != ? LIMIT 1",
                (image_path, card_id),
            ) as cur:
                shared = await cur.fetchone() is not None
        await db.execute("DELETE FROM cards WHERE id = ?", (card_id,))
        if image_path and not shared:
            name = _upload_basename(image_path)
            if name is not None:
                await db.execute("DELETE FROM uploads WHERE filename = ?", (name,))
        await db.execute("COMMIT")
        return shared
    except BaseException:
        await db.execute("ROLLBACK")
        raise


# --- Image upload (local disk, Pillow validate + re-encode) ----------------

async def ensure_accepting_cards(db: aiosqlite.Connection, slug: str) -> int:
    """Guard the upload path with the same 404/409 as card-create; return board id.

    Called BEFORE any bytes hit disk so a locked or soft-deleted board never
    accumulates orphan files that no card will ever reference. The returned id is
    used to bind the minted file to this board (see ``register_upload``).
    """
    board = await _board_row(db, slug)  # 404 if missing or soft-deleted
    if board["locked"]:
        raise api_error(409, "board_locked", "This card is closed for new wishes")
    # Cap the per-board upload pile so a caller cannot fill the disk by uploading
    # (without ever attaching) forever; orphans are otherwise freed at board delete.
    async with db.execute(
        "SELECT COUNT(*) AS n FROM uploads WHERE board_id = ?", (board["id"],)
    ) as cur:
        if (await cur.fetchone())["n"] >= _UPLOADS_MAX:
            raise api_error(429, "upload_limit", "Too many uploads for this card")
    return board["id"]


async def register_upload(db: aiosqlite.Connection, board_id: int, image_path: str) -> None:
    """Bind a freshly minted upload filename to the board it was uploaded for, so
    ``add_card`` can enforce that a card only references its own board's files and
    delete can find files to unlink."""
    name = _upload_basename(image_path)
    if name is None:  # defensive: save_upload always mints a bare name
        return
    await db.execute(
        "INSERT OR IGNORE INTO uploads (filename, board_id) VALUES (?, ?)",
        (name, board_id),
    )
    await db.commit()


def save_upload(data: bytes) -> str:
    """Validate + re-encode an uploaded image to local disk; return its URL path.

    Enforces the size cap (413), the jpg/png/webp allowlist (415) and a
    decompression-bomb pixel cap (413) on the server, independent of the client.
    The pixel count is checked from the header BEFORE ``load()`` so a small file
    declaring huge dimensions is rejected without decoding it. EXIF orientation
    is applied then stripped by re-encoding through Pillow. Returns
    ``/uploads/<name><ext>``.
    """
    settings = get_settings()
    if len(data) > settings.max_upload_mb * 1024 * 1024:
        raise api_error(413, "image_too_large", "Image is too large")

    try:
        # Silence Pillow's MAX..2*MAX warning at open(): the explicit size check
        # below rejects that band ourselves. The > 2*MAX case still raises
        # DecompressionBombError (an error, not a warning) and is handled here.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", Image.DecompressionBombWarning)
            img = Image.open(io.BytesIO(data))  # header only, no decode yet
    except Image.DecompressionBombError as exc:
        # Pillow rejects a header declaring > 2 * MAX_IMAGE_PIXELS at open() time.
        raise api_error(413, "image_too_large", "Image dimensions are too large") from exc
    except (UnidentifiedImageError, OSError) as exc:
        raise api_error(415, "image_unsupported_type", "Unsupported image type") from exc

    # Decompression-bomb guard for the MAX..2*MAX band: reject on declared
    # dimensions before decoding.
    width, height = img.size
    if width * height > _MAX_PIXELS:
        raise api_error(413, "image_too_large", "Image dimensions are too large")

    if _ALLOWED_FORMATS.get(img.format or "") is None:
        raise api_error(415, "image_unsupported_type", "Only JPEG, PNG or WEBP images are allowed")
    fmt = img.format
    ext = _ALLOWED_FORMATS[fmt]

    try:
        # DecompressionBombWarning -> error, so a file between MAX_PIXELS and the
        # header check's blind spot still fails closed on decode.
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            img.load()
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
        raise api_error(415, "image_unsupported_type", "Unsupported image type") from exc
    except Image.DecompressionBombWarning as exc:
        raise api_error(413, "image_too_large", "Image dimensions are too large") from exc

    # Respect EXIF orientation (phone photos), then re-encode strips all metadata.
    img = ImageOps.exif_transpose(img)
    if max(img.size) > _MAX_IMAGE_DIM:
        img.thumbnail((_MAX_IMAGE_DIM, _MAX_IMAGE_DIM))
    if fmt == "JPEG" and img.mode not in ("RGB", "L"):
        img = img.convert("RGB")

    os.makedirs(settings.upload_dir, exist_ok=True)
    filename = secrets.token_urlsafe(16) + ext
    save_kwargs = {"quality": 85, "optimize": True} if fmt == "JPEG" else {}
    img.save(os.path.join(settings.upload_dir, filename), format=fmt, **save_kwargs)
    return f"{_UPLOAD_PREFIX}{filename}"
