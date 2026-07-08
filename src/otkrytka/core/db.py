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
    # DEFAULT isolation_level (implicit transactions): a multi-statement write
    # such as delete_board (UPDATE + DELETE) is auto-wrapped in one transaction
    # committed by ``db.commit()`` -> atomic for free. The atomic card-cap path
    # issues an explicit ``BEGIN IMMEDIATE`` preceded ONLY by SELECTs, so no
    # implicit transaction is open when it runs (mirrors the Verdict roster
    # pattern); a plain ``BEGIN`` after a DML would raise, hence the read-only
    # preamble is a hard invariant of _insert_card_atomic.
    async with aiosqlite.connect(settings.db_path) as db:
        await db.execute("PRAGMA foreign_keys = ON")
        # Wait up to 5s for a competing writer instead of raising a raw
        # ``database is locked`` (which would surface as an opaque 500).
        await db.execute("PRAGMA busy_timeout = 5000")
        yield db


async def init_db():
    settings = get_settings()
    async with aiosqlite.connect(settings.db_path) as db:
        await db.execute("PRAGMA foreign_keys = ON")
        # WAL lets readers run concurrently with a single writer; set once, it is
        # persisted in the database file.
        await db.execute("PRAGMA journal_mode = WAL")
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
        # Upload ownership: a filename is minted here at upload time and bound to
        # the board it was uploaded for, so ``add_card`` can reject an image_path
        # minted for a different board, and delete can find files to unlink.
        await db.execute("""
            CREATE TABLE IF NOT EXISTS uploads (
                filename TEXT PRIMARY KEY,
                board_id INTEGER NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (board_id) REFERENCES boards (id) ON DELETE CASCADE
            )
        """)
        await db.execute(
            "CREATE INDEX IF NOT EXISTS idx_cards_board ON cards (board_id)"
        )
        await db.execute(
            "CREATE INDEX IF NOT EXISTS idx_uploads_board ON uploads (board_id)"
        )
        await db.commit()
