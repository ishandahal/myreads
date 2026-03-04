import sqlite3
from pathlib import Path

from bookshelf.db import init_db, add_book
from bookshelf.models import Book


def test_init_db_creates_books_table(tmp_path: Path):
    db_path = tmp_path / "test.db"
    init_db(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='books'"
    )
    assert cursor.fetchone() is not None
    conn.close()
