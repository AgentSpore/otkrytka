import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .api import boards, pages
from .core.config import get_settings
from .core.db import init_db
from .core.limits import BodySizeLimitMiddleware

logger = logging.getLogger(__name__)


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
# it does not shadow the API. html=True serves index.html at '/'.
app.mount("/", StaticFiles(directory=settings.frontend_dir, html=True), name="frontend")
