"""
Helper module with functions that check a dependency's version
on the PyPI repository.
"""

from typing import Final, Optional

import requests

PYPI_API_PROJECT_URL: Final[str] = "https://pypi.org/pypi/{project_name}/json"


def get_project_latest_version(project_name: str) -> Optional[str]:
    """
    Attempts to request and return the latest version, given a project name
    in PyPI. Will return `None` if the version can't be fetched.
    """

    response = requests.get(
        PYPI_API_PROJECT_URL.format(project_name=project_name)
    )

    if response.status_code != 200:
        return None

    response_json = response.json()
    return response_json["info"]["version"]
