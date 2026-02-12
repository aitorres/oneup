"""
Unit test collection for the command-line interface functions.
"""

import sys
from pathlib import Path
from typing import Callable, Final, Optional

import pytest
from oneup import __version__, cli

SAMPLE_FILES_PATH: Final[Path] = Path("tests/sample_files")


def test_get_parser() -> None:
    """
    Unit tests for the function that returns a parser for
    the tool's CLi
    """

    parser = cli.get_parser()
    assert isinstance(parser.description, str)
    assert "A CLI tool" in parser.description
    assert parser.epilog == f"(v{__version__}) | Happy coding! :-)"


def test_discover_all_requirement_files(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Unit tests that make sure that file discovery is working as expected.
    """

    monkeypatch.setattr("os.path.isfile", lambda name: "/" not in name)

    monkeypatch.setattr("os.listdir", lambda: [])
    assert cli.discover_all_requirement_files() == []

    monkeypatch.setattr("os.listdir", lambda: ["test", "another_test.txt"])
    assert cli.discover_all_requirement_files() == []

    monkeypatch.setattr("os.listdir", lambda: ["requirements.txt", "another_test.txt"])
    assert cli.discover_all_requirement_files() == [Path("requirements.txt")]

    monkeypatch.setattr("os.listdir", lambda: ["pyproject.toml", "another_test.txt"])
    assert cli.discover_all_requirement_files() == [Path("pyproject.toml")]

    monkeypatch.setattr("os.listdir", lambda: ["pyproject.toml", "requirements.txt"])
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
        ],
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

    monkeypatch.setattr(cli, "discover_all_requirement_files", lambda: None)
    assert cli.discover_requirement_file(True) is None
    assert cli.discover_requirement_file(False) is None

    monkeypatch.setattr(
        cli, "discover_all_requirement_files", lambda: [Path("requirements.txt")]
    )
    assert cli.discover_requirement_file(True) == Path("requirements.txt")
    assert cli.discover_requirement_file(False) == Path("requirements.txt")

    monkeypatch.setattr(
        cli,
        "discover_all_requirement_files",
        lambda: [Path("requirements.txt"), Path("pyproject.toml")],
    )
    assert cli.discover_requirement_file(False) == Path("requirements.txt")

    monkeypatch.setattr("builtins.input", lambda _: "0")
    assert cli.discover_requirement_file(True) == Path("requirements.txt")

    monkeypatch.setattr("builtins.input", lambda _: "1")
    assert cli.discover_requirement_file(True) == Path("pyproject.toml")

    def mock_double_input_function() -> Callable[[str], str]:
        values = ["2", "1"]
        idx: int = 0

        def mock_double_input(_: str) -> str:
            nonlocal idx
            value = values[idx]
            idx += 1
            return value

        return mock_double_input

    monkeypatch.setattr("builtins.input", mock_double_input_function())
    assert cli.discover_requirement_file(True) == Path("pyproject.toml")


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
    ) == [("package1", "1.2.3"), ("package2", "4.5.6")]

    assert cli.get_dependencies_from_pyproject_file(
        {
            "install_requires": {
                "package1": "1.2.3",
                "package2": "4.5.6",
            }
        }
    ) == [("package1", "1.2.3"), ("package2", "4.5.6")]

    assert cli.get_dependencies_from_pyproject_file(
        {
            "requires": {
                "package1": "1.2.3",
                "package2": "4.5.6",
            }
        }
    ) == [("package1", "1.2.3"), ("package2", "4.5.6")]

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
    ) == [("package1", "1.2.3"), ("package2", "4.5.6")]

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
    ) == [("package3", "1.2.3"), ("package4", "4.5.6")]

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
                    },
                }
            }
        }
    ) == [
        ("package1", "1.2.3"),
        ("package2", "4.5.6"),
        ("package3", "1.2.3"),
        ("package4", "4.5.6"),
    ]

    output = cli.get_dependencies_from_pyproject_file({})
    expected: list[str] = []
    assert output == expected


def test_scan_file(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Unit test for the function that scans and prints dependency versions
    from a requirements file
    """

    printed_dependencies: list[tuple[str, Optional[str]]] = []

    def mock_print_project_latest_version_and_url(
        dependency: str, version: Optional[str]
    ) -> None:
        printed_dependencies.append((dependency, version))

    monkeypatch.setattr(
        cli,
        "print_project_latest_version_and_url",
        mock_print_project_latest_version_and_url,
    )

    # case: requirements.txt
    test_file_path_1 = SAMPLE_FILES_PATH / "requirements.txt"
    cli.scan_file(test_file_path_1, 1)
    assert printed_dependencies == [
        ("mypy", "0.930"),
        ("pytest", "6.2.5"),
        ("toml", None),
    ]

    # case: pyproject.toml (poetry)
    printed_dependencies = []
    test_file_path_2 = SAMPLE_FILES_PATH / "pyproject.toml"
    cli.scan_file(test_file_path_2, 1)
    assert printed_dependencies == [
        ("requests", "^2.26.0"),
        ("toml", "^0.10.2"),
        ("pytest", "^6.2.5"),
        ("pytest-cov", "^3.0.0"),
        ("flake8", "^4.0.1"),
        ("Django", "^4.2.1"),
        ("django-stubs", "^1.7.0"),
        ("standard-imghdr", "^3.13.0"),
    ]

    # case: pyproject.toml (uv)
    printed_dependencies = []
    test_file_path_3 = SAMPLE_FILES_PATH / "uv" / "pyproject.toml"
    cli.scan_file(test_file_path_3, 1)
    assert printed_dependencies == [
        ("barkr", "0.9.6"),
        ("python-dotenv", "1.0.1"),
        ("sentry-sdk", "2.25.1"),
        ("black", "25.1.0"),
        ("flake8", "7.1.2"),
        ("isort", "6.0.1"),
    ]

    # case: pyproject.toml (poetry 2 with PEP 621 project.dependencies)
    printed_dependencies = []
    test_file_path_poetry2 = SAMPLE_FILES_PATH / "poetry2" / "pyproject.toml"
    cli.scan_file(test_file_path_poetry2, 1)
    assert printed_dependencies == [
        ("tweepy", "4.16.0"),
        ("requests", "2.32.5"),
        ("atproto", "0.0.57"),
    ]

    # case: pyproject.toml (poetry) with multiple threads
    printed_dependencies = []
    test_file_path_4 = SAMPLE_FILES_PATH / "pyproject.toml"
    cli.scan_file(test_file_path_4, 2)
    assert set(printed_dependencies) == {
        ("requests", "^2.26.0"),
        ("toml", "^0.10.2"),
        ("pytest", "^6.2.5"),
        ("pytest-cov", "^3.0.0"),
        ("flake8", "^4.0.1"),
        ("Django", "^4.2.1"),
        ("django-stubs", "^1.7.0"),
        ("standard-imghdr", "^3.13.0"),
    }

    # case: unknown file
    with pytest.raises(SystemExit):
        cli.scan_file(Path("unknown_file.txt"), 1)


def test_main_with_file_arg(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Tests the main function when a file is provided via command line argument
    """
    test_file = SAMPLE_FILES_PATH / "requirements.txt"
    test_args = ["oneup", "--file", str(test_file)]
    monkeypatch.setattr(sys, "argv", test_args)

    scanned_files = []

    def mock_scan_file(file_path: Path, n_threads: int) -> None:
        scanned_files.append((file_path, n_threads))

    monkeypatch.setattr(cli, "scan_file", mock_scan_file)
    cli.main()
    assert scanned_files == [(test_file, 1)]


def test_main_with_threads(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Tests the main function when thread count is specified
    """
    test_file = SAMPLE_FILES_PATH / "requirements.txt"
    test_args = ["oneup", "--file", str(test_file), "--threads", "4"]
    monkeypatch.setattr(sys, "argv", test_args)

    scanned_files = []

    def mock_scan_file(file_path: Path, n_threads: int) -> None:
        scanned_files.append((file_path, n_threads))

    monkeypatch.setattr(cli, "scan_file", mock_scan_file)
    cli.main()
    assert scanned_files == [(test_file, 4)]


def test_main_no_file_found(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Tests the main function when no requirements file is found
    """
    test_args = ["oneup"]
    monkeypatch.setattr(sys, "argv", test_args)
    monkeypatch.setattr(cli, "discover_requirement_file", lambda _: None)

    with pytest.raises(SystemExit):
        cli.main()


def test_main_auto_discover(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Tests the main function when it auto-discovers a requirements file
    """
    test_file = Path("requirements.txt")
    test_args = ["oneup"]
    monkeypatch.setattr(sys, "argv", test_args)

    def mock_discover_requirement_file(_: bool) -> Optional[Path]:
        return test_file

    scanned_files = []

    def mock_scan_file(file_path: Path, n_threads: int) -> None:
        scanned_files.append((file_path, n_threads))

    monkeypatch.setattr(
        cli, "discover_requirement_file", mock_discover_requirement_file
    )
    monkeypatch.setattr(cli, "scan_file", mock_scan_file)

    cli.main()
    assert scanned_files == [(test_file, 1)]
