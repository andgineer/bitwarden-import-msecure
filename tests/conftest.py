import pathlib

import pytest


def _get_repo_root_dir() -> str:
    """
    :return: path to the project folder.
    `tests/` should be in the same folder and this file should be in the root of `tests/`.
    """
    return str(pathlib.Path(__file__).parent.parent)


ROOT_DIR = _get_repo_root_dir()
RESOURCES = pathlib.Path(f"{ROOT_DIR}/tests/resources")


@pytest.fixture
def msecure_export():
    with open(RESOURCES / "mSecure Export File.csv") as f:
        return f.read()


@pytest.fixture
def bitwarden_file():
    return RESOURCES / "bitwarden_export.csv"


@pytest.fixture
def bitwarden_notes_file():
    return RESOURCES / "bitwarden_notes_export.csv"