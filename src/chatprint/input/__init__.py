"""Input parsing and file format detection for ChatPrint CLI."""

from chatprint.input.detector import InputFormat, detect_format
from chatprint.input.html_reader import HTMLDocument, read_html_file
from chatprint.input.mhtml_reader import MHTMLDocument, read_mhtml_file

__all__ = [
    "HTMLDocument",
    "InputFormat",
    "MHTMLDocument",
    "detect_format",
    "read_html_file",
    "read_mhtml_file",
]
