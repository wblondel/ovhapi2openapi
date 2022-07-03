from click.testing import CliRunner

from ovhapi2openapi.cli import main


def test_version() -> None:
    runner = CliRunner()
    result = runner.invoke(main, "--version")
    assert result.exit_code == 0
    assert "ovhapi2openapi, version" in result.output
