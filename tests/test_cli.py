from click.testing import CliRunner
from ovhapi2openapi.console.application import cli


def test_sync():
    runner = CliRunner()
    result = runner.invoke(cli, ['--debug', 'sync'])
    assert result.exit_code == 0
    assert 'Debug mode is on' in result.output
    assert 'Syncing' in result.output


def test_sync_no_debug():
    runner = CliRunner()
    result = runner.invoke(cli, ['sync'])
    assert result.exit_code == 0
    assert 'Debug mode is off' in result.output
    assert 'Syncing' in result.output
