"""Social-unfurl routes: dynamic OG page + per-board OG image.

Covers the security-critical escaping of user-input title/recipient injected
into OG meta, plus back-compat (unknown board still serves 200) and the image
endpoint's content type.
"""

from pathlib import Path

import pytest

from otkrytka.core.config import get_settings


async def _make_board(client, title="С днём рождения, Аня!", recipient="Аня"):
    res = await client.post(
        "/api/v1/boards", json={"title": title, "recipient": recipient, "cover": "🎂"}
    )
    assert res.status_code == 200
    return res.json()["slug"]


@pytest.mark.asyncio
async def test_card_page_has_per_board_og(client):
    slug = await _make_board(client)
    res = await client.get(f"/c/{slug}")
    assert res.status_code == 200
    body = res.text
    assert 'property="og:title" content="С днём рождения, Аня!"' in body
    assert f"/c/{slug}" in body  # canonical og:url
    assert f"/og/{slug}.png" in body  # per-board og:image
    # RU default description carries the recipient.
    assert "Открытка для Аня" in body


@pytest.mark.asyncio
async def test_card_page_escapes_xss_in_title(client):
    payload = '"><script>alert(1)</script>'
    slug = await _make_board(client, title=payload, recipient="Аня")
    body = (await client.get(f"/c/{slug}")).text
    # The raw breakout sequence must never appear verbatim in the document.
    assert "<script>alert(1)</script>" not in body
    assert '"><script>' not in body
    # It is present, fully escaped, inside the meta content attribute.
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in body


@pytest.mark.asyncio
async def test_card_page_english_description(client):
    slug = await _make_board(client)
    body = (await client.get(f"/c/{slug}?lang=en")).text
    assert "A group card for Аня" in body


@pytest.mark.asyncio
async def test_unknown_slug_still_serves_spa_200(client):
    res = await client.get("/c/nope000")
    assert res.status_code == 200
    # Falls back to the generic static OG (markers untouched by the swap).
    assert 'property="og:title"' in res.text


@pytest.mark.asyncio
async def test_card_page_never_leaks_organizer_token(client):
    res = await client.post("/api/v1/boards", json={"title": "Тест"})
    token = res.json()["organizer_token"]
    slug = res.json()["slug"]
    body = (await client.get(f"/c/{slug}")).text
    assert token not in body


@pytest.mark.asyncio
async def test_canonical_base_url_ignores_spoofed_host(client, monkeypatch):
    # With a fixed canonical origin, a forged X-Forwarded-Host must NOT reach the
    # unfurl (host-injection / phishing defense).
    settings = get_settings()
    monkeypatch.setattr(settings, "canonical_base_url", "https://otkrytka.agentspore.com")
    slug = await _make_board(client)
    body = (
        await client.get(f"/c/{slug}", headers={"X-Forwarded-Host": "evil.example"})
    ).text
    assert 'content="https://otkrytka.agentspore.com/c/' in body
    assert 'content="https://otkrytka.agentspore.com/og/' in body
    assert "evil.example" not in body


@pytest.mark.asyncio
async def test_og_image_is_png_and_cached(client):
    slug = await _make_board(client)
    res = await client.get(f"/og/{slug}.png")
    assert res.status_code == 200
    assert res.headers["content-type"] == "image/png"
    assert res.headers["cache-control"] == "public, max-age=3600"
    assert res.content[:8] == b"\x89PNG\r\n\x1a\n"


@pytest.mark.asyncio
async def test_og_image_unknown_slug_is_png(client):
    res = await client.get("/og/nope000.png")
    assert res.status_code == 200
    assert res.headers["content-type"] == "image/png"


def test_share_builder_uses_real_path():
    # The guest share + copy links must build the crawler-visible /c/{slug} path.
    app_js = (Path(get_settings().frontend_dir) / "app.js").read_text(encoding="utf-8")
    assert "${location.origin}/c/${slug}" in app_js
