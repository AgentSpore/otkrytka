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

The API needs no auth: anyone with a board's `slug` can read it and add a card
(via `POST .../cards` or the multipart `POST .../upload`); only the secret
`organizer_token` gates pin / lock / delete. Live updates arrive over the
`WS .../ws` channel.

### Share / social-unfurl (server-rendered, outside `/api/v1`)

- `GET /c/{slug}` — the guest share link. Serves the SPA with the Open Graph /
  Twitter tags rewritten per-board (occasion title + a localized line naming the
  recipient) so a shared link previews the actual card in Telegram / WhatsApp /
  Slack. An unknown or deleted slug still returns 200 with the generic landing
  OG. Locale is `?lang=ru|en`, else `Accept-Language`, default RU. User input is
  HTML-escaped before injection. This is the link the copy/QR/TG/WA/VK buttons
  produce; the organizer link stays a `#/{slug}/k/{token}` hash so the token is
  never in a server path or access log.
- `GET /og/{slug}.png` — a 1200x630 branded per-board preview image (warm
  identity, recipient + occasion), rendered with Pillow. Falls back to the
  static `og-image.png` when no TrueType font is installed.
- `GET /embed/{slug}` — a read-only, framable version of the card for embedding
  in a blog, tribute page or Notion. Serves the SPA with a `window.__EMBED__`
  signal so it hides add-wish, all organizer controls, the share row and the
  nav, keeps the live WebSocket updates, and shows an "Open the card" link to
  `/c/{slug}`. Never carries the organizer token. No `X-Frame-Options` /
  CSP `frame-ancestors` is set, so framing is allowed. The share row's
  "Embed" button copies the `<iframe>` snippet for this URL.
- `GET /oembed?url=&format=json&maxwidth=&maxheight=` — oEmbed 1.0 `rich`
  response for a canonical `/c/{slug}` or `/embed/{slug}` URL, returning the
  `<iframe>` embed HTML. Only `format=json` (else 501); foreign hosts / non-card
  paths are rejected (404) and unparseable URLs are 400. The board title is
  HTML-escaped into the iframe and JSON-encoded into the `title` field. A
  `<link rel="alternate" type="application/json+oembed">` discovery tag is added
  to the `/c/{slug}` head.

## Not in this version (v2)

- **Video contributions** — storage-heavy; deferred.
- **Payment / collected gift money (ЮKassa)** — deferred; the service is free
  with a generous per-board card cap.
