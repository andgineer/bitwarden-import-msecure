"""Bitwarden Import mSecure Export."""

from pathlib import Path

import rich_click as click
from rich.console import Console

from bitwarden_import_msecure.__about__ import __version__
from bitwarden_import_msecure import msecure_to_bitwarden

click.rich_click.USE_MARKDOWN = True


OUTPUT_FILE_DEFAULT = "bitwarden"
NOTES_MODE = "notes"


def error(message: str, show_patch_help: bool = True) -> None:
    """Print error message and exit."""
    console = Console()
    console.print(message, style="bold red")
    if show_patch_help:
        msecure_to_bitwarden.patch_help()
    raise click.Abort()


@click.command()
@click.version_option(version=__version__, prog_name="bitwarden-import-msecure")
@click.argument("input_file", type=click.Path(exists=True), required=False)
@click.argument("output_file", type=click.Path(), required=False)
@click.option("--force", is_flag=True, help="Overwrite the output file if it exists.")
@click.option(
    "--patch",
    is_flag=True,
    help="Patch Bitwarden export with data from mSecure export that previously was not imported. "
    "See `--patch-help` for more details.",
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
        msecure_to_bitwarden.patch_help()
        return

    if not input_file:
        error("No input file provided.")
    input_path = Path(input_file)
    if not input_path.exists():
        error(f"Input file `{input_path}` does not exist.")

    if force and patch:
        error("--force and --patch cannot be used simultaneously.")

    output_path = (
        Path(output_file)
        if output_file
        else input_path.parent / f"{OUTPUT_FILE_DEFAULT}.{output_format}"
    )

    if patch:
        if output_format != "json":
            error("Patching is only supported for JSON format.", show_patch_help=True)
        if not output_path.exists():
            error(
                f"Output file `{output_path}` does not exist. Cannot patch un-existed file.",
                show_patch_help=True,
            )
        msecure_to_bitwarden.patch(input_path, output_path)
    else:
        if output_path.exists() and not force:
            error(f"Output file `{output_path}` already exists. Use --force to overwrite.")

        msecure_to_bitwarden.convert(
            input_path,
            output_path,
            output_format=output_format,
            extra_fields_to_notes=extra_fields == NOTES_MODE,
        )
    click.echo(f"File to import into Bitwarden saved to `{output_path}`")


if __name__ == "__main__":  # pragma: no cover
    bitwarden_import_msecure()  # pylint: disable=no-value-for-parameter
