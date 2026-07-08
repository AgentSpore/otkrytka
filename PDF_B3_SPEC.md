# SPEC — Otkrytka printable / PDF delivery card

Goal: let the organizer download / print the finished greeting card as a nice keepsake (PDF via the browser's
print-to-PDF, no heavy server dep). Read `frontend/{index.html,app.js,styles.css}` — especially the delivery
view (`/#/{slug}/deliver` / `renderDeliver`).

## 1. Print-optimized delivery + button
- On the delivery view (the "Подарить"/reveal screen), add a "Скачать PDF / Печать" button (localize: ru
  «Скачать PDF», en "Download PDF") that calls `window.print()`.
- Add an `@media print` stylesheet that makes the delivery view print beautifully to A4/Letter:
  - Hide everything except the card content (nav, buttons, footers, the print button itself → `display:none` in print).
  - Show the recipient + occasion title + ALL wish cards in a clean, paginated flow (cards should not be cut
    mid-card across a page: `break-inside: avoid`). Keep the warm identity but ensure text is legible on white
    paper (dark ink on light; the warm cream bg can stay light or go white for ink economy — your call, keep it tasteful).
  - Ensure images/GIFs in cards print (set `-webkit-print-color-adjust: exact; print-color-adjust: exact` so
    background tints/colors render if you keep them).
  - A tasteful print header/footer: card title + "otkrytka.agentspore.com" small in the footer is fine.
- The button + print CSS are frontend-only (no server PDF library). Browser "Save as PDF" = the deliverable.

## 2. (optional, only if trivial) delivery meta
- If the deliver view lacks a clean page title for the print/PDF filename, set `document.title` to the card
  title on the deliver route so the saved PDF is named sensibly. Reuse the existing i18n title wiring.

## Hard rules
Frontend-only (`frontend/{app.js,styles.css}`, maybe index.html). Do NOT touch backend, WS, upload, or any
route. Do NOT break the deliver view, masonry, confetti, or any existing flow. No #000/#fff in screen styles
(print styles MAY use white paper + dark ink — that's print, not the forbidden inline-hex screen rule; but
prefer the OKLCH tokens / named values where possible). No em-dash in new copy. New STR keys 2× (en+ru).
`node --check frontend/app.js` must pass.

## Tests
- `uv run pytest -q` must stay green (frontend-only change; backend untouched).
- Since print output can't be unit-tested, verify: the print button STR keys exist 2×, an `@media print` block
  exists in styles.css, `window.print` is wired on the deliver view. Describe in RESULT.

## Scope: ONLY /tmp/otkrytka. No deploy/commit/push. Run Skill("dev-self-review", stack=python).
## Verify (paste): pytest -q green, node --check OK, ruff clean, greps (print button STR 2×, @media print present, no em-dash). Append ## RESULT. Caveman ultra.

## RESULT

DONE. Frontend-only. Backend/WS/upload/routes untouched.

### Diff
- `frontend/app.js` — STR `download_pdf` x2 (en "Download PDF", ru "Скачать PDF"); `renderDeliver` now emits a `.no-print` "🖨 Скачать PDF" btn (`#deliver-print` -> `window.print()`) beside the back link, a `.print-only .deliver-colophon` footer (`{title} · otkrytka.agentspore.com`), `deliver-view`/`deliver-head` classes on the main/head, and `document.title = b.title` so the saved PDF is named after the card.
- `frontend/styles.css` — `.print-only{display:none}` + `@media print` block: `@page margin:16mm`; `print-color-adjust:exact` (tints/photos/GIFs render); white paper, dark `--ink` text; hides `.no-print`/`#confetti-canvas`/`.toast`/`.live-pip`/`.modal-overlay`/`.lang-btn`; kills blobs+reveal anims; `.deliver-view .masonry` 2-up; `.wish` `break-inside/page-break-inside:avoid` (no mid-card slice); fixed running colophon each page.

### Verify (evidence)
- `node --check frontend/app.js` -> NODE_CHECK_OK
- `uv run pytest -q` -> 55 passed in 0.61s (backend untouched, still green)
- `ruff check .` -> All checks passed!
- grep `download_pdf:` app.js -> 2 (en+ru)
- grep `@media print` styles.css -> 1 (present)
- grep `window.print` app.js -> 1321 (wired on deliver view)
- em-dash scan of new copy/lines -> none (used middot `·`)
- No `#000`/`#fff` in screen styles; single `#ffffff` is inside `@media print` (spec-permitted paper).
- Empty catches flagged by self-review greps (app.js 398/854/1008/1106) are all PRE-EXISTING, not this change.

### Not covered
- Actual print raster/PDF pagination not renderable headless here; verified structurally (STR x2, `@media print` block, `break-inside:avoid`, `window.print` wired, colophon element). Deliver view / masonry / confetti / back-link flow left intact (only additive class + button + footer).
