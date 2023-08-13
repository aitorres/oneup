"""
Collection of sanity tests for oneup module.
"""

from oneup import __version__


def test_version():
    """
    Tests that the oneup module is set to the correct version
    """

    assert __version__ == "0.2.1"
