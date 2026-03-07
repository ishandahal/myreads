from pathlib import Path

import click

from bookshelf.db import (
    add_book,
    delete_book,
    init_db,
    list_books,
    search_books,
    update_book,
)
from bookshelf.models import VALID_STATUSES, Book, BookNotFoundError, InvalidColumnError

DEFAULT_DB = Path.home() / ".bookshelf.db"


@click.group()
@click.option("--db", default=str(DEFAULT_DB), help="Path to the database file.")
@click.pass_context
def cli(ctx: click.Context, db: str) -> None:
    """Bookshelf — a CLI tool to track your books."""
    ctx.ensure_object(dict)
    db_path = Path(db)
    init_db(db_path)
    ctx.obj["db_path"] = db_path


@cli.command()
@click.option("--title", required=True, help="Book title.")
@click.option("--author", required=True, help="Book author.")
@click.option(
    "--status",
    type=click.Choice(VALID_STATUSES, case_sensitive=False),
    default="want-to-read",
    help="Reading status.",
)
@click.option("--genre", default="", help="Book genre.")
@click.option("--notes", default="", help="Short notes.")
@click.option("--source", default="", help="Where you heard about it.")
@click.pass_context
def add(
    ctx: click.Context,
    title: str,
    author: str,
    status: str,
    genre: str,
    notes: str,
    source: str,
) -> None:
    """Add a book to your shelf."""
    book = Book(
        title=title,
        author=author,
        status=status,
        genre=genre,
        notes=notes,
        source=source,
    )
    book_id = add_book(ctx.obj["db_path"], book)
    click.echo(f"Added '{title}' by {author} (id: {book_id})")


@cli.command("list")
@click.option("--status", default=None, help="Filter by status.")
@click.option("--genre", default=None, help="Filter by genre.")
@click.option("--sort-by", default="added_at", help="Column to sort by.")
@click.pass_context
def list_cmd(
    ctx: click.Context, status: str | None, genre: str | None, sort_by: str
) -> None:
    """List books on your shelf."""
    books = list_books(ctx.obj["db_path"], status=status, genre=genre, sort_by=sort_by)
    if not books:
        click.echo("No books found.")
        return
    for book in books:
        click.echo(
            f"[{book.id}] {book.title} by {book.author} ({book.status}) genre:{book.genre}"
        )


@cli.command()
@click.argument("book_id", type=int)
@click.option("--title", default=None, help="Book title.")
@click.option("--author", default=None, help="Book author.")
@click.option(
    "--status",
    type=click.Choice(VALID_STATUSES, case_sensitive=False),
    default=None,
    help="Reading status.",
)
@click.option("--genre", default=None, help="Book genre.")
@click.option("--notes", default=None, help="Short notes.")
@click.option("--source", default=None, help="Where you heard about it.")
@click.pass_context
def update(ctx: click.Context, book_id: int, **kwargs: str | None) -> None:
    """Update a book on your shelf by ID."""
    changes = {k: v for k, v in kwargs.items() if v is not None}
    if not changes:
        click.echo("Nothing to update — provide at least one option.")
        return
    try:
        update_book(ctx.obj["db_path"], book_id, changes)
    except (BookNotFoundError, InvalidColumnError) as e:
        click.echo(str(e))
        ctx.exit(1)
    else:
        summary = ", ".join(f"{k}='{v}'" for k, v in changes.items())
        click.echo(f"Updated book #{book_id}: {summary}")


@cli.command()
@click.argument("term")
@click.option("--field", default=None, help="Limit search to a specific field.")
@click.pass_context
def search(ctx: click.Context, term: str, field: str | None) -> None:
    """Search books by keyword across all text fields."""
    try:
        books = search_books(ctx.obj["db_path"], term, field=field)
    except InvalidColumnError as e:
        click.echo(str(e))
        ctx.exit(1)
    else:
        if not books:
            click.echo(f"No books matching '{term}'.")
            return
        for book in books:
            click.echo(
                f"[{book.id}] {book.title} by {book.author} ({book.status}) genre:{book.genre}"
            )


@cli.command()
@click.argument("book_id", type=int)
@click.pass_context
def delete(ctx: click.Context, book_id: int) -> None:
    """Delete a book from your shelf by ID."""
    try:
        delete_book(ctx.obj["db_path"], book_id)
    except BookNotFoundError as e:
        click.echo(str(e))
        ctx.exit(1)
    else:
        click.echo(f"Removed book #{book_id}")
