"""Bitwarden CSV import."""

import csv
from pathlib import Path
from typing import Dict, Any


class BitwardenCsv:
    """Write Bitwarden compatible CSV file."""

    def __init__(self, output_path: Path):
        self.file = output_path.open("w")
        self.writer = csv.writer(self.file, quoting=csv.QUOTE_MINIMAL)
        header = [
            "folder",
            "favorite",
            "type",
            "name",
            "notes",
            "fields",
            "reprompt",
            "login_uri",
            "login_username",
            "login_password",
            "login_totp",
        ]
        self.writer.writerow(header)

    def write_record(self, data: Dict[str, Any]) -> None:
        """Export data to CSV."""
        row = [
            data["folder"],
            "",  # favorite
            data["type"],
            data["name"],
            data["notes"],
            data["fields"],
            "",  # reprompt
            data["login_uri"],
            data["login_username"],
            data["login_password"],
            "",  # login_totp
        ]
        self.writer.writerow(row)

    def close(self) -> None:
        """Close the CSV file."""
        self.file.close()
