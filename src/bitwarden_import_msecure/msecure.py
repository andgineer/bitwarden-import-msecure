"""mSecure export parser."""

from typing import Dict, List, Tuple, Any
import rich_click as click


BANK_FOLDER = "bank"


def import_msecure_row(row: List[str], extra_fields_to_notes: bool) -> Dict[str, Any]:
    """Extract data from mSecure row."""
    name = row[0].split("|")[0]
    if len(row[0].split("|")) > 2:
        print(f"Warning: name has more than one '|' character :`{row[0]}`.")
    record_type = "login"
    if row[1].strip() not in ["Login", "Credit Card", "Email Account"]:
        print(f"Warning: record type is not 'Login' :`{row[1]}`.")
    tag = row[2].strip()
    special_fields, fields, notes = extract_fields(row, extra_fields_to_notes)
    notes_parts = [part for part in [row[3].replace("\\n", "\n"), notes] if part]
    notes = "\n".join(notes_parts)
    password, username = get_creds(special_fields, row)
    if special_fields["Card Number"]:
        if tag:
            click.echo(f"Warning: Tag `{tag}` present for Credit Card, ignored:\n{row}")
        else:
            tag = BANK_FOLDER
        record_type = "card"
    if not username and not password and not special_fields["Website"]:
        record_type = "note"
    if special_fields["PIN"]:
        fields["PIN"] = special_fields["PIN"]  # todo: place hidden fields to separate list

    return {
        "folder": tag,
        "type": record_type,
        "name": name,
        "notes": notes,
        "fields": fields,
        "login_uri": special_fields["Website"],
        "login_username": username,
        "login_password": password,
    }


def extract_fields(
    row: List[str], extra_fields_to_notes: bool
) -> Tuple[Dict[str, str], Dict[str, str], str]:
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


def get_creds(field_values: Dict[str, str], row: List[str]) -> Tuple[str, str]:
    """Get username and password."""
    username = field_values["Card Number"] or field_values["Username"]
    password = field_values["Security Code"] or field_values["Password"]
    if field_values["Card Number"] and field_values["Username"]:
        click.echo(f"Error: Both Card Number and Username present in row:\n{row}")
    if field_values["Security Code"] and field_values["Password"]:
        click.echo(f"Error: Both Security Code and Password present in row:\n{row}")
    return password, username
