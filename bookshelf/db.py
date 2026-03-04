import sqlite3
from pathlib import Path


def init_db(db_path: Path) -> None:
    """Create the bookshelf database and books table if they don't exist.

    Args:
        db_path: Path to the SQLite database file.
    """
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'want-to-read',
            genre TEXT NOT NULL DEFAULT '',
            notes TEXT NOT NULL DEFAULT '',
            source TEXT NOT NULL DEFAULT '',
            added_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()
