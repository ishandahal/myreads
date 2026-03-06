# Bookshelf

A command-line tool to track your reading list. Add books, update their status, search across your library, and filter by genre or reading status — all from the terminal.

Data is stored locally in a SQLite database (default: `~/.bookshelf.db`).

## Installation

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone <your-repo-url>
cd bookshelf
uv sync
```

## Usage

All commands are run via `uv run bookshelf` (or just `bookshelf` if installed globally).

### Add a book

```bash
bookshelf add --title "Dune" --author "Frank Herbert" --genre "sci-fi" --source "Reddit"
```

Options: `--title` (required), `--author` (required), `--status`, `--genre`, `--notes`, `--source`

Valid statuses: `want-to-read` (default), `reading`, `read`

### List books

```bash
bookshelf list
bookshelf list --status reading
bookshelf list --genre sci-fi --sort-by title
```

Options: `--status`, `--genre`, `--sort-by` (default: `added_at`)

### Update a book

```bash
bookshelf update 1 --status read --notes "Loved it"
```

Pass the book ID (shown in `list` output) followed by any fields to change.

### Search

```bash
bookshelf search "Herbert"
bookshelf search "sci-fi" --field genre
```

Searches across title, author, genre, notes, and source by default. Use `--field` to limit to a specific column.

### Database location

By default, bookshelf stores data in `~/.bookshelf.db`. Override with `--db`:

```bash
bookshelf --db /path/to/custom.db list
```

## Quick example

```bash
bookshelf add --title "Dune" --author "Frank Herbert" --genre "sci-fi"
bookshelf add --title "1984" --author "George Orwell" --genre "dystopian"
bookshelf list
bookshelf update 1 --status reading
bookshelf search "Orwell"
```

## Project structure

```
bookshelf/
├── bookshelf/
│   ├── __init__.py
│   ├── cli.py        # Click CLI commands
│   ├── db.py         # SQLite database operations
│   └── models.py     # Book dataclass and custom exceptions
├── tests/
│   ├── test_cli.py
│   └── test_db.py
├── pyproject.toml
└── README.md
```

All public functions include docstrings with parameter and return value documentation. Use `help()` in a Python shell or read the source for details.

## Development

```bash
uv sync
uv run pytest tests/ -v       # Run tests
uv run ruff check .            # Lint
uv run ruff format .           # Format
uv run mypy bookshelf/         # Type check
```

## Dependencies

- [click](https://click.palletsprojects.com/) — CLI framework
- [sqlite3](https://docs.python.org/3/library/sqlite3.html) — database (Python standard library)

Dev dependencies: pytest, ruff, mypy

## License

MIT
