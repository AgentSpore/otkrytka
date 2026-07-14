"""Pydantic request schemas for «Открытка».

Response bodies for ``GET /boards/{slug}`` are intentionally loose (``dict``)
because the payload is an assembled board + cards list; request bodies are
tightly typed. The API is directly callable (no auth), so these Field caps are
the real defense against oversized payloads, not just the frontend maxlength
attributes.
"""

from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, Field, StringConstraints

_TITLE_MAX = 120
_RECIPIENT_MAX = 80
_AUTHOR_MAX = 48
_TEXT_MAX = 2000
_GIF_URL_MAX = 500
_COVER_MAX = 40
_IMAGE_PATH_MAX = 200
_TOKEN_MAX = 128

# Whitespace-only names/titles are meaningless, so strip first, then enforce
# min_length — a "   " title/author collapses to "" and is rejected (422).
_Title = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=_TITLE_MAX)]
_Recipient = Annotated[str, StringConstraints(strip_whitespace=True, max_length=_RECIPIENT_MAX)]
_Author = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=_AUTHOR_MAX)]

# Occasion preset (drives the create/guest prompt copy + a themed accent). ``None``
# / absent == "birthday" == the original behaviour, so a legacy board is unchanged.
Occasion = Literal["birthday", "farewell", "teacher", "retirement", "thanks"]

# Corp-brand accent: a strict 6-digit hex colour (``#RRGGBB``). The pattern is the
# real validation (the API is directly callable), rejecting anything else with 422.
_BrandColor = Annotated[
    str, StringConstraints(strip_whitespace=True, pattern=r"^#[0-9a-fA-F]{6}$")
]


class BoardCreate(BaseModel):
    title: _Title
    recipient: _Recipient | None = None
    cover: str | None = Field(default=None, max_length=_COVER_MAX)
    # All three are optional and additive: omit them for a plain birthday card.
    occasion: Occasion | None = None
    # ISO-8601 datetime; a future value gates the reveal until then (None = open,
    # the current manual-only behaviour). Pydantic parses "Z" / offset / naive.
    reveal_at: datetime | None = None
    brand_color: _BrandColor | None = None


class BoardSettings(BaseModel):
    """Organizer-gated update of the occasion / scheduled-reveal / brand accent.

    Full-replace semantics: each optional field is written as sent (``None``
    clears it). Setting a ``reveal_at`` re-gates the board; clearing it re-opens
    the board (mirrors create). ``reveal_board`` is the separate manual override.
    """

    organizer_token: str = Field(min_length=1, max_length=_TOKEN_MAX)
    occasion: Occasion | None = None
    reveal_at: datetime | None = None
    brand_color: _BrandColor | None = None


class CardCreate(BaseModel):
    author_name: _Author
    text: str | None = Field(default=None, max_length=_TEXT_MAX)
    gif_url: str | None = Field(default=None, max_length=_GIF_URL_MAX)
    image_path: str | None = Field(default=None, max_length=_IMAGE_PATH_MAX)


class OrganizerAction(BaseModel):
    """Secret-gated organizer request (pin, delete, lock, restore)."""

    organizer_token: str = Field(min_length=1, max_length=_TOKEN_MAX)
