from bitwarden_import_msecure.__about__ import __version__
from bitwarden_import_msecure.main import bitwarden_import_msecure


def test_version_option(runner):
    result = runner.invoke(bitwarden_import_msecure, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_force_and_patch_together(runner, tmp_path):
    dummy_input = tmp_path / "dummy_input.csv"
    dummy_input.touch()  # Create an empty file to satisfy existence check

    dummy_output = tmp_path / "dummy_output.json"
    dummy_output.touch()  # Create an empty file to potentially be patched

    result = runner.invoke(
        bitwarden_import_msecure, [str(dummy_input), str(dummy_output), "--force", "--patch"]
    )

    assert result.exit_code == 1
    assert "--force and --patch cannot be used simultaneously." in result.output


def test_patch_without_existing_output_file(runner, tmp_path):
    dummy_input = tmp_path / "dummy_input.csv"
    dummy_input.touch()  # Create an empty file to satisfy the input file existence check

    non_existent_output = tmp_path / "non_existent_output.json"

    result = runner.invoke(
        bitwarden_import_msecure, [str(dummy_input), str(non_existent_output), "--patch"]
    )

    assert result.exit_code == 1
    assert f"Output file `{non_existent_output}` does not exist." in result.output.replace("\n", "")


def test_patch_with_incorrect_format(runner, tmp_path):
    dummy_input = tmp_path / "dummy_input.csv"
    dummy_input.touch()  # Create an empty file

    incorrect_format_output = tmp_path / "output.csv"
    incorrect_format_output.touch()  # Ensure the file exists for the patch command

    result = runner.invoke(
        bitwarden_import_msecure,
        [str(dummy_input), str(incorrect_format_output), "--format", "csv", "--patch"],
    )

    assert result.exit_code == 1
    assert "Patching is only supported for JSON format." in result.output


def test_overwrite_without_force(runner, tmp_path):
    # Create a dummy input file to satisfy the input file check
    dummy_input = tmp_path / "dummy_input.csv"
    dummy_input.touch()  # Create an empty file

    # Create a file to attempt to overwrite
    test_output = tmp_path / "test_output.json"
    test_output.write_text("test content")  # create and write to the file

    # Run the command without --force, correctly setting input and output file arguments
    result = runner.invoke(
        bitwarden_import_msecure,
        [
            str(dummy_input),  # the input file
            str(test_output),  # the output file
            "--format",
            "json",  # specifying format explicitly if necessary
        ],
    )

    assert result.exit_code == 1, f"Expected exit code 1, got {result.exit_code}"
    assert "--force" in result.output.replace("\n", ""), (
        f"Expected error message not found in output: {result.output}"
    )
