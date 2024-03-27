"""Bitwarden Import mSecure Export."""

import os
import csv
from pathlib import Path
from typing import List

import rich_click as click

OUTPUT_FILE_DEFAULT = "bitwarden.csv"


@click.command()
@click.argument("input_file", type=click.Path(exists=True))  # ~/Downloads/mSecure Export File.csv
@click.argument("output_file", type=click.Path(), required=False)
@click.option("--force", is_flag=True, help="Overwrite the output file if it exists.")
def bitwarden_import_msecure(input_file: str, output_file: str, force: bool) -> None:
    """
    Converts file `INPUT_FILE` exported from mSecure to Bitwarden compatible format
    to `OUTPUT_FILE`.

    1.Export CSV from mSecure
    2.Run this script on the exported CSV file
    3.Import the processed file into Bitwarden a Bitwarden CSV
    """
    if not output_file:
        output_file = (Path(input_file).parent / OUTPUT_FILE_DEFAULT).as_posix()

    if os.path.exists(output_file) and not force:
        click.echo(f"Output file {output_file} already exists. Use --force to overwrite.")
        return

    with (
        open(input_file, newline="", encoding="utf-8") as infile,
        open(output_file, "w", newline="", encoding="utf-8") as outfile,
    ):
        reader = csv.reader(infile, delimiter=",")
        writer = csv.writer(outfile, quoting=csv.QUOTE_MINIMAL)

        # Bitwarden CSV header: https://bitwarden.com/help/condition-bitwarden-import/
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
        writer.writerow(header)

        for row in reader:
            if row and not row[0].startswith("mSecure"):
                writer.writerow(convert_row(row))

    click.echo(f"Bitwarden CSV saved to {output_file}")


def convert_row(row: List[str]) -> List[str]:
    """Convert mSecure row to Bitwarden row."""
    name = row[0].split("|")[0]
    if len(row[0].split("|")) > 2:
        print(f"Warning: name has more than one '|' character :`{row[0]}`.")
    record_type = "login"
    if row[1].strip() not in ["Login", "Credit Card", "Email Account"]:
        print(f"Warning: record type is not 'Login' :`{row[1]}`.")
    tag = row[2].strip()
    notes = row[3].replace("\\n", "\n")
    field_values = {
        "Website": "",
        "Username": "",
        "Password": "",
        "Card Number": "",
        "Security Code": "",
        "PIN": "",
        # "Name on Card": "",
        # "Expiration Date": "",
    }
    for field in row[4:]:
        parts = field.split("|")
        if parts[0] in field_values:
            if field_values[parts[0]]:
                print(f"Warning: Duplicate field `{parts[0]}` in row `{row}`.")
            field_values[parts[0]] = "|".join(parts[2:])
        elif any(value.strip() for value in parts[2:]):
            notes += f"\n{parts[0]}: {','.join(parts[2:])}"
    username = field_values["Card Number"] or field_values["Username"]
    password = field_values["Security Code"] or field_values["Password"]
    if field_values["Card Number"] and field_values["Username"]:
        click.echo(f"Error: Both Card Number and Username present in row: {row}")
    if field_values["Security Code"] and field_values["Password"]:
        click.echo(f"Error: Both Security Code and Password present in row: {row}")
    if field_values["Card Number"]:
        tag = "card"
    if not username and not password and not field_values["Website"]:
        record_type = "note"
    fields = f"PIN: {field_values['PIN']}" if field_values["PIN"] else ""  # todo: set hidden type

    return [
        tag,  # folder
        "",  # favorite
        record_type,  # type
        name,  # name
        notes,  # notes
        fields,  # fields
        "",  # reprompt
        field_values["Website"],  # login_uri
        username,  # login_username
        password,  # login_password
        "",  # login_totp
    ]


if __name__ == "__main__":
    bitwarden_import_msecure()  # pylint: disable=no-value-for-parameter
