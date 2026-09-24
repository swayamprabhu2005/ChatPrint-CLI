"""Pytest configuration and shared fixtures for ChatPrint CLI."""

from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixtures_dir() -> Path:
    """Path to the test fixtures directory."""
    return FIXTURES_DIR


@pytest.fixture
def gemini_simple_html(fixtures_dir) -> Path:
    return fixtures_dir / "gemini" / "gemini_simple.html"


@pytest.fixture
def gemini_with_sidebar_mhtml(fixtures_dir) -> Path:
    return fixtures_dir / "gemini" / "gemini_search_with_sidebar.mhtml"


@pytest.fixture
def gemini_multiturn_html(fixtures_dir) -> Path:
    return fixtures_dir / "gemini" / "gemini_multiturn.html"


@pytest.fixture
def chatgpt_simple_html(fixtures_dir) -> Path:
    return fixtures_dir / "chatgpt" / "chatgpt_simple.html"


@pytest.fixture
def chatgpt_multiturn_mhtml(fixtures_dir) -> Path:
    return fixtures_dir / "chatgpt" / "chatgpt_multiturn.mhtml"


@pytest.fixture
def chatgpt_with_code_html(fixtures_dir) -> Path:
    return fixtures_dir / "chatgpt" / "chatgpt_with_code.html"


@pytest.fixture
def malformed_empty_mhtml(fixtures_dir) -> Path:
    return fixtures_dir / "malformed" / "empty.mhtml"


@pytest.fixture
def malformed_corrupt_mht(fixtures_dir) -> Path:
    return fixtures_dir / "malformed" / "corrupt.mht"
