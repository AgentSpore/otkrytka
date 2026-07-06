# SPEC — Otkrytka integration batch 2 (embeddable card + copy-embed + oEmbed)

Goal: let users DROP a live Otkrytka card into a blog, a memorial/tribute page, Notion, a website — via an
embeddable iframe + "copy embed code" + oEmbed. Builds on batch 1 (`/c/{slug}` real URLs exist). Read
`frontend/{index.html,app.js,styles.css}`, `src/otkrytka/api/pages.py`, `src/otkrytka/services/og_service.py`,
`main.py`, `core/config.py` first.

## 1. Embeddable read-only card `GET /embed/{slug}`
- Add `GET /embed/{slug}` (in pages.py, before static mount) that serves index.html with an EMBED-MODE signal
  to the frontend (inject `window.__EMBED__=true` via the batch-1 marked-block helper; don't duplicate HTML).
- Frontend embed mode: render the card READ-ONLY + warm/compact:
  - Show board title + recipient + the masonry of wish cards (pinned first), live WS updates.
  - HIDE add-wish, organizer controls (pin/lock/delete/deliver), share row, nav chrome, landing.
  - 🔴 Do NOT expose the organizer token in embed mode at all (embed has no manage access).
  - Small footer "Открыть открытку / Open the card" → full `/c/{slug}` (_blank).
  - Fits an iframe from ~320px up; masonry collapses to 1 col on narrow width.
- Iframe-embeddable: no `X-Frame-Options`/CSP `frame-ancestors` blocking (grep; allow framing for `/embed/*`). Public read-only.

## 2. "Copy embed code" in the share UI
- On the existing share row, add "Встроить / Embed" → box with the iframe snippet + copy button:
  `<iframe src="https://<canonical>/embed/{slug}" width="100%" height="560" style="border:0;border-radius:16px" loading="lazy" title="..."></iframe>`
  Build src from `canonical_base_url` (batch-1 config). Localize labels (STR ×2 en+ru).

## 3. oEmbed endpoint `GET /oembed`
- `GET /oembed?url=<card or embed url>&format=json&maxwidth=&maxheight=` → oEmbed 1.0 JSON
  `{"version":"1.0","type":"rich","provider_name":"Otkrytka","provider_url":"<canonical>","title":<board title>,
   "width":<w>,"height":<h>,"html":"<iframe src='.../embed/{slug}' ...></iframe>"}`.
  - Parse `slug` from the `url` param (accept `/c/{slug}` and `/embed/{slug}` of the canonical host; reject
    foreign host → 404; malformed → 400).
  - 🔴 SECURITY: board title into JSON `title` (json-encode) and into the iframe `title="..."` (HTML-escape);
    escape slug in the src. Only `format=json` (501 for xml). Never expose organizer token.
- Discovery: in the batch-1 `/c/{slug}` head injection, ADD
  `<link rel="alternate" type="application/json+oembed" href="<canonical>/oembed?url=<canonical>/c/{slug}&format=json" title="...">`.

## Hard rules
aiosqlite only. Module-level imports. Router→Service→db. No #000/#fff. No em-dash in new copy. New STR keys 2×.
Do NOT break batch-1 `/c/{slug}`, masonry/modal/upload/pin/lock/deliver/WS, hash back-compat, the organizer
token privacy, or the normal card render. Keep tests green + ADD tests (embed 200 read-only + no organizer
controls + no token in body, oEmbed JSON valid + escaped + rejects foreign url, discovery link in /c head).

## Scope: ONLY /tmp/otkrytka. No deploy/commit/push. Run Skill("dev-self-review", stack=python) before finishing.
## Verify (paste): pytest -q green (+new), node --check OK, ruff clean, greps, describe /embed + /oembed. Append ## RESULT. Caveman ultra.

## RESULT

SHIP: live embeddable read-only card + copy-embed + oEmbed. Builds on B1 marker-swap.

### Files
- `src/otkrytka/services/og_service.py` — generalize marker-swap `_replace_og`->`_replace_marked`; `<!--SIG-->` block `_sig_block` (canonical origin + `__EMBED__` flag, `json.dumps` JS-safe); `render_embed_page` (embed signal + per-board OG, NO token); oEmbed: `oembed_slug` (parse `/c/`|`/embed/` of canonical host, `OembedMalformedError`->400 / `OembedForeignError`->404), `render_oembed` (+clamp maxw/maxh, def 480x560), `_oembed_payload` (title HTML-esc into iframe `title=`, json-enc into `title`, src esc); `_og_block` adds oEmbed discovery `<link>` (url-enc href, esc title).
- `src/otkrytka/api/pages.py` — `GET /embed/{slug}` (read-only HTML, framing allowed, no token); `GET /oembed` (json only else 501; maps malformed/foreign exc -> 400/404).
- `frontend/index.html` — `<!--SIG--><!--/SIG-->` marker (empty on static landing).
- `frontend/app.js` — STR embed_* x2 (en+ru); `state.embed`; parseRoute `/embed/{slug}`->view embed; render dispatch; `renderEmbed`+`paintEmbed` (compact read-only, `wishHtml(c,false,..)`=no organizer tools, no add-wish/share/nav, live WS via `applyObserverRefresh` embed branch, footer "Open the card"->`/c/{slug}` _blank); share-row "⧉ Embed" btn + `showEmbedModal` (iframe snippet from `__CANONICAL__`||origin, copy).
- `frontend/styles.css` — `.embed-wrap/.embed-head/.embed-foot` (masonry already 1-col <560px).
- `tests/test_embed.py` (NEW, 13) — embed 200+`__EMBED__` signal, /c not embed, embed no-token, FE read-only static-check, oEmbed json valid, embed-url+size clamp, title-escape (no `"><script>`, has `&lt;script&gt;`), reject foreign 404 / malformed 400 / non-card 404 / xml 501, discovery link in /c head, oEmbed no-token.
- `README.md` — documented `/embed/{slug}` + `/oembed` + discovery.

### Verify
- `uv run pytest -q` -> 52 passed (39 pre-existing + 13 new), 0.47s.
- `node --check frontend/app.js` -> OK.
- `uv run ruff check .` -> All checks passed.
- greps (og_service.py, pages.py): local-imports / ==None / len==0 / bare-except / print -> ALL EMPTY. em-dash: none in new STR copy. #000/#fff: none in embed css.
- dev-self-review: ready_to_commit=true (scope clean, no protected files, all greps+checklist pass).

### /embed + /oembed described
- `GET /embed/{slug}` -> SPA with `window.__EMBED__=true`; SPA renders compact read-only card (title+recipient+masonry pinned-first, live WS), hides add-wish + ALL organizer controls + share + nav + landing; footer -> full `/c/{slug}` _blank. Framable (no X-Frame/CSP anywhere in repo). Token NEVER injected.
- `GET /oembed?url=&format=json&maxwidth=&maxheight=` -> oEmbed 1.0 rich JSON {version,type,provider_name=Otkrytka,provider_url,title,width,height,html=<iframe .../embed/{slug}>}. Accepts `/c/`|`/embed/` of canonical host only; foreign->404, malformed->400, xml->501. Title escaped in iframe `title=`+JSON. Discovery `<link application/json+oembed>` added to `/c/{slug}` head.

### Not done / notes
- No commit/push/deploy (per scope). SIG block also injects `window.__CANONICAL__` on `/c/{slug}` so the copy-embed snippet uses the server-trusted origin; bare `/#/slug` hash route (static mount, no injection) falls back to `location.origin` (== canonical in prod).

### Robustness follow-up (reviewer)
- **oEmbed host-check fails closed on canonical.** `render_oembed` now compares the url= host against `get_settings().canonical_base_url` ONLY (not the spoofable request-derived `_base_url`); unset -> `OembedNotConfiguredError` -> 500. Route dropped the `request` param + `_base_url` for oEmbed. Provider_url + iframe src now built from canonical too. Prod always sets `OTKRYTKA_CANONICAL_BASE_URL`, so this only hardens dev/misconfig.
- **Cache-Control `public, max-age=300`** on both `/embed/{slug}` (HTMLResponse) and `/oembed` (JSONResponse) — parity with the OG image, 5-min TTL balances crawler re-fetch vs live content.
- New tests (+3): oEmbed uses canonical not spoofed `X-Forwarded-Host`; fails closed 500 when canonical unset; both responses carry Cache-Control. Cleaned em-dash in the new pages.py docstring.
- Re-verify: `uv run pytest -q` -> 55 passed (39 pre-existing + 16 new); `node --check frontend/app.js` -> OK; `uv run ruff check .` -> clean.
