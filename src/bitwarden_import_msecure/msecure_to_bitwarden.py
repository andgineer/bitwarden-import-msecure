"""Conversion logic."""

import csv
import json
from functools import reduce
from pathlib import Path
from typing import Optional

import rich_click as click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.theme import Theme

from bitwarden_import_msecure.bitwarden_csv import BitwardenCsv
from bitwarden_import_msecure.bitwarden_json import BitwardenJson
from bitwarden_import_msecure.msecure import import_msecure_row


def patch(input_path: Path, output_path: Path) -> None:  # noqa: C901
    """Patch Bitwarden export with data from mSecure export that previously was not imported

    Some old versions of `bitwarden-import-msecure` worked incorrectly.
    For example versions before 1.5.0 did not export logins' URLs.

    If you migrated to Bitwarden some time ago and cannot just drop all records
    and import them again, use option `--patch`:

    - export json from Bitwarden, let's name the result as `bitwarden_new.json`.
    please backup this file in case something goes wrong
    - patch this export with data from the mSecure export
        `bitwarden-import-msecure "mSecure Export File.csv" bitwarden_new.json --patch`
    - now you have `bitwarden_new.json` with additional data
    - unfortunately Bitwarden does not respect item IDs on import, so to avoid duplicates
    remove all items from Bitwarden, preferably using web interface.
    It is save as you have full backup in `bitwarden_new.json`
    - import bitwarden_new.json to Bitwarden as Bitwarden json file
    - clean up mSecure export file, `bitwarden_new.json` and it's backup
    """

    def get_row_dict(csv_row: list[str]) -> Optional[dict[str, str]]:
        """Get dict from mSecure CSV line."""
        if csv_row and not csv_row[0].startswith("mSecure"):
            row = import_msecure_row(csv_row, False)
            if row and row["type"] == "login":
                return {"type": "login", "login_uri": row["login_uri"], "name": row["name"]}
        return None

    def filter_logins_with_url(rows: list[dict[str, str]]) -> list[dict[str, str]]:
        """Filter logins with non-empty URL."""
        return list(
            filter(lambda x: x is not None and x["type"] == "login" and x["login_uri"], rows),
        )

    def reduce_to_uri_dict(rows: list[dict[str, str]]) -> dict[str, str]:
        """Reduce list of logins' dicts to dict with login name as key and login URL as value."""

        def reduce_reporting_name_collisions(
            acc: dict[str, str],
            row: dict[str, str],
        ) -> dict[str, str]:
            if row["name"] in acc and acc[row["name"]] != row["login_uri"]:
                print(
                    f"Name collision: item `{row['name']}`, has different URLs: "
                    f"`{acc[row['name']]}` and `{row['login_uri']}`.\n"
                    f"Using first one.",
                )
            else:
                acc[row["name"]] = row["login_uri"]
            return acc

        return reduce(reduce_reporting_name_collisions, rows, {})

    if not output_path.exists():
        click.echo(f"Output file `{output_path}` does not exist.")
        raise click.Abort()

    try:
        print(f"Reading output file: {output_path}..")
        with output_path.open("r+") as file:
            output_data = json.load(file)

            with input_path.open(newline="", encoding="utf-8") as infile:
                reader = csv.reader(infile, delimiter=",")
                rows = [row for row in map(get_row_dict, reader) if row is not None]
                uri_dict = reduce_to_uri_dict(filter_logins_with_url(rows))

            replaced = 0
            for item in output_data.get("items", []):
                if item.get("type") == 1 and (
                    item["name"] in uri_dict and not item.get("login", {}).get("uris", [])
                ):
                    item["login"]["uris"] = [{"match": None, "uri": uri_dict[item["name"]]}]
                    replaced += 1
            click.echo(f"Added {replaced} URLs.")

            file.seek(0)
            json.dump(output_data, file, indent=4)
            file.truncate()

    except json.JSONDecodeError as e:
        print(f"Error: {output_path} is not a valid JSON file:\n{e}")
        return
    except FileNotFoundError as e:
        print(f"Error: {output_path} not found:\n{e}")
        return


def patch_help() -> None:
    """Show help message for `--patch` option."""
    custom_theme = Theme(
        {
            "markdown.heading": "bold magenta",  # Styling for headings
            "markdown.code": "bold",  # Code blocks often stand out
            "markdown.list": "dim",  # Lists are usually less emphasized
            "markdown.block_quote": "italic",  # Block quotes may be italicized
            "markdown.link": "underline blue",  # Links can be underlined and blue
            "markdown.italic": "italic",  # Explicit style for italic text
            "markdown.bold": "bold",  # Explicit style for bold text
        },
    )
    console = Console(theme=custom_theme)
    assert patch.__doc__
    lines = [line.strip() for line in patch.__doc__.strip().split("\n")]
    title = lines[0]
    markdown_content = "\n".join(lines[2:])  # Skip title and empty line
    markdown = Markdown(markdown_content)
    panel = Panel(markdown, title=title, border_style="gray46")

    console.print(panel)


def convert(
    input_path: Path,
    output_path: Path,
    *,
    output_format: str,
    extra_fields_to_notes: bool,
) -> None:
    """Convert mSecure export to Bitwarden format."""
    writer = BitwardenCsv(output_path) if output_format == "csv" else BitwardenJson(output_path)
    with input_path.open(newline="", encoding="utf-8") as infile:
        reader = csv.reader(infile, delimiter=",")
        for row in reader:
            if row and not row[0].startswith("mSecure"):
                data = import_msecure_row(row, extra_fields_to_notes)
                writer.write_record(data)
    writer.close()
