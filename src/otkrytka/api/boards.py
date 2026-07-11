"""HTTP routes for «Открытка» under ``/api/v1`` (no trailing slash).

The DB connection is created in the dependency and passed into the service; the
service owns transactions + guards. Routes stay thin: validate, delegate,
notify, return. Every mutation broadcasts a live ``changed`` signal over the
board's WebSocket so new cards appear for everyone watching.
"""

import aiosqlite
from fastapi import (
    APIRouter,
    Depends,
    File,
    UploadFile,
    WebSocket,
    WebSocketDisconnect,
)

from ..core.config import get_settings
from ..core.db import get_db
from ..core.realtime import hub
from ..schemas.board import BoardCreate, CardCreate, OrganizerAction
from ..services import board_service

router = APIRouter()

# Read the upload body in bounded chunks so an oversized stream is rejected
# before the whole file is buffered into RAM (413), rather than after. This is an
# intentional second layer behind the ASGI BodySizeLimitMiddleware: the middleware
# caps raw wire bytes (envelope + overhead) while this caps the decoded file part,
# and save_upload re-checks len(data) — redundant on purpose across the
# multipart-vs-raw boundary, defense in depth for the one DoS-prone route.
_UPLOAD_CHUNK = 64 * 1024


async def _read_capped(file: UploadFile, max_bytes: int) -> bytes:
    """Buffer the upload up to ``max_bytes``; stop and raise 413 once exceeded.

    Never buffers more than one chunk past the cap, so an attacker cannot force
    an unbounded read by lying about Content-Length.
    """
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = await file.read(_UPLOAD_CHUNK)
        if not chunk:
            break
        total += len(chunk)
        if total > max_bytes:
            raise board_service.api_error(413, "image_too_large", "Image is too large")
        chunks.append(chunk)
    return b"".join(chunks)


async def _notify(slug: str | None) -> None:
    """Best-effort live-update broadcast; ``hub.publish`` never raises."""
    if slug:
        await hub.publish(slug)


# --- Live updates ----------------------------------------------------------

@router.websocket("/boards/{slug}/ws")
async def board_ws(slug: str, ws: WebSocket):
    """Live channel for a board: pushes ``{"type": "changed"}`` on any mutation.

    Inbound client messages are ignored; the receive loop exists only to detect
    disconnects. The client refetches ``GET /boards/{slug}`` on each signal.
    """
    await hub.connect(slug, ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        await hub.disconnect(slug, ws)


# --- Boards ----------------------------------------------------------------

@router.post("/boards", response_model=dict)
async def create_board(payload: BoardCreate, db: aiosqlite.Connection = Depends(get_db)):
    return await board_service.create_board(
        db, payload.title, payload.recipient, payload.cover
    )


@router.get("/boards/{slug}", response_model=dict)
async def get_board(slug: str, db: aiosqlite.Connection = Depends(get_db)):
    return await board_service.get_board(db, slug)


@router.post("/boards/{slug}/cards", response_model=dict)
async def add_card(
    slug: str, payload: CardCreate, db: aiosqlite.Connection = Depends(get_db)
):
    out = await board_service.add_card(
        db, slug, payload.author_name, payload.text, payload.gif_url, payload.image_path
    )
    await _notify(slug)
    return out


@router.post("/boards/{slug}/upload", response_model=dict)
async def upload_image(
    slug: str,
    file: UploadFile = File(...),
    db: aiosqlite.Connection = Depends(get_db),
):
    # 404 if the board is gone, 409 if it is locked — checked BEFORE reading the
    # upload so a closed/deleted board never accumulates an orphan file on disk.
    board_id = await board_service.ensure_accepting_cards(db, slug)
    max_bytes = get_settings().max_upload_mb * 1024 * 1024
    data = await _read_capped(file, max_bytes)
    image_path = board_service.save_upload(data)
    # Bind the minted file to this board so add_card can enforce ownership (422)
    # and delete can later unlink it.
    await board_service.register_upload(db, board_id, image_path)
    return {"image_path": image_path}


@router.patch("/boards/{board_id}/lock", response_model=dict)
async def lock_board(
    board_id: int, payload: OrganizerAction, db: aiosqlite.Connection = Depends(get_db)
):
    out = await board_service.lock_board(db, board_id, payload.organizer_token)
    await _notify(await board_service.slug_for_board_id(db, board_id))
    return out


@router.patch("/boards/{board_id}/unlock", response_model=dict)
async def unlock_board(
    board_id: int, payload: OrganizerAction, db: aiosqlite.Connection = Depends(get_db)
):
    out = await board_service.unlock_board(db, board_id, payload.organizer_token)
    await _notify(await board_service.slug_for_board_id(db, board_id))
    return out


@router.delete("/boards/{board_id}", status_code=204)
async def delete_board(
    board_id: int, payload: OrganizerAction, db: aiosqlite.Connection = Depends(get_db)
):
    slug = await board_service.slug_for_board_id(db, board_id)
    await board_service.delete_board(db, board_id, payload.organizer_token)
    await _notify(slug)
    return None


@router.post("/boards/{board_id}/restore", response_model=dict)
async def restore_board(
    board_id: int, payload: OrganizerAction, db: aiosqlite.Connection = Depends(get_db)
):
    out = await board_service.restore_board(db, board_id, payload.organizer_token)
    await _notify(await board_service.slug_for_board_id(db, board_id))
    return out


# --- Cards (organizer-gated) -----------------------------------------------

@router.post("/cards/{card_id}/pin", response_model=dict)
async def pin_card(
    card_id: int, payload: OrganizerAction, db: aiosqlite.Connection = Depends(get_db)
):
    out = await board_service.pin_card(db, card_id, payload.organizer_token)
    await _notify(await board_service.slug_for_card(db, card_id))
    return out


@router.delete("/cards/{card_id}", status_code=204)
async def delete_card(
    card_id: int, payload: OrganizerAction, db: aiosqlite.Connection = Depends(get_db)
):
    slug = await board_service.slug_for_card(db, card_id)
    await board_service.delete_card(db, card_id, payload.organizer_token)
    await _notify(slug)
    return None
