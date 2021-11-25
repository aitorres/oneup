"""
Unit test collection for the command-line interface functions.
"""

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
