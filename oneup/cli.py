"""
Functions and other helpers for `oneup`'s command-line interface.
"""

import argparse
import os
import sys
from pathlib import Path
from threading import Thread
from typing import Any, Final, MutableMapping, Optional

import requirements
import toml
from oneup.output import ERROR_STR, ONEUP_STR, style_requirements_specs, to_bold
from oneup.version_checks import print_project_latest_version_and_url

REQUIREMENTS_TXT: Final[str] = "requirements.txt"
REQUIREMENTS_DEV_TXT: Final[str] = "requirements_dex.txt"
PYPROJECT_TOML: Final[str] = "pyproject.toml"
SUPPORTED_REQUIREMENT_FILES: Final[list[str]] = [
    REQUIREMENTS_TXT,
    REQUIREMENTS_DEV_TXT,
    PYPROJECT_TOML,
]


def discover_all_requirement_files() -> list[Path]:
    """
    Attempts to discover and return a list of possible
    requirement files.
    """

    current_path_files = [f for f in os.listdir() if os.path.isfile(f)]

    return [Path(f) for f in current_path_files if f in SUPPORTED_REQUIREMENT_FILES]


def is_valid_idx(maybe_idx: str, min_value: int, max_value: int) -> bool:
    """
    Given a potential index as a string, and a range of values, determines
    if the string is castable to an integer and if said integer stays
    within the range (inclusive of the min value, exclusive of the max value)
    """

    if not maybe_idx.isdigit():
        return False

    return min_value <= int(maybe_idx) < max_value


def discover_requirement_file(interactive_mode: bool) -> Optional[Path]:
    """
    Potentially returns the path to a supported requirements file
    to be used as the main file for the tool's run.

    If more than one file is discovered, either asks the user to choose
    the file to be used (if interactive mode is on) or selects the first
    one.
    """

    potential_files = discover_all_requirement_files()

    if not potential_files:
        return None

    if len(potential_files) == 1:
        return potential_files[0]

    print(
        f"{ONEUP_STR} has discovered more than one requirements file in "
        "the current directory:",
        end="\n\n",
    )

    for idx, potential_file in enumerate(potential_files):
        print(f"({idx}) {potential_file}")

    if not interactive_mode:
        first_file: Path = potential_files[0]
        print(f"\n`{first_file}` will be selected automatically.")
        return first_file

    amount_of_potential_files = len(potential_files)
    maybe_idx: str = input("Please select an option by entering its number: ")
    while not is_valid_idx(maybe_idx, 0, amount_of_potential_files):
        maybe_idx = input("Invalid input. Please try again: ")

    return potential_files[int(maybe_idx)]


def get_dependencies_from_pyproject_file(
    parsed_toml: MutableMapping[str, Any]
) -> list[tuple[str, Optional[str]]]:
    """
    Given a parsed pyproject file (in toml format), returns a list of all the
    dependencies included in said file according to PEP-621
    """

    # according to PEP 621, dependencies should be located in either
    # `requires` (flit), `tool.poetry.dependencies` (poetry),
    # `install_requires` (setuptools) or `dependencies`
    for key in ["dependencies", "install_requires", "requires"]:
        if key in parsed_toml:
            return list(parsed_toml[key].items())

    dependencies: list[tuple[str, Optional[str]]] = []
    if "tool" in parsed_toml:

        tool_specs: MutableMapping[str, Any] = parsed_toml["tool"]
        if "poetry" in tool_specs:
            poetry_specs: MutableMapping[str, Any] = tool_specs["poetry"]

            for key in ("dependencies", "dev-dependencies"):
                if key in poetry_specs:
                    dependencies.extend(list(poetry_specs[key].items()))

            if "group" in poetry_specs:
                for _, group_dependencies in poetry_specs["group"].items():
                    dependencies.extend(
                        list(group_dependencies["dependencies"].items())
                    )

    return flatten_dependencies(dependencies)


def flatten_dependencies(
    dependencies: list[tuple[str, Optional[str]]]
) -> list[tuple[str, Optional[str]]]:
    """
    Flattens a list of dependencies by selecting versions
    inside dictionaries, if any
    """

    for idx, (name, version) in enumerate(dependencies):
        if isinstance(version, dict):
            dependencies[idx] = (name, version["version"])

    return dependencies


def scan_dependency_list(dependencies: list[tuple[str, Optional[str]]]) -> None:
    """
    Scans a list of dependencies and queries for their latest version
    """

    for dependency in dependencies:
        name, version = dependency
        print_project_latest_version_and_url(name, version)


def scan_file(requirements_file_path: Path, n_threads: int) -> None:
    """
    Scans a supported requirements file to check for dependencies
    and query for their latest version
    """

    file_name = requirements_file_path.name
    if file_name in (REQUIREMENTS_TXT, REQUIREMENTS_DEV_TXT):
        with open(requirements_file_path, "r", encoding="utf8") as requirements_file:
            parsed_file = requirements.parse(requirements_file)
            dependencies: list[tuple[str, Optional[str]]] = [
                (req["name"], style_requirements_specs(req["specs"]))
                for req in parsed_file
            ]

    elif file_name == PYPROJECT_TOML:
        parsed_toml = toml.load(requirements_file_path)
        dependencies = get_dependencies_from_pyproject_file(parsed_toml)

    else:
        print(f"{ERROR_STR}: Unsupported requirements file!")
        sys.exit(1)

    # Start threads to query PyPI
    threads: list[Thread] = []
    for i in range(n_threads):
        thread = Thread(
            target=scan_dependency_list,
            args=[dependencies[i::n_threads]],
        )
        threads.append(thread)
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()


def get_parser() -> argparse.ArgumentParser:
    """
    Generate and return a parser for the CLI tool
    """
    parser = argparse.ArgumentParser(
        prog="oneup",
        description="A CLI tool to check for dependency updates for Python",
        epilog="Happy coding! :-)",
    )
    parser.add_argument(
        "--file",
        metavar="FILE",
        type=Path,
        help=(
            "Path to a supported requirements file. "
            "If not provided, will be detected automatically from the "
            "current directory."
        ),
    )
    parser.add_argument(
        "--threads",
        metavar="T",
        type=int,
        default=1,
        help="Number of threads to use for querying PyPI (default: 1)",
    )
    parser.add_argument(
        "--no-input",
        action="store_false",
        dest="interactive_mode",
        help="Deactivate interactive mode (no input will be required)",
    )

    parser.set_defaults(interactive_mode=True)

    return parser


def main() -> None:
    """
    Run the tool's CLI
    """

    parser = get_parser()
    args = parser.parse_args()
    interactive_mode: bool = args.interactive_mode
    n_threads: int = args.threads

    # Determine file that will be scanned
    maybe_file_path: Optional[Path] = args.file

    if maybe_file_path is None:
        maybe_file_path = discover_requirement_file(interactive_mode)
    if maybe_file_path is None:
        print(
            f"{ERROR_STR}: no suitable requirements file detected "
            "in current directory!"
        )
        sys.exit(1)

    file_path = maybe_file_path
    print(f"{ONEUP_STR} will scan {to_bold(str(file_path))} for updates")
    scan_file(file_path, n_threads)


if __name__ == "__main__":
    main()
