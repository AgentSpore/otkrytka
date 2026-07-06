import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .api import boards, pages
from .core.config import get_settings
from .core.db import init_db

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_db()
    yield


app = FastAPI(title="Otkrytka", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
