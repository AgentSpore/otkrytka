"""Farewell / occasion mode: occasion preset, scheduled reveal gate, corp-brand.

The feature is additive and backward-compatible: a plain board (no occasion /
reveal_at / brand) must behave byte-identically to before. The reveal gate is
server-enforced — a guest cannot read a not-yet-revealed board's wishes, while
the organizer previews them with the token. Occasion + brand_color are validated
and organizer-gated on the settings endpoint.
"""

import os
import tempfile
from datetime import datetime, timedelta, timezone

import aiosqlite
import pytest

from otkrytka.core.config import get_settings
from otkrytka.core.db import _ensure_column

# The pre-feature boards schema (no occasion / reveal_at / revealed / brand_color),
# used to prove the additive migration backfills a legacy database losslessly.
_LEGACY_BOARDS_DDL = """
    CREATE TABLE boards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slug TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        recipient TEXT,
        cover TEXT NOT NULL DEFAULT '',
        organizer_token TEXT NOT NULL,
        locked INTEGER NOT NULL DEFAULT 0,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        deleted_at TIMESTAMP
    )
"""


def _future() -> str:
    return (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()


def _past() -> str:
    return (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()


async def _api_board(client, **extra):
    body = (
        await client.post("/api/v1/boards", json={"title": "Проводы", **extra})
    ).json()
    return body["slug"], body["organizer_token"]


async def _board_id(client, slug):
    return (await client.get(f"/api/v1/boards/{slug}")).json()["id"]


# --- Backward-compat: legacy DB migration --------------------------------------

@pytest.mark.asyncio
async def test_legacy_db_backfilled_open_and_idempotent():
    """A board created before this feature keeps its data and becomes revealed=1.

    Proves the additive ALTER path: existing rows pick up the column DEFAULTs
    (revealed=1 -> open, everything else NULL) with no data loss, and re-running
    the migration is a no-op (idempotent).
    """
    path = os.path.join(tempfile.gettempdir(), f"otk_legacy_{os.getpid()}.db")
    if os.path.exists(path):
        os.remove(path)
    try:
        async with aiosqlite.connect(path) as db:
            await db.execute(_LEGACY_BOARDS_DDL)
            await db.execute(
                "INSERT INTO boards (slug, title, organizer_token) "
                "VALUES ('legacy1', 'Старая открытка', 'tok')"
            )
            await db.commit()
            await _ensure_column(db, "boards", "occasion", "occasion TEXT")
            await _ensure_column(db, "boards", "reveal_at", "reveal_at TEXT")
            await _ensure_column(
                db, "boards", "revealed", "revealed INTEGER NOT NULL DEFAULT 1"
            )
            await _ensure_column(db, "boards", "brand_color", "brand_color TEXT")
            await db.commit()
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM boards WHERE slug = 'legacy1'"
            ) as cur:
                row = await cur.fetchone()
            assert row["title"] == "Старая открытка"  # data preserved
            assert row["revealed"] == 1  # legacy board is open
            assert row["occasion"] is None
            assert row["reveal_at"] is None
            assert row["brand_color"] is None
            # Idempotent: a second migration run must not raise.
            await _ensure_column(db, "boards", "revealed", "revealed INTEGER")
    finally:
        if os.path.exists(path):
            os.remove(path)


# --- Backward-compat: a plain board is unchanged -------------------------------

@pytest.mark.asyncio
async def test_default_board_is_birthday_open_and_unchanged(client):
    """No occasion / reveal_at / brand: birthday-mode, always revealed, cards shown."""
    slug, token = await _api_board(client)
    await client.post(
        f"/api/v1/boards/{slug}/cards", json={"author_name": "Аня", "text": "Ура"}
    )
    b = (await client.get(f"/api/v1/boards/{slug}")).json()
    assert b["occasion"] is None
    assert b["reveal_at"] is None
    assert b["revealed"] is True
    assert b["brand_color"] is None
    assert b["card_count"] == 1
    assert len(b["cards"]) == 1  # wishes visible to everyone, no gate


@pytest.mark.asyncio
async def test_two_default_boards_are_dict_equal(client):
    """Null-everything boards are structurally identical (ignoring id/slug)."""
    s1, _ = await _api_board(client)
    s2, _ = await _api_board(client)
    a = (await client.get(f"/api/v1/boards/{s1}")).json()
    b = (await client.get(f"/api/v1/boards/{s2}")).json()
    for d in (a, b):
        d.pop("id")
        d.pop("slug")
    assert a == b
    assert a == {
        "title": "Проводы",
        "recipient": None,
        "cover": "",
        "locked": False,
        "occasion": None,
        "reveal_at": None,
        "revealed": True,
        "brand_color": None,
        "card_count": 0,
        "cards": [],
    }


# --- Occasion preset -----------------------------------------------------------

@pytest.mark.asyncio
async def test_occasion_stored_and_returned(client):
    slug, _ = await _api_board(client, occasion="farewell")
    assert (await client.get(f"/api/v1/boards/{slug}")).json()["occasion"] == "farewell"


@pytest.mark.asyncio
async def test_invalid_occasion_rejected(client):
    res = await client.post(
        "/api/v1/boards", json={"title": "X", "occasion": "wedding"}
    )
    assert res.status_code == 422


# --- Scheduled reveal gate -----------------------------------------------------

@pytest.mark.asyncio
async def test_future_reveal_gates_wishes_from_guest(client):
    slug, token = await _api_board(client, reveal_at=_future())
    await client.post(
        f"/api/v1/boards/{slug}/cards", json={"author_name": "Гость", "text": "Секрет"}
    )
    # Guests can still add wishes, but cannot read them before the reveal.
    guest = (await client.get(f"/api/v1/boards/{slug}")).json()
    assert guest["revealed"] is False
    assert guest["cards"] == []
    assert guest["card_count"] == 1  # count leaks, content does not
    # The organizer previews the wishes with the token header.
    org = (
        await client.get(
            f"/api/v1/boards/{slug}", headers={"X-Organizer-Token": token}
        )
    ).json()
    assert org["revealed"] is False
    assert len(org["cards"]) == 1


@pytest.mark.asyncio
async def test_wrong_token_does_not_preview(client):
    slug, _ = await _api_board(client, reveal_at=_future())
    await client.post(
        f"/api/v1/boards/{slug}/cards", json={"author_name": "Гость", "text": "тс"}
    )
    r = (
        await client.get(
            f"/api/v1/boards/{slug}", headers={"X-Organizer-Token": "wrong"}
        )
    ).json()
    assert r["cards"] == []


@pytest.mark.asyncio
async def test_malformed_reveal_at_fails_closed(client):
    """A garbage reveal_at value in the DB keeps the board gated, never crashes.

    Defense in depth: reveal_at is normally written as a canonical UTC ISO string,
    but a corrupt / hand-edited / legacy value must not throw or leak wishes.
    ``_is_revealed`` catches the parse error and returns False (stay gated).
    """
    slug, token = await _api_board(client, reveal_at=_future())
    await client.post(
        f"/api/v1/boards/{slug}/cards", json={"author_name": "Гость", "text": "тайна"}
    )
    bid = await _board_id(client, slug)
    # Corrupt the stored value directly (bypassing validation) to simulate a bad row.
    async with aiosqlite.connect(get_settings().db_path) as db:
        await db.execute(
            "UPDATE boards SET reveal_at = 'not-a-date' WHERE id = ?", (bid,)
        )
        await db.commit()
    # Guest: fails closed -> still gated, no wishes leaked, no 500.
    res = await client.get(f"/api/v1/boards/{slug}")
    assert res.status_code == 200
    body = res.json()
    assert body["revealed"] is False
    assert body["cards"] == []
    assert body["card_count"] == 1


@pytest.mark.asyncio
async def test_past_reveal_is_open_to_all(client):
    slug, _ = await _api_board(client, reveal_at=_past())
    await client.post(
        f"/api/v1/boards/{slug}/cards", json={"author_name": "Гость", "text": "Видно"}
    )
    b = (await client.get(f"/api/v1/boards/{slug}")).json()
    assert b["revealed"] is True
    assert len(b["cards"]) == 1


@pytest.mark.asyncio
async def test_manual_reveal_opens_gated_board(client):
    slug, token = await _api_board(client, reveal_at=_future())
    await client.post(
        f"/api/v1/boards/{slug}/cards", json={"author_name": "Гость", "text": "Сюрприз"}
    )
    bid = await _board_id(client, slug)
    res = await client.patch(
        f"/api/v1/boards/{bid}/reveal", json={"organizer_token": token}
    )
    assert res.status_code == 200
    assert res.json()["revealed"] is True
    # Now open to guests too, even though reveal_at is still in the future.
    guest = (await client.get(f"/api/v1/boards/{slug}")).json()
    assert guest["revealed"] is True
    assert len(guest["cards"]) == 1


@pytest.mark.asyncio
async def test_reveal_requires_token(client):
    slug, _ = await _api_board(client, reveal_at=_future())
    bid = await _board_id(client, slug)
    res = await client.patch(
        f"/api/v1/boards/{bid}/reveal", json={"organizer_token": "wrong"}
    )
    assert res.status_code == 403
    assert res.json()["detail"]["code"] == "organizer_token_required"
    assert (await client.patch(f"/api/v1/boards/{bid}/reveal", json={})).status_code == 422


# --- Corp-brand + settings (organizer-gated) -----------------------------------

@pytest.mark.asyncio
async def test_brand_color_valid_hex_stored(client):
    slug, _ = await _api_board(client, brand_color="#1A2B3C")
    assert (await client.get(f"/api/v1/boards/{slug}")).json()["brand_color"] == "#1A2B3C"


@pytest.mark.asyncio
@pytest.mark.parametrize("bad", ["red", "#12345", "1A2B3C", "#12345G", "#1234567"])
async def test_brand_color_bad_hex_rejected(client, bad):
    res = await client.post("/api/v1/boards", json={"title": "X", "brand_color": bad})
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_settings_update_occasion_reveal_brand(client):
    slug, token = await _api_board(client)
    bid = await _board_id(client, slug)
    res = await client.patch(
        f"/api/v1/boards/{bid}/settings",
        json={
            "organizer_token": token,
            "occasion": "teacher",
            "reveal_at": _future(),
            "brand_color": "#00FF00",
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["occasion"] == "teacher"
    assert body["brand_color"] == "#00FF00"
    assert body["revealed"] is False  # setting reveal_at re-gated the board


@pytest.mark.asyncio
async def test_settings_requires_token(client):
    slug, _ = await _api_board(client)
    bid = await _board_id(client, slug)
    res = await client.patch(
        f"/api/v1/boards/{bid}/settings",
        json={"organizer_token": "wrong", "occasion": "farewell"},
    )
    assert res.status_code == 403
    assert res.json()["detail"]["code"] == "organizer_token_required"
    # Missing token field -> 422 (guest cannot forge the call).
    assert (
        await client.patch(f"/api/v1/boards/{bid}/settings", json={"occasion": "farewell"})
    ).status_code == 422


@pytest.mark.asyncio
async def test_settings_bad_brand_rejected(client):
    slug, token = await _api_board(client)
    bid = await _board_id(client, slug)
    res = await client.patch(
        f"/api/v1/boards/{bid}/settings",
        json={"organizer_token": token, "brand_color": "notacolor"},
    )
    assert res.status_code == 422
