"""Locked boards reject new cards, and organizer gates hold at the service layer.

Once the organizer locks a board it is ready for delivery; adding further cards
would rewrite a frozen greeting, so ``add_card`` must reject with HTTP 409. The
lock / delete / restore operations require the secret organizer token (403).
"""

import pytest
from fastapi import HTTPException

from otkrytka.core.db import get_db, init_db
from otkrytka.services import board_service


async def _fresh_db():
    db_gen = get_db()
    db = await db_gen.__anext__()
    return db, db_gen


async def _board(db):
    return await board_service.create_board(db, "Открытка", "Аня", "🎂")


@pytest.mark.asyncio
async def test_locked_board_rejects_new_card():
    await init_db()
    db, gen = await _fresh_db()
    try:
        b = await _board(db)
        await board_service.lock_board(db, (await _board_id(db, b["slug"])), b["organizer_token"])
        with pytest.raises(HTTPException) as exc:
            await board_service.add_card(db, b["slug"], "Петя", "Поздно", None, None)
        assert exc.value.status_code == 409
    finally:
        await gen.aclose()


@pytest.mark.asyncio
async def test_lock_requires_token():
    await init_db()
    db, gen = await _fresh_db()
    try:
        b = await _board(db)
        bid = await _board_id(db, b["slug"])
        with pytest.raises(HTTPException) as exc:
            await board_service.lock_board(db, bid, "wrong-token")
        assert exc.value.status_code == 403
    finally:
        await gen.aclose()


@pytest.mark.asyncio
async def test_card_cap_enforced_service():
    await init_db()
    db, gen = await _fresh_db()
    try:
        b = await _board(db)
        for i in range(100):
            await board_service.add_card(db, b["slug"], f"Гость {i}", "!", None, None)
        with pytest.raises(HTTPException) as exc:
            await board_service.add_card(db, b["slug"], "Лишний", "!", None, None)
        assert exc.value.status_code == 400
    finally:
        await gen.aclose()


@pytest.mark.asyncio
async def test_empty_card_rejected_service():
    await init_db()
    db, gen = await _fresh_db()
    try:
        b = await _board(db)
        with pytest.raises(HTTPException) as exc:
            await board_service.add_card(db, b["slug"], "Петя", None, None, None)
        assert exc.value.status_code == 400
    finally:
        await gen.aclose()


@pytest.mark.asyncio
async def test_blank_author_rejected_service():
    """The direct-service path must also reject a whitespace-only author (400)."""
    await init_db()
    db, gen = await _fresh_db()
    try:
        b = await _board(db)
        with pytest.raises(HTTPException) as exc:
            await board_service.add_card(db, b["slug"], "   ", "Привет", None, None)
        assert exc.value.status_code == 400
    finally:
        await gen.aclose()


@pytest.mark.asyncio
async def test_soft_deleted_board_blocks_id_based_mutation():
    """A soft-deleted board must not be lockable via its guessable numeric id."""
    await init_db()
    db, gen = await _fresh_db()
    try:
        b = await _board(db)
        bid = await _board_id(db, b["slug"])
        await board_service.delete_board(db, bid, b["organizer_token"])
        with pytest.raises(HTTPException) as exc:
            await board_service.lock_board(db, bid, b["organizer_token"])
        assert exc.value.status_code == 404
    finally:
        await gen.aclose()


@pytest.mark.asyncio
async def test_restore_survives_deleted_filter():
    await init_db()
    db, gen = await _fresh_db()
    try:
        b = await _board(db)
        bid = await _board_id(db, b["slug"])
        await board_service.delete_board(db, bid, b["organizer_token"])
        restored = await board_service.restore_board(db, bid, b["organizer_token"])
        assert restored["slug"] == b["slug"]
        assert restored["locked"] is False
    finally:
        await gen.aclose()


async def _board_id(db, slug):
    board = await board_service.get_board(db, slug)
    return board["id"]
