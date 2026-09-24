"""Unit tests for input format detection and HTML/MHTML readers."""

from pathlib import Path

import pytest

from chatprint.errors import InvalidInputError, MHTMLParseError
from chatprint.input.detector import InputFormat, detect_format
from chatprint.input.html_reader import read_html_file
from chatprint.input.mhtml_reader import read_mhtml_file


def test_detect_format_html(gemini_simple_html: Path):
    fmt = detect_format(gemini_simple_html)
    assert fmt == InputFormat.HTML


def test_detect_format_mhtml(gemini_with_sidebar_mhtml: Path):
    fmt = detect_format(gemini_with_sidebar_mhtml)
    assert fmt == InputFormat.MHTML


def test_detect_format_missing_file(tmp_path: Path):
    missing = tmp_path / "does_not_exist.mhtml"
    with pytest.raises(InvalidInputError, match="not found"):
        detect_format(missing)


def test_read_html_file(gemini_simple_html: Path):
    doc = read_html_file(gemini_simple_html)
    assert "is kilowatt a good company" in doc.title
    assert "AI Overview" in doc.raw_html
    assert doc.soup.find("h2") is not None


def test_read_mhtml_file(gemini_with_sidebar_mhtml: Path):
    doc = read_mhtml_file(gemini_with_sidebar_mhtml)
    assert "is kilowatt a good company" in doc.title
    assert "https://www.google.com/search?q=is+kilowatt+a+good+company" in doc.snapshot_location
    assert "AI Overview" in doc.raw_html
    # Check that CSS resource was extracted
    assert any("styles.css" in loc for loc in doc.resources)


def test_read_mhtml_empty_file(malformed_empty_mhtml: Path):
    with pytest.raises(MHTMLParseError, match="empty"):
        read_mhtml_file(malformed_empty_mhtml)


def test_read_mhtml_corrupt_file(malformed_corrupt_mht: Path):
    with pytest.raises(MHTMLParseError):
        read_mhtml_file(malformed_corrupt_mht)
