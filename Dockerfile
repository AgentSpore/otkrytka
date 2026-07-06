FROM python:3.11-slim
WORKDIR /app
# libjpeg + zlib + libwebp are the runtime libs Pillow needs to decode/encode
# jpg / png / webp uploads. slim images ship without them.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libjpeg62-turbo zlib1g libwebp7 \
    && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml README.md ./
COPY src ./src
COPY frontend ./frontend
RUN pip install --no-cache-dir .
# Uploads + the sqlite db live under /data (a persistent volume in compose).
RUN mkdir -p /data/uploads
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["uvicorn", "otkrytka.main:app", "--host", "0.0.0.0", "--port", "8000"]
