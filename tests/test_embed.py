"""Embeddable read-only card (/embed/{slug}), oEmbed endpoint + discovery.

Security focus: the embed page and oEmbed output must never carry the organizer
token, must HTML-escape the board title into the iframe, and /oembed must reject
foreign-host and malformed URLs so it cannot be turned into an open proxy. The
oEmbed host-check compares against the configured canonical origin ONLY (never
the spoofable request-derived host) and fails closed when it is unset.
"""

import json
from pathlib import Path

import pytest

from otkrytka.core.config import get_settings

_CANON = "https://otkrytka.agentspore.com"


def _set_canonical(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "canonical_base_url", _CANON)


async def _make_board(client, title="С днём рождения, Аня!", recipient="Аня"):
    res = await client.post(
        "/api/v1/boards", json={"title": title, "recipient": recipient, "cover": "🎂"}
    )
    assert res.status_code == 200
    return res.json()


# --- Embed page ----------------------------------------------------------------

@pytest.mark.asyncio
async def test_embed_page_signals_read_only_mode(client):
    slug = (await _make_board(client))["slug"]
    res = await client.get(f"/embed/{slug}")
    assert res.status_code == 200
    body = res.text
    # The SPA reads this flag to render the read-only embed screen.
    assert "window.__EMBED__=true" in body
    # Per-board OG still swapped in (a shared embed URL previews the card).
    assert 'property="og:title" content="С днём рождения, Аня!"' in body


@pytest.mark.asyncio
async def test_embed_page_has_cache_control(client):
    slug = (await _make_board(client))["slug"]
    res = await client.get(f"/embed/{slug}")
    assert res.headers["cache-control"] == "public, max-age=300"


@pytest.mark.asyncio
async def test_card_page_is_not_embed_mode(client):
    # The normal /c/{slug} render must NOT flip the SPA into read-only embed.
    slug = (await _make_board(client))["slug"]
    body = (await client.get(f"/c/{slug}")).text
    assert "window.__EMBED__" not in body
    assert "window.__CANONICAL__" in body  # canonical origin still injected


@pytest.mark.asyncio
async def test_embed_page_never_leaks_organizer_token(client):
    created = await _make_board(client)
    body = (await client.get(f"/embed/{created['slug']}")).text
    assert created["organizer_token"] not in body


def test_embed_frontend_renders_read_only():
    # The embed screen must paint wishes with isOrganizer=false (no pin/delete
    # tools) and never read the organizer token.
    app_js = (Path(get_settings().frontend_dir) / "app.js").read_text(encoding="utf-8")
    assert "function paintEmbed" in app_js
    assert "wishHtml(c, false" in app_js  # read-only card render in paintEmbed
    # parseRoute recognises the real /embed/{slug} path.
    assert "/^\\/embed\\/([a-z0-9]+)" in app_js


# --- oEmbed --------------------------------------------------------------------

@pytest.mark.asyncio
async def test_oembed_json_valid(client, monkeypatch):
    _set_canonical(monkeypatch)
    slug = (await _make_board(client))["slug"]
    res = await client.get(f"/oembed?url={_CANON}/c/{slug}&format=json")
    assert res.status_code == 200
    assert res.headers["cache-control"] == "public, max-age=300"
    data = res.json()
    assert data["version"] == "1.0"
    assert data["type"] == "rich"
    assert data["provider_name"] == "Otkrytka"
    assert data["provider_url"] == _CANON
    assert data["title"] == "С днём рождения, Аня!"
    assert f"{_CANON}/embed/{slug}" in data["html"]
    assert data["html"].startswith("<iframe")


@pytest.mark.asyncio
async def test_oembed_accepts_embed_url_and_clamps_size(client, monkeypatch):
    _set_canonical(monkeypatch)
    slug = (await _make_board(client))["slug"]
    res = await client.get(
        f"/oembed?url={_CANON}/embed/{slug}&format=json&maxwidth=200&maxheight=300"
    )
    assert res.status_code == 200
    data = res.json()
    assert data["width"] == 200
    assert data["height"] == 300


@pytest.mark.asyncio
async def test_oembed_escapes_title_in_iframe(client, monkeypatch):
    _set_canonical(monkeypatch)
    payload = '"><script>alert(1)</script>'
    slug = (await _make_board(client, title=payload))["slug"]
    res = await client.get(f"/oembed?url={_CANON}/c/{slug}&format=json")
    data = res.json()
    # Iframe title="..." must be HTML-escaped (no attribute breakout).
    assert '"><script>' not in data["html"]
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in data["html"]
    # The JSON title field carries the raw value, safely inside a JSON string.
    assert data["title"] == payload
    # And the whole response is valid JSON (round-trips).
    assert json.loads(res.text)["type"] == "rich"


@pytest.mark.asyncio
async def test_oembed_host_check_uses_canonical_not_spoofed_header(client, monkeypatch):
    # The foreign-host comparison must use the configured canonical origin, NOT a
    # request-derived host: a forged X-Forwarded-Host cannot make a foreign URL
    # pass, nor block a genuine canonical URL.
    _set_canonical(monkeypatch)
    slug = (await _make_board(client))["slug"]
    # Genuine canonical URL still accepted despite a spoofed forwarded host.
    ok = await client.get(
        f"/oembed?url={_CANON}/c/{slug}&format=json",
        headers={"X-Forwarded-Host": "evil.example"},
    )
    assert ok.status_code == 200
    # A URL on the spoofed host is rejected even when it matches the header.
    bad = await client.get(
        f"/oembed?url=https://evil.example/c/{slug}&format=json",
        headers={"X-Forwarded-Host": "evil.example"},
    )
    assert bad.status_code == 404


@pytest.mark.asyncio
async def test_oembed_fails_closed_when_canonical_unset(client):
    # Default settings have no canonical origin, so the host-check has no trusted
    # reference -> fail closed (500) rather than trust the request host.
    slug = (await _make_board(client))["slug"]
    res = await client.get(f"/oembed?url={_CANON}/c/{slug}&format=json")
    assert res.status_code == 500


@pytest.mark.asyncio
async def test_oembed_rejects_foreign_host(client, monkeypatch):
    _set_canonical(monkeypatch)
    slug = (await _make_board(client))["slug"]
    res = await client.get(f"/oembed?url=https://evil.example/c/{slug}&format=json")
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_oembed_rejects_malformed_url(client, monkeypatch):
    _set_canonical(monkeypatch)
    res = await client.get("/oembed?url=not-a-url&format=json")
    assert res.status_code == 400


@pytest.mark.asyncio
async def test_oembed_rejects_non_card_path(client, monkeypatch):
    _set_canonical(monkeypatch)
    res = await client.get(f"/oembed?url={_CANON}/other/thing&format=json")
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_oembed_xml_not_implemented(client, monkeypatch):
    _set_canonical(monkeypatch)
    slug = (await _make_board(client))["slug"]
    res = await client.get(f"/oembed?url={_CANON}/c/{slug}&format=xml")
    assert res.status_code == 501


@pytest.mark.asyncio
async def test_oembed_never_leaks_organizer_token(client, monkeypatch):
    _set_canonical(monkeypatch)
    created = await _make_board(client)
    res = await client.get(f"/oembed?url={_CANON}/c/{created['slug']}&format=json")
    assert created["organizer_token"] not in res.text


# --- Discovery -----------------------------------------------------------------

@pytest.mark.asyncio
async def test_discovery_link_in_card_head(client):
    slug = (await _make_board(client))["slug"]
    body = (await client.get(f"/c/{slug}")).text
    assert 'type="application/json+oembed"' in body
    assert "/oembed?url=" in body
    assert f"c/{slug}" in body
