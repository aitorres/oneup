"""
Helper module with functions that check a dependency's version
on the PyPI repository.
"""

from typing import Final, Optional

import requests

from oneup.output import to_bold

PYPI_API_PROJECT_URL: Final[str] = "https://pypi.org/pypi/{project_name}/json"
REQUEST_TIMEOUT: Final[int] = 5


def get_project_latest_version_and_url(project_name: str) -> Optional[tuple[str, str]]:
    """
    Attempts to request and return the latest version, given a project name
    in PyPI. Will return `None` if the version can't be fetched.
    """

    response = requests.get(
        PYPI_API_PROJECT_URL.format(project_name=project_name),
        timeout=REQUEST_TIMEOUT
    )

    if response.status_code != 200:
        return None

    response_json = response.json()
    return (response_json["info"]["version"], response_json["info"]["home_page"])


def print_project_latest_version_and_url(project_name: str) -> None:
    """
    Given a project name, get its latest version from PyPI and
    prints it to the standard output
    """

    # skipping python for pyproject files
    if project_name == "python":
        return

    latest_version_url_tuple = get_project_latest_version_and_url(project_name)
    if latest_version_url_tuple is not None:
        latest_version, url = latest_version_url_tuple
        print(
            f"{to_bold(project_name)}'s latest version "
            f"is: {to_bold(latest_version)}" + (f" ({url})" if url else "")
        )
    else:
        print(
            f"Could not get {to_bold(project_name)}'s "
            "latest version"
        )
