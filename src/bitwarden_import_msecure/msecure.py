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
        tag = BANK_FOLDER
        # todo: record_type = "card"
    if not username and not password and not field_values["Website"]:
        record_type = "note"
    if field_values["PIN"]:
        fields["PIN"] = field_values["PIN"]

    return {
        "folder": tag,
        "type": record_type,
        "name": name,
        "notes": notes,
        "fields": "\n".join([f"{field_name}: {value}" for field_name, value in fields.items()]),
        "login_uri": field_values.get("Website", ""),
        "login_username": username,
        "login_password": password,
    }


def get_creds(field_values: Dict[str, str], row: List[str]) -> Tuple[str, str]:
    """Get username and password."""
    username = field_values["Card Number"] or field_values["Username"]
    password = field_values["Security Code"] or field_values["Password"]
    if field_values["Card Number"] and field_values["Username"]:
        click.echo(f"Error: Both Card Number and Username present in row:\n{row}")
    if field_values["Security Code"] and field_values["Password"]:
        click.echo(f"Error: Both Security Code and Password present in row:\n{row}")
    return password, username
