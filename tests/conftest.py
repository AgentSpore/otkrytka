import os
import tempfile
from collections.abc import AsyncIterator

# Point the app at a throwaway db + upload dir BEFORE importing otkrytka modules
# so get_settings() (lru-cached) picks up the temp paths on first read.
# Unique per xdist worker (and per PID) so parallel test runs never share files.
_WORKER = os.environ.get("PYTEST_XDIST_WORKER", f"main{os.getpid()}")
_TMP_DB = os.path.join(tempfile.gettempdir(), f"otkrytka_pytest_{_WORKER}.db")
_TMP_UPLOADS = os.path.join(tempfile.gettempdir(), f"otkrytka_uploads_{_WORKER}")
os.environ["OTKRYTKA_DB_PATH"] = _TMP_DB
os.environ["OTKRYTKA_UPLOAD_DIR"] = _TMP_UPLOADS

import pytest_asyncio  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402

from otkrytka.core.config import get_settings  # noqa: E402
from otkrytka.core.db import init_db  # noqa: E402
from otkrytka.main import app  # noqa: E402


@pytest_asyncio.fixture
async def client() -> AsyncIterator[AsyncClient]:
    # Fresh schema per test.
    if os.path.exists(_TMP_DB):
        os.remove(_TMP_DB)
    os.makedirs(_TMP_UPLOADS, exist_ok=True)
    get_settings.cache_clear()
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
