import click.exceptions

from bitwarden_import_msecure.__about__ import __version__
from bitwarden_import_msecure.main import bitwarden_import_msecure
from click.testing import CliRunner


def test_version():
    assert __version__


def test_bitwarden_import_msecure_inplace(tmpdir, msecure_export, bitwarden_file):
    input_file = tmpdir.join("input.csv")
    input_file.write(msecure_export)

    runner = CliRunner()
    result = runner.invoke(bitwarden_import_msecure, [str(input_file)])

    assert result.exit_code == 0
    output_file = tmpdir.join("bitwarden.csv")
    assert output_file.read() == bitwarden_file.read_text()


def test_bitwarden_import_msecure_existing_output_file(tmpdir, msecure_export, bitwarden_file):
    input_file = tmpdir.join("input.txt")
    input_file.write(msecure_export)

    output_file = tmpdir.join("output.txt")
    output_file.write("existing data")

    runner = CliRunner()
    result = runner.invoke(bitwarden_import_msecure, [str(input_file), str(output_file)])
    assert "Output file" in result.output and "already exists" in result.output
    assert result.exception
    assert isinstance(result.exception, SystemExit)
    assert result.exception.code == 1


def test_bitwarden_import_msecure_to_output_file(tmpdir, msecure_export, bitwarden_file):
    input_file = tmpdir.join("input.txt")
    input_file.write(msecure_export)

    output_file = tmpdir.join("output.txt")
    output_file.write("existing data")

    runner = CliRunner()
    result = runner.invoke(bitwarden_import_msecure, [str(input_file), str(output_file), "--force"])

    assert result.exit_code == 0
    assert output_file.read() == bitwarden_file.read_text()
    assert input_file.read() == msecure_export  # Ensure input file remains unchanged
