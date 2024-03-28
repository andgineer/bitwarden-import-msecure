import click.exceptions

from bitwarden_import_msecure.__about__ import __version__
from bitwarden_import_msecure.main import bitwarden_import_msecure
from click.testing import CliRunner


def test_version():
    assert __version__


def assert_files_context_is_equal(file_path1, file_path2):
    """Compare the content of two files, abstracting away platform differences in newline characters."""
    with open(file_path1, 'r', newline=None, encoding='utf-8') as f1, open(file_path2, 'r', newline=None,
                                                                           encoding='utf-8') as f2:
        lines1 = f1.readlines()
        lines2 = f2.readlines()

        lines1 = [line.replace('\r\n', '\n').replace('\r', '\n') for line in lines1 if line.strip()]
        lines2 = [line.replace('\r\n', '\n').replace('\r', '\n') for line in lines2 if line.strip()]
        assert lines1 == lines2


def test_bitwarden_import_msecure_default_output(tmpdir, msecure_export, bitwarden_file):
    input_file = tmpdir.join("input.csv")
    input_file.write(msecure_export)

    runner = CliRunner()
    result = runner.invoke(bitwarden_import_msecure, [str(input_file)])
    assert result.exit_code == 0

    output_file = tmpdir.join("bitwarden.csv")

    # bitwarden_file.write_text(output_file.read_text(encoding="utf8"))  # uncomment to refresh the expected output
    assert_files_context_is_equal(output_file, bitwarden_file)


def test_bitwarden_import_msecure_note_mode_default_output(tmpdir, msecure_export, bitwarden_notes_file):
    input_file = tmpdir.join("input.csv")
    input_file.write(msecure_export)

    runner = CliRunner()
    result = runner.invoke(bitwarden_import_msecure, [str(input_file), "--extra-fields", "notes"])
    assert result.exit_code == 0

    output_file = tmpdir.join("bitwarden.csv")

    # bitwarden_notes_file.write_text(output_file.read_text(encoding="utf8"))  # uncomment to refresh the expected output
    assert_files_context_is_equal(output_file, bitwarden_notes_file)


def test_bitwarden_import_msecure_existing_output_file(tmpdir, msecure_export, bitwarden_file):
    input_file = tmpdir.join("input.txt")
    input_file.write(msecure_export)

    output_file = tmpdir.join("output.txt")
    output_file.write("existing data")

    runner = CliRunner()
    result = runner.invoke(bitwarden_import_msecure, [str(input_file), str(output_file)])
    assert result.exit_code == 1
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

    assert_files_context_is_equal(output_file, bitwarden_file)
    assert input_file.read() == msecure_export  # Ensure input file remains unchanged
