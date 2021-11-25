"""
Collection of unit tests for formatting helpers
"""

from oneup import output


def test_constants() -> None:
    """
    Test that ensures that output constants are properly formatted
    """

    assert output.ERROR_STR == "\x1b[1m\x1b[31mERROR\x1b[0m"
    assert output.ONEUP_STR == "\x1b[1moneup\x1b[0m"


def test_to_bold() -> None:
    """
    Test that ensures that text is bolded properly
    """

    assert output.to_bold("this is a text") == "\x1b[1mthis is a text\x1b[0m"
