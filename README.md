# Открытка (otkrytka)

A no-signup, link-shareable collaborative group greeting card. The organizer
creates a board with one link; everyone adds a card (a name, a few warm words,
and an optional photo or GIF) with no account. Cards land on a cozy masonry
board that updates live for everyone watching. The organizer can pin the best
wishes, lock the board, and deliver it with a little confetti.

## Stack

- **Backend**: FastAPI + aiosqlite (a single SQLite file, no ORM).
- **Media**: uploaded images are validated + re-encoded server-side with Pillow
  and stored on local disk (`/data/uploads`); no S3. GIFs are added by pasting an
  image URL, so no third-party API key is needed.
- **Frontend**: buildless — Tailwind Play CDN + vanilla JS, served as static
  files. Full EN + RU parity, OKLCH warm palette.
- **Realtime**: an in-process WebSocket hub broadcasts a `changed` signal on
  every mutation; clients refetch. Single-process uvicorn.

## Layout

```
src/otkrytka/
  main.py                     FastAPI app, mounts /uploads + the frontend last
  core/config.py              pydantic-settings (OTKRYTKA_ env prefix)
  core/db.py                  aiosqlite schema init (boards + cards)
  core/realtime.py            BoardHub WebSocket pub/sub
  api/boards.py               thin router -> service
  schemas/board.py            pydantic request models (Field caps)
  services/board_service.py   store + orchestration, owns commits, guards, uploads
frontend/                     index.html + app.js + styles.css
tests/                        pytest (api, cards, status guards, upload)
```

## Domain

- **Board** (the card) — `slug` (short link), `title`, `recipient`, `cover`
  (emoji or palette key), a secret `organizer_token`, `locked`. Soft-deletable.
- **Card** (one contribution) — `author_name`, `text`, optional `image_path`
  (a local upload) or `gif_url`, `pinned`. No account, no PII beyond a name.

## Develop

```bash
uv venv
uv pip install -e ".[dev]"
uv run uvicorn otkrytka.main:app --reload
# tests
uv run pytest -q
```

Open http://localhost:8000.

## Deploy

`docker compose up -d`. Both the SQLite file and the uploaded images live on an
external named volume `otkrytka-data` mounted at `/data`, with
`OTKRYTKA_DB_PATH=/data/otkrytka.db` and `OTKRYTKA_UPLOAD_DIR=/data/uploads`, so
redeploys never wipe boards or photos. Create the volume once before the first
deploy:

```bash
docker volume create otkrytka-data
```

## API

- `POST /api/v1/boards` `{title, recipient?, cover?}` -> `{slug, organizer_token}`
  (the token is shown once, to the creator)
- `GET /api/v1/boards/{slug}` -> board + cards (pinned first, then newest)
- `POST /api/v1/boards/{slug}/cards` `{author_name, text?, gif_url?, image_path?}`
- `POST /api/v1/boards/{slug}/upload` (multipart) -> `{image_path}`
- `POST /api/v1/cards/{card_id}/pin` `{organizer_token}` (toggle)
- `DELETE /api/v1/cards/{card_id}` `{organizer_token}`
- `PATCH /api/v1/boards/{board_id}/lock` `{organizer_token}`
- `DELETE /api/v1/boards/{board_id}` + `POST /api/v1/boards/{board_id}/restore`
  `{organizer_token}`
- `WS /api/v1/boards/{slug}/ws` — live `changed` signal

## Not in this version (v2)

- **Video contributions** — storage-heavy; deferred.
- **Payment / collected gift money (ЮKassa)** — deferred; the service is free
  with a generous per-board card cap.
