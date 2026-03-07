import sqlite3
from datetime import datetime
from pathlib import Path
from typing import cast

from bookshelf.models import Book, BookNotFoundError, InvalidColumnError

# Module-level column whitelists: these are security boundaries that guard
# against SQL injection in dynamically built queries (ORDER BY / SET clauses).
SORTABLE_COLUMNS = {"title", "author", "status", "genre", "added_at", "updated_at"}
UPDATABLE_COLUMNS = {"title", "author", "status", "genre", "notes", "source"}
SEARCHABLE_COLUMNS = {"title", "author", "genre", "notes", "source"}

BOOK_COLUMNS = "id, title, author, status, genre, notes, source, added_at, updated_at"


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


def add_book(db_path: Path, book: Book) -> int:
    """Insert a book into the database.

    Args:
        db_path: Path to the SQLite database file.
        book: Book instance to insert.

    Returns:
        The ID of the newly inserted book.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.execute(
        """
        INSERT INTO books (title, author, status, genre, notes, source, added_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            book.title,
            book.author,
            book.status,
            book.genre,
            book.notes,
            book.source,
            book.added_at,
            book.updated_at,
        ),
    )
    conn.commit()
    # lastrowid is always set after INSERT but typed as int | None in stubs
    book_id = cast(int, cursor.lastrowid)
    conn.close()
    return book_id


def list_books(
    db_path: Path,
    status: str | None = None,
    genre: str | None = None,
    sort_by: str = "added_at",
) -> list[Book]:
    """Fetch books from the database with optional filters and sorting.

    Args:
        db_path: Path to the SQLite database file.
        status: Filter by status if provided.
        genre: Filter by genre if provided.
        sort_by: Column name to sort results by.

    Returns:
        List of matching Book instances.

    Raises:
        InvalidColumnError: If sort_by is not a valid column name.
    """
    if sort_by not in SORTABLE_COLUMNS:
        raise InvalidColumnError(f"Invalid sort column: {sort_by}")

    query = f"SELECT {BOOK_COLUMNS} FROM books"
    conditions = []
    params = []

    if status is not None:
        conditions.append("status = ?")
        params.append(status)
    if genre is not None:
        conditions.append("genre = ?")
        params.append(genre)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += f" ORDER BY {sort_by}"

    conn = sqlite3.connect(db_path)
    rows = conn.execute(query, params).fetchall()
    conn.close()

    return [
        Book(
            id=row[0],
            title=row[1],
            author=row[2],
            status=row[3],
            genre=row[4],
            notes=row[5],
            source=row[6],
            added_at=row[7],
            updated_at=row[8],
        )
        for row in rows
    ]


def update_book(db_path: Path, book_id: int, book: dict) -> None:
    """Update book in the database with provided columns and values.

    Args:
        db_path: Path to the SQLite database file.
        book_id: Id of the book to be updated.
        book: Dict of field names to new values.

    Returns:
        None

    Raises:
        InvalidColumnError: If column is not updatable.
        BookNotFoundError: If book_id is not found in the db.
    """
    for col in book:
        if col not in UPDATABLE_COLUMNS:
            raise InvalidColumnError(f"Invalid update column: {col}")

    updated_book = {**book, "updated_at": datetime.now().isoformat()}
    set_clauses = [f"{key} = :{key}" for key in updated_book]
    set_clause = ", ".join(set_clauses)

    sql_statement = f"UPDATE books SET {set_clause} WHERE id=:id"

    conn = sqlite3.connect(db_path)
    params = {**updated_book, "id": book_id}
    cursor = conn.execute(sql_statement, params)
    if cursor.rowcount == 0:
        conn.close()
        raise BookNotFoundError(f"No book with id {book_id}")
    conn.commit()
    conn.close()
def delete_book(db_path: Path, book_id: int) -> None:
    """Delete a book from the database by ID.

    Args:
        db_path: Path to the SQLite database file.
        book_id: ID of the book to delete.

    Raises:
        BookNotFoundError: If no book with the given ID exists.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.execute("DELETE FROM books WHERE id=:id", {"id": book_id})

    if cursor.rowcount == 0:
        conn.close()
        raise BookNotFoundError(f"No book with id {book_id}")

    conn.commit()
    conn.close()


def delete_book(db_path: Path, book_id: int) -> None:
    """Delete a book from the database by ID.

    Args:
        db_path: Path to the SQLite database file.
        book_id: ID of the book to delete.

    Raises:
        BookNotFoundError: If no book with the given ID exists.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.execute("DELETE FROM books WHERE id=:id", {"id": book_id})

    if cursor.rowcount == 0:
        conn.close()
        raise BookNotFoundError(f"No book with id {book_id}")

    conn.commit()
    conn.close()


def search_books(
    db_path: Path,
    term: str,
    field: str | None = None,
) -> list[Book]:
    """Search books by term across one or all searchable fields.

    Args:
        db_path: Path to the SQLite database file.
        term: Search term (substring match).
        field: Limit search to this column. If None, searches all.

    Returns:
        List of matching Book instances.

    Raises:
        InvalidColumnError: If field is not a valid searchable column.
    """
    if field is not None and field not in SEARCHABLE_COLUMNS:
        raise InvalidColumnError(f"Invalid search column: {field}")

    like_param = f"%{term}%"
    params: tuple[str, ...]

    if field is not None:
        where_clause = f"WHERE {field} LIKE ?"
        params = (like_param,)
    else:
        where_clause = "WHERE " + " OR ".join(
            f"{col} LIKE ?" for col in SEARCHABLE_COLUMNS
        )
        params = tuple(like_param for _ in SEARCHABLE_COLUMNS)

    query = f"SELECT {BOOK_COLUMNS} FROM books {where_clause} ORDER BY added_at"

    conn = sqlite3.connect(db_path)
    rows = conn.execute(query, params).fetchall()
    conn.close()

    return [
        Book(
            id=row[0],
            title=row[1],
            author=row[2],
            status=row[3],
            genre=row[4],
            notes=row[5],
            source=row[6],
            added_at=row[7],
            updated_at=row[8],
        )
        for row in rows
    ]