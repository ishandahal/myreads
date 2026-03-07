from pathlib import Path

from click.testing import CliRunner

from bookshelf.cli import cli


def test_add_command(tmp_path: Path):
    db_path = str(tmp_path / "test.db")
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "--db",
            db_path,
            "add",
            "--title",
            "Dune",
            "--author",
            "Frank Herbert",
        ],
    )

    assert result.exit_code == 0
    assert "Added" in result.output


def test_list_command_shows_books(tmp_path: Path):
    db_path = str(tmp_path / "test.db")
    runner = CliRunner()
    runner.invoke(
        cli,
        [
            "--db",
            db_path,
            "add",
            "--title",
            "Dune",
            "--author",
            "Frank Herbert",
            "--genre",
            "sci-fi",
        ],
    )

    result = runner.invoke(cli, ["--db", db_path, "list"])

    assert result.exit_code == 0
    assert "Dune" in result.output
    assert "Frank Herbert" in result.output


def test_list_command_filters_by_status(tmp_path: Path):
    db_path = str(tmp_path / "test.db")
    runner = CliRunner()
    runner.invoke(
        cli,
        [
            "--db",
            db_path,
            "add",
            "--title",
            "Dune",
            "--author",
            "Frank Herbert",
            "--status",
            "read",
        ],
    )
    runner.invoke(
        cli,
        [
            "--db",
            db_path,
            "add",
            "--title",
            "Neuromancer",
            "--author",
            "William Gibson",
        ],
    )

    result = runner.invoke(cli, ["--db", db_path, "list", "--status", "read"])

    assert result.exit_code == 0
    assert "Dune" in result.output
    assert "Neuromancer" not in result.output


def test_update_command(tmp_path: Path):
    db_path = str(tmp_path / "test.db")
    runner = CliRunner()
    runner.invoke(
        cli,
        [
            "--db",
            db_path,
            "add",
            "--title",
            "Dune",
            "--author",
            "Frank Herbert",
        ],
    )

    result = runner.invoke(
        cli,
        [
            "--db",
            db_path,
            "update",
            "1",
            "--status",
            "read",
        ],
    )

    assert result.exit_code == 0
    assert "Updated book #1" in result.output
    assert "status='read'" in result.output


def test_update_command_no_options(tmp_path: Path):
    db_path = str(tmp_path / "test.db")
    runner = CliRunner()
    runner.invoke(
        cli,
        [
            "--db",
            db_path,
            "add",
            "--title",
            "Dune",
            "--author",
            "Frank Herbert",
        ],
    )

    result = runner.invoke(cli, ["--db", db_path, "update", "1"])

    assert result.exit_code == 0
    assert "Nothing to update" in result.output


def test_search_command(tmp_path: Path):
    db_path = str(tmp_path / "test.db")
    runner = CliRunner()
    runner.invoke(
        cli,
        [
            "--db",
            db_path,
            "add",
            "--title",
            "Dune",
            "--author",
            "Frank Herbert",
            "--genre",
            "sci-fi",
        ],
    )
    runner.invoke(
        cli,
        [
            "--db",
            db_path,
            "add",
            "--title",
            "1984",
            "--author",
            "George Orwell",
        ],
    )

    result = runner.invoke(cli, ["--db", db_path, "search", "Dune"])

    assert result.exit_code == 0
    assert "Dune" in result.output
    assert "1984" not in result.output


def test_search_command_no_results(tmp_path: Path):
    db_path = str(tmp_path / "test.db")
    runner = CliRunner()
    runner.invoke(
        cli,
        [
            "--db",
            db_path,
            "add",
            "--title",
            "Dune",
            "--author",
            "Frank Herbert",
        ],
    )

    result = runner.invoke(cli, ["--db", db_path, "search", "nonexistent"])

    assert result.exit_code == 0
    assert "No books matching" in result.output


def test_update_command_invalid_book_id(tmp_path: Path):
    db_path = str(tmp_path / "test.db")
    runner = CliRunner()
    runner.invoke(
        cli,
        [
            "--db",
            db_path,
            "add",
            "--title",
            "Dune",
            "--author",
            "Frank Herbert",
        ],
    )

    result = runner.invoke(
        cli,
        [
            "--db",
            db_path,
            "update",
            "999",
            "--status",
            "read",
        ],
    )

    assert result.exit_code == 1
    assert "No book with id 999" in result.output


def test_search_command_invalid_field(tmp_path: Path):
    db_path = str(tmp_path / "test.db")
    runner = CliRunner()
    runner.invoke(
        cli,
        [
            "--db",
            db_path,
            "add",
            "--title",
            "Dune",
            "--author",
            "Frank Herbert",
        ],
    )

    result = runner.invoke(
        cli,
        [
            "--db",
            db_path,
            "search",
            "Dune",
            "--field",
            "banana",
        ],
    )

    assert result.exit_code == 1
    assert "Invalid search column" in result.output


def test_delete_command(tmp_path: Path):
    db_path = str(tmp_path / "test.db")
    runner = CliRunner()
    runner.invoke(
        cli,
        [
            "--db",
            db_path,
            "add",
            "--title",
            "Dune",
            "--author",
            "Frank Herbert",
        ],
    )

    result = runner.invoke(cli, ["--db", db_path, "delete", "1"])

    assert result.exit_code == 0
    assert "Removed book #1" in result.output

    result = runner.invoke(cli, ["--db", db_path, "list"])
    assert "Dune" not in result.output


def test_delete_command_invalid_book_id(tmp_path: Path):
    db_path = str(tmp_path / "test.db")
    runner = CliRunner()

    result = runner.invoke(cli, ["--db", db_path, "delete", "999"])

    assert result.exit_code == 1
    assert "No book with id 999" in result.output
