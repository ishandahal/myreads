import pytest
import sqlite3
from pathlib import Path

from bookshelf.db import add_book, init_db, list_books, search_books, update_book
from bookshelf.models import Book, BookNotFoundError, InvalidColumnError


def test_init_db_creates_books_table(tmp_path: Path):
    db_path = tmp_path / "test.db"
    init_db(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='books'"
    )
    assert cursor.fetchone() is not None
    conn.close()


def test_add_book_returns_id(tmp_path: Path):
    db_path = tmp_path / "test.db"
    init_db(db_path)

    book = Book(title="Dune", author="Frank Herbert")
    book_id = add_book(db_path, book)

    assert isinstance(book_id, int)
    assert book_id > 0


def test_add_book_persists_data(tmp_path: Path):
    db_path = tmp_path / "test.db"
    init_db(db_path)

    book = Book(title="Dune", author="Frank Herbert", genre="sci-fi")
    add_book(db_path, book)

    conn = sqlite3.connect(db_path)
    row = conn.execute("SELECT title, author, genre FROM books WHERE id=1").fetchone()
    conn.close()

    assert row == ("Dune", "Frank Herbert", "sci-fi")


def test_list_books_returns_all(tmp_path: Path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    add_book(db_path, Book(title="Dune", author="Frank Herbert"))
    add_book(db_path, Book(title="Neuromancer", author="William Gibson"))

    books = list_books(db_path)

    assert len(books) == 2
    assert all(isinstance(b, Book) for b in books)


def test_list_books_filters_by_status(tmp_path: Path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    add_book(db_path, Book(title="Dune", author="Frank Herbert", status="read"))
    add_book(db_path, Book(title="Neuromancer", author="William Gibson"))

    books = list_books(db_path, status="read")

    assert len(books) == 1
    assert books[0].title == "Dune"


def test_list_books_filters_by_genre(tmp_path: Path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    add_book(db_path, Book(title="Dune", author="Frank Herbert", genre="sci-fi"))
    add_book(db_path, Book(title="1984", author="George Orwell", genre="dystopian"))

    books = list_books(db_path, genre="sci-fi")

    assert len(books) == 1
    assert books[0].title == "Dune"


def test_list_books_sorts_by_column(tmp_path: Path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    add_book(db_path, Book(title="Neuromancer", author="William Gibson"))
    add_book(db_path, Book(title="Dune", author="Frank Herbert"))

    books = list_books(db_path, sort_by="title")

    assert books[0].title == "Dune"
    assert books[1].title == "Neuromancer"


def test_update_book_single_field(tmp_path: Path):
    db_path = tmp_path / "test.db"
    init_db(db_path)

    book = Book(title="Dune", author="Frank Herbert", genre="sci-fi")
    book_id = add_book(db_path, book)

    update_book(db_path, book_id, {"author": "Jack Boyle"})

    conn = sqlite3.connect(db_path)
    row = conn.execute(
        "SELECT title, author, genre FROM books WHERE id=?", (book_id,)
    ).fetchone()
    conn.close()

    assert row == ("Dune", "Jack Boyle", "sci-fi")


def test_update_book_multiple_fields(tmp_path: Path):
    db_path = tmp_path / "test.db"
    init_db(db_path)

    book = Book(title="Dune", author="Frank Herbert", status="want-to-read", genre="sci-fi")
    book_id = add_book(db_path, book)

    update_book(db_path, book_id, {"status": "read", "genre": "classic sci-fi", "notes": "Loved it"})

    conn = sqlite3.connect(db_path)
    row = conn.execute(
        "SELECT status, genre, notes FROM books WHERE id=?", (book_id,)
    ).fetchone()
    conn.close()

    assert row == ("read", "classic sci-fi", "Loved it")


def test_update_book_invalid_column(tmp_path: Path):
    db_path = tmp_path / "test.db"
    init_db(db_path)

    book = Book(title="Dune", author="Frank Herbert", genre="sci-fi")
    book_id = add_book(db_path, book)

    with pytest.raises(InvalidColumnError):
        update_book(db_path, book_id, {"invalid column": "Jack Boyle"})


def test_update_book_invalid_book_id(tmp_path: Path):
    db_path = tmp_path / "test.db"
    init_db(db_path)

    book = Book(title="Dune", author="Frank Herbert", genre="sci-fi")
    add_book(db_path, book)

    with pytest.raises(BookNotFoundError):
        update_book(db_path, 999, {"author": "Jack Boyle"})

def test_search_books(tmp_path: Path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    add_book(db_path, Book(title="Dune", author="Frank Herbert", genre="sci-fi"))
    add_book(db_path, Book(title="1984", author="George Orwell", genre="dystopian", notes="some with Dune"))
    add_book(db_path, Book(title="test", author="test test", genre="sci-fi"))

    books = search_books(db_path, term="Dune")
    titles = {b.title for b in books}
    authors = {b.author for b in books}

    assert len(books) == 2
    assert titles == {"Dune", "1984"}
    assert authors == {"Frank Herbert", "George Orwell"}

    # Negative case: no matches
    books = search_books(db_path, term="nonexistent")
    assert len(books) == 0


def test_search_books_with_field(tmp_path: Path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    add_book(db_path, Book(title="Dune", author="Frank Herbert", genre="sci-fi"))
    add_book(db_path, Book(title="1984", author="George Orwell", genre="dystopian", notes="some with Dune"))
    add_book(db_path, Book(title="test", author="test test", genre="sci-fi"))

    books = search_books(db_path, term="1984", field="title")

    assert len(books) == 1
    assert books[0].genre == "dystopian"


def test_list_books_invalid_sort_column(tmp_path: Path):
    db_path = tmp_path / "test.db"
    init_db(db_path)

    with pytest.raises(InvalidColumnError):
        list_books(db_path, sort_by="invalid_column")


def test_search_books_invalid_field(tmp_path: Path):
    db_path = tmp_path / "test.db"
    init_db(db_path)

    with pytest.raises(InvalidColumnError):
        search_books(db_path, term="Dune", field="banana")