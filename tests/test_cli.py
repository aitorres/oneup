"""
Unit test collection for the command-line interface functions.
"""

from pathlib import Path

import pytest

from oneup import cli


def test_get_parser() -> None:
    """
    Unit tests for the function that returns a parser for
    the tool's CLi
    """

    parser = cli.get_parser()
    assert isinstance(parser.description, str)
    assert "A CLI tool" in parser.description
    assert parser.epilog == "Happy coding! :-)"


def test_discover_all_requirement_files(
    monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    Unit tests that make sure that file discovery is working as expected.
    """

    monkeypatch.setattr("os.path.isfile", lambda name: "/" not in name)

    monkeypatch.setattr("os.listdir", lambda: [])
    assert cli.discover_all_requirement_files() == []

    monkeypatch.setattr("os.listdir", lambda: ["test", "another_test.txt"])
    assert cli.discover_all_requirement_files() == []

    monkeypatch.setattr(
        "os.listdir",
        lambda: [
            "requirements.txt",
            "another_test.txt"
        ]
    )
    assert cli.discover_all_requirement_files() == [Path("requirements.txt")]

    monkeypatch.setattr(
        "os.listdir",
        lambda: [
            "pyproject.toml",
            "another_test.txt"
        ]
    )
    assert cli.discover_all_requirement_files() == [Path("pyproject.toml")]

    monkeypatch.setattr(
        "os.listdir",
        lambda: [
            "pyproject.toml",
            "requirements.txt"
        ]
    )
    assert cli.discover_all_requirement_files() == [
        Path("pyproject.toml"),
        Path("requirements.txt"),
    ]

    monkeypatch.setattr(
        "os.listdir",
        lambda: [
            "pyproject.toml.png",
            "requirements.txt.svg",
            "this is not a requirements file.txt",
            "not requirements.txt",
            "definitely not a pyproject.toml",
        ]
    )
    assert cli.discover_all_requirement_files() == []


def test_is_valid_idx() -> None:
    """
    Test for the potential index validator
    """

    assert not cli.is_valid_idx("3", 0, 3)
    assert not cli.is_valid_idx("5", 0, 3)
    assert not cli.is_valid_idx("-1", 0, 3)
    assert not cli.is_valid_idx("not a number", 0, 3)
    assert not cli.is_valid_idx("", 0, 3)

    assert cli.is_valid_idx("0", 0, 3)
    assert cli.is_valid_idx("1", 0, 3)
    assert cli.is_valid_idx("2", 0, 3)


def test_discover_requirement_file(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test that the function that determines what file to use
    is behaving properly
    """

    monkeypatch.setattr(
        cli,
        "discover_all_requirement_files",
        lambda: None
    )
    assert cli.discover_requirement_file(True) is None
    assert cli.discover_requirement_file(False) is None

    monkeypatch.setattr(
        cli,
        "discover_all_requirement_files",
        lambda: [Path("requirements.txt")]
    )
    assert cli.discover_requirement_file(True) == Path("requirements.txt")
    assert cli.discover_requirement_file(False) == Path("requirements.txt")

    monkeypatch.setattr(
        cli,
        "discover_all_requirement_files",
        lambda: [Path("requirements.txt"), Path("pyproject.toml")]
    )
    assert (
        cli.discover_requirement_file(False)
        == Path("requirements.txt")
    )

    monkeypatch.setattr('builtins.input', lambda _: "0")
    assert (
        cli.discover_requirement_file(True)
        == Path("requirements.txt")
    )

    monkeypatch.setattr('builtins.input', lambda _: "1")
    assert (
        cli.discover_requirement_file(True)
        == Path("pyproject.toml")
    )


def test_get_dependencies_from_pyproject_file() -> None:
    """
    Tests the function that returns dependencies given a parsed
    pyproject file map
    """

    assert cli.get_dependencies_from_pyproject_file(
        {
            "dependencies": {
                "package1": "1.2.3",
                "package2": "4.5.6",
            }
        }
    ) == ["package1", "package2"]

    assert cli.get_dependencies_from_pyproject_file(
        {
            "install_requires": {
                "package1": "1.2.3",
                "package2": "4.5.6",
            }
        }
    ) == ["package1", "package2"]

    assert cli.get_dependencies_from_pyproject_file(
        {
            "requires": {
                "package1": "1.2.3",
                "package2": "4.5.6",
            }
        }
    ) == ["package1", "package2"]

    assert cli.get_dependencies_from_pyproject_file(
        {
            "tool": {
                "poetry": {
                    "dependencies": {
                        "package1": "1.2.3",
                        "package2": "4.5.6",
                    },
                }
            }
        }
    ) == ["package1", "package2"]

    assert cli.get_dependencies_from_pyproject_file(
        {
            "tool": {
                "poetry": {
                    "dev-dependencies": {
                        "package3": "1.2.3",
                        "package4": "4.5.6",
                    }
                }
            }
        }
    ) == ["package3", "package4"]

    assert cli.get_dependencies_from_pyproject_file(
        {
            "tool": {
                "poetry": {
                    "dependencies": {
                        "package1": "1.2.3",
                        "package2": "4.5.6",
                    },
                    "dev-dependencies": {
                        "package3": "1.2.3",
                        "package4": "4.5.6",
                    }
                }
            }
        }
    ) == ["package1", "package2", "package3", "package4"]

    assert cli.get_dependencies_from_pyproject_file({}) == []
