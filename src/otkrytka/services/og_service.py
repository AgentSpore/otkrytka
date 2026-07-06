"""Per-board social-unfurl rendering for «Открытка».

Two products live here, both owned by the service layer (Router -> Service ->
db), both derived from a board looked up by slug:

* ``render_card_page`` — serves ``frontend/index.html`` with the static Open
  Graph / Twitter block swapped for per-board tags so a shared ``/c/{slug}``
  link previews the actual card (occasion + recipient) in Telegram / WhatsApp /
  Slack instead of the generic landing.
* ``render_og_image`` — a 1200x630 branded PNG in the warm identity, rendered
  with Pillow (already a dependency). Falls back to ``None`` (caller serves the
  static ``og-image.png``) when no usable TrueType font is installed.

Every user-input value (title, recipient) is HTML-escaped before it is injected
into a ``content="..."`` attribute — these are attacker-controlled, so an
un-escaped ``"><script>`` would otherwise break out of the tag.
"""

import html
import io
from pathlib import Path

import aiosqlite
from PIL import Image, ImageDraw, ImageFont

from ..core.config import get_settings

# Markers placed around the static OG block in index.html so we swap exactly that
# region without templating the whole document.
_OG_START = "<!--OG-->"
_OG_END = "<!--/OG-->"

_OG_W, _OG_H = 1200, 630

# Warm identity, sRGB (mirrors the frontend OKLCH palette; kept literal here
# because Pillow draws in sRGB).
_RASPBERRY = (201, 59, 87)
_GOLD = (227, 154, 61)
_CREAM = (253, 246, 238)
_SAND = (244, 225, 205)
_INK = (51, 32, 43)
_MUTED = (122, 90, 100)
_NOTE_COLORS = ((244, 225, 205), (247, 220, 176), (199, 154, 214), (127, 203, 176))

# First existing font wins; regular + bold probed separately. Covers macOS (dev)
# and Debian-slim (the Docker runtime, which installs fonts-dejavu-core).
_FONTS_BOLD = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
)
_FONTS_REGULAR = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
)

_SITE_NAME = {"ru": "Открытка", "en": "Otkrytka"}
_GENERIC_TITLE = {"ru": "Открытка вскладчину", "en": "A group card, together"}


# --- Locale --------------------------------------------------------------------

def pick_lang(query_lang: str | None, accept_language: str | None) -> str:
    """RU by default; ``?lang=`` wins over ``Accept-Language``. Only ru/en."""
    if query_lang:
        low = query_lang.strip().lower()
        if low.startswith("en"):
            return "en"
        if low.startswith("ru"):
            return "ru"
    if accept_language and accept_language.strip().lower().startswith("en"):
        return "en"
    return "ru"


def _description(recipient: str | None, lang: str) -> str:
    if lang == "en":
        return (
            f"A group card for {recipient} · add your wish"
            if recipient
            else "A group card · add your wish"
        )
    return (
        f"Открытка для {recipient} · добавьте тёплое пожелание"
        if recipient
        else "Тёплые слова вскладчину · добавьте пожелание"
    )


# --- DB lookup (non-raising: a missing board still serves the generic SPA) ------

async def _board_for_og(db: aiosqlite.Connection, slug: str) -> aiosqlite.Row | None:
    db.row_factory = aiosqlite.Row
    async with db.execute(
        "SELECT slug, title, recipient "
        "FROM boards WHERE slug = ? AND deleted_at IS NULL",
        (slug,),
    ) as cur:
        return await cur.fetchone()


# --- HTML page (dynamic OG injection) ------------------------------------------

def _index_html() -> str:
    path = Path(get_settings().frontend_dir) / "index.html"
    return path.read_text(encoding="utf-8")


def _og_block(board: aiosqlite.Row, lang: str, base_url: str) -> str:
    title = board["title"]
    recipient = board["recipient"]
    url = f"{base_url}/c/{board['slug']}"
    image = f"{base_url}/og/{board['slug']}.png"
    desc = _description(recipient, lang)

    def e(value: str) -> str:  # HTML-escapes & < > " ' (quote=True)
        return html.escape(value, quote=True)

    return (
        f'<meta property="og:type" content="website">\n'
        f'  <meta property="og:site_name" content="{e(_SITE_NAME[lang])}">\n'
        f'  <meta property="og:title" content="{e(title)}">\n'
        f'  <meta property="og:description" content="{e(desc)}">\n'
        f'  <meta property="og:url" content="{e(url)}">\n'
        f'  <meta property="og:image" content="{e(image)}">\n'
        f'  <meta property="og:image:width" content="1200">\n'
        f'  <meta property="og:image:height" content="630">\n'
        f'  <meta name="twitter:card" content="summary_large_image">\n'
        f'  <meta name="twitter:title" content="{e(title)}">\n'
        f'  <meta name="twitter:description" content="{e(desc)}">\n'
        f'  <meta name="twitter:image" content="{e(image)}">'
    )


def _replace_og(template: str, block: str) -> str:
    start = template.find(_OG_START)
    end = template.find(_OG_END)
    if start == -1 or end == -1 or end < start:
        return template  # markers absent -> serve unchanged rather than mangle
    return template[:start] + block + template[end + len(_OG_END):]


async def render_card_page(
    db: aiosqlite.Connection, slug: str, lang: str, base_url: str
) -> str:
    """index.html with per-board OG tags; unchanged (generic OG) if no board."""
    template = _index_html()
    board = await _board_for_og(db, slug)
    if board is None:
        return template
    return _replace_og(template, _og_block(board, lang, base_url))


# --- OG image (Pillow) ---------------------------------------------------------

def _load_font(candidates: tuple[str, ...], size: int) -> ImageFont.FreeTypeFont | None:
    for path in candidates:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return None


def _wrap(draw: ImageDraw.ImageDraw, text: str, font, max_w: int, max_lines: int) -> list[str]:
    lines: list[str] = []
    for word in text.split():
        if lines and draw.textlength(f"{lines[-1]} {word}", font=font) <= max_w:
            lines[-1] = f"{lines[-1]} {word}"
        else:
            lines.append(word)
        if len(lines) > max_lines:
            break
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        while lines and draw.textlength(lines[-1] + "…", font=font) > max_w:
            lines[-1] = lines[-1][:-1]
        lines[-1] = lines[-1] + "…"
    return lines or [""]


async def render_og_image(db: aiosqlite.Connection, slug: str) -> bytes | None:
    """Render a branded per-board PNG; ``None`` -> caller serves the static image."""
    title_font = _load_font(_FONTS_BOLD, 78)
    recipient_font = _load_font(_FONTS_REGULAR, 44)
    wordmark_font = _load_font(_FONTS_BOLD, 34)
    if title_font is None or recipient_font is None or wordmark_font is None:
        return None  # no usable font -> fall back to the static og-image.png

    board = await _board_for_og(db, slug)
    title = board["title"] if board else _GENERIC_TITLE["ru"]
    recipient = board["recipient"] if board else None

    img = Image.new("RGB", (_OG_W, _OG_H), _RASPBERRY)
    draw = ImageDraw.Draw(img)
    # Inset cream card.
    m = 48
    draw.rounded_rectangle((m, m, _OG_W - m, _OG_H - m), radius=40, fill=_CREAM)
    # Gold top accent inside the card.
    draw.rounded_rectangle((m, m, _OG_W - m, m + 14), radius=7, fill=_GOLD)

    pad = m + 64
    draw.text((pad, m + 56), _SITE_NAME["ru"], font=wordmark_font, fill=_GOLD)

    y = m + 130
    if recipient:
        for_line = f"Для {recipient}"  # «Для {recipient}»
        draw.text((pad, y), for_line, font=recipient_font, fill=_RASPBERRY)
        y += 68

    max_w = _OG_W - 2 * pad
    for line in _wrap(draw, title, title_font, max_w, 3):
        draw.text((pad, y), line, font=title_font, fill=_INK)
        y += 96

    # Masonry hint: a few rounded note shapes along the bottom.
    note_y = _OG_H - m - 118
    x = pad
    for i, color in enumerate(_NOTE_COLORS):
        w = 150 + (i % 2) * 40
        draw.rounded_rectangle((x, note_y, x + w, note_y + 70), radius=16, fill=color)
        x += w + 22
        if x > _OG_W - pad:
            break

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()
