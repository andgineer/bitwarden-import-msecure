"""Write Bitwarden compatible JSON file."""

import json
import uuid
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

BITWARDEN_TYPES = {"login": 1, "note": 2, "card": 3}


def now_string() -> str:
    """Return current time in Bitwarden format."""
    return datetime.now().astimezone().isoformat()


class BitwardenJson:
    """Write Bitwarden compatible JSON file."""

    data: Dict[str, Any]
    folder_ids: Dict[str, str]

    def __init__(self, output_path: Path):
        self.file = output_path
        self.data = {"encrypted": False, "folders": [], "items": []}
        self.folder_ids = {}

    @property
    def folders(self) -> Any:
        """Folder ID for the name.

        Creates a new folder if it doesn't exist.
        """
        parent = self

        class FolderManager:  # pylint: disable=too-few-public-methods
            """Dict like object."""

            def __getitem__(self, name: str) -> str:
                if name in parent.folder_ids:
                    return parent.folder_ids[name]
                folder_id = str(uuid.uuid4())
                parent.data["folders"].append({"id": folder_id, "name": name})
                parent.folder_ids[name] = folder_id
                return folder_id

        return FolderManager()

    def write_record(self, data: Dict[str, Any]) -> None:
        """Export data to JSON."""
        now = now_string()

        item = {
            "passwordHistory": None,
            "revisionDate": now,
            "creationDate": now,
            "deletedDate": None,
            "id": str(uuid.uuid4()),
            "organizationId": None,
            "folderId": self.folders[data["folder"]] if data["folder"] else None,
            "type": BITWARDEN_TYPES[data["type"]],
            "reprompt": 0,
            "name": data["name"],
            "notes": data["notes"],
            "favorite": False,
            "collectionIds": None,
        }
        if data["type"] == "login":
            item["login"] = {
                "fido2Credentials": [],
                "uris": [
                    {
                        "match": None,
                        "uri": data["login_uri"],
                    }
                ],
                "username": data["login_username"],
                "password": data["login_password"],
                "totp": None,
            }
            if not data["login_uri"]:
                item["login"]["uris"] = []
        if data["type"] == "card":
            exp_month, exp_year = (
                data["fields"].pop("Expiration Date", "").split("/") + ["", ""]
            )[:2]
            cardholder_name = data["fields"].pop("Name on Card", "") or data["fields"].pop(
                "Name", ""
            )
            item["card"] = {
                "cardholderName": cardholder_name,
                "brand": "",
                "number": data["login_username"],
                "expMonth": exp_month,
                "expYear": exp_year,
                "code": data["login_password"],
            }
        if data["type"] == "note":
            item["secureNote"] = {"type": 0}
        item["fields"] = [
            {
                "name": k,
                "value": v,
                "type": 1 if k in data["hidden_fields"] else 0,
                "linkedId": None,
            }
            for k, v in data["fields"].items()
        ]
        self.data["items"].append(item)

    def close(self) -> None:
        """Write the collected data to a JSON file."""
        with self.file.open("w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4)
