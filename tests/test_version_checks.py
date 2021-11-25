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
