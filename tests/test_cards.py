"""Card lifecycle: pin/delete organizer gating, empty-card + cap guards."""

import pytest


async def _make_board(client):
    res = await client.post(
        "/api/v1/boards", json={"title": "Открытка", "recipient": "Аня"}
    )
    body = res.json()
    return body["slug"], body["organizer_token"]


async def _add_card(client, slug, name="Петя", text="Привет"):
    return (await client.post(
        f"/api/v1/boards/{slug}/cards", json={"author_name": name, "text": text}
    )).json()


@pytest.mark.asyncio
async def test_empty_card_rejected(client):
    slug, _ = await _make_board(client)
    res = await client.post(
        f"/api/v1/boards/{slug}/cards", json={"author_name": "Петя"}
    )
    assert res.status_code == 400
    # Whitespace-only text is also empty.
    res2 = await client.post(
        f"/api/v1/boards/{slug}/cards", json={"author_name": "Петя", "text": "   "}
    )
    assert res2.status_code == 400


@pytest.mark.asyncio
async def test_card_cap_enforced(client):
    slug, _ = await _make_board(client)
    for i in range(100):
        r = await client.post(
            f"/api/v1/boards/{slug}/cards",
            json={"author_name": f"Гость {i}", "text": "!"},
        )
        assert r.status_code == 200
    over = await client.post(
        f"/api/v1/boards/{slug}/cards", json={"author_name": "Лишний", "text": "!"}
    )
    assert over.status_code == 400


@pytest.mark.asyncio
async def test_pin_requires_token(client):
    slug, token = await _make_board(client)
    card = await _add_card(client, slug)

    forbidden = await client.post(
        f"/api/v1/cards/{card['id']}/pin", json={"organizer_token": "wrong"}
    )
    assert forbidden.status_code == 403

    ok = await client.post(
        f"/api/v1/cards/{card['id']}/pin", json={"organizer_token": token}
    )
    assert ok.status_code == 200
    assert ok.json()["pinned"] is True


@pytest.mark.asyncio
async def test_delete_card_requires_token(client):
    slug, token = await _make_board(client)
    card = await _add_card(client, slug)

    forbidden = await client.request(
        "DELETE", f"/api/v1/cards/{card['id']}", json={"organizer_token": "nope"}
    )
    assert forbidden.status_code == 403

    ok = await client.request(
        "DELETE", f"/api/v1/cards/{card['id']}", json={"organizer_token": token}
    )
    assert ok.status_code == 204
    body = (await client.get(f"/api/v1/boards/{slug}")).json()
    assert body["cards"] == []


@pytest.mark.asyncio
async def test_pinned_card_floats_to_top(client):
    slug, token = await _make_board(client)
    await _add_card(client, slug, name="Первый")
    second = await _add_card(client, slug, name="Второй")
    await _add_card(client, slug, name="Третий")

    # Pin the oldest so it should jump above the newer ones.
    await client.post(
        f"/api/v1/cards/{second['id']}/pin", json={"organizer_token": token}
    )
    body = (await client.get(f"/api/v1/boards/{slug}")).json()
    assert body["cards"][0]["author_name"] == "Второй"
    assert body["cards"][0]["pinned"] is True
    # remaining are newest-first
    assert [c["author_name"] for c in body["cards"][1:]] == ["Третий", "Первый"]
