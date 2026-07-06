"""aiosqlite schema init for «Открытка» (otkrytka) collaborative greeting card.

aiosqlite ONLY (no ORM). ``settings.db_path`` is a file path, not a
``sqlite:///`` URL. A board (the card) collects many contributor cards, each
carrying a typed name, some text, and an optional local image or GIF URL. The
organizer holds a secret ``organizer_token`` that gates pin / delete / lock.
"""

import aiosqlite

from .config import get_settings


async def get_db():
    settings = get_settings()
    async with aiosqlite.connect(settings.db_path) as db:
        await db.execute("PRAGMA foreign_keys = ON")
        yield db


async def init_db():
    settings = get_settings()
    async with aiosqlite.connect(settings.db_path) as db:
        await db.execute("PRAGMA foreign_keys = ON")
        await db.execute("""
            CREATE TABLE IF NOT EXISTS boards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                slug TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                recipient TEXT,
                cover TEXT NOT NULL DEFAULT '',
                organizer_token TEXT NOT NULL,
                locked INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                deleted_at TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                board_id INTEGER NOT NULL,
                author_name TEXT NOT NULL,
                text TEXT,
                image_path TEXT,
                gif_url TEXT,
                pinned INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (board_id) REFERENCES boards (id) ON DELETE CASCADE
            )
        """)
        await db.execute(
            "CREATE INDEX IF NOT EXISTS idx_cards_board ON cards (board_id)"
        )
        await db.commit()
