"""End-to-end API tests against the ASGI app via httpx AsyncClient."""

import pytest


async def _make_board(client, title="С днём рождения, Аня!", recipient="Аня", cover="🎂"):
    res = await client.post(
        "/api/v1/boards", json={"title": title, "recipient": recipient, "cover": cover}
    )
    assert res.status_code == 200
    body = res.json()
    return body["slug"], body["organizer_token"]


@pytest.mark.asyncio
async def test_create_and_get_board(client):
    slug, token = await _make_board(client)
    assert token  # organizer_token returned once to the creator
    res = await client.get(f"/api/v1/boards/{slug}")
    assert res.status_code == 200
    body = res.json()
    assert body["slug"] == slug
    assert body["title"] == "С днём рождения, Аня!"
    assert body["recipient"] == "Аня"
    assert body["cover"] == "🎂"
    assert body["locked"] is False
    assert body["cards"] == []
    # GET must never leak the organizer secret.
    assert "organizer_token" not in body


@pytest.mark.asyncio
async def test_unknown_board_is_404(client):
    res = await client.get("/api/v1/boards/nope000")
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_add_cards_and_ordering(client):
    slug, _ = await _make_board(client)
    c1 = (await client.post(
        f"/api/v1/boards/{slug}/cards",
        json={"author_name": "Петя", "text": "С праздником!"},
    )).json()
    c2 = (await client.post(
        f"/api/v1/boards/{slug}/cards",
        json={"author_name": "Оля", "text": "Обнимаю"},
    )).json()
    assert c1["author_name"] == "Петя"
    assert c2["author_name"] == "Оля"

    body = (await client.get(f"/api/v1/boards/{slug}")).json()
    # Newest first when nothing is pinned.
    assert [c["author_name"] for c in body["cards"]] == ["Оля", "Петя"]


@pytest.mark.asyncio
async def test_add_card_with_gif(client):
    slug, _ = await _make_board(client)
    res = await client.post(
        f"/api/v1/boards/{slug}/cards",
        json={"author_name": "Ким", "gif_url": "https://media.example.com/hug.gif"},
    )
    assert res.status_code == 200
    assert res.json()["gif_url"] == "https://media.example.com/hug.gif"


@pytest.mark.asyncio
async def test_add_card_with_image_path(client):
    slug, _ = await _make_board(client)
    res = await client.post(
        f"/api/v1/boards/{slug}/cards",
        json={"author_name": "Лев", "image_path": "/uploads/abc123.jpg"},
    )
    assert res.status_code == 200
    assert res.json()["image_path"] == "/uploads/abc123.jpg"


@pytest.mark.asyncio
async def test_add_card_rejects_bad_gif_url(client):
    slug, _ = await _make_board(client)
    bad = await client.post(
        f"/api/v1/boards/{slug}/cards",
        json={"author_name": "X", "gif_url": "javascript:alert(1)"},
    )
    assert bad.status_code == 400
    not_image = await client.post(
        f"/api/v1/boards/{slug}/cards",
        json={"author_name": "X", "gif_url": "https://example.com/page"},
    )
    assert not_image.status_code == 400


@pytest.mark.asyncio
async def test_add_card_rejects_foreign_image_path(client):
    slug, _ = await _make_board(client)
    res = await client.post(
        f"/api/v1/boards/{slug}/cards",
        json={"author_name": "X", "image_path": "/etc/passwd"},
    )
    assert res.status_code == 400


@pytest.mark.asyncio
async def test_field_caps_reject_oversized(client):
    long_title = "x" * 121
    res = await client.post("/api/v1/boards", json={"title": long_title})
    assert res.status_code == 422
    empty = await client.post("/api/v1/boards", json={"title": ""})
    assert empty.status_code == 422


@pytest.mark.asyncio
async def test_blank_title_after_strip_rejected(client):
    res = await client.post("/api/v1/boards", json={"title": "   "})
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_blank_author_after_strip_rejected(client):
    slug, _ = await _make_board(client)
    res = await client.post(
        f"/api/v1/boards/{slug}/cards",
        json={"author_name": "   ", "text": "Привет"},
    )
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_title_and_recipient_are_stripped(client):
    res = await client.post(
        "/api/v1/boards", json={"title": "  С праздником  ", "recipient": "  Аня  "}
    )
    assert res.status_code == 200
    board = (await client.get(f"/api/v1/boards/{res.json()['slug']}")).json()
    assert board["title"] == "С праздником"
    assert board["recipient"] == "Аня"


@pytest.mark.asyncio
async def test_soft_delete_and_restore(client):
    slug, token = await _make_board(client)
    board = (await client.get(f"/api/v1/boards/{slug}")).json()
    res = await client.request(
        "DELETE", f"/api/v1/boards/{board['id']}", json={"organizer_token": token}
    )
    assert res.status_code == 204
    assert (await client.get(f"/api/v1/boards/{slug}")).status_code == 404
    restored = await client.post(
        f"/api/v1/boards/{board['id']}/restore", json={"organizer_token": token}
    )
    assert restored.status_code == 200
    assert (await client.get(f"/api/v1/boards/{slug}")).status_code == 200
