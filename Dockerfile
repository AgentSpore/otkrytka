FROM python:3.11-slim-bookworm@sha256:0a310eeecf4e1f5a0743f9a6520c90c88d089c903ca5fd283f501e3a805f5f89 AS builder
COPY --from=ghcr.io/astral-sh/uv:0.9.30@sha256:538e0b39736e7feae937a65983e49d2ab75e1559d35041f9878b7b7e51de91e4 /uv /usr/local/bin/uv
WORKDIR /app
ENV UV_PYTHON_DOWNLOADS=never UV_NO_CACHE=1
COPY pyproject.toml uv.lock README.md ./
COPY src ./src
RUN uv sync --locked --no-dev --no-editable
COPY frontend /frontend-source
RUN /app/.venv/bin/python -m otkrytka.core.frontend_assets /frontend-source /frontend-built

FROM python:3.11-slim-bookworm@sha256:0a310eeecf4e1f5a0743f9a6520c90c88d089c903ca5fd283f501e3a805f5f89
WORKDIR /app
# libjpeg + zlib + libwebp are the runtime libs Pillow needs to decode/encode
# jpg / png / webp uploads. fonts-dejavu-core gives Pillow a Cyrillic-capable
# TrueType face so GET /og/{slug}.png can render per-board previews (without it
# the route falls back to the static og-image.png). slim images ship none of it.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libjpeg62-turbo zlib1g libwebp7 fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /frontend-built ./frontend
# Uploads + the sqlite db live under /data (a persistent volume in compose).
RUN groupadd --system --gid 10001 appuser \
    && useradd --system --uid 10001 --gid appuser --no-create-home appuser \
    && mkdir -p /data/uploads \
    && chown -R appuser:appuser /data
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
USER 10001:10001
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD ["/app/.venv/bin/python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3).close()"]
CMD ["/app/.venv/bin/uvicorn", "otkrytka.main:app", "--host", "0.0.0.0", "--port", "8000"]
