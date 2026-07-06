"""Pydantic request schemas for «Открытка».

Response bodies for ``GET /boards/{slug}`` are intentionally loose (``dict``)
because the payload is an assembled board + cards list; request bodies are
tightly typed. The API is directly callable (no auth), so these Field caps are
the real defense against oversized payloads, not just the frontend maxlength
attributes.
"""

from typing import Annotated

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


class BoardCreate(BaseModel):
    title: _Title
    recipient: _Recipient | None = None
    cover: str | None = Field(default=None, max_length=_COVER_MAX)


class CardCreate(BaseModel):
    author_name: _Author
    text: str | None = Field(default=None, max_length=_TEXT_MAX)
    gif_url: str | None = Field(default=None, max_length=_GIF_URL_MAX)
    image_path: str | None = Field(default=None, max_length=_IMAGE_PATH_MAX)


class OrganizerAction(BaseModel):
    """Secret-gated organizer request (pin, delete, lock, restore)."""

    organizer_token: str = Field(min_length=1, max_length=_TOKEN_MAX)
