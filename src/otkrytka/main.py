import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from .api import boards, pages
from .core.config import get_settings
from .core.db import init_db
from .core.limits import BodySizeLimitMiddleware

logger = logging.getLogger(__name__)

# Prefixes that must keep their native 404 (JSON for API paths, plain 404 for
# missing assets) instead of falling back to the SPA shell. Everything else that
# is extensionless and unknown is treated as a client-side SPA route.
_SPA_RESERVED_PREFIXES = (
    "api/",
    "uploads/",
    "vendor/",
    "og/",
    "c/",
    "embed",
    "oembed",
    "health",
)


def _is_spa_route(path: str) -> bool:
    """True for a clean, unknown top-level path that the SPA router should own.

    Excludes API/asset/page prefixes (so their 404s stay untouched) and any path
    whose last segment carries a file extension (a genuinely missing static asset
    stays a real 404 rather than silently returning HTML).
    """
    if path.startswith(_SPA_RESERVED_PREFIXES):
        return False
    return "." not in path.rsplit("/", 1)[-1]


class SPAStaticFiles(StaticFiles):
    """StaticFiles that serves index.html for unknown extensionless GET paths.

    Real files are served as-is; unknown SPA routes (e.g. ``/totally-bogus``)
    return the app shell so the client router can render its own localized
    not-found instead of leaking a raw ``{"detail":"Not Found"}`` JSON body.
    Unknown API paths and missing assets keep their native 404 (see
    ``_is_spa_route``). Registered last, so API routers and page routes above it
    are never shadowed.
    """

    async def get_response(self, path, scope):
        try:
            return await super().get_response(path, scope)
        except StarletteHTTPException as exc:
            if exc.status_code == 404 and _is_spa_route(path):
                return await super().get_response("index.html", scope)
            raise

# Deliberately scoped deferrals for this first release (explicit, not oversights):
#   - Rate limiting is enforced at the Caddy edge for otkrytka.agentspore.com
#     (ratelimit_post + ratelimit_badua); no app-level limiter is added here.
#   - Tailwind Play CDN (cdn.tailwindcss.com) stays as a documented residual: it is
#     unversioned so it cannot carry an SRI hash; self-hosting Tailwind needs a
#     build step, which is out of scope for the buildless model. The versioned libs
#     (confetti, qrcode) are vendored same-origin under /vendor.
#   - Automated Playwright / a11y / mobile / print coverage is deferred; a11y and
#     mobile were verified manually against the live deploy.
#   - Moderation, backups, export and retention are product decisions deferred for a
#     first release; card delete is a genuine hard delete, board delete is a soft
#     delete with restore (see the honest UI copy in the frontend).


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_db()
    yield


app = FastAPI(title="Otkrytka", version="1.0.0", lifespan=lifespan)

# Reject an oversized upload body at the ASGI layer (413) before Starlette spools
# the whole multipart body to a temp file. Added AFTER CORS below so CORS wraps
# it (outermost); the cap uses the configured per-image limit.
_max_upload_bytes = get_settings().max_upload_mb * 1024 * 1024
app.add_middleware(BodySizeLimitMiddleware, max_upload_bytes=_max_upload_bytes)

# CORS from settings: a comma-separated allowlist, "*" (dev default) opens it to
# any origin. Credentials stay off, so a wildcard is safe for the public
# read/embed API; restrict in prod by setting OTKRYTKA_CORS_ORIGINS.
_cors_origins = [o.strip() for o in get_settings().cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins or ["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(boards.router, prefix="/api/v1")

# Server-rendered social-unfurl pages (/c/{slug}, /og/{slug}.png). Registered
# BEFORE the SPA static mount below so the '/' catch-all never shadows them.
app.include_router(pages.router)

# Serve uploaded images read-only from the upload dir (created if missing so the
# mount never fails on a fresh volume).
settings = get_settings()
os.makedirs(settings.upload_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

# Mount the buildless frontend LAST (after all routers, /health and /uploads) so
# it does not shadow the API. html=True serves index.html at '/'; SPAStaticFiles
# adds the catch-all that serves index.html for unknown extensionless routes.
app.mount("/", SPAStaticFiles(directory=settings.frontend_dir, html=True), name="frontend")
