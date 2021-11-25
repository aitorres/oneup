"""
Collection of helper functions to format output of the tool
"""

from typing import Final

from termcolor import colored

ERROR_STR: Final[str] = colored("ERROR", "red", attrs=["bold"])
ONEUP_STR: Final[str] = colored("oneup", attrs=["bold"])


def to_bold(string: str) -> str:
    """
    Turns a string into bold for the standard output
    """

    return colored(string, attrs=["bold"])
