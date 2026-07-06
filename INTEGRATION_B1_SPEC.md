# SPEC — Otkrytka integration batch 1 (dynamic OG + real-path share)

Goal: make a shared Otkrytka link actually PREVIEW the card (recipient + occasion) in Telegram/WhatsApp/
Slack/iMessage, via real server-visible URLs + dynamic per-board OG. It ALREADY has share buttons (TG/WA/VK)
+ QR + a static og-image + Pillow — reuse those. Read `frontend/{index.html,app.js}`, `src/otkrytka/main.py`,
`src/otkrytka/api/boards.py`, `src/otkrytka/services/board_service.py` first.

## Problem
Links are hash-routed `/#/slug`. Crawlers fetch `/` → see only the STATIC landing OG, never the card. Fix
with real URLs + dynamic per-board OG.

## 1. Real-path card URL + dynamic OG (core fix)
- Add backend route `GET /c/{slug}` (before the SPA static mount) that:
  - Loads the board by slug. If missing/deleted → still serve the SPA (generic OG) 200.
  - Serves `frontend/index.html` with the `<head>` OG/Twitter tags REPLACED per-board: `og:title` = board
    title (e.g. «С днём рождения, Аня!»), `og:description` = a short localized line (e.g. «Открытка для {recipient} · добавьте тёплое пожелание» / "A group card for {recipient} · add your wish"), `og:url` = the absolute `/c/{slug}` URL, `og:image` = `/og/{slug}.png` (below), twitter:card=summary_large_image + same fields. Keep 💌 favicon.
  - 🔴 SECURITY: title/recipient are USER INPUT — HTML-escape every injected value (`& < > " '`) before putting into `content="..."`. Add a test: title `"><script>alert(1)</script>` → escaped, no breakout.
  - Locale RU/EN from `?lang=` else `Accept-Language`, default RU.
  - Inject cleanly via explicit `<!--OG-->...<!--/OG-->` markers around the current static OG block in index.html + a Python string replace (don't duplicate the whole HTML).
- Keep `GET /` serving the landing with the existing static OG.

## 2. Per-board OG image `GET /og/{slug}.png`
- Reuse the existing Pillow dep. Render a 1200×630 branded PNG in the WARM identity: cover emoji + recipient
  («Для {recipient}») + occasion title, warm raspberry/gold OKLCH-equivalent sRGB colors, 💌 wordmark, a
  hint of the masonry (a couple note shapes). If the board is missing → generic branded card. If a slug has
  no recipient, just show the title. Prefer per-board; if fragile, fall back to the static `og-image.png`.

## 3. Frontend router reads the real path
- SPA must render a board at `/c/{SLUG}` (read `location.pathname`) in ADDITION to the existing `/#/slug`
  hash route (keep hash = back-compat). Handle load + `popstate`. The organizer deep link `/#/slug/k/token`
  and delivery `/#/slug/deliver` MUST keep working — do not break token/deliver routing.
- Change share-link + copy-link builders to produce `https://<host>/c/{slug}` (guest link). The organizer
  manage link stays private (keep it as the token hash form or a `/c/{slug}/k/{token}` real path — your call,
  but it must NOT leak the token into any crawler-visible or logged place; keep current safety).

## 4. Docs
- Verify `README.md` matches the real API; add the new `GET /c/{slug}` + `GET /og/{slug}.png`. Note no-auth + upload + WS.

## Hard rules
aiosqlite only. Module-level imports. Router→Service→db. No #000/#fff in frontend. No em-dash in new copy.
New STR keys each exactly 2× (en+ru). Do NOT break masonry/modal/upload/pin/lock/deliver/WS or the token/
deliver hash routes. Keep tests green + ADD tests (OG escaping, /c/{slug} 200 contains escaped title, /og/{slug}.png image/png, share builder uses /c/).

## Scope: ONLY /tmp/otkrytka. Do NOT deploy/commit/push. Run Skill("dev-self-review", stack=python) before finishing.
## Verify (paste): pytest -q green (+new), node --check OK, ruff clean, greps, describe `/c/{slug}` head. Append ## RESULT. Caveman ultra.

## RESULT

Shipped: shared Otkrytka links now preview the CARD (recipient + occasion) via
real crawler-visible URLs + dynamic per-board OG.

### Files changed
- `src/otkrytka/services/og_service.py` (NEW) — dynamic OG HTML injection (marker
  swap, HTML-escaped title/recipient), 1200x630 Pillow per-board PNG (warm
  identity, «Для {recipient}» + occasion + masonry note shapes), locale RU/EN,
  font-fallback to static og-image.png when no TTF present.
- `src/otkrytka/api/pages.py` (NEW) — `GET /c/{slug}` (200 even if missing/deleted),
  `GET /og/{slug}.png`; base-url honors X-Forwarded-Proto/Host.
- `src/otkrytka/main.py` — include pages.router BEFORE the SPA static mount.
- `frontend/index.html` — `<!--OG-->...<!--/OG-->` markers around the static OG block.
- `frontend/app.js` — parseRoute reads real path `/c/{slug}` (hash routes take
  precedence, so `/#/slug`, `/#/slug/k/token`, `/#/slug/deliver` all keep working);
  popstate + goHome (pushState '/'); share/copy/QR/TG/WA/VK guest link = `/c/{slug}`;
  organizer manage link stays `/#/slug/k/token` (token never in a server path/log).
- `tests/test_og.py` (NEW) — 8 tests: per-board OG, XSS escape of `"><script>`,
  EN description, unknown-slug 200, no token leak, png content-type + signature,
  unknown-slug png, share-builder uses /c/.
- `README.md` — documented `GET /c/{slug}` + `GET /og/{slug}.png`, no-auth/upload/WS.
- `Dockerfile` — add `fonts-dejavu-core` so per-board PNG renders in prod (ack'd
  protected edit via .claude/allow-protected, removed after).

### Verify
- `pytest -q` -> **38 passed** (30 pre-existing + 8 new), green.
- `node --check frontend/app.js` -> OK.
- `ruff check .` -> All checks passed.
- greps (local-imports / bare-except / ==None / len()==0 / loguru-fstring /
  print-non-test) -> clean on all changed py files.
- Live head of `/c/{slug}`: og:title + twitter:title = `&quot;&gt;&lt;script&gt;
  alert(1)&lt;/script&gt;` (fully escaped, no breakout); og:url=`https://.../c/{slug}`,
  og:image=`https://.../og/{slug}.png`; RU desc `Открытка для Аня · ...`, EN
  `A group card for Аня · ...`. og image = 200 image/png, ~20KB, `\x89PNG` sig.

### Not done / notes
- OG PNG renders typographic warm card (recipient+occasion+note shapes); raw cover
  emoji NOT drawn (Arial/DejaVu lack color-emoji glyphs -> would tofu). Preview text
  is the load-bearing content; reliable over a broken box.
- In a prod image WITHOUT the new font layer, `/og/{slug}.png` gracefully falls
  back to static og-image.png; the dynamic OG *meta* (the actual preview text)
  still works regardless.

### RESULT — security/robustness follow-up (reviewer)
- **Host-injection fixed**: `core/config.py` adds `canonical_base_url` (env
  `OTKRYTKA_CANONICAL_BASE_URL`). When set (prod), `_base_url` uses it verbatim
  and ignores Host / X-Forwarded-* — og:url/og:image can no longer be spoofed to
  a phishing domain. Empty (dev) = request-derived. Verified live: spoofed
  `X-Forwarded-Host: evil.example` -> og stays `https://otkrytka.agentspore.com`,
  `evil.example` absent.
- **DoS surface reduced**: `/og/{slug}.png` now sends `Cache-Control: public,
  max-age=3600` (deterministic per slug+content) so crawlers/CDN/Caddy dedupe the
  Pillow render. Applied to both dynamic + static-fallback responses.
- Dropped unused `cover` from `_board_for_og` SELECT.
- Config edit ack'd via .claude/allow-protected (removed after).
- Re-verify: pytest **39 passed**, node --check OK, ruff clean.
