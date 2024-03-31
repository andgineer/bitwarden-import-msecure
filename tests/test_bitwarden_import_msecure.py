from bitwarden_import_msecure.__about__ import __version__
from bitwarden_import_msecure.main import bitwarden_import_msecure
from click.testing import CliRunner


def test_version():
    assert __version__


def test_version_option():
    runner = CliRunner()
    result = runner.invoke(bitwarden_import_msecure, ['--version'])
    assert result.exit_code == 0
    assert __version__ in result.output

