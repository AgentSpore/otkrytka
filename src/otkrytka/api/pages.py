"""Server-rendered pages (outside ``/api/v1``) for social-unfurl.

These routes MUST be registered before the SPA static mount at ``/`` so they are
not shadowed by it. They are read-only and never touch the organizer token, so a
crawler fetching ``/c/{slug}`` or ``/og/{slug}.png`` sees only public card data.
"""

from pathlib import Path

import aiosqlite
from fastapi import APIRouter, Depends, Request
from fastapi.responses import FileResponse, HTMLResponse, Response

from ..core.config import get_settings
from ..core.db import get_db
from ..services import og_service

router = APIRouter()


# Deterministic per slug+content, so crawlers / CDN / Caddy can dedupe the render.
_OG_CACHE_CONTROL = "public, max-age=3600"


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


@router.get("/og/{slug}.png")
async def og_image(slug: str, db: aiosqlite.Connection = Depends(get_db)):
    """1200x630 per-board card image; static og-image.png when fonts are absent."""
    headers = {"Cache-Control": _OG_CACHE_CONTROL}
    png = await og_service.render_og_image(db, slug)
    if png is not None:
        return Response(content=png, media_type="image/png", headers=headers)
    static = Path(get_settings().frontend_dir) / "og-image.png"
    return FileResponse(static, media_type="image/png", headers=headers)
