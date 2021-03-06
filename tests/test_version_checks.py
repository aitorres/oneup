"""
Unit tests collection for the helper functions that check a project's
versions on PyPI
"""

from dataclasses import dataclass
from typing import Any

import pytest

from oneup import version_checks


@dataclass(frozen=True)
class ResponseMock():
    """
    Wrapper to mock a `requests` response during unit tests
    """

    body: dict[str, Any]
    status_code: int = 200

    def json(self):
        """
        Returns the body of the response as a dictionary
        """

        return self.body


def test_get_project_latest_version(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Unit test that makes sure that the function that gets
    a package's latest version works as expected
    """

    monkeypatch.setattr(
        "requests.get",
        lambda _: ResponseMock(
            {},
            status_code=500
        )
    )
    assert version_checks.get_project_latest_version("project_name") is None

    monkeypatch.setattr(
        "requests.get",
        lambda _: ResponseMock(
            {},
            status_code=404
        )
    )
    assert version_checks.get_project_latest_version("project_name") is None

    monkeypatch.setattr(
        "requests.get",
        lambda _: ResponseMock(
            {
                "info": {
                    "version": "1.2.0"
                }
            }
        )
    )
    assert version_checks.get_project_latest_version("project_name") == "1.2.0"


def test_print_project_latest_version_for_python(
    capfd: pytest.CaptureFixture
) -> None:
    """
    Unit test to ensure that no project version is printed
    if the specified package is python
    """

    version_checks.print_project_latest_version("python")
    out, _ = capfd.readouterr()
    assert out == ""


def test_print_project_latest_version_for_right_version(
    monkeypatch: pytest.MonkeyPatch,
    capfd: pytest.CaptureFixture
) -> None:
    """
    Unit test to ensure that project versions are properly printed
    when they're successfully downloaded
    """

    monkeypatch.setattr(
        "requests.get",
        lambda _: ResponseMock(
            {
                "info": {
                    "version": "1.2.0"
                }
            }
        )
    )
    version_checks.print_project_latest_version("package-name")
    out, _ = capfd.readouterr()
    assert out == (
        "\x1b[1mpackage-name\x1b[0m's latest version is: \x1b[1m1.2.0\x1b[0m\n"
    )


def test_print_project_latest_version_for_invalid_version(
    monkeypatch: pytest.MonkeyPatch,
    capfd: pytest.CaptureFixture
) -> None:
    """
    Unit test to ensure that a warning message is printed if a
    package's version could not be found
    """

    monkeypatch.setattr(
        "requests.get",
        lambda _: ResponseMock(
            {},
            status_code=404
        )
    )
    version_checks.print_project_latest_version("package-name")
    out, _ = capfd.readouterr()
    assert out == "Could not get \x1b[1mpackage-name\x1b[0m's latest version\n"
