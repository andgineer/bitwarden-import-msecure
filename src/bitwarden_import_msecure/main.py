"""Bitwarden Import mSecure Export."""

import csv
from pathlib import Path

import rich_click as click

from bitwarden_import_msecure.bitwarden_csv import BitwardenCsv
from bitwarden_import_msecure.bitwarden_json import BitwardenJson
from bitwarden_import_msecure.msecure import import_msecure_row
from bitwarden_import_msecure.__about__ import __version__
from bitwarden_import_msecure import patch_export

click.rich_click.USE_MARKDOWN = True


OUTPUT_FILE_DEFAULT = "bitwarden"
NOTES_MODE = "notes"


@click.command()
@click.version_option(version=__version__, prog_name="bitwarden-import-msecure")
@click.argument("input_file", type=click.Path(exists=True), required=False)
@click.argument("output_file", type=click.Path(), required=False)
@click.option("--force", is_flag=True, help="Overwrite the output file if it exists.")
@click.option(
    "--patch", is_flag=True, help="Fix old exports, see `--patch-help` for more details."
)
@click.option("--patch-help", is_flag=True, help="Show help for `--patch` option.")
@click.option(
    "--extra-fields",
    type=click.Choice(["custom-fields", NOTES_MODE]),
    default="custom-fields",
    help=(
        "How to handle mSecure fields that don't match Bitwarden fields."
        f"By default, they are added as custom fields. Use '{NOTES_MODE}' to add them to notes."
    ),
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["csv", "json"]),
    default="json",
    help="Output file format. JSON by default. CSV is legacy format with less features.",
)
def bitwarden_import_msecure(  # pylint: disable=too-many-arguments
    input_file: str,
    output_file: str,
    force: bool,
    patch: bool,
    extra_fields: str,
    output_format: str,
    patch_help: bool,
) -> None:
    """
    Converts file `INPUT_FILE` exported from mSecure to Bitwarden compatible format
    to `OUTPUT_FILE`.

    - Export CSV from mSecure
    - Run this script on the exported CSV file
    - Import the processed file into Bitwarden
    """
    if patch_help:
        patch_export.show_help()
        return

    input_path = Path(input_file)
    if not input_path.exists():
        click.echo(f"Input file `{input_path}` does not exist.")
        raise click.Abort()

    if force and patch:
        click.echo("--force and --patch cannot be used simultaneously.")
        raise click.Abort()

    output_path = (
        Path(output_file)
        if output_file
        else input_path.parent / f"{OUTPUT_FILE_DEFAULT}.{output_format}"
    )

    if patch:
        if not output_path.exists():
            click.echo(f"Cannot patch `{output_path}` - does not exists.")
            raise click.Abort()
        patch_export.patch(input_path, output_path)
    else:
        if output_path.exists() and not force:
            click.echo(f"Output file `{output_path}` already exists. Use --force to overwrite.")
            raise click.Abort()

        if output_format == "csv":
            writer = BitwardenCsv(output_path)
        else:
            writer = BitwardenJson(output_path)

        with input_path.open(newline="", encoding="utf-8") as infile:
            reader = csv.reader(infile, delimiter=",")
            for row in reader:
                if row and not row[0].startswith("mSecure"):
                    data = import_msecure_row(row, extra_fields == NOTES_MODE)
                    writer.write_record(data)

        writer.close()
    click.echo(f"File to import into Bitwarden saved to `{output_path}`")


if __name__ == "__main__":  # pragma: no cover
    bitwarden_import_msecure()  # pylint: disable=no-value-for-parameter
