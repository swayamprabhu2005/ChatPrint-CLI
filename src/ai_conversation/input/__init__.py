"""Input parsing and file format detection for AI Conversation CLI."""

from ai_conversation.input.detector import InputFormat, detect_format
from ai_conversation.input.html_reader import HTMLDocument, read_html_file
from ai_conversation.input.mhtml_reader import MHTMLDocument, read_mhtml_file

__all__ = [
    "HTMLDocument",
    "InputFormat",
    "MHTMLDocument",
    "detect_format",
    "read_html_file",
    "read_mhtml_file",
]
