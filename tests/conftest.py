import pathlib
import uuid
from datetime import datetime, timezone, timedelta
from unittest.mock import patch

import pytest
from freezegun import freeze_time


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


fixed_now = datetime(2024, 3, 29, 9, 49, 23, 836557, tzinfo=timezone(timedelta(hours=1)))
fixed_uuid = uuid.UUID('12345678-1234-5678-1234-567812345678')


@pytest.fixture
def bitwarden_file():
    with freeze_time(fixed_now), patch('uuid.uuid4', return_value=fixed_uuid):
        yield  RESOURCES / "bitwarden_export.json"


@pytest.fixture
def bitwarden_notes_file():
    with freeze_time(fixed_now), patch('uuid.uuid4', return_value=fixed_uuid):
        yield  RESOURCES / "bitwarden_notes_export.json"


@pytest.fixture
def bitwarden_csv_file():
    return RESOURCES / "bitwarden_export.csv"


@pytest.fixture
def bitwarden_notes_csv_file():
    return RESOURCES / "bitwarden_notes_export.csv"