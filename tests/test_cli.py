from pathlib import Path

from click.testing import CliRunner

from bookshelf.cli import cli


def test_add_command(tmp_path: Path):
    db_path = str(tmp_path / "test.db")
    runner = CliRunner()
    result = runner.invoke(cli, [
        "--db", db_path,
        "add",
        "--title", "Dune",
        "--author", "Frank Herbert",
    ])

    assert result.exit_code == 0
    assert "Added" in result.output


def test_list_command_shows_books(tmp_path: Path):
    db_path = str(tmp_path / "test.db")
    runner = CliRunner()
    runner.invoke(cli, [
        "--db", db_path, "add",
        "--title", "Dune", "--author", "Frank Herbert", "--genre", "sci-fi",
    ])

    result = runner.invoke(cli, ["--db", db_path, "list"])

    assert result.exit_code == 0
    assert "Dune" in result.output
    assert "Frank Herbert" in result.output


def test_list_command_filters_by_status(tmp_path: Path):
    db_path = str(tmp_path / "test.db")
    runner = CliRunner()
    runner.invoke(cli, [
        "--db", db_path, "add",
        "--title", "Dune", "--author", "Frank Herbert", "--status", "read",
    ])
    runner.invoke(cli, [
        "--db", db_path, "add",
        "--title", "Neuromancer", "--author", "William Gibson",
    ])

    result = runner.invoke(cli, ["--db", db_path, "list", "--status", "read"])

    assert result.exit_code == 0
    assert "Dune" in result.output
    assert "Neuromancer" not in result.output