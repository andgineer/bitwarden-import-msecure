"""mSecure export parser."""

from typing import Any

import rich_click as click

BANK_FOLDER = "bank"


def import_msecure_row(row: list[str], extra_fields_to_notes: bool) -> dict[str, Any]:
    """Extract data from mSecure CSV row."""
    name = row[0].split("|")[0]
    max_name_parts = 2
    if len(row[0].split("|")) > max_name_parts:
        print(f"Warning: name has more than one '|' character :`{row[0]}`.")
    record_type = "login"
    if row[1].strip() not in ["Login", "Credit Card", "Email Account"]:
        print(f"Warning: record type is not 'Login' :`{row[1]}`.")
    tag = row[2].strip()
    special_fields, fields, notes = extract_fields(row, extra_fields_to_notes)
    hidden_fields = []
    notes = "\n".join([part.replace("\\n", "\n") for part in [row[3], notes] if part.strip()])
    password, username = get_creds(special_fields, row)
    if special_fields["Card Number"]:
        if tag:
            click.echo(f"Warning: Tag `{tag}` present for Credit Card, ignored:\n{row}")
        else:
            tag = BANK_FOLDER
        record_type = "card"
    if "bank" in name.lower() and not tag:
        tag = BANK_FOLDER
    if not username and not password and not special_fields["Website"]:
        record_type = "note"
    if special_fields["PIN"]:
        fields["PIN"] = special_fields["PIN"]
        hidden_fields.append("PIN")

    return {
        "folder": tag,
        "type": record_type,
        "name": name,
        "notes": notes,
        "fields": fields,
        "hidden_fields": hidden_fields,  # names of fields to hide
        "login_uri": special_fields["Website"],
        "login_username": username,
        "login_password": password,
    }


def extract_fields(
    row: list[str],
    extra_fields_to_notes: bool,
) -> tuple[dict[str, str], dict[str, str], str]:
    """Extract fields from mSecure row.

    Return (special_fields, fields, notes)
    """
    special_fields = {
        "Website": "",
        "Username": "",
        "Password": "",
        "Card Number": "",
        "Security Code": "",
        "PIN": "",
    }
    fields = {}
    for field in row[4:]:
        parts = field.split("|")
        if parts[0] in special_fields:
            if special_fields[parts[0]]:
                print(f"Warning: Duplicate field `{parts[0]}` in row `{row}`.")
            special_fields[parts[0]] = "|".join(parts[2:])
        elif any(value.strip() for value in parts[2:]):
            fields[parts[0]] = ",".join(parts[2:])
    if extra_fields_to_notes:
        notes = "\n".join([f"{name}: {value}" for name, value in fields.items()])
        fields = {}
    else:
        notes = ""
    return special_fields, fields, notes


def get_creds(field_values: dict[str, str], row: list[str]) -> tuple[str, str]:
    """Get username and password."""
    username = field_values["Card Number"] or field_values["Username"]
    password = field_values["Security Code"] or field_values["Password"]
    if field_values["Card Number"] and field_values["Username"]:
        click.echo(f"Error: Both Card Number and Username present in row:\n{row}")
    if field_values["Security Code"] and field_values["Password"]:
        click.echo(f"Error: Both Security Code and Password present in row:\n{row}")
    return password, username
