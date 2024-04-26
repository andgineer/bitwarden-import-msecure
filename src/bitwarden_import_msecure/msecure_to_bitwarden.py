"""Conversion logic."""

import csv
import json
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.theme import Theme

import rich_click as click

from bitwarden_import_msecure.bitwarden_csv import BitwardenCsv
from bitwarden_import_msecure.bitwarden_json import BitwardenJson
from bitwarden_import_msecure.msecure import import_msecure_row


def patch(input_path: Path, output_path: Path) -> None:
    """Fix errors in old exports.

    Some old versions of `bitwarden-import-msecure` worked incorrectly.
    For example versions before 1.5.0 did not export logins' URLs.

    If you migrated to Bitwarden some time ago and cannot just drop all records
    and import them again, use option `--patch`:

    - process the mSecure export `mSecure Export File.csv` with the new `bitwarden-import-msecure`:
        `bitwarden-import-msecure "mSecure Export File.csv" bitwarden.json`
    - export json from Bitwarden, let's name the result as `bitwarden_new.json`
    - patch this export with additional data from the mSecure export:
        `bitwarden-import-msecure bitwarden.json bitwarden_new.json --patch`
    - now you have `bitwarden_new.json` with all necessary changes, import it to Bitwarden
    """
    if not output_path.exists():
        click.echo(f"Output file `{output_path}` does not exist.")
        raise click.Abort()

    try:
        print(f"Reading input file: {input_path}..")
        with input_path.open("r") as file:
            input_data = json.load(file)
    except json.JSONDecodeError as e:
        print(f"Error: {input_path} is not a valid JSON file:\n{e}")
        return
    except FileNotFoundError as e:
        print(f"Error: {input_path} not found:\n{e}")
        return

    try:
        print(f"Reading output file: {output_path}..")
        with output_path.open("r+") as file:
            output_data = json.load(file)

            uri_dict = {}
            for item in input_data.get("items", []):
                if item.get("type") == 1:
                    uris = item.get("login", {}).get("uris", [])
                    if uris:
                        if item["name"] in uri_dict:
                            print(f"Name collision: {item['name']}, skipping..")
                        else:
                            uri_dict[item["name"]] = uris

            replaced = 0
            for item in output_data.get("items", []):
                if item.get("type") == 1 and (
                    item["name"] in uri_dict and not item.get("login", {}).get("uris", [])
                ):
                    item["login"]["uris"] = uri_dict[item["name"]]
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
        }
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
    input_path: Path, output_path: Path, *, output_format: str, extra_fields_to_notes: bool
) -> None:
    """Convert mSecure export to Bitwarden format."""
    if output_format == "csv":
        writer = BitwardenCsv(output_path)
    else:
        writer = BitwardenJson(output_path)
    with input_path.open(newline="", encoding="utf-8") as infile:
        reader = csv.reader(infile, delimiter=",")
        for row in reader:
            if row and not row[0].startswith("mSecure"):
                data = import_msecure_row(row, extra_fields_to_notes)
                writer.write_record(data)
    writer.close()
