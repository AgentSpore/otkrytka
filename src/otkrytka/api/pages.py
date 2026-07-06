"""Server-rendered pages (outside ``/api/v1``) for social-unfurl.

These routes MUST be registered before the SPA static mount at ``/`` so they are
not shadowed by it. They are read-only and never touch the organizer token, so a
crawler fetching ``/c/{slug}`` or ``/og/{slug}.png`` sees only public card data.
"""

from pathlib import Path

import aiosqlite
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, Response

from ..core.config import get_settings
from ..core.db import get_db
from ..services import og_service

router = APIRouter()


# Deterministic per slug+content, so crawlers / CDN / Caddy can dedupe the render.
_OG_CACHE_CONTROL = "public, max-age=3600"

# Shorter TTL for the embed HTML + oEmbed JSON: many consumer crawlers re-fetch
# these, but the card content updates live, so a 5-minute cache balances both.
_EMBED_CACHE_CONTROL = "public, max-age=300"


def _base_url(request: Request) -> str:
    """Absolute origin for og:url / og:image.

    When ``canonical_base_url`` is configured (prod), use it verbatim and ignore
    all client-supplied Host / X-Forwarded-* headers — otherwise an attacker
    could set ``X-Forwarded-Host: evil.com`` and point the unfurl at a phishing
    domain. Empty (dev) derives the origin from the request, honoring the
    TLS-terminating reverse proxy.
    """
    canonical = get_settings().canonical_base_url
    if canonical:
        return canonical.rstrip("/")
    proto = request.headers.get("x-forwarded-proto") or request.url.scheme
    host = request.headers.get("x-forwarded-host") or request.url.netloc
    return f"{proto}://{host}"


@router.get("/c/{slug}", response_class=HTMLResponse)
async def card_page(
    slug: str, request: Request, db: aiosqlite.Connection = Depends(get_db)
):
    """Serve the SPA with per-board OG tags so the shared link previews the card.

    A missing/deleted board still returns 200 with the generic landing OG — the
    SPA then shows its own not-found state client-side.
    """
    lang = og_service.pick_lang(
        request.query_params.get("lang"), request.headers.get("accept-language")
    )
    body = await og_service.render_card_page(db, slug, lang, _base_url(request))
    return HTMLResponse(body)


@router.get("/embed/{slug}", response_class=HTMLResponse)
async def embed_page(
    slug: str, request: Request, db: aiosqlite.Connection = Depends(get_db)
):
    """Serve the SPA in READ-ONLY embed mode (a signal script sets ``__EMBED__``).

    Framing is intentionally allowed: no ``X-Frame-Options`` / CSP
    ``frame-ancestors`` is set anywhere, so this public read-only card can be
    dropped into a blog / tribute page / Notion. The organizer token is never
    injected here (embed has no manage access).
    """
    lang = og_service.pick_lang(
        request.query_params.get("lang"), request.headers.get("accept-language")
    )
    body = await og_service.render_embed_page(db, slug, lang, _base_url(request))
    return HTMLResponse(body, headers={"Cache-Control": _EMBED_CACHE_CONTROL})


@router.get("/oembed")
async def oembed(
    url: str,
    format: str = "json",
    maxwidth: int | None = None,
    maxheight: int | None = None,
    db: aiosqlite.Connection = Depends(get_db),
):
    """oEmbed 1.0 endpoint for a canonical ``/c/{slug}`` or ``/embed/{slug}`` URL.

    Only ``format=json`` is supported (501 otherwise). Foreign hosts / non-card
    paths are rejected (404) and unparseable URLs are 400 so oEmbed never proxies
    a third party. The board title is escaped into both the JSON and the iframe.
    """
    if format != "json":
        raise HTTPException(status_code=501, detail="only format=json is supported")
    try:
        payload = await og_service.render_oembed(db, url, maxwidth, maxheight)
    except og_service.OembedMalformedError:
        raise HTTPException(status_code=400, detail="malformed url") from None
    except og_service.OembedForeignError:
        raise HTTPException(status_code=404, detail="not a card url") from None
    except og_service.OembedNotConfiguredError:
        raise HTTPException(status_code=500, detail="oembed not configured") from None
    return JSONResponse(payload, headers={"Cache-Control": _EMBED_CACHE_CONTROL})


@router.get("/og/{slug}.png")
async def og_image(slug: str, db: aiosqlite.Connection = Depends(get_db)):
    """1200x630 per-board card image; static og-image.png when fonts are absent."""
    headers = {"Cache-Control": _OG_CACHE_CONTROL}
    png = await og_service.render_og_image(db, slug)
    if png is not None:
        return Response(content=png, media_type="image/png", headers=headers)
    static = Path(get_settings().frontend_dir) / "og-image.png"
    return FileResponse(static, media_type="image/png", headers=headers)
