"""Bitwarden Import mSecure Export."""

import os
import csv
from pathlib import Path
from typing import List, Dict, Tuple

import rich_click as click

OUTPUT_FILE_DEFAULT = "bitwarden.csv"
NOTES_MODE = "notes"


@click.command()
@click.argument("input_file", type=click.Path(exists=True))  # ~/Downloads/mSecure Export File.csv
@click.argument("output_file", type=click.Path(), required=False)
@click.option("--force", is_flag=True, help="Overwrite the output file if it exists.")
@click.option(
    "--extra-fields",
    type=click.Choice(["custom-fields", NOTES_MODE]),
    default="custom-fields",
    help=(
        "How to handle mSecure fields that don't match Bitwarden fields."
        f"By default, they are added as custom fields. Use '{NOTES_MODE}' to add them to notes."
    ),
)
def bitwarden_import_msecure(
    input_file: str, output_file: str, force: bool, extra_fields: str
) -> None:
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
        raise click.Abort()

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
                writer.writerow(convert_row(row, extra_fields == NOTES_MODE))

    click.echo(f"Bitwarden CSV saved to {output_file}")


def convert_row(row: List[str], extra_fields_to_notes: bool) -> List[str]:
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
    fields = {}
    for field in row[4:]:
        parts = field.split("|")
        if parts[0] in field_values:
            if field_values[parts[0]]:
                print(f"Warning: Duplicate field `{parts[0]}` in row `{row}`.")
            field_values[parts[0]] = "|".join(parts[2:])
        elif any(value.strip() for value in parts[2:]):
            if extra_fields_to_notes:
                notes += f"\n{parts[0]}: {','.join(parts[2:])}"
            else:
                fields[parts[0]] = ",".join(parts[2:])
    password, username = get_creds(field_values, row)
    if field_values["Card Number"]:
        if tag:
            click.echo(f"Warning: Tag `{tag}` present for Card, override with `card`:\n{row}")
        tag = "card"
    if not username and not password and not field_values["Website"]:
        record_type = "note"
    if field_values["PIN"]:
        fields["PIN"] = field_values["PIN"]

    return [
        tag,  # folder
        "",  # favorite
        record_type,  # type
        name,  # name
        notes,  # notes
        "\n".join([f"{name}: {value}" for name, value in fields.items()]),  # fields
        "",  # reprompt
        field_values["Website"],  # login_uri
        username,  # login_username
        password,  # login_password
        "",  # login_totp
    ]


def get_creds(field_values: Dict[str, str], row: List[str]) -> Tuple[str, str]:
    """Get username and password."""
    username = field_values["Card Number"] or field_values["Username"]
    password = field_values["Security Code"] or field_values["Password"]
    if field_values["Card Number"] and field_values["Username"]:
        click.echo(f"Error: Both Card Number and Username present in row:\n{row}")
    if field_values["Security Code"] and field_values["Password"]:
        click.echo(f"Error: Both Security Code and Password present in row:\n{row}")
    return password, username


if __name__ == "__main__":  # pragma: no cover
    bitwarden_import_msecure()  # pylint: disable=no-value-for-parameter
