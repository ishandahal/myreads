from pathlib import Path

import click

from bookshelf.db import add_book, init_db, list_books
from bookshelf.models import VALID_STATUSES, Book

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
def add(ctx: click.Context, title: str, author: str, status: str, genre: str, notes: str, source: str) -> None:
    """Add a book to your shelf."""
    book = Book(title=title, author=author, status=status, genre=genre, notes=notes, source=source)
    book_id = add_book(ctx.obj["db_path"], book)
    click.echo(f"Added '{title}' by {author} (id: {book_id})")


@cli.command("list")
@click.option("--status", default=None, help="Filter by status.")
@click.option("--genre", default=None, help="Filter by genre.")
@click.option("--sort-by", default="added_at", help="Column to sort by.")
@click.pass_context
def list_cmd(ctx: click.Context, status: str | None, genre: str | None, sort_by: str) -> None:
    """List books on your shelf."""
    books = list_books(ctx.obj["db_path"], status=status, genre=genre, sort_by=sort_by)
    if not books:
        click.echo("No books found.")
        return
    for book in books:
        click.echo(f"[{book.id}] {book.title} by {book.author} ({book.status}) genre:{book.genre}")