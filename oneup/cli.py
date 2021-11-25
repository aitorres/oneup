"""
Functions and other helpers for `oneup`'s command-line interface.
"""


import argparse


def get_parser() -> argparse.ArgumentParser:
    """
    Generate and return a parser for the CLI tool
    """
    parser = argparse.ArgumentParser(
        prog="oneup",
        description="A CLI tool to check for dependency updates for Python",
        epilog="Happy coding! :-)"
    )
    return parser


def main() -> None:
    """
    Run the tool's CLI
    """

    parser = get_parser()
    parser.parse_args()


if __name__ == "__main__":
    main()
