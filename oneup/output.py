"""
Collection of helper functions to format output of the tool
"""

from typing import Final, Optional

from termcolor import colored

ERROR_STR: Final[str] = colored("ERROR", "red", attrs=["bold"])
ONEUP_STR: Final[str] = colored("oneup", attrs=["bold"])
VERSION_MATCH_STR: Final[str] = colored("version match", "green", attrs=["bold"])
VERSION_MISMATCH_STR: Final[str] = colored("version mismatch", "yellow", attrs=["bold"])


def to_bold(string: str) -> str:
    """
    Turns a string into bold for the standard output
    """

    return colored(string, attrs=["bold"])


def style_requirements_specs(specs: list[tuple[str, ...]]) -> Optional[str]:
    """
    Styles a requirements.txt file's specs list to be printed
    """

    if not specs:
        return None

    if len(specs) == 1:
        op, version = specs[0]
        if op == "==":
            return version
        if op == "~=":
            return f"~={version}"

    return ", ".join(f"{op} {version}" for op, version in specs)
