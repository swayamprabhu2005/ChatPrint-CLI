"""Integration tests for inspect and doctor CLI commands."""

from pathlib import Path

from click.testing import CliRunner

from ai_conversation.cli import cli


def test_cli_inspect_gemini(gemini_with_sidebar_mhtml: Path):
    runner = CliRunner()
    result = runner.invoke(cli, ["inspect", str(gemini_with_sidebar_mhtml)])

    assert result.exit_code == 0
    assert "Google Gemini AI Mode" in result.output
    assert "MHTML" in result.output
    assert "User messages:" in result.output
    assert "Assistant messages:" in result.output


def test_cli_inspect_chatgpt(chatgpt_multiturn_mhtml: Path):
    runner = CliRunner()
    result = runner.invoke(cli, ["inspect", str(chatgpt_multiturn_mhtml)])

    assert result.exit_code == 0
    assert "ChatGPT" in result.output
    assert "Total messages:" in result.output
    assert "4" in result.output


def test_cli_doctor():
    runner = CliRunner()
    result = runner.invoke(cli, ["doctor"])

    assert result.exit_code == 0
    assert "Python:" in result.output
    assert "Platform:" in result.output
    assert "PDF engine:" in result.output
    assert "System ready." in result.output
