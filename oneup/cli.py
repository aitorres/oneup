"""
Functions and other helpers for `oneup`'s command-line interface.
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Final, Optional

from oneup.output import ERROR_STR, ONEUP_STR, to_bold

SUPPORTED_REQUIREMENT_FILES: Final[list[str]] = [
    "requirements.txt",
    "pyproject.toml",
]


def discover_all_requirement_files() -> list[Path]:
    """
    Attempts to discover and return a list of possible
    requirement files.
    """

    current_path_files = [f for f in os.listdir() if os.path.isfile(f)]

    return [
        Path(f)
        for f in current_path_files
        if f in SUPPORTED_REQUIREMENT_FILES
    ]


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
        end="\n\n"
    )

    for idx, potential_file in enumerate(potential_files):
        print(f"({idx}) {potential_file}")

    if not interactive_mode:
        print("\nThe first file will be selected automatically.")
        return potential_files[0]

    amount_of_potential_files = len(potential_files)
    maybe_idx: str = input("Please select an option by entering its number: ")
    while not is_valid_idx(maybe_idx, 0, amount_of_potential_files):
        maybe_idx = input("Invalid input. Please try again: ")

    return potential_files[int(maybe_idx)]


def get_parser() -> argparse.ArgumentParser:
    """
    Generate and return a parser for the CLI tool
    """
    parser = argparse.ArgumentParser(
        prog="oneup",
        description="A CLI tool to check for dependency updates for Python",
        epilog="Happy coding! :-)"
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
        "--no-input",
        action="store_false",
        dest="interactive_mode",
        help="Deactivate interactive mode (no input will be required)",
    )

    parser.set_defaults(
        interactive_mode=True
    )

    return parser


def main() -> None:
    """
    Run the tool's CLI
    """

    parser = get_parser()
    args = parser.parse_args()
    interactive_mode: bool = args.interactive_mode

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


if __name__ == "__main__":
    main()
