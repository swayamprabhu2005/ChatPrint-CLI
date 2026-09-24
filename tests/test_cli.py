"""End-to-end CLI tests."""

from pathlib import Path

from click.testing import CliRunner

from ai_conversation import __version__
from ai_conversation.cli import cli


def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "convert" in result.output
    assert "inspect" in result.output
    assert "doctor" in result.output


def test_cli_convert_gemini(gemini_with_sidebar_mhtml: Path, tmp_path: Path):
    runner = CliRunner()
    out_dir = tmp_path / "cli_out"
    result = runner.invoke(cli, ["convert", str(gemini_with_sidebar_mhtml), "--output", str(out_dir)])

    assert result.exit_code == 0
    assert "PDF generated successfully" in result.output
    expected_pdf = out_dir / f"{gemini_with_sidebar_mhtml.stem}.pdf"
    assert expected_pdf.exists()


def test_cli_convert_chatgpt(chatgpt_multiturn_mhtml: Path, tmp_path: Path):
    runner = CliRunner()
    out_file = tmp_path / "custom_chatgpt.pdf"
    result = runner.invoke(cli, ["convert", str(chatgpt_multiturn_mhtml), "--output-file", str(out_file)])

    assert result.exit_code == 0
    assert "PDF generated successfully" in result.output
    assert out_file.exists()


def test_cli_convert_nonexistent_file(tmp_path: Path):
    runner = CliRunner()
    bad_path = tmp_path / "not_there.mhtml"
    result = runner.invoke(cli, ["convert", str(bad_path)])

    assert result.exit_code != 0


def test_cli_convert_empty_file(malformed_empty_mhtml: Path, tmp_path: Path):
    runner = CliRunner()
    result = runner.invoke(cli, ["convert", str(malformed_empty_mhtml)])

    assert result.exit_code != 0
    assert "Error:" in result.output
