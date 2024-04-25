"""Fix errors in old exports."""

import json
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.theme import Theme

import rich_click as click


def patch(input_path: Path, output_path: Path) -> None:
    """Fix errors in old exports.

    Some old versions of `bitwarden-import-msecure` worked incorrectly.
    For example versions before 1.5.0 did not export logins' URLs.

    If you migrated to Bitwarden some time ago and cannot just drop all records
    and import them again, use option `--patch`:

    - process mSecure export `mSecure Export File.csv` with new `bitwarden-import-msecure`:
        `bitwarden-import-msecure "mSecure Export File.csv" bitwarden.json`
    - export json from Bitwarden, lets name result as `bitwarden_new.json`
    - patch this export with additional data from mSecure export:
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
            json.dump(output_data, file, indent=2)
            file.truncate()

    except json.JSONDecodeError as e:
        print(f"Error: {output_path} is not a valid JSON file:\n{e}")
        return
    except FileNotFoundError as e:
        print(f"Error: {output_path} not found:\n{e}")
        return


def show_help() -> None:
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
    doc = "\n".join([line.lstrip() for line in patch.__doc__.split("\n")])
    syntax = Syntax(doc, "markdown", word_wrap=True, background_color="default")
    panel = Panel(syntax, border_style="gray46")
    console.print(panel)
